"""Publish and verify the executed, explicitly exploratory manuscript edition."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EDITION = '2026-09-10_recursive-epistemics_v1.4'
PREVIOUS = '2026-09-08_recursive-epistemics_v1.3'
CAMPAIGNS = ('EXP-EMP-20260910', 'EXP-EMP-20260910-SCALE-V2')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


def inventory(path: Path) -> dict[str, str]:
    return {str(p.relative_to(path)): sha(p) for p in sorted(path.rglob('*')) if p.is_file() and p.name != 'ARTIFACTS.json'}


def copy_data(source: Path, name: str) -> tuple[Path, dict[str, Any]]:
    if not load(source / 'completion.json')['source_unchanged']:
        raise ValueError('Source changed during measurement')
    summary = load(source / 'summary.json')
    if summary['campaign'] != name or summary['accepted_evidence'] is not False:
        raise ValueError('Unexpected campaign identity/authority')
    target = ROOT / 'research/experiments' / name
    if target.exists():
        raise ValueError('Published DATA are immutable; choose a new amendment')
    target.mkdir(parents=True)
    for item in sorted(source.iterdir()):
        if item.is_symlink():
            raise ValueError('No symlink imports')
        if item.is_dir():
            shutil.copytree(item, target / item.name)
        elif item.suffix in ('.md', '.json'):
            shutil.copy2(item, target / item.name)
    return target, summary


def measured_table(plan: dict[str, Any], summary: dict[str, Any], prefix: str) -> str:
    lines = ['## Primarmessungen je Protokoll', '', 'n bezeichnet gespeicherte Laeufe, nicht automatisch unabhaengige inferentielle Einheiten. Zahlen: Mittel [Minimum;Maximum]; Boolean: true/n. Vollstaendige strukturierte Messungen stehen in den Rohdaten.', '']
    for spec, item in zip(plan['selections'], summary['protocols']):
        if spec['protocol'] != item['protocol']:
            raise ValueError('Plan/result order mismatch')
        lines += [f"### {item['protocol']}", '', f"Ausfuehrung: {item['status']}; {item['runs']} gespeicherte Laeufe.", '', '| Bedingung | n | Primaere Beobachtungen |', '| --- | ---: | --- |']
        for condition, group in item.get('conditions', {}).items():
            values = []
            for metric in spec['primary_outcomes']:
                number = group['metrics'].get(metric)
                boolean = group['boolean_outcomes'].get(metric)
                if number:
                    values.append(f"{metric}: {number['mean']:.6g} [{number['min']:.6g};{number['max']:.6g}]")
                elif boolean is not None:
                    values.append(f"{metric}: {sum(v is True for v in boolean)}/{len(boolean)} true")
                else:
                    values.append(f'{metric}: strukturiert/kategorial, siehe Rohdaten')
            lines.append(f"| {condition} | {group['runs']} | {'; '.join(values) or 'Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json'} |")
        lines += ['', f"[Unveraenderte Originaldaten]({prefix}{item['data']})", '']
    return '\n'.join(lines)


FINDINGS = '''# Beobachtungen, Fehlversuche und begrenzte Schlussfolgerungen

KI-unterstuetzte nachtraegliche Auswertung. Explorative DATA, keine akzeptierte EVID, kein Peer-Review oder externes Ethikvotum.

## Native synaptische Assoziation

Zehn gepaarte Initialisierungs-/Umwelt-Seeds und 40 neue balancierte Testepisoden je Seed und Arm. Learning-on erreicht im Mittel 78,5 Prozent Genauigkeit, jeder der vier Kontrollarme 50 Prozent. Differenz: 28,5 Prozentpunkte; punktweises 95-Prozent-Bootstrapintervall [20;37] Prozentpunkte; exakter zweiseitiger Vorzeichenwechseltest p=0,001953125, Holm-p=0,0078125. Sensitivitaet des Lernarms: 0,57; falsch-positive Rate: 0.

Die Testgewichte sind eingefroren, Testnetze frisch initialisiert, kein Teacher-Strom und keine Lernengine waehrend der Tests. Kontrollen: Learning-off, Sham-Replay, Gewichtsreset und Permutation desselben Gewichtsmultisets. 400 verschiedene Testepisoden werden bedingungsuebergreifend gepaart; die 2000 Arm-Episoden sind keine 2000 unabhaengigen Netzinitialisierungen. Vier identische Kontrollausgaenge sind auch keine vier unabhaengigen Replikationen.

Dieser positive Befund stuetzt einen begrenzten Mechanismus angeleiteter, reward-/eligibility-vermittelter synaptischer Anpassung im nativen SNN. Er belegt keine autonome Zielbildung, allgemeine Kognition, langfristiges Gedaechtnis oder sensorimotorische Generalisierung. Die Aufgabe und die Eingabepopulationen sind konstruiert; externe Instruktion waehrend der Akquisition wird offengelegt.

## Reale Dimensionsablation

2D, 3D, 4D, 5D, 6D und 8D erzeugen tatsaechlich unterschiedliche gerichtete Nachbarschaftsgraphen. Pro Bedingung: 128 Neuronen, 1024 Kanten, Ausgangsgrad acht, Gewicht 20, gleiche Verzoegerungsbudgets und Eingabe-/Ausgabeknoten. Die sechs Labels eines identischen 5D-Graphen dienen getrennt als Etikettenkontrolle.

Alle fuenf vorab deklarierten 5D-minus-andere-D-Kontraste der Output-Spikezahl haben Intervalle, die null einschliessen, und Holm-p=1. Ein belastbarer 5D-Vorteil ist damit nicht gezeigt. Mehr Output-Spikes sind zudem kein allgemeines Aufgabenqualitaetsmass. Eingangsgrade und Motive variieren mit der Graphgeometrie; das isoliert keinen universellen Effekt der Dimensionszahl. Die persistierte ID-Kodierung bleibt fuenfdimensional.

## Negativer Brian2-Vergleich

Der Einzelzellvergleich wurde ausgefuehrt, aber das vorab deklarierte Konformitaetskriterium wurde in allen drei Laeufen verfehlt. Maximale Spannungsabweichung: 99,5810677; maximale Recovery-Abweichung: 13,9959569. Die Spikefolgen stimmen nicht exakt ueberein. Im ersten Lauf wird die Spannungsabweichung 1e-8 erstmals bei Tickindex 137 ueberschritten; zuvor bestehen bereits kleinere Rechendifferenzen.

Die Verstaerkung kleiner numerischer Unterschiede in einem schwellenden System ist eine plausible Erklaerung, aber ihre konkrete Ursache wurde nicht durch eine separate Intervention isoliert. Der Befund wird weder entfernt noch durch eine nachtraeglich gelockerte Toleranz positiv gemacht. Naechster Versuch: vorab spezifizierte Ein-Schritt-Fehler, Auswertungsreihenfolge, Datentyp und Ereignisphasen isolieren. Die Kern-Dynamik wird nicht bloss zum Bestehen dieses Vergleichs veraendert.

Brian2 wurde mit NumPy-Backend und derselben zweiteiligen v-Aktualisierung, anschliessender u-Aktualisierung, Reset und deaktivierter Adaptation betrieben. Das ist kein Vergleich aller Faehigkeiten von Brian2, NEST oder Lava und kein fairer Framework-Geschwindigkeitsrang. Setup-/Codegenerierungszeiten sind enthalten und explizit bezeichnet.

## Stabilitaet und historische Tests

20 Stabilitaetslaeufe, zehn Seeds, zwei Bedingungen, jeweils 100000 Ticks. Alle Zustands-/Topologiepruefungen bestanden. Nach Burn-in: 300 Spikes pro 1000-Tick-Fenster im tonischen Arm des kleinen Drei-Zellen-Netzes, null im Nullinputarm; CV und relativer Drift null. Seed-invariante Resultate sind keine zehn unabhaengigen zufaelligen Netzreplikationen.

Der historische Lern-Runner nennt deklarierte Validierungs-/Holdout-Partitionsgroessen, fuehrt aber nur je eine Vorher-/Nachher-Probe aus. Diese Zahlen werden nicht als absolvierte Testepisoden interpretiert. Der neue Assoziationsversuch besitzt dagegen echte neue Testepisoden. Der historische Interferenz-Screen verwendet getrennte Task-Netzwerke: kein Nachweis gegen katastrophales Vergessen eines gemeinsam trainierten Netzes. Der lokale independent_replication-Runner ersetzt kein unabhaengiges Team. Memory-, Weltmodell- und Profil-Screens pruefen Komponenten, nicht automatisch neuronales Lernen. MSBA-Energieeinheiten sind keine gemessenen Joule; softwareberechnete Reglerleistungen sind nicht ohne Attribution dem SNN zuzuschreiben.

## Skalierung: offener Fehler und dokumentierte Korrektur

Der urspruengliche Skalierungsversuch v1 brach ab, als ein linearer Neuronenindex von 256 unzulaessig in die erste 8-Bit-Koordinate geschrieben wurde. Die Ergebnisliste wurde nicht zurueckgegeben; interne Teilmessungen werden deshalb nicht als gespeicherte Resultate behauptet. Der Fehlversuch bleibt im Originalbericht.

Die explizite v2-Amendierung zerlegt Indizes in fuenf gueltige Base256-Koordinaten. Graphbudgets, 32-Tick-Last und Messgroessen bleiben gleich; frische Seeds 21001 bis 21003. Das ist keine N-D-Migration der Persistenz. Die getrennte Ergebnistabelle nennt nur tatsaechlich absolvierte Groessen. RSS-Samples sind Prozessspeicher einschliesslich Interpreter/Bibliotheken, keine isolierten Allokationsspitzen. Keine Langzeit-, Vollplastizitaets-, Echtzeit-, GPU-, Energie- oder biologische Skalierungsaussage.
'''

METHODS = '''# Methodik, Reproduktion und Versionsbindung

Die neue Fassung uebernimmt die 57 Kapitel der Fassung 1.3 unveraendert als datierte historische Bestandsaufnahme und ergaenzt vier Aktualisierungskapitel. Damalige Testzahlen und Aussagen zum damaligen Datenstand sind keine Beschreibung des neuen Messstands. Die urspruenglichen Editionsdateien, Messdaten und eingefrorenen Plaene werden nicht ueberschrieben.

Die Ausgangskampagne versucht alle 28 damals registrierten maschinell ausfuehrbaren Protokolle plus die siebenfamilige Basissuite. 22 Vorlagen verlangen menschliche Beurteilung; 43 Registerfragen besitzen noch kein eigenes passendes operationalisiertes Protokoll. Ein generischer Tick-/PING-Lauf ersetzt dies nicht. Unabhaengige Begutachtung, institutionalisiertes Mandat und erforderliche Ethikentscheidungen bleiben reale externe Arbeit.

Die neuen Studien wurden vor ihrer Messung als EXPLORATORY im Repository versioniert. Das wird nicht als externe OSF-/AsPredicted-Praeregistrierung bezeichnet. Bereits vorhandene konfirmatorisch bezeichnete Protokolle werden hier als explorative Reausfuehrung dokumentiert. Der Eingabedigest bindet getrackten Code, Konfiguration, Protokolle und Register vor dem Lauf; ein anschliessender Vergleich kontrolliert Quellveraenderungen. Er ist nicht derselbe Digest wie eine kombinierte Code/Config/Prompt/DATA-Provenienz oder eine Test-Baseline mit anderem Umfang.

## Budgets und statistische Einheit

Geometrie: 128 Knoten in einer gemeinsamen achtkoordinatigen Zufallswolke, acht gerichtete naechste Nachbarn unter den ersten D Koordinaten, zweimalige Inputpulse, 256 Ticks. Native Assoziation: positive/negative neue Inputs mit bis zu acht ausgelassenen Quellen und Zeitjitter, 40 Episoden pro Seed/Arm, 12 Ticks pro Testepisode. Einzelzellen: fuenf Strombedingungen, 1000 Ticks, 1 ms, drei Seeds. Skalierung: 128/1024/5000/25000/100000 Neuronen, vier Kanten je Neuron, 32 Ticks, zwei Inputpulse, drei Seeds, serielle Ausfuehrung.

Gepaarte Statistik auf Seed-Ebene: 2000 Bootstrapresamples, fester Analyse-Seed 910, punktweise 95-Prozent-Perzentilintervalle; alle 2^10 Vorzeichenwechsel fuer den zweiseitigen Test. Der Test setzt entsprechende Austauschbarkeit/Symmetrie der Paardifferenzen unter der Nullhypothese voraus; diese wird nicht empirisch bewiesen. Holm-Korrektur innerhalb der fuenf Dimensions- und vier Lernkontraste. Standardisierte Effektgroesse d_z ist mittlere Paardifferenz geteilt durch ihre Stichprobenstandardabweichung; bei Nullvarianz undefiniert statt erfunden. Keine nachtraeglichen Signifikanztests fuer die Altprotokolle und keine Stichprobengroesse aus einzelnen Ticks vortaeuschen.

## Ausfuehrung

Den exakten Quellcommit aus dem jeweiligen plan.json auschecken und eine saubere Arbeitskopie benutzen. Abhaengigkeiten: Python 3.13, Projektinstallation und Brian2 2.10.1. Jeder Protokollprozess wird separat, aber seriell ausgefuehrt. Bestehende Ausgabeordner und Ordner innerhalb des Quellbaums werden abgewiesen. Der Sicherheits-Timeout ist vorab dokumentiert. Keine Wiederholung missliebiger Ausgaenge.

```bash
python -m pip install -e '.[dev,docs]' 'brian2==2.10.1'
python scripts/empirical_campaign.py --output /absolute/private/path/new-campaign
python scripts/empirical_campaign.py --output /absolute/private/path/new-campaign --analyze
python scripts/publication_empirical.py --verify
```

Ein spaeterer Reproduktionslauf ist nicht automatisch eine unabhaengige Replikation. Fuer v2 wird der in dessen eigenem Plan genannte Commit und die dort dokumentierte Protokollauswahl verwendet. Keine neue DOCX-/PDF-Erzeugung, Promotion, Publikationsannahme oder externe Begutachtung wird behauptet.

## Primaere methodische Referenzen

Izhikevich (2003), Simple Model of Spiking Neurons, DOI 10.1109/TNN.2003.820440. Brian2, offizielles Beispiel frompapers.Izhikevich_2003 und Scheduling-Dokumentation: https://brian2.readthedocs.io/en/2.10.1/examples/frompapers.Izhikevich_2003.html . SciPy, offizielle Dokumentation scipy.stats.permutation_test: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html . Diese Quellen erklaeren Methoden; sie validieren nicht die MHRN-Ergebnisse. Das vollstaendige bisherige Literaturverzeichnis bleibt in den uebernommenen Kapiteln erhalten.
'''


def publish(source: Path, amendment: Path) -> None:
    original = load(source / 'summary.json')
    if original['source'] != 'f9ed3c2153858b14face0b1d8410741c662fb028' or original['total_runs'] != 1272:
        raise ValueError('This dated interpretation requires the reviewed original campaign')
    folder = ROOT / 'research/publications' / EDITION
    if folder.exists() or any((ROOT / 'research/experiments' / name).exists() for name in CAMPAIGNS):
        raise ValueError('Refusing to overwrite a published edition or campaign')
    target, summary = copy_data(source, CAMPAIGNS[0])
    amended_target, amended = copy_data(amendment, CAMPAIGNS[1])
    datasets = [(target, summary), (amended_target, amended)]
    key_results = []
    outcome = '# Ausfuehrungsbilanz und zentrale Messgroessen\n\n'
    for directory, data in datasets:
        outcome += f"{data['campaign']}: {data['status_counts']}; {data['total_runs']} gespeicherte Laeufe; Quellcommit `{data['source']}`; Eingabedigest `{data['source_digest']}`.\n\n"
    outcome += '| Protokoll / Bedingung | n | Messgroesse | Mittel | Minimum | Maximum |\n| --- | ---: | --- | ---: | ---: | ---: |\n'
    chosen = {'dimensional_connectivity_v1': 'output_spikes', 'native_association_holdout_v1': 'test_accuracy', 'brian2_single_neuron_v1': 'max_abs_voltage_error', 'active_scaling_v2': 'ticks_per_second'}
    for data in (summary, amended):
        for item in data['protocols']:
            metric = chosen.get(item['protocol'])
            if metric is None:
                continue
            for condition, group in item.get('conditions', {}).items():
                record = group['metrics'].get(metric)
                if record:
                    outcome += f"| {item['protocol']} / {condition} | {group['runs']} | {metric} | {record['mean']:.6g} | {record['min']:.6g} | {record['max']:.6g} |\n"
                    key_results.append({'protocol': item['protocol'], 'condition': condition, 'metric': metric, **record})
    outcome += '\n## Vorab deklarierte gepaarte Vergleiche\n\n| Referenz minus Kontrolle | n | Differenz | 95%-Bootstrapintervall | p exakt | p Holm |\n| --- | ---: | ---: | --- | ---: | ---: |\n'
    for contrasts in summary['comparisons'].values():
        for c in contrasts:
            outcome += f"| {c['reference']} - {c['control']} | {c['n_seed_pairs']} | {c['mean_difference']:.6g} | {c['bootstrap_percentile_95_ci']} | {c['exact_two_sided_sign_flip_p']:.6g} | {c['holm_adjusted_p']:.6g} |\n"
    analysis = FINDINGS + '\n' + outcome + '\n' + measured_table(load(target / 'plan.json'), summary, '')
    analysis += '\n## Fragen ohne passenden Runner\n\n' + ', '.join(summary['questions_without_specific_runnable_protocol']) + '\n'
    (target / 'ANALYSIS.md').write_text(analysis, encoding='utf-8')
    save(target / 'key_results.json', {'measurements': key_results, 'accepted_evidence': False})
    for directory, data in datasets:
        save(directory / 'ARTIFACTS.json', {'files_sha256': inventory(directory), 'source_commit': data['source'], 'accepted_evidence': False, 'original_data_unchanged': True})
    previous = folder.parent / PREVIOUS
    shutil.copytree(previous, folder)
    (folder / 'manifest.json').unlink()
    chapter57 = outcome + '\n' + measured_table(load(target / 'plan.json'), summary, '../../experiments/EXP-EMP-20260910/')
    chapters = {57: chapter57, 58: FINDINGS, 59: METHODS, 60: '# Kritikbezogener Arbeitsstand\n\nDie Behauptung, es gebe ausschliesslich Softwaretests und gar keine Messdaten, trifft auf diese neue Fassung nicht mehr zu. Der begrenzte native Lernbefund, die fehlende 5D-Ueberlegenheit, die negative Brian2-Konformitaet und der offen dokumentierte Skalierungsfehler sind eigenstaendige Beobachtungen. Keiner dieser Befunde wurde automatisch in akzeptierte EVID umgewandelt.\n\nWeiter offen: echte unabhaengige Replikation und fachliche Freigabe; valide langfristige Gedaechtnis-/Kognitionsaufgaben; kontrollierte sensorimotorische Attribution; NEST-/Lava-Netz- und Lernbenchmarks; Langzeitskalierung; 43 RQ-spezifische Runner; tatsaechliche Bearbeitung der 22 menschlichen Review-Vorlagen und ein nachgewiesenes Gremienmandat, soweit erforderlich. Ein Fragebogenscore ersetzt keine dieser Entscheidungen.\n\n[Originalkampagne](../../experiments/EXP-EMP-20260910/REPORT.md), [Auswertung](../../experiments/EXP-EMP-20260910/ANALYSIS.md), [Skalierungs-Amendierung](../../experiments/EXP-EMP-20260910-SCALE-V2/REPORT.md), [externe Begutachtung](../../external_review/INTEGRATION.md).\n\nLegacy-Slugs und .b5d sind kompatibilitaetsgebundene technische Kennungen, keine ontologische Festlegung. Die Kapitel 0-56 sind datierte historische Uebernahmen; die Kapitel 57-60 definieren den neuen empirischen Stand.\n'}
    for index, text in chapters.items():
        (folder / f'section-{index:03d}.md').write_text(text, encoding='utf-8')
    header = '# Recursive Epistemics in Embodied Spiking Neural Architectures\n\n## Fassung 1.4: Explorative Messdaten, negative Befunde und Grenzen\n\nThomas Heisig, 10. September 2026. KI-unterstuetzte wissenschaftliche Abhandlung; keine EVID-Freigabe, kein externer Ethikbeschluss. Kapitel 0-56 bleiben datierte historische Uebernahmen aus 1.3; Kapitel 57-60 aktualisieren den Messstand.\n\n'
    sections = sorted(folder.glob('section-*.md'))
    navigation = '\n'.join(f"- [{next((line[2:] for line in p.read_text(encoding='utf-8').splitlines() if line.startswith('# ')), p.stem)}]({p.name})" for p in sections)
    (folder / 'README.md').write_text(header + '[Gesamte Lesefassung](MANUSCRIPT.md) - [Manifest](manifest.json)\n\n' + navigation + '\n', encoding='utf-8')
    (folder / 'MANUSCRIPT.md').write_text(header + '\n\n---\n\n'.join(p.read_text(encoding='utf-8') for p in sections), encoding='utf-8')
    for name in ('CITATION.cff', 'CITATION.bib'):
        p = folder / name
        p.write_text(p.read_text(encoding='utf-8').replace('1.3', '1.4').replace('2026-09-08', '2026-09-10'), encoding='utf-8')
    manifest = load(previous / 'manifest.json')
    manifest.update(edition='1.4', date='2026-09-10', section_count=61, section_order=[p.name for p in sections], inherited_edition='../' + PREVIOUS, inherited_file_sha256={p.name: sha(p) for p in previous.iterdir() if p.is_file()}, revision_scope='exploratory_measurements_and_limitations', new_empirical_findings=True, accepted_evidence=False, automatic_evidence_promotion=False, authority='interpretation_only', human_review='pending', campaigns={d.name: {'source': a['source'], 'summary_sha256': sha(d / 'summary.json')} for d, a in datasets})
    manifest['files'] = {p.name: {'sha256': sha(p), 'size': p.stat().st_size} for p in folder.iterdir() if p.is_file()}
    save(folder / 'manifest.json', manifest)
    identity = load(ROOT / 'project_identity.json')
    identity['publication'].update(edition='1.4', path=str(folder.relative_to(ROOT)))
    save(ROOT / 'project_identity.json', identity)
    catalog = load(folder.parent / 'catalog.json')
    for item in catalog['publications']:
        item.update(current=False, edition_status='historical')
    pubid = 'PUB-RECURSIVE-EPISTEMICS-20260910-V1.4'
    entry = f'publications/{EDITION}/README.md'
    catalog['publications'].insert(0, {'id': pubid, 'title': identity['publication']['title_en'], 'version': '1.4', 'date': '2026-09-10', 'author': 'Thomas Heisig', 'type': 'wissenschaftliche_abhandlung', 'current': True, 'edition_status': 'current', 'entrypoint': entry, 'reader': entry, 'snapshot': f'publications/{EDITION}', 'manifest': f'publications/{EDITION}/manifest.json', 'authority': 'interpretation_only', 'read_only': True, 'automatic_evidence_promotion': False})
    catalog.update(current_publication=pubid, current_publication_id=pubid, current_entrypoint=entry)
    save(folder.parent / 'catalog.json', catalog)
    index = folder.parent / 'README.md'
    index.write_text(header + f'[Aktuelle Fassung 1.4]({EDITION}/README.md) - [Messdaten und Auswertung](../experiments/EXP-EMP-20260910/ANALYSIS.md)\n\n<details><summary>Historischer Index bis 1.3 (damaliger Stand)</summary>\n\n' + index.read_text(encoding='utf-8') + '\n</details>\n', encoding='utf-8')
    status = f"\n## Empirical results / Messstand 2026-09-10\n\nOriginal campaign: {summary['total_runs']} seed/condition records; execution states `{summary['status_counts']}`. Addressing-only amendment: {amended['total_runs']} records; states `{amended['status_counts']}`. Twenty-two human reviews remain pending; 43 questions still lack their own operational runner.\n\nNative synthetic association: 78.5% vs 50% for each of four controls, paired difference 28.5 percentage points, pointwise 95% bootstrap CI [20,37], Holm-p 0.0078125 (ten paired seeds). No supported 5D propagation advantage (all Holm-p 1). Brian2 exact single-cell conformance failed in all three runs; this negative is retained. Original scaling failed at coordinate 256; its addressing amendment and results are recorded separately. These are exploratory DATA, not accepted EVID, general cognition, independent replication or ethics approval.\n\n[Full measurements, limitations and failure inventory](research/experiments/EXP-EMP-20260910/ANALYSIS.md) - [Complete manuscript 1.4](research/publications/{EDITION}/README.md).\n"
    for name in ('README.md', 'HF_README.md'):
        p = ROOT / name
        p.write_text(p.read_text(encoding='utf-8') + status, encoding='utf-8')
    todo = ROOT / 'docs/08-roadmap/TODO.md'
    todo.write_text(todo.read_text(encoding='utf-8') + '\n## Empirical evaluation, 2026-09-10\n\n- [x] Execute the available protocol campaign with immutable raw observations, failures and source receipts.\n- [x] Add real graph geometry ablations, frozen native association tests, Brian2 conformance and active scaling with explicit amendment.\n- [x] Publish manuscript 1.4 and data-bound uncertainty analysis without automatic EVID promotion.\n- [ ] Diagnose Brian2 numerical divergence using separately frozen interventions.\n- [ ] Implement the remaining 43 question-specific native protocols; retain 22 human-review tasks as pending.\n- [ ] Obtain independent replication, human EVID review and required external ethics decisions.\n- [ ] Add NEST/Lava task-matched network/learning benchmarks and long-horizon scaling.\n', encoding='utf-8')
    verify()


def verify() -> None:
    folder = ROOT / 'research/publications' / EDITION
    manifest = load(folder / 'manifest.json')
    if manifest['section_count'] != 61 or manifest['accepted_evidence'] or manifest['automatic_evidence_promotion']:
        raise ValueError('Edition scope/authority mismatch')
    for name, item in manifest['files'].items():
        p = (folder / name).resolve()
        if p.parent != folder.resolve() or sha(p) != item['sha256'] or p.stat().st_size != item['size']:
            raise ValueError(f'Edition digest mismatch: {name}')
    for name, value in manifest['inherited_file_sha256'].items():
        if sha(folder.parent / PREVIOUS / name) != value:
            raise ValueError(f'Historical edition changed: {name}')
    for name in CAMPAIGNS:
        target = ROOT / 'research/experiments' / name
        if sha(target / 'summary.json') != manifest['campaigns'][name]['summary_sha256']:
            raise ValueError('Summary digest mismatch')
        if inventory(target) != load(target / 'ARTIFACTS.json')['files_sha256']:
            raise ValueError('DATA inventory mismatch')
        for p in target.glob('*/runs.json.gz'):
            receipt = load(p.parent / 'receipt.json')
            if p.stat().st_size > 600000 or sha(p) != receipt['compressed_data_sha256']:
                raise ValueError('DATA archive digest/size mismatch')
            if hashlib.sha256(gzip.decompress(p.read_bytes())).hexdigest() != receipt['uncompressed_data_sha256']:
                raise ValueError('Uncompressed observations changed')
    from scripts.publication_revision import check_links
    check_links(ROOT, list(folder.glob('*.md')))
    print('Empirical edition:61 chapters, both DATA inventories and historical checksums verified')


if __name__ == '__main__':
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', type=Path)
    parser.add_argument('--amendment', type=Path)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.publish:
        if args.amendment is None:
            parser.error('--amendment is required')
        publish(args.publish, args.amendment)
    else:
        verify()
