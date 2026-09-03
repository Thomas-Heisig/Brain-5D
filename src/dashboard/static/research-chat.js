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
  return { id: crypto.randomUUID(), title: 'Neuer Chat', messages: [], archived: false, collapsed: false };
}

const DEFAULT_PROMPT = 'Beantworte Fragen strikt faktenbasiert aus Research und Docs. Zitiere exakte Pfade, trenne DATA, EVIDENCE und AI interpretation, markiere Unsicherheit und fuehre niemals Experimente aus freiem Text aus.';

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
  const archivedToggle = document.getElementById('chat-room-archived');
  const promptGenerate = document.getElementById('chat-prompt-generate');
  const settingsReset = document.getElementById('chat-settings-reset');
  const settingsToggle = document.getElementById('chat-settings-toggle');
  const settings = document.getElementById('chat-settings');
  const settingsRefresh = document.getElementById('chat-settings-refresh');
  const settingsSave = document.getElementById('chat-settings-save');
  const webSearch = document.getElementById('chat-web-search');
  if (!form || !input || !log || !modal || !toggle || !close || !roomList || !newRoom || !childRoom || !archivedToggle || !settingsToggle || !settings || !settingsRefresh || !settingsSave || !promptGenerate || !settingsReset || !webSearch) return;
  const state = loadState();
  webSearch.checked = state.webSearchEnabled === true;

  function activeRoom() {
    return state.rooms.find((room) => room.id === state.activeId) || state.rooms[0];
  }

  function render() {
    const visible = state.rooms.filter((room) => (state.showArchived || !room.archived) && (state.showArchived || !isHiddenByParent(room)));
    roomList.innerHTML = visible.map((room) => `<div class="chat-room-row"><button type="button" class="chat-room${room.id === state.activeId ? ' active' : ''}${room.parentId ? ' child' : ''}${room.archived ? ' archived' : ''}" data-room-id="${escapeChat(room.id)}">${room.parentId ? '↳ ' : ''}${escapeChat(room.title)}</button><button type="button" class="chat-room-action" data-collapse-id="${room.id}" title="Chat einklappen">${room.collapsed ? '+' : '−'}</button><button type="button" class="chat-room-action" data-archive-id="${room.id}" title="${room.archived ? 'Chat wiederherstellen' : 'Chat archivieren'}">${room.archived ? '↥' : '□'}</button><button type="button" class="chat-room-action danger" data-delete-id="${room.id}" title="Chat löschen">×</button></div>`).join('');
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

  function isHiddenByParent(room) {
    let parent = state.rooms.find((candidate) => candidate.id === room.parentId);
    while (parent) {
      if (parent.collapsed || parent.archived) return true;
      parent = state.rooms.find((candidate) => candidate.id === parent.parentId);
    }
    return false;
  }

  function hierarchyContext(room) {
    const chain = [];
    let current = room;
    while (current) {
      if (current.messages.length) chain.unshift(`${current.title}:\n${current.messages.slice(-8).map((message) => `${message.role}: ${message.content}`).join('\n')}`);
      current = state.rooms.find((candidate) => candidate.id === current.parentId);
    }
    return chain.join('\n\n').slice(-20000);
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
    const action = event.target.closest('[data-collapse-id], [data-archive-id], [data-delete-id]');
    if (action) {
      const id = action.dataset.collapseId || action.dataset.archiveId || action.dataset.deleteId;
      const room = state.rooms.find((candidate) => candidate.id === id);
      if (!room) return;
      if (action.dataset.collapseId) room.collapsed = !room.collapsed;
      if (action.dataset.archiveId) room.archived = !room.archived;
      if (action.dataset.deleteId && window.confirm(`Chat "${room.title}" wirklich löschen?`)) {
        state.rooms = state.rooms.filter((candidate) => candidate.id !== id && candidate.parentId !== id);
        state.activeId = state.rooms[0]?.id || createRoom().id;
        if (!state.rooms.length) state.rooms = [createRoom()];
      }
      saveState(state); render(); return;
    }
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
  archivedToggle.addEventListener('click', () => { state.showArchived = !state.showArchived; render(); });
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
      const providers = await (await fetch('/api/research/chat/providers')).json();
      document.getElementById('chat-model-options').innerHTML = (providers.models || []).map((model) => `<option value="${escapeChat(model)}"></option>`).join('');
    } catch (_) {
      document.getElementById('chat-setting-provider').value = 'unavailable';
    }
  }
  settingsToggle.addEventListener('click', () => {
    settings.hidden = !settings.hidden;
    if (!settings.hidden) loadSettings();
  });
  settingsRefresh.addEventListener('click', loadSettings);
  promptGenerate.addEventListener('click', () => { document.getElementById('chat-setting-prompt').value = DEFAULT_PROMPT; });
  settingsReset.addEventListener('click', () => {
    document.getElementById('chat-setting-temperature').value = 0;
    document.getElementById('chat-setting-top-p').value = .9;
    document.getElementById('chat-setting-max-tokens').value = 2048;
    document.getElementById('chat-setting-context').value = 24000;
    document.getElementById('chat-setting-prompt').value = DEFAULT_PROMPT;
  });
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
      const response = await fetch('/api/research/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message, web_search: webSearch.checked, conversation_context: hierarchyContext(room)}) });
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