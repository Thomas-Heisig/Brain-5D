"use strict";

function escapeChat(value) {
  const node = document.createElement('div');
  node.textContent = value;
  return node.innerHTML;
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
      log.insertAdjacentHTML('beforeend', `<div class="chat-message assistant"><strong>Research AI · grounded in Research + Docs</strong><p>${escapeChat(payload.answer || '')}</p></div>`);
    } catch (error) {
      log.insertAdjacentHTML('beforeend', `<div class="chat-message error"><strong>Unavailable</strong><p>${escapeChat(error.message)}</p></div>`);
    }
    log.scrollTop = log.scrollHeight;
  });
}