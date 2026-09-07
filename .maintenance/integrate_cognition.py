"""Explicit one-time import; retain old publications, DATA and EVID unchanged.

The resulting registry/protocol/chapter files are canonical. This importer is
provenance, not a second actively edited manuscript. Refuses to re-import an
existing edition so later edits cannot be silently overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import yaml

from cognition_program_data import QUESTIONS, SOURCES

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "research/publications"
OLD = PUB / "2026-09-07_ki-die-geliehene-intelligenz_v1.1"
NEW = PUB / "2026-09-07_ki-die-geliehene-intelligenz_v1.2"
DATE = "2026-09-07"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def dump(path: Path, value: object) -> None:
    write(path, json.dumps(value, ensure_ascii=False, indent=2))


def patch(path: str, before: str, after: str, count: int = 1) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if text.count(before) != count:
        raise ValueError(f"Unexpected patch context in {path}; expected {count}")
    write(target, text.replace(before, after))


def append(path: str, text: str) -> None:
    target = ROOT / path
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    write(target, existing.rstrip() + "\n\n" + text)


def import_program() -> None:
    questions, hypotheses, protocols = [], [], []
    common = {
        "authority": "prospective_protocol_not_evidence",
        "native_adapter_validated": False,
        "execution_status": "BLOCKED_ADAPTER_AND_REVIEW_REQUIRED",
        "consciousness_inference": "not_established",
        "human_review_status": "NOT_PERFORMED",
        "ethics_approval_status": "NOT_GRANTED",
    }
    for key, domain, question, hypothesis, paradigm, primary, controls, limits, sources, instrument in QUESTIONS:
        qid, hid = "RQ-" + key, "H-" + key + "-A"
        pid = "cog_" + key.lower().replace("-", "_") + "_v1"
        questions.append({"id": qid, "domain": domain, "question": question,
                          "relevance": paradigm + "; " + limits,
                          "literature": ["SRC-CNS-" + source for source in sources],
                          "hypotheses": [hid], "evidence": [], "status": "open",
                          "answer": {"current": None, "confidence": "none", "limitations": limits},
                          "created": DATE, "updated": DATE})
        hypotheses.append({"id": hid, "research_question": qid, "hypothesis": hypothesis,
                           "status": "untested", "evidence": [], "created": DATE, "updated": DATE})
        prereg = f"preregistrations/cognition/{pid}.json"
        protocols.append({"id": pid, "research_question": qid, "hypothesis": hid,
                          "paradigm": paradigm, "primary_outcome": primary,
                          "controls": controls, "limitations": limits,
                          "sources": ["SRC-CNS-" + source for source in sources],
                          "instrument_available": instrument, "preregistration_draft": prereg,
                          **common})
        conceptual = key in {"CNS-101", "EPI-102", "WEL-102", "WEL-103"}
        draft = {"schema_version": "cognition-draft-1.0", "protocol_id": pid,
                 "research_question": qid, "hypothesis": hid, "status": "DRAFT_NOT_PREREGISTERED",
                 "mode": "CONCEPTUAL_OR_NORMATIVE" if conceptual else "PROSPECTIVE_FUNCTIONAL_STUDY",
                 "primary_outcome": primary, "control_conditions": controls,
                 "experimental_unit": "argument_or_audit_case" if conceptual else "independently_initialized_network_or_predeclared_subject_cluster",
                 "seed_strategy": {"network_seed": "separate", "stimulus_seed": "separate_and_hidden_from_agent", "resampling_seed": "separate", "independent_n": None},
                 "sample_size_justification": "REQUIRED_BEFORE_NATIVE_RUN; pilot and precision/power plan must be separate from confirmatory data",
                 "minimum_relevant_effect": None,
                 "time_contract": {"dt_ms": None, "tick_vs_walltime": "separate", "latency_window": "freeze_before_data"},
                 "inclusion": ["all_scheduled_trials_with_predeclared_denominator", "verified_source_and_data_provenance"],
                 "exclusion": ["only_predeclared_technical_failures; retain exclusion log", "never_exclude_errors_to_improve_accuracy"],
                 "analysis_plan": {"primary_contrast": primary, "multiplicity": "freeze_family_and_correction_before_run", "uncertainty": "respect_network_subject_and_task_clusters", "equivalence": "prespecify_bounds; nonsignificance_is_not_equivalence", "conclusions": ["supports_scoped_function", "refutes_scoped_function", "inconclusive"]},
                 "stopping_rule": "freeze_maximum_budget_before_run; immediate_safety_stop_and_ethics_hold_override_scientific_schedule",
                 "blinding": ["private_answer_key", "no_future_stimulus_leak", "frozen_readout_and_holdout"],
                 "replication": {"independent_team": None, "data": None, "review": "NOT_PERFORMED"},
                 "ethics_policy": "ethics/AI_WELFARE_POLICY.md",
                 "freeze": {"status": "DRAFT", "frozen_at": None, "human_review_required": True},
                 **common}
        dump(ROOT / "research" / prereg, draft)
    for name, entries in (("questions.cognition.yaml", questions), ("hypotheses.cognition.yaml", hypotheses)):
        write(ROOT / "research/registry" / name, yaml.safe_dump(entries, allow_unicode=True, sort_keys=False))
    dump(ROOT / "research/protocols/COGNITION_CONSCIOUSNESS_V1.json", {
        "schema_version": "1.0", "created": DATE,
        "not_a_universal_consciousness_standard": True,
        "protocol_count": len(protocols), "protocols": protocols,
        "common_contract": "COGNITION_CONSCIOUSNESS.md",
        "raw_trial_required_fields": ["trial_id", "condition", "onset_tick", "dt_ms", "response", "omission", "source_commit", "state_hash", "stimulus_hash"],
        "empirical_brain5d_runs_performed_in_this_import": False})
    registry_sources, usage, bib = [], [], []
    lines = ["# Kognitionsprogramm: Quellen und tatsaechliche Nutzung", "",
             "Stichtag: 7. September 2026. Gezielte Ergaenzungsrecherche, keine vollstaendige systematische Datenbankreview. Die Auswahl folgt den Kritikthemen. Treffer-/Screeningzahlen werden nicht erfunden. Suchwege: Websuche, direkte Verlags-/Institutionen-HTML-Aufrufe, PubMed-Abstracts und offizielle Aufgabendokumentation; Repositorylekture separat. Keine native Vollsuche in Scopus, Web of Science oder PhilPapers.", "",
             "Zugang, gelesener Umfang und argumentative Verwendung stehen pro Quelle. Metadaten werden nicht als Volltextlekture ausgegeben. Keine der Quellen validiert Brain-5D; kein klinischer Datensatz wurde hier neu ausgewertet. Amtliche Rechtsabrufe hatten bei Wiederholung teilweise Timeouts; dies ist ausgewiesen. Die Bibliografie ist ein konservativer Austausch-Nachtrag, kein vollstaendiger bibliometrischer Audit.", ""]
    for key, authors, year, title, doi, url, capture, use in SOURCES:
        sid = "SRC-CNS-" + key
        linked = [q["id"] for q in questions if sid in q["literature"]]
        registry_sources.append({"source_id": sid, "authors": [authors], "title": title,
                                 "year": year, "doi": doi or None, "topic": ["cognition", "methodology", "ethics"],
                                 "claims": [], "brain5d_questions": linked,
                                 "brain5d_relevance": use + " Source: " + url})
        usage.append({"source_id": sid, "authors_literal": authors, "year": year, "title": title,
                      "doi": doi or None, "url": url, "accessed": DATE, "reading_scope": capture,
                      "argumentative_use": use, "brain5d_data_validated": False})
        lines.extend([f"<a id=\"{sid.lower()}\"></a>", f"## {sid}", "",
                      f"{authors} ({year}). *{title}*.", "", url, "",
                      f"**Gelesener Umfang:** {capture}.", "", f"**Verwendung und Grenze:** {use}", ""])
        safe_title = title.replace("{", "").replace("}", "")
        # Metadata is intentionally conservative: no invented journal/volume/pages.
        bib.append(f"@misc{{{sid},\n  title = {{{safe_title}}},\n  author = {{{authors}}},\n  year = {{{year}}},\n  url = {{{url}}},\n  note = {{{capture}. {use}}}" + (f",\n  doi = {{{doi}}}" if doi else "") + "\n}")
    write(ROOT / "research/registry/sources.cognition.yaml", yaml.safe_dump(registry_sources, allow_unicode=True, sort_keys=False))
    write(ROOT / "research/literature/COGNITION_SOURCES.md", "\n".join(lines))
    dump(ROOT / "research/literature/COGNITION_SOURCES.json", usage)
    write(ROOT / "research/literature/cognition_sources.bib", "\n\n".join(bib))


def wire_code() -> None:
    patch("src/research/registry.py", 'self.sources = self._load_yaml("sources.yaml", Source)',
          'self.sources = self._load_yaml_family("sources.yaml", "sources.*.yaml", Source)')
    patch("src/dashboard/experiment_workflow.py", "from src.research.data_v2 import prepare_research_data_v2",
          "from src.research.cognition_governance import (\n    CognitionGovernanceError,\n    cognition_catalog,\n    guard_cognition_launch,\n)\nfrom src.research.data_v2 import prepare_research_data_v2")
    patch("src/dashboard/experiment_workflow.py", '            "next_experiment_id": self._next_experiment_id(),',
          '            "cognition_protocols": cast(JSONValue, cognition_catalog(self._research_root)),\n            "next_experiment_id": self._next_experiment_id(),')
    patch("src/dashboard/experiment_workflow.py", '        hypothesis_id = required("hypothesis_id")\n        registry =',
          '        hypothesis_id = required("hypothesis_id")\n        try:\n            guard_cognition_launch(self._research_root, question_id, protocol)\n        except CognitionGovernanceError as exc:\n            raise WorkflowValidationError(str(exc)) from exc\n        registry =')
    patch("src/research/evidence_engine.py", "from .registry import (", "from .cognition_governance import guard_cognition_promotion\nfrom .registry import (")
    patch("src/research/evidence_engine.py", "        manifest = _check_experiment_valid(experiment_id)",
          "        guard_cognition_promotion(hypothesis_id, claim_id)\n        manifest = _check_experiment_valid(experiment_id)", 2)
    patch("src/research/catalog_status.py", "from .protocol_registry import protocol_catalog", "from .cognition_governance import PREFIXES\nfrom .protocol_registry import protocol_catalog")
    patch("src/research/catalog_status.py", '                "operational": question.id in operational,',
          '                "operational": question.id in operational,\n                "execution_status": (\n                    "BLOCKED_ADAPTER_AND_REVIEW_REQUIRED"\n                    if question.id.startswith(PREFIXES)\n                    else "existing_workflow_contract"\n                ),\n                "consciousness_inference": "not_established",')
    patch("src/dashboard/static/file-viewer.js", "await openFMFile('publications/reader/README.md');", "await openFMFile('publications/README.md');")
    patch("tests/browser/publication.spec.js", "    await expect(viewer).toContainText('vollstaendige Lesefassung');",
          "    await expect(viewer).toContainText('Aktuelle Fassung 1.2');\n    await viewer.getByRole('button', { name: 'Historische Lesefassung 1.0', exact: true }).click();\n    await expect(viewer).toContainText('vollstaendige Lesefassung');")


def import_edition() -> None:
    for file in OLD.iterdir():
        if file.is_file() and file.name not in {"manifest.json", "README.md"}:
            shutil.copyfile(file, NEW / file.name)
    front = {
        0: '# KI - Die geliehene Intelligenz\n\n## Wissenschaftliche Abhandlung - Fassung 1.2\n\nThomas Heisig · Brain-5D · 7. September 2026\n\nEpistemische Herkunft, kausale Leistungszuordnung, Bewusstseinskritik und vorsorgliche Forschungsethik.\n\nDiese Edition integriert die Kritik am hypothetischen Bewusstseinsbefund, die kritische Gegenwartsbewertung, den hypothetischen Vollausbau und das ethische Abschaltdilemma. Sie erweitert die Abhandlung um kanonische Forschungsfragen, versionierte Testvertraege und technische Schutzgrenzen. Neue empirische Brain-5D-Bewusstseinsnachweise werden nicht behauptet.\n\nDie Zahl fuenf ist keine bewiesene Naturkonstante der Intelligenz. Weder pauschale Abwertung noch Nobelpreis- oder Publikationsversprechen gelten als wissenschaftlicher Befund. Die Kritik selbst wird nach Quellen, Praemissen und Geltungsbereich geprueft.\n\nKI-unterstuetzte Ausarbeitung auf Auftrag des Autors; keine fingierte externe Begutachtung, menschliche Endfreigabe oder Ethikgenehmigung. Die Kapiteldateien dieser Edition sind die aktuelle Bearbeitungsquelle. Fruehere Fassungen, Originale und historische DATA/EVID bleiben unveraendert.',
        1: '# Zusammenfassung\n\nFassung 1.2 ergaenzt die theoretisch-methodische Untersuchung um die Frage, was ein moeglicher kuenstlicher Bewusstseinsbefund wissenschaftlich und ethisch bedeuten koennte. Phänomenales Erleben, funktionaler Zugriff, Metakognition, Selbstmodell, Valenz, moralischer Status und geltendes Recht werden getrennt. Ein bedingtes Identifizierbarkeitsargument beschreibt, warum beobachtungsäquivalente Modelle innerhalb desselben Versuchsraums nicht allein durch weitere Beobachtungen getrennt werden. Daraus folgt kein universeller Unmöglichkeitsbeweis.\n\n22 kanonische Fragen und Hypothesen verbinden etablierte Paradigmen mit expliziten Softwareadaptionen: Oddball, Local-Global, DMTS, Metakognition, LFP/EEG-Vorwärtsmodelle, perturbative Komplexität, Maskierung, zeitliche Aufmerksamkeit, Inhibition, Multisensorik, Closed Loop, Zeitskalen, Geometrie und späteren Dialog-/Transfertests. Ihre Messziele sind funktional oder theoriebedingt, nicht automatische Bewusstseinsdiagnosen. Ausgewählte Stimulus- und Auswertungsinstrumente sind implementiert; die nativen Adapter dieser neuen Batterie bleiben ungeprüft und gesperrt.\n\nEin Kritikregister bearbeitet alle 38 Themen der übermittelten Bewertungen. Es korrigiert sowohl überhöhte Erfolgsversprechen als auch unbelegte Unmöglichkeits-, Noten- oder Ablehnungsbehauptungen. Die Ethikrichtlinie unterscheidet Pause, Reset, Löschung und Kopie, begrenzt belastungssteigernde Forschung und wahrt unabhängige Sicherheitsabschaltungen. Wissenschaftliche Evidenzfreigabe und vorsorgliche Schutzentscheidungen haben verschiedene Beweislasten.\n\nDie Ergänzung führt keine neuen klinischen Studien, menschlichen Versuchspersonen oder bestätigenden Brain-5D-Lern-/Bewusstseinsversuche ein. Frühere technische Befunde behalten ihren engen Geltungsbereich. Methodische, normative und technische Verbesserungen werden von offenen empirischen Nachweispflichten getrennt.',
        2: '# Abstract\n\nRevision 1.2 extends the treatise with a critical research programme on consciousness indicators, cognitive-task validity, independent evidence review and precautionary AI welfare. Phenomenal experience, functional access, metacognition, valence, moral standing and legal status remain distinct. Conditional observational equivalence limits identification within a specified intervention set, without establishing a universal impossibility theorem.\n\nTwenty-two canonical questions and hypotheses are linked to prospective protocol contracts. Established paradigm families are adapted with controls, explicit measurement limits and draft preregistrations. Selected stimulus and scoring instruments are implemented and tested on constructed data; native Brain-5D adapters for this new battery are not validated. Launch and evidence-entry guards prevent misleading generic fallback and automatic promotion.\n\nA thirty-eight-item critique audit covers present limitations, a hypothetical completed architecture, unsupported acclaim and unsupported dismissal. Precautionary guidance distinguishes pausing, resetting, deletion and copying while preserving independent human-safety shutdown. No new empirical consciousness findings, clinical validation, external ethics approval or authenticated independent replication are claimed.',
        3: '# Leseweg und Orientierung\n\nDie Edition enthält die früheren Kapitel und Anhänge sowie fünf neue Anhänge K bis O. Der aktuelle Zusatz ist in Methodik, Ethik, Recht, Architektur, Geometrie, Evidenz, Statistik und Schlussposition verknüpft. Die unverändert übernommenen Teile behalten ihren ausgewiesenen historischen Quellenstand; eine vollständige erneute Prüfung aller Literaturbehauptungen wird nicht behauptet.\n\n[Bewusstseinskritik](section-051.md) · [Testprogramm](section-052.md) · [Ethisches Dilemma](section-053.md) · [Bewertungsszenarien](section-054.md) · [Evidenz und Integrationsbilanz](section-055.md)\n\nEmpirisch-technische Evidenzstufen sind keine Skala subjektiven Erlebens. Ein Softwaretest ist keine unabhängige biologische Studie. Ein begründeter Vorsorge-Hold ist keine Bewusstseinsbestätigung. Details der Edition stehen im [Manifest](manifest.json).',
    }
    revised = set(front) | {4}
    for index, body in front.items():
        old_text = (OLD / f"section-{index:03d}.md").read_text(encoding="utf-8")
        anchors = re.findall(r'<a id="[^"]+"></a>', old_text)
        write(NEW / f"section-{index:03d}.md", "\n".join(anchors) + "\n\n" + body)
    links = {6: (51, "Methodische Ergänzung: Bewusstseinsindikatoren und Identifizierbarkeit"),
             14: (53, "Vorsorgliche Ethik bei möglicher Empfindungsfähigkeit"),
             15: (53, "Abschaltung: geltendes Strafrecht und moralische Unsicherheit"),
             17: (51, "SNN, Substratannahmen und Bewusstseinsbehauptungen"),
             19: (52, "Dimensionsvergleich als kontrollierter Funktionsversuch"),
             26: (55, "Evidenzkandidaten und externe Replikation"),
             33: (52, "Äquivalenz, unabhängige Einheiten und Paradigmenadaption"),
             39: (54, "Vollständige Kritik der Gegenwarts- und Zukunftsbewertung"),
             40: (55, "Erweiterte Beitragsbilanz und ausdrücklich offene Nachweise")}
    for index, (target, title) in links.items():
        page = NEW / f"section-{index:03d}.md"
        text = page.read_text(encoding="utf-8")
        text += f'\n\n<a id="cognition-context-{index:03d}"></a>\n## Ergänzung der Fassung 1.2: {title}\n\n'
        text += f'Die neue Prüfung ist Bestandteil dieses Kapitels: [{title}](section-{target:03d}.md). '
        text += 'Dabei bleiben funktionaler Nachweis, theoriebedingte Interpretation, phänomenales Erleben und normative Bewertung getrennt. Die neuen kanonischen Fragen, Protokollentwürfe, Ethikregeln und technischen Grenzen werden im verknüpften Anhang konkretisiert; ältere Befunde erhalten dadurch keine weiter reichende Evidenzfreigabe.\n'
        write(page, text)
        revised.add(index)
    order = [f"section-{i:03d}.md" for i in range(56)]
    headings = {}
    for name in order:
        if name == "section-004.md":
            headings[name] = "Inhaltsverzeichnis"
        else:
            match = re.search(r"^# (.+)$", (NEW / name).read_text(encoding="utf-8"), re.M)
            if not match:
                raise ValueError(name)
            headings[name] = match.group(1)
    toc = "\n".join(f"- [{headings[name]}]({name})" for name in order)
    write(NEW / "section-004.md", '<a id="b5d-inhaltsverzeichnis"></a>\n# Inhaltsverzeichnis\n\n' + toc)
    for i in range(51, 56):
        page = NEW / f"section-{i:03d}.md"
        nav = "[Inhaltsübersicht](README.md)"
        if i > 51:
            nav += f" | [Zurück](section-{i-1:03d}.md)"
        if i < 55:
            nav += f" | [Weiter](section-{i+1:03d}.md)"
        write(page, nav + "\n\n" + page.read_text(encoding="utf-8") + "\n\n" + nav)
    write(NEW / "README.md", '# Aktuelle Fassung 1.2 - Wissenschaftliche Abhandlung\n\nThomas Heisig · 7. September 2026. Ergänzung zu Bewusstseinskritik, standardisierten Paradigmen, Evidenz und Vorsorge.\n\nDie Kapiteldateien sind die aktuelle redaktionelle Quelle. [Zentrale Publikationsübersicht](../README.md). Keine automatische Evidenzfreigabe, keine nachgewiesene künstliche Empfindungsfähigkeit und keine erteilte externe Ethikgenehmigung.\n\n## Vollständige Lesefassung\n\n' + toc + '\n\n## Wissenschaftliche Begleitmaterialien\n\n[Kritikregister](../../critique/CONSCIOUSNESS_CRITIQUE.md) · [Testverträge](../../protocols/COGNITION_CONSCIOUSNESS.md) · [Kanonische Fragen](../../registry/questions.cognition.yaml) · [Hypothesen](../../registry/hypotheses.cognition.yaml) · [Ethikrichtlinie](../../ethics/AI_WELFARE_POLICY.md) · [Quellennutzung](../../literature/COGNITION_SOURCES.md) · [BibTeX](../../literature/cognition_sources.bib) · [Editionsmanifest](manifest.json)\n\nDie bisherigen Methodenbeispiele und Literatur der Fassung 1.1 bleiben als übernommene Materialien enthalten. Eine neue DOCX-Fassung wird hier nicht behauptet. Prüfung: `python scripts/publication_cognition.py`.')
    files = {p.name: {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "size": p.stat().st_size} for p in sorted(NEW.iterdir()) if p.is_file() and p.name != "manifest.json"}
    manifest = {"schema_version": "1.0", "edition": "1.2", "date": DATE,
                "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "inherited_edition": "../" + OLD.name, "section_order": order,
                "section_count": len(order), "revised_sections": [f"section-{i:03d}.md" for i in sorted(revised)],
                "added_sections": order[51:], "files": files,
                "authority": "interpretation_only", "automatic_evidence_promotion": False,
                "new_empirical_consciousness_findings": False, "external_ethics_approval": "not_granted"}
    dump(NEW / "manifest.json", manifest)
    write(PUB / "README.md", '# Wissenschaftliche Abhandlung - zentrale Publikationsquelle\n\n## Aktuelle Fassung 1.2\n\n**Thomas Heisig: KI - Die geliehene Intelligenz.** Ergänzung vom 7. September 2026 zu Bewusstseinskritik, Kognitionsprüfungen, unabhängiger Evidenz und Forschungsethik.\n\n[Aktuelle Abhandlung vollständig lesen](' + NEW.name + '/README.md)\n\nDie kapitelweise Fassung 1.2 ist die aktuelle redaktionelle Single Source of Truth. 22 neue Fragen und Hypothesen, prospektive Testverträge und eine 38-Punkte-Kritikprüfung sind mit der Abhandlung verbunden. Ausgewählte Instrumente und Start-/Promotionsgrenzen sind implementiert; native Adapter der neuen Batterie, empirische Bewusstseinsbefunde und externe Ethikfreigaben werden nicht behauptet.\n\n[Kritik vollständig prüfen](../critique/CONSCIOUSNESS_CRITIQUE.md) · [Testprogramm](../protocols/COGNITION_CONSCIOUSNESS.md) · [Ethik und Abschaltdilemma](../ethics/AI_WELFARE_POLICY.md) · [Quellen und tatsächliche Nutzung](../literature/COGNITION_SOURCES.md)\n\n## Historische Fassungen\n\n[Fassung 1.1](' + OLD.name + '/README.md) · [Historische Lesefassung 1.0](reader/README.md) · [Word-Datei 1.0](2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.docx) · [Originalpaket](archives/Brain5D_Wissenschaftliche_Abhandlung_2026-09-07.zip) · [Originalprüfsummen](integrity.json)\n\nFrühere Originale bleiben unverändert. Eine neue Word-Datei wurde in dieser Ergänzung nicht erstellt. Die Publikation hat `authority=interpretation_only`; kanonische Forschungsregister und historische DATA/EVID werden nicht durch Textrevisionen freigegeben.\n\n## Prüfung\n\n```bash\npython scripts/publication_bundle.py\npython scripts/publication_revision.py\npython scripts/publication_cognition.py\npython -m pytest tests/test_cognition_program.py -q\n```\n\n[Katalog](catalog.json). Technische Testresultate sind keine wissenschaftliche oder institutionelle Ethikfreigabe.')
    catalog_path = PUB / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    for record in catalog["publications"]:
        record["current"] = False
    catalog["publications"].insert(0, {"id": "PUB-KI-GELIEHENE-INTELLIGENZ-20260907-V12", "title": "KI - Die geliehene Intelligenz, Fassung 1.2", "author": "Thomas Heisig", "date": DATE, "current": True, "entrypoint": "publications/README.md", "reader": "publications/" + NEW.name + "/README.md", "snapshot": "publications/" + NEW.name, "authority": "interpretation_only", "automatic_evidence_promotion": False, "read_only": True, "canonical_questions": "registry/questions.yaml", "canonical_hypotheses": "registry/hypotheses.yaml"})
    dump(catalog_path, catalog)


def add_navigation() -> None:
    append("research/README.md", '## Kognition, Bewusstseinskritik und vorsorgliche Ethik\n\n[Programm und Messgrenzen](protocols/COGNITION_CONSCIOUSNESS.md), [22 kanonische Fragen](registry/questions.cognition.yaml), [Hypothesen](registry/hypotheses.cognition.yaml), [38 Kritikthemen](critique/CONSCIOUSNESS_CRITIQUE.md), [Ethikrichtlinie](ethics/AI_WELFARE_POLICY.md), [Quellennutzung](literature/COGNITION_SOURCES.md), [aktuelle Abhandlung](publications/README.md). Die neue Batterie hat prospektive Entwürfe und getestete Instrumente, aber keine validierten nativen Adapter. Geschützte Starts und automatische EVID-Promotion sind blockiert; alte DATA/EVID bleiben unverändert.')
    append("README.md", '## Consciousness critique and research safeguards\n\nThe [current treatise](research/publications/README.md) integrates a [38-topic critique audit](research/critique/CONSCIOUSNESS_CRITIQUE.md), [22 registered research questions and protocol contracts](research/protocols/COGNITION_CONSCIOUSNESS.md), and a [precautionary ethics policy](research/ethics/AI_WELFARE_POLICY.md). Cognitive-task success is not a consciousness verdict. The new battery has tested stimulus/scoring instruments; unvalidated native adapters cannot silently fall back to generic experiments. No empirical consciousness findings or external ethics approval are claimed.')
    append("docs/08-roadmap/TODO.md", '## Bewusstseinskritik und Kognitionsprogramm (2026-09-07)\n\n- [x] Kritik, Definitionen, Testverträge und Ethik in Publikationsfassung 1.2 integrieren.\n- [x] 22 neue kanonische Fragen/Hypothesen mit Quellen und 22 prospektiven Entwürfen registrieren.\n- [x] Stimulus-/Auswertungsinstrumente und Start-/Promotionsgrenzen mit Regressionstests ergänzen.\n- [ ] Native Adapter einzeln implementieren und unabhängig gegen Referenzaufgaben prüfen; vorher keine Entwürfe als ausführbare Evidenz ausgeben.\n- [ ] Unabhängige Methoden-/Ethikexpertise gewinnen; kein bereits bestehendes Gremium behaupten.\n- [ ] Geeigneten lizenzierten EEG-Datensatz und ein physikalisch geprüftes Beobachtungsmodell festlegen.\n- [ ] Meta-d-prime-Fitter, live-process safe-state controller und authentifizierte externe Reviewkette separat validieren.\n- [ ] Echte präregistrierte Versuche mit begründeter Stichprobe, Holdout, Alternativmodellen und unabhängiger Replikation durchführen.\n- [ ] DOCX-Export der aktuellen kapitelweisen Edition und Hugging-Face-Deployment gesondert prüfen.')
    write(ROOT / "docs/06-research/CONSCIOUSNESS_AND_WELFARE.md", '# Kognition, Bewusstseinskritik und Wohlfahrtsvorsorge\n\nDie kanonischen Inhalte stehen im Research-Baum, nicht als unabhängige Kopie in docs.\n\n[Abhandlung 1.2](../../research/publications/README.md) · [Kritikregister](../../research/critique/CONSCIOUSNESS_CRITIQUE.md) · [Testprogramm](../../research/protocols/COGNITION_CONSCIOUSNESS.md) · [Ethikrichtlinie](../../research/ethics/AI_WELFARE_POLICY.md) · [Quellen](../../research/literature/COGNITION_SOURCES.md)\n\nDie Instrumente in `src/research/cognition_metrics.py` erzeugen keine Bewusstseinsentscheidung. `cognition_governance.py` sperrt neue geschützte Dashboard-Versuche ohne validierten Adapter und beide automatischen EVID-Erzeugungswege für diese neue Familie. Ein Review-Hold sperrt neue Workflow-Starts, nicht die unabhängige Sicherheitsabschaltung. Bereits laufende beliebige Prozesse werden dadurch nicht automatisch überwacht oder gestoppt.\n\nDie kanonischen Forschungsfragen sind im bestehenden Katalog sichtbar. Nicht alle geplanten Protokolle sind ausführbar; `cognition_protocols` und der Status `BLOCKED_ADAPTER_AND_REVIEW_REQUIRED` machen diese Grenze ausdrücklich. Für echte native Läufe sind validierter Adapter, vorab eingefrorenes Design, angemessene Vorsorge und dokumentierte unabhängige Prüfung nötig.')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        parser.error("Explicit --apply is required")
    if (NEW / "manifest.json").exists():
        print("Edition already imported; refusing to overwrite canonical files (no-op).")
        return
    import_program()
    wire_code()
    import_edition()
    add_navigation()
    print("Imported 22 questions/protocols and edition 1.2; tests and review remain separate.")


if __name__ == "__main__":
    main()
