"use strict";

function escapeChat(value) {
  const node = document.createElement('div');
  node.textContent = value;
  return node.innerHTML;
}

function renderMarkdown(value) {
  let html = escapeChat(value.trim());
  html = html.replace(/^### (.+)$/gm, '<h5>$1</h5>');
  html = html.replace(/^## (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^# (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^[-*] (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (items) => `<ul>${items}</ul>`);
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  return html.replace(/\n{2,}/g, '</p><p>').replace(/\n/g, '<br>');
}

export function initResearchChat() {
  const form = document.getElementById('research-chat-form');
  const input = document.getElementById('research-chat-input');
  const log = document.getElementById('research-chat-log');
  if (!form || !input || !log) return;
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;
    log.querySelector('.chat-empty')?.remove();
    log.insertAdjacentHTML('beforeend', `<div class="chat-message user"><strong>You</strong><p>${escapeChat(message)}</p></div>`);
    input.value = '';
    try {
      const response = await fetch('/api/research/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message}) });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
      log.insertAdjacentHTML('beforeend', `<div class="chat-message assistant"><strong>Research AI · grounded in Research + Docs</strong><div class="chat-markdown"><p>${renderMarkdown(payload.answer || '')}</p></div></div>`);
    } catch (error) {
      log.insertAdjacentHTML('beforeend', `<div class="chat-message error"><strong>Unavailable</strong><p>${escapeChat(error.message)}</p></div>`);
    }
    log.scrollTop = log.scrollHeight;
  });
}