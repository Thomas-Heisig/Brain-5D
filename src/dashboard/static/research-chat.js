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

const STORAGE_KEY = 'brain5d.research-chat.rooms.v1';

function createRoom() {
  return { id: crypto.randomUUID(), title: 'Neuer Chat', messages: [] };
}

function loadState() {
  try {
    const state = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    if (Array.isArray(state.rooms) && state.rooms.length) {
      return { rooms: state.rooms, activeId: state.activeId || state.rooms[0].id };
    }
  } catch (_) {
    // Reset invalid local state below.
  }
  const room = createRoom();
  return { rooms: [room], activeId: room.id };
}

function saveState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function initResearchChat() {
  const form = document.getElementById('research-chat-form');
  const input = document.getElementById('research-chat-input');
  const log = document.getElementById('research-chat-log');
  const modal = document.getElementById('research-chat');
  const toggle = document.getElementById('chat-toggle');
  const close = document.getElementById('chat-close');
  const roomList = document.getElementById('chat-room-list');
  const newRoom = document.getElementById('chat-room-new');
  const childRoom = document.getElementById('chat-room-child');
  const settingsToggle = document.getElementById('chat-settings-toggle');
  const settings = document.getElementById('chat-settings');
  const settingsRefresh = document.getElementById('chat-settings-refresh');
  const settingsSave = document.getElementById('chat-settings-save');
  const webSearch = document.getElementById('chat-web-search');
  if (!form || !input || !log || !modal || !toggle || !close || !roomList || !newRoom || !childRoom || !settingsToggle || !settings || !settingsRefresh || !settingsSave || !webSearch) return;
  const state = loadState();
  webSearch.checked = state.webSearchEnabled === true;

  function activeRoom() {
    return state.rooms.find((room) => room.id === state.activeId) || state.rooms[0];
  }

  function render() {
    roomList.innerHTML = state.rooms.map((room) => `<button type="button" class="chat-room${room.id === state.activeId ? ' active' : ''}${room.parentId ? ' child' : ''}" data-room-id="${escapeChat(room.id)}">${room.parentId ? '↳ ' : ''}${escapeChat(room.title)}</button>`).join('');
    log.innerHTML = '';
    const room = activeRoom();
    if (!room.messages.length) {
      log.innerHTML = '<p class="chat-empty">Stelle eine Frage zu Research, Dokumentation oder registrierten Experimenten.</p>';
      return;
    }
    room.messages.forEach((message) => {
      const content = message.role === 'assistant' ? `<div class="chat-markdown"><p>${renderMarkdown(message.content)}</p></div>` : `<p>${escapeChat(message.content)}</p>`;
      log.insertAdjacentHTML('beforeend', `<div class="chat-message ${message.role}"><strong>${message.role === 'assistant' ? 'Research AI · grounded in Research + Docs' : 'You'}</strong>${content}</div>`);
    });
  }

  function open() {
    modal.hidden = false;
    toggle.setAttribute('aria-expanded', 'true');
    input.focus();
  }

  function closeChat() {
    modal.hidden = true;
    toggle.setAttribute('aria-expanded', 'false');
  }

  toggle.setAttribute('aria-expanded', 'false');
  toggle.addEventListener('click', open);
  close.addEventListener('click', closeChat);
  modal.addEventListener('click', (event) => { if (event.target === modal) closeChat(); });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && !modal.hidden) closeChat(); });
  roomList.addEventListener('click', (event) => {
    const button = event.target.closest('[data-room-id]');
    if (!button) return;
    state.activeId = button.dataset.roomId;
    saveState(state);
    render();
  });
  newRoom.addEventListener('click', () => {
    const room = createRoom();
    state.rooms.unshift(room);
    state.activeId = room.id;
    saveState(state);
    render();
    input.focus();
  });
  childRoom.addEventListener('click', () => {
    const room = createRoom();
    room.title = `Unterchat: ${activeRoom().title}`.slice(0, 32);
    room.parentId = activeRoom().id;
    state.rooms.splice(state.rooms.indexOf(activeRoom()) + 1, 0, room);
    state.activeId = room.id;
    saveState(state);
    render();
    input.focus();
  });
  async function loadSettings() {
    try {
      const response = await fetch('/api/research/chat/settings');
      const payload = await response.json();
      document.getElementById('chat-setting-provider').value = payload.provider || '';
      document.getElementById('chat-setting-model').value = payload.model || '';
      document.getElementById('chat-setting-endpoint').value = payload.endpoint || '';
      document.getElementById('chat-setting-temperature').value = payload.temperature ?? 0;
      document.getElementById('chat-setting-top-p').value = payload.top_p ?? 0.9;
      document.getElementById('chat-setting-max-tokens').value = payload.max_tokens ?? 2048;
      document.getElementById('chat-setting-context').value = payload.max_context_chars ?? 24000;
      document.getElementById('chat-setting-prompt').value = payload.system_prompt || '';
      const health = document.getElementById('chat-provider-health');
      health.className = 'provider-health pending';
      health.lastChild.textContent = ' checking';
      const healthResponse = await fetch('/api/research/chat/health');
      const healthPayload = await healthResponse.json();
      health.className = `provider-health ${healthPayload.ok ? 'online' : 'offline'}`;
      health.lastChild.textContent = healthPayload.ok ? ' online' : ' offline';
    } catch (_) {
      document.getElementById('chat-setting-provider').textContent = 'unavailable';
    }
  }
  settingsToggle.addEventListener('click', () => {
    settings.hidden = !settings.hidden;
    if (!settings.hidden) loadSettings();
  });
  settingsRefresh.addEventListener('click', loadSettings);
  settingsSave.addEventListener('click', async () => {
    const value = (id) => document.getElementById(id).value;
    const response = await fetch('/api/research/chat/settings', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({
      model: value('chat-setting-model'), endpoint: value('chat-setting-endpoint'), temperature: Number(value('chat-setting-temperature')),
      top_p: Number(value('chat-setting-top-p')), max_tokens: Number(value('chat-setting-max-tokens')), max_context_chars: Number(value('chat-setting-context')),
      system_prompt: value('chat-setting-prompt')
    })});
    if (!response.ok) window.alert((await response.json()).error || 'Settings konnten nicht gespeichert werden.');
    else await loadSettings();
  });
  webSearch.addEventListener('change', () => {
    state.webSearchEnabled = webSearch.checked;
    saveState(state);
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;
    const room = activeRoom();
    room.messages.push({ role: 'user', content: message });
    if (room.messages.length === 1) room.title = message.slice(0, 32);
    saveState(state);
    render();
    input.value = '';
    try {
      const response = await fetch('/api/research/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message, web_search: webSearch.checked}) });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
      room.messages.push({ role: 'assistant', content: payload.answer || '' });
      saveState(state);
      render();
    } catch (error) {
      log.insertAdjacentHTML('beforeend', `<div class="chat-message error"><strong>Unavailable</strong><p>${escapeChat(error.message)}</p></div>`);
    }
    log.scrollTop = log.scrollHeight;
  });
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });
  render();
}