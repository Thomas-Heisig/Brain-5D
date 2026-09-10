import { INSTRUMENT, DIGEST } from './instrument.js';
import { MISSING, STORAGE_KEY, MAX_BYTES, LOCAL_STUDY,
  visibleSections, isFilled, validateResponse, qualityFlags, toCSV } from './model.js';

const $ = id => document.getElementById(id);
const el = (tag, text, cls) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (cls) node.className = cls;
  return node;
};
let study = { ...LOCAL_STUDY };
let response = null;
let step = 0;
let submitted = false;
let receipt = null;
let envelope = null;
let busy = false;
let dirty = false;
const status = text => { $('status').textContent = text; };

function randomToken() {
  return Array.from(crypto.getRandomValues(new Uint8Array(32)), b => b.toString(16).padStart(2, '0')).join('');
}
function download(name, text, type = 'application/json') {
  const url = URL.createObjectURL(new Blob([text], {type}));
  const a = el('a'); a.href = url; a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}
function displayStudy() {
  const root = $('study'); root.replaceChildren();
  root.append(el('strong', study.title));
  const link = el('a', `Pruefunterlagen: ${study.reviewed_revision.slice(0,12)}`);
  link.href = study.materials_url; link.target = '_blank'; link.rel = 'noopener noreferrer';
  const p = el('p'); p.append(link); root.append(p);
  root.append(el('p', `Erhebung: ${study.study_id} / ${study.wave}. Zweck: ${study.purpose}`));
  if (study.collection_enabled) {
    root.append(el('p', `Verantwortlich: ${study.controller}. Kontakt: ${study.contact}.`));
    root.append(el('p', `Aufbewahrung: ${study.retention_days} Tage ab Abgabe. ${study.compensation}`));
    root.append(el('p', study.privacy_notice));
  } else {
    root.append(el('p', 'Kein zentraler Erhebungsdienst verbunden. Ausfuellen, lokale Sicherung und Datei-Export sind verfuegbar; ein Export wird nicht automatisch versendet.'));
  }
  $('mode').textContent = study.collection_enabled ? 'Geschuetzte Online-Abgabe' : 'Lokales Formular - kein Versand';
}
async function loadConfig() {
  try {
    const res = await fetch('/api/review/config', {credentials:'omit', cache:'no-store', signal:AbortSignal.timeout(4000)});
    if (!res.ok || !res.headers.get('content-type')?.includes('application/json')) return;
    const config = await res.json();
    if (config.protocol !== 'mhrn-review-v1' || config.instrument_sha256 !== DIGEST) return;
    if (config.collection_enabled && config.materials_url?.startsWith('https://')) study = config;
  } catch { /* Static hosting intentionally has no API. */ }
  finally { displayStudy(); $('start').disabled = false; }
}
function freshResponse() {
  const now = new Date().toISOString();
  return {
    instrument_id:INSTRUMENT.id, instrument_version:INSTRUMENT.version, instrument_sha256:DIGEST,
    study_id:study.study_id, wave:study.wave, reviewed_revision:study.reviewed_revision, materials_url:study.materials_url, study_config_sha256:study.study_config_sha256,
    response_id:crypto.randomUUID(), participant_code:crypto.randomUUID(), participant_type:'reviewer', modules:['Q'],
    answers:{}, notes:{}, consent:{accepted:true, adult:true, version:INSTRUMENT.consent_version, accepted_at:now},
    started_at:now, completed_at:null,
  };
}
function touch() {
  if (!response) return;
  response.completed_at = null; envelope = null; dirty = true;
  if ($('persist').checked) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(response)); status('Entwurf auf diesem Geraet gespeichert.'); dirty = false; }
    catch { $('persist').checked = false; status('Geraetespeicherung nicht moeglich. Bitte den JSON-Entwurf sichern.'); }
  }
  updateProgress();
}
function updateProgress() {
  const sections = visibleSections(response);
  const questions = sections.flatMap(s => s.items);
  const count = questions.filter(q => isFilled(response.answers[q.id])).length;
  $('progress').max = questions.length; $('progress').value = count;
  $('count').textContent = `${count} von ${questions.length} bearbeitet (einschliesslich Keine Angabe / Nicht beurteilbar).`;
}
function choice(q, value, label, group) {
  const wrapper = el('label', undefined, 'option');
  const input = el('input'); input.type = 'radio'; input.name = q.id;
  input.value = String(value); input.checked = response.answers[q.id] === value;
  input.addEventListener('change', () => { response.answers[q.id] = value; touch(); });
  wrapper.append(input, el('span', label)); group.append(wrapper);
}
function renderQuestion(q) {
  const field = el('fieldset', undefined, 'question');
  const legend = el('legend'); legend.append(el('span', q.id, 'qid'), document.createTextNode(q.text)); field.append(legend);
  const value = response.answers[q.id];
  if (q.kind === 'scale' || q.kind === 'choice') {
    const options = el('div', undefined, q.kind === 'scale' ? 'scale' : 'missing');
    if (q.kind === 'scale') q.labels.forEach((label, i) => choice(q, i+1, label, options));
    else q.choices.forEach(option => choice(q, option, option, options));
    field.append(options);
    const missing = el('div', undefined, 'missing');
    MISSING.forEach(option => choice(q, option, option, missing)); field.append(missing);
  } else if (q.kind === 'signature') {
    const dateLabel = el('label', 'Datum (freiwillig)'); const date = el('input'); date.type = 'date'; date.value = value?.date || '';
    const signatureLabel = el('label', 'Unterschrift / Namensbestaetigung (freiwillig; hebt Anonymitaet auf, keine qualifizierte elektronische Signatur)');
    const signature = el('input'); signature.type = 'text'; signature.maxLength = 160; signature.autocomplete = 'off'; signature.value = value?.signature || '';
    const update = () => { response.answers[q.id] = {date:date.value, signature:signature.value}; touch(); };
    date.addEventListener('input', update); signature.addEventListener('input', update);
    dateLabel.append(date); signatureLabel.append(signature); field.append(dateLabel, signatureLabel);
  } else {
    const label = el('label', q.kind === 'number' ? 'Zahl (freiwillig)' : 'Ihre Antwort (freiwillig, maximal 4000 Zeichen)');
    const input = el(q.kind === 'number' ? 'input' : 'textarea');
    if (q.kind === 'number') { input.type = 'number'; input.min = q.minimum; input.max = q.maximum; input.step = '1'; }
    else input.maxLength = 4000;
    input.value = value ?? ''; input.autocomplete = 'off';
    input.addEventListener('input', () => {
      response.answers[q.id] = q.kind === 'number' && input.value !== '' ? Number(input.value) : input.value;
      touch();
    });
    label.append(input); field.append(label);
  }
  const details = el('details'); details.append(el('summary', 'Beleg / Erlaeuterung (optional)'));
  const label = el('label', `Erlaeuterung zu ${q.id}; keine Daten Dritter, maximal 2000 Zeichen`);
  const note = el('textarea'); note.maxLength = 2000; note.value = response.notes[q.id] || '';
  note.addEventListener('input', () => { response.notes[q.id] = note.value; touch(); });
  label.append(note); details.append(label); field.append(details);
  return field;
}
function renderNavigation() {
  const nav = $('sections'); nav.replaceChildren();
  [...visibleSections(response), {id:'END',title:'Abschluss'}].forEach((s,i) => {
    const button = el('button', `${s.id} - ${s.title}`); button.type = 'button';
    if (i === step) button.setAttribute('aria-current','step');
    button.addEventListener('click', () => { step = i; render(); }); nav.append(button);
  });
}
function render(focus = true) {
  const sections = visibleSections(response); step = Math.min(step, sections.length);
  renderNavigation(); updateProgress();
  const complete = step === sections.length;
  $('question-form').hidden = complete; $('completion').hidden = !complete;
  if (complete) {
    const qs = sections.flatMap(s => s.items);
    const unanswered = qs.filter(q => !isFilled(response.answers[q.id])).map(q => q.id);
    $('completion-status').textContent = unanswered.length ? `Noch offen: ${unanswered.join(', ')}. Auslassen ist erlaubt.` : 'Alle sichtbaren Fragen wurden bearbeitet.';
    $('flags').replaceChildren(...qualityFlags(response).map(flag => el('li', flag)));
    $('online').hidden = !study.collection_enabled; $('offline').hidden = study.collection_enabled;
    if (focus) $('completion').querySelector('h2').focus();
  } else {
    const s = sections[step]; $('section-title').textContent = `${s.id} - ${s.title}`;
    $('section-help').textContent = ['B','C','D','E'].includes(s.id) ? '1 = stimme ueberhaupt nicht zu; 5 = stimme voll zu. Nicht beurteilbar wird separat ausgewertet.' : 'Alle Angaben sind freiwillig. Bitte beachten Sie die jeweilige Skalenbeschriftung.';
    $('questions').replaceChildren(...s.items.map(renderQuestion));
    $('previous').disabled = step === 0;
    if (focus) $('section-title').focus();
  }
  if (submitted) $('question-form').querySelectorAll('input,textarea,select').forEach(node => { node.disabled = true; });
}
function setupControls() {
  $('participant-type').value = response.participant_type;
  $('participant-code').value = response.participant_code;
  $('modules').replaceChildren(el('legend', 'Zusaetzliche Module (frei waehlbar)'));
  INSTRUMENT.specialists.forEach(s => {
    const label = el('label', undefined, 'check'); const input = el('input'); input.type = 'checkbox'; input.value = s.id;
    input.checked = response.modules.includes(s.id);
    input.addEventListener('change', () => {
      response.modules = Array.from($('modules').querySelectorAll('input:checked'), n => n.value);
      step = 0; touch(); render();
    }); label.append(input, el('span', `${s.title} (${s.items.length})`)); $('modules').append(label);
  });
  $('context').textContent = `Instrument ${INSTRUMENT.version} | ${study.study_id} / ${study.wave} | Unterlagen ${study.reviewed_revision.slice(0,12)}`;
}
function finalResponse() {
  validateResponse(response);
  const selected = new Set(visibleSections(response).flatMap(s => s.items.map(q => q.id)));
  const r = structuredClone(response);
  r.answers = Object.fromEntries(Object.entries(r.answers).filter(([id]) => selected.has(id)));
  r.notes = Object.fromEntries(Object.entries(r.notes).filter(([id]) => selected.has(id)));
  r.completed_at = response.completed_at || new Date().toISOString(); response.completed_at = r.completed_at;
  if (new TextEncoder().encode(JSON.stringify(r)).length > MAX_BYTES - 1024) throw new Error('Antwortdatei ist zu gross (maximal 2 MiB). Bitte Freitexte kuerzen.');
  return r;
}
function importResponse(raw) {
  if (submitted) throw new Error('Bereits abgegeben. Beginnen Sie eine neue lokale Sitzung.');
  const r = validateResponse(raw);
  if (r.study_id !== study.study_id || r.wave !== study.wave || r.reviewed_revision !== study.reviewed_revision || r.materials_url !== study.materials_url || r.study_config_sha256 !== study.study_config_sha256)
    throw new Error('Andere Erhebung oder andere Pruefunterlagen. Keine automatische Zuordnung oder Migration.');
  response = structuredClone(r); step = 0; setupControls(); touch(); render();
}
function handleError(error) { status(error instanceof Error ? error.message : 'Vorgang fehlgeschlagen.'); }
$('start').disabled = true; displayStudy(); loadConfig();
$('version').textContent = `Instrument ${INSTRUMENT.version} | SHA-256 ${DIGEST.slice(0,16)}`;
$('start').addEventListener('click', () => {
  if (!$('adult').checked || !$('consent').checked) { $('intro-error').textContent = 'Bitte beide freiwilligen Bestaetigungen aktivieren, bevor Sie beginnen.'; return; }
  response = freshResponse(); $('intro').hidden = true; $('workspace').hidden = false;
  setupControls(); render();
});
$('question-form').addEventListener('submit', event => event.preventDefault());
$('previous').addEventListener('click', () => { step = Math.max(0,step-1); render(); });
$('next').addEventListener('click', () => { step++; render(); });
$('participant-type').addEventListener('change', () => {
  response.participant_type = $('participant-type').value;
  if (response.participant_type !== 'proband' && !response.modules.includes('Q')) response.modules.push('Q');
  setupControls(); touch(); render(false);
});
$('participant-code').addEventListener('input', () => { response.participant_code = $('participant-code').value; touch(); });
$('persist').addEventListener('change', () => {
  if (!$('persist').checked) { try { localStorage.removeItem(STORAGE_KEY); } catch { /* unavailable */ } }
  touch();
});
$('save').addEventListener('click', () => {
  try { validateResponse(response); download(`mhrn-entwurf-${response.response_id}.json`, JSON.stringify(response,null,2)); dirty = false; status('Entwurf als Datei erzeugt; nicht an einen Server gesendet.'); } catch(e) { handleError(e); }
});
$('import').addEventListener('change', async () => {
  try {
    const file = $('import').files?.[0]; if (!file) return;
    if (file.size > MAX_BYTES) throw new Error('Datei ist groesser als 2 MiB.');
    importResponse(JSON.parse(await file.text())); status('Entwurf geladen.');
  } catch(e) { handleError(e); } finally { $('import').value = ''; }
});
$('restore').addEventListener('click', () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY); if (!raw) throw new Error('Kein Geraeteentwurf vorhanden.');
    if (new TextEncoder().encode(raw).length > MAX_BYTES) throw new Error('Geraeteentwurf zu gross.');
    importResponse(JSON.parse(raw)); status('Geraeteentwurf geladen. Speicherung bleibt ohne erneute Auswahl aus.');
  } catch(e) { handleError(e); }
});
$('clear').addEventListener('click', () => {
  if (!confirm('Lokalen Entwurf und lokalen Speicher loeschen? Eine Serverabgabe wird dadurch NICHT geloescht.')) return;
  try { localStorage.removeItem(STORAGE_KEY); } catch { /* unavailable */ }
  response = null; receipt = null; envelope = null; submitted = false; dirty = false;
  location.reload();
});
$('export-json').addEventListener('click', () => {
  try { const r = finalResponse(); download(`mhrn-antworten-${r.response_id}.json`, JSON.stringify(r,null,2)); dirty = false; status('Private Antwortdatei erzeugt. Dies ist keine Serverabgabe.'); } catch(e) { handleError(e); }
});
$('export-csv').addEventListener('click', () => {
  try { const r = finalResponse(); download(`mhrn-antworten-${r.response_id}.csv`, toCSV(r), 'text/csv;charset=utf-8'); status('Private CSV-Datei erzeugt. Freitexte sind gegen Tabellenformeln abgesichert.'); } catch(e) { handleError(e); }
});
$('print').addEventListener('click', () => {
  try {
    const r = finalResponse(); const container = el('section'); container.id = 'print-view';
    container.append(el('h1', 'MHRN - persoenliches Review'), el('p', `Abgabe-ID ${r.response_id}; Instrument ${r.instrument_version}; Unterlagen ${r.reviewed_revision}`));
    for (const s of visibleSections(r)) {
      container.append(el('h2', `${s.id} - ${s.title}`));
      for (const q of s.items) {
        const block = el('div', undefined, 'question'); block.append(el('strong', `${q.id} ${q.text}`));
        const value = r.answers[q.id];
        block.append(el('p', typeof value === 'object' && value ? `${value.date || ''} ${value.signature || ''}` : String(value ?? 'Nicht beantwortet')));
        if (r.notes[q.id]) block.append(el('p', `Beleg / Erlaeuterung: ${r.notes[q.id]}`)); container.append(block);
      }
    }
    $('workspace').hidden = true; document.querySelector('main').append(container);
    try { window.print(); } finally { container.remove(); $('workspace').hidden = false; }
  } catch(e) { handleError(e); }
});
$('submit').addEventListener('click', async () => {
  if (busy || submitted) return;
  busy = true; $('submit').disabled = true;
  try {
    if (!study.collection_enabled) throw new Error('Online-Erhebung nicht freigeschaltet.');
    const code = $('invitation').value.trim(); if (!code) throw new Error('Einladungscode fehlt.');
    if (!envelope) {
      const r = finalResponse(); receipt = {response_id:r.response_id, withdrawal_token:randomToken(), study_id:study.study_id, server:location.origin, notice:'Persoenlicher Ruecktrittscode. Die Datei allein bestaetigt noch keine erfolgreiche Abgabe.'};
      envelope = {response:r, withdrawal_token:receipt.withdrawal_token};
      download(`mhrn-ruecktritt-${r.response_id}.json`, JSON.stringify(receipt,null,2));
    }
    const res = await fetch('/api/review/responses', {method:'POST', credentials:'omit', headers:{'Content-Type':'application/json','X-Review-Invitation':code}, body:JSON.stringify(envelope), signal:AbortSignal.timeout(20000)});
    if (!res.ok) { const err = await res.json().catch(() => ({})); throw new Error(err.detail || `Abgabe fehlgeschlagen (HTTP ${res.status}).`); }
    const result = await res.json();
    submitted = true; dirty = false; $('invitation').value = '';
    try { localStorage.removeItem(STORAGE_KEY); } catch { /* unavailable */ }
    $('persist').checked = false;
    $('receipt').textContent = `Serverabgabe bestaetigt: ${result.response_id}. Ruecktrittsbeleg sicher aufbewahren. Keine Veroeffentlichung und keine Evidenzfreigabe.`;
    $('withdraw-id').value = receipt.response_id; $('withdraw-token').value = receipt.withdrawal_token;
    document.querySelectorAll('.controls input,.controls select,.controls button').forEach(node => { if(node.id !== 'clear') node.disabled = true; });
    status('Antworten verschluesselt abgegeben.');
  } catch(e) { handleError(e); } finally { busy = false; $('submit').disabled = submitted; }
});
$('withdraw').addEventListener('click', async () => {
  const target = $('withdraw-status'); target.textContent = '';
  try {
    if (!study.collection_enabled) throw new Error('Kein Erhebungsdienst verbunden. Wenden Sie sich an die Verwaltung Ihrer Abgabe.');
    const id = $('withdraw-id').value.trim(), token = $('withdraw-token').value.trim();
    if (!id || !token) throw new Error('Abgabe-ID und Ruecktrittscode erforderlich.');
    const res = await fetch('/api/review/withdraw', {method:'POST', credentials:'omit', headers:{'Content-Type':'application/json'}, body:JSON.stringify({response_id:id,withdrawal_token:token}), signal:AbortSignal.timeout(20000)});
    if (!res.ok) throw new Error(`Ruecktritt nicht verarbeitet (HTTP ${res.status}).`);
    target.textContent = 'Anfrage verarbeitet. Eine zu ID und Code passende Serverabgabe wurde geloescht. Aus Datenschutzgruenden wird nicht bestaetigt, ob andere IDs existieren. Loeschen Sie auch Ihre lokalen Kopien.';
    $('withdraw-token').value = '';
  } catch(e) { target.textContent = e.message || 'Ruecktritt fehlgeschlagen.'; }
});
window.addEventListener('beforeunload', event => { if (dirty && !submitted) { event.preventDefault(); event.returnValue = ''; } });
