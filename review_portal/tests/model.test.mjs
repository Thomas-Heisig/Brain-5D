import test from 'node:test';
import assert from 'node:assert/strict';
import { INSTRUMENT, DIGEST } from '../../src/dashboard/static/review/instrument.js';
import { ITEMS, validateAnswer, visibleSections, csvCell, qualityFlags } from '../../src/dashboard/static/review/model.js';

test('all 135 questions have stable IDs', () => { assert.equal(ITEMS.size,135); assert.equal(INSTRUMENT.sections.flatMap(s=>s.items).length,75); assert.equal(DIGEST.length,64); });
test('NA is not middle scale and no implicit default', () => { assert.equal(validateAnswer(ITEMS.get('B1'),'Nicht beurteilbar'),true); assert.equal(validateAnswer(ITEMS.get('B1'),6),false); assert.equal(validateAnswer(ITEMS.get('B1'),true),false); });
test('optional modules do not change the base catalogue', () => { assert.equal(visibleSections({modules:[]}).flatMap(s=>s.items).length,75); assert.equal(visibleSections({modules:['IT','Q']}).flatMap(s=>s.items).length,95); });
test('CSV formula injection is escaped including whitespace', () => { assert.equal(csvCell('=1+1'),'"\'=1+1"'); assert.equal(csvCell('\t@SUM(A1)'),'"\'\t@SUM(A1)"'); assert.equal(csvCell('hello, "there"'),'"hello, ""there"""'); });
test('attention flag is not automatic deletion', () => { const r={answers:{H1:4,H3:'Ja'},notes:{}}; assert.equal(qualityFlags(r).length,1); assert.equal(r.answers.H1,4); });
test('calendar date validation and optional signature', () => { assert.equal(validateAnswer(ITEMS.get('H5'),{date:'2026-02-31',signature:''}),false); assert.equal(validateAnswer(ITEMS.get('H5'),{date:'2026-09-10',signature:''}),true); });
