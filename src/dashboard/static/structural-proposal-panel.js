"use strict";

function byId(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  if (!value) return "";
  const div = document.createElement("div");
  div.textContent = String(value);
  return div.innerHTML;
}

/**
 * Owns structural proposal rendering and approval actions.
 */
export class StructuralProposalPanel {
  constructor({ api, logger, onChanged = async () => {} }) {
    this.api = api;
    this.logger = logger;
    this.onChanged = onChanged;
    this.commandInFlight = false;
    this.proposals = [];
    this.handleApprove = this.handleApprove.bind(this);
    this.handleReject = this.handleReject.bind(this);
  }

  async load() {
    try {
      const data = await this.api.getProposals();
      this.proposals = data.proposals || [];
      this.render(this.proposals);
    } catch (error) {
      this.logger.log(`⚠️ Failed to load proposals: ${error.message}`, "warning");
    }
  }

  render(proposals) {
    const container = byId("b5d-proposals");
    if (!container) return;
    if (!proposals || proposals.length === 0) {
      container.innerHTML = '<div class="proposal-empty">No pending proposals</div>';
      return;
    }

    container.innerHTML = proposals.map((proposal) => {
      const confidence = (proposal.confidence || 0) * 100;
      const id = escapeHtml(proposal.proposal_id);
      return `
        <div class="proposal-item" data-id="${id}">
          <span class="proposal-kind">${escapeHtml(proposal.kind || "unknown")}</span>
          <span class="proposal-desc">Neuron ${proposal.neuron_id || "?"} → ${proposal.target_id || "?"}</span>
          <span class="proposal-conf" style="--conf: ${confidence}%">${confidence.toFixed(0)}%</span>
          <span class="proposal-reason">${escapeHtml(proposal.reason || "")}</span>
          <div class="proposal-actions">
            <button class="btn-approve" data-id="${id}">✓ Approve</button>
            <button class="btn-reject" data-id="${id}">✗ Reject</button>
          </div>
        </div>
      `;
    }).join("");

    container.querySelectorAll(".btn-approve").forEach((button) => {
      button.addEventListener("click", () => this.handleApprove(button.dataset.id));
    });
    container.querySelectorAll(".btn-reject").forEach((button) => {
      button.addEventListener("click", () => this.handleReject(button.dataset.id));
    });
  }

  async handleApprove(proposalId) {
    await this.execute(proposalId, "approve", () => this.api.approveProposal(proposalId));
  }

  async handleReject(proposalId) {
    await this.execute(proposalId, "reject", () => this.api.rejectProposal(proposalId));
  }

  async execute(proposalId, action, request) {
    if (this.commandInFlight) {
      this.logger.log("⏳ Command in progress...", "warning");
      return;
    }
    this.commandInFlight = true;
    this.logger.log(`${action === "approve" ? "✓ Approving" : "✗ Rejecting"} proposal ${proposalId}...`, "info");
    try {
      const result = await request();
      if (result.ok) {
        this.logger.log(`✅ Proposal ${proposalId} ${action}d`, "success");
        await this.load();
        await this.onChanged();
      } else {
        this.logger.log(`❌ Failed to ${action}: ${result.message || "Unknown error"}`, "error");
      }
    } catch (error) {
      this.logger.log(`❌ Failed to ${action}: ${error.message}`, "error");
    } finally {
      this.commandInFlight = false;
    }
  }
}
