import { INSTRUMENT, DIGEST } from './instrument.js';
export const ALL_SECTIONS = [...INSTRUMENT.sections, ...INSTRUMENT.specialists];
export const ITEMS = new Map(ALL_SECTIONS.flatMap(s => s.items.map(q => [q.id, q])));
export const MISSING = INSTRUMENT.missing_values;
export const STORAGE_KEY = `mhrn-review-${INSTRUMENT.version}`;
export const MAX_BYTES = 2 * 1024 * 1024;
export const LOCAL_STUDY = {
  protocol: 'mhrn-review-v1', study_config_sha256: 'local-only', collection_enabled: false, study_id: 'local-review', wave: 'baseline',
  title: 'Lokales, freiwilliges Review', reviewed_revision: INSTRUMENT.base_revision,
  materials_url: `https://github.com/Thomas-Heisig/MHRN/tree/${INSTRUMENT.base_revision}`,
  controller: '', contact: '', purpose: 'Eigenstaendige Einschaetzung der bereitgestellten Projektunterlagen',
  retention_days: null, compensation: 'Keine Verguetung durch dieses Formular.',
};
export function visibleSections(response) {
  return [...INSTRUMENT.sections, ...INSTRUMENT.specialists.filter(s => response.modules.includes(s.id))];
}
export function isFilled(value) {
  return value !== undefined && value !== null && value !== '' &&
    (typeof value !== 'object' || Boolean(value.date || value.signature));
}
export function validateAnswer(q, value) {
  if (value === null || value === '' || MISSING.includes(value)) return true;
  if (q.kind === 'scale') return Number.isInteger(value) && value >= 1 && value <= 5;
  if (q.kind === 'number') return Number.isInteger(value) && value >= q.minimum && value <= q.maximum;
  if (q.kind === 'choice') return q.choices.includes(value);
  if (q.kind === 'text') return typeof value === 'string' && value.length <= 4000;
  if (q.kind === 'signature') return value && typeof value === 'object' && !Array.isArray(value) &&
    Object.keys(value).every(k => ['date', 'signature'].includes(k)) && typeof value.signature === 'string' &&
    value.signature.length <= 160 && typeof value.date === 'string' &&
    (value.date === '' || (/^\d{4}-\d{2}-\d{2}$/.test(value.date) &&
      !Number.isNaN(Date.parse(value.date)) && new Date(value.date).toISOString().slice(0,10) === value.date));
  return false;
}
const RESPONSE_FIELDS = ['instrument_id','instrument_version','instrument_sha256','study_id','wave','reviewed_revision','materials_url','study_config_sha256','response_id','participant_code','participant_type','modules','answers','notes','consent','started_at','completed_at'];
const timestamp = value => typeof value === 'string' && value.length <= 40 &&
  /(?:Z|[+-]\d{2}:\d{2})$/.test(value) && !Number.isNaN(Date.parse(value));
export function validateResponse(r) {
  if (!r || typeof r !== 'object' || Array.isArray(r)) throw new Error('Keine gueltige Antwortdatei.');
  if (Object.keys(r).length !== RESPONSE_FIELDS.length || RESPONSE_FIELDS.some(key => !Object.hasOwn(r,key)))
    throw new Error('Unbekannte oder fehlende Antwortfelder.');
  if (r.instrument_id !== INSTRUMENT.id || r.instrument_version !== INSTRUMENT.version || r.instrument_sha256 !== DIGEST)
    throw new Error('Die Instrumentversion stimmt nicht ueberein. Alte Antworten werden nicht still migriert.');
  if (!r.consent || r.consent.accepted !== true || r.consent.adult !== true || r.consent.version !== INSTRUMENT.consent_version)
    throw new Error('Die Einwilligung fehlt.');
  if (Object.keys(r.consent).length !== 4 || !timestamp(r.consent.accepted_at) || !timestamp(r.started_at) ||
      (r.completed_at !== null && !timestamp(r.completed_at))) throw new Error('Ungueltige Einwilligungs- oder Zeitangaben.');
  if (typeof r.response_id !== 'string' || !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(r.response_id))
    throw new Error('Ungueltige Abgabe-ID.');
  for (const key of ['response_id', 'participant_code', 'participant_type', 'study_id', 'wave', 'reviewed_revision', 'materials_url', 'study_config_sha256', 'started_at'])
    if (typeof r[key] !== 'string' || r[key].length > 600) throw new Error(`Ungueltiges Feld: ${key}`);
  if (!['proband','reviewer','committee'].includes(r.participant_type) || r.participant_code.length > 80)
    throw new Error('Ungueltige Teilnahmeangaben.');
  if (!Array.isArray(r.modules) || new Set(r.modules).size !== r.modules.length || r.modules.some(id => !INSTRUMENT.specialists.some(s => s.id === id)))
    throw new Error('Unbekanntes oder doppeltes Modul.');
  for (const field of ['answers', 'notes']) {
    if (!r[field] || typeof r[field] !== 'object' || Array.isArray(r[field])) throw new Error(`Ungueltig: ${field}`);
    for (const [id, value] of Object.entries(r[field])) {
      const q = ITEMS.get(id);
      if (!q || (field === 'answers' ? !validateAnswer(q, value) : typeof value !== 'string' || value.length > 2000))
        throw new Error(`Ungueltiger Wert bei ${id}`);
    }
  }
  return r;
}
export function qualityFlags(r) {
  const flags = [];
  if (typeof r.answers.H1 === 'number' && r.answers.H1 !== 3) flags.push('H1: Aufmerksamkeitshinweis; kein automatischer Ausschluss.');
  if (r.answers.H3 === 'Nein') flags.push('H3: Antworten nicht nach bestem Wissen bestaetigt.');
  if (r.answers.H4 === 'Ja' && !r.notes.H4) flags.push('H4: Interessenkonflikt ohne Erlaeuterung.');
  const base = INSTRUMENT.sections.flatMap(s => s.items).filter(q => !isFilled(r.answers[q.id]));
  if (r.answers.H2 === 'Ja' && base.length) flags.push('H2: Vollstaendigkeit angegeben, aber Basisfragen sind offen.');
  if (r.answers.H5?.signature) flags.push('H5: Namensangabe vorhanden; diese Antwort ist nicht anonym.');
  return flags;
}
export function csvCell(value) {
  let text = typeof value === 'object' && value !== null ? JSON.stringify(value) : String(value ?? '');
  if (/^[\s]*[=+@-]/u.test(text)) text = `'${text}`;
  return `"${text.replaceAll('"', '""')}"`;
}
export function toCSV(r) {
  const rows = [['response_id','instrument_version','instrument_sha256','study_id','wave','reviewed_revision','participant_code','participant_type','question_id','question','answer','note']];
  for (const s of visibleSections(r)) for (const q of s.items) rows.push([
    r.response_id, r.instrument_version, r.instrument_sha256, r.study_id, r.wave, r.reviewed_revision,
    r.participant_code, r.participant_type, q.id, q.text, r.answers[q.id] ?? '', r.notes[q.id] ?? '',
  ]);
  return '\uFEFF' + rows.map(row => row.map(csvCell).join(',')).join('\r\n');
}
