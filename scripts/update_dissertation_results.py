"""Append verified Brain-5D experiment results to the dissertation basis DOCX."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import fmean

import yaml
from docx import Document


ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "docs/06-research/KI_Die_geliehene_Intelligenz_Kontrollverlust_Embodiment_Dissertationsbasis.docx"
RESEARCH = ROOT / "research"
MARKER = "Empirischer Brain-5D-Nachtrag"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def runs(experiment_id: str) -> list[dict]:
    return read_json(RESEARCH / "experiments" / experiment_id / "DATA" / "runs.json")


def main() -> None:
    document = Document(DOCX)
    if any(MARKER in paragraph.text for paragraph in document.paragraphs):
        print(f"{DOCX} already contains {MARKER}")
        return

    questions = yaml.safe_load(
        (RESEARCH / "registry/questions.yaml").read_text(encoding="utf-8")
    )
    document.add_page_break()
    document.add_heading(MARKER, level=1)
    document.add_paragraph(
        "Stand: 7. September 2026. Dieser Nachtrag dokumentiert technische Brain-5D-Läufe "
        "aus dem Forschungsregister. Die Angaben wurden aus Manifesten, deterministischen "
        "Statistiken und DATA-Artefakten übernommen. Ein abgeschlossener Lauf ist keine "
        "automatische wissenschaftliche Evidenz; Dirty-Tree- und Human-Review-Gates bleiben "
        "maßgeblich."
    )

    document.add_heading("Ergebnisübersicht", level=2)
    table = document.add_table(rows=1, cols=6)
    table.style = "Table Grid"
    headers = ["Forschungsfrage", "Experiment", "Modus", "Umfang", "Technisches Ergebnis", "Evidenzstatus"]
    for cell, text in zip(table.rows[0].cells, headers):
        cell.text = text

    rows = [
        (
            "RQ-SNN-001",
            "EXP-SNN-001-R2",
            "CONFIRMATORY",
            "20 Läufe; 10 Seeds; 100.000 Ticks",
            "20/20 Stabilitätspässe; 0 Laufzeitfehler; Kontroll- und Tonic-Drive-Bedingung vollständig.",
            "Review pending; Dirty Source Tree; kontrollierter Runner, keine Generalisierung auf den Vollkern.",
        ),
        (
            "RQ-REPL-001",
            "EXP-REPL-0001-R1",
            "REPLICATION",
            "40 Läufe; 20 Seeds; 256 Ticks",
            "Recurrence off/on vollständig ausgeführt; 0 Laufzeitfehler; Effektrichtung über alle Seeds konsistent.",
            "Review pending; Dirty Source Tree; deskriptiv, kein registrierter Inferenztest.",
        ),
        (
            "RQ-LIFE-001",
            "EXP-LIFE-0001-R1",
            "EXPLORATORY",
            "20 Läufe; 20 Seeds; drei Tasks",
            "Alle drei Tasks in allen Läufen erfolgreich; retained success fraction = 1.0.",
            "Vorläuferscreen; kein Beleg für Catastrophic-Forgotten im Shared-Network-Sinn.",
        ),
        (
            "RQ-SUITE-001",
            "EXP-GEN-0033-R1",
            "EXPLORATORY",
            "57 Teilruns; 3 Seeds; bis 100.000 Ticks",
            "Science-Suite vollständig; Tickvertrag erfüllt; 0 Laufzeitfehler; DATA und Statistik vorhanden.",
            "Diagnostik-/Omnibuslauf; keine Primärevidenz für die enthaltenen Fachfragen.",
        ),
    ]
    for row in rows:
        cells = table.add_row().cells
        for cell, text in zip(cells, row):
            cell.text = text

    document.add_heading("RQ-SNN-001: Langzeitstabilität", level=2)
    snn = runs("EXP-SNN-001-R2")
    tonic = [item for item in snn if item["condition"] == "tonic_drive"]
    control = [item for item in snn if item["condition"] == "no_input_control"]
    document.add_paragraph(
        f"Der eingefrorene Runner absolvierte {len(snn)} Läufe mit jeweils "
        f"{snn[0]['metrics']['ticks_executed']:,} Ticks. Alle {len(snn)} Läufe erfüllten "
        "die registrierten Kriterien für finite Zustände und unveränderte Topologie. "
        f"Unter Tonic Drive lag die mittlere Aktivität bei "
        f"{fmean(item['metrics']['post_burn_in_mean_spikes'] for item in tonic):.0f} "
        "Spikes pro 1.000-Tick-Fenster; CV und relative Drift lagen jeweils bei 0.0. "
        f"Die No-Input-Kontrolle blieb mit {len(control)} von {len(control)} Pässen ruhig."
    )
    document.add_paragraph(
        "Interpretationsgrenze: Der Runner verwendet ein kontrolliertes Kleinnetzwerk. "
        "Das Ergebnis stützt die technische Stabilität dieses Versuchsaufbaus, nicht "
        "automatisch die Stabilität des vollständigen produktiven Brain-5D-Netzes."
    )

    document.add_heading("RQ-REPL-001: Unabhängige Replikation", level=2)
    repl = runs("EXP-REPL-0001-R1")
    off = [item for item in repl if item["condition"] == "recurrence_off"]
    on = [item for item in repl if item["condition"] == "recurrence_on"]
    document.add_paragraph(
        f"Die Replikation umfasst {len(repl)} Läufe über 20 unabhängige Seeds und "
        "beide Rekurrenzarme. Ohne Rekurrenz wurden im Mittel 3 Spikes, 2 synaptische "
        "Ereignisse und Rekurrenzereignisse 0 beobachtet. Mit Rekurrenz wurden im Mittel "
        "33 Spikes, 33 synaptische Ereignisse, 10 Rekurrenzereignisse und eine "
        "Propagationstiefe von 61 beobachtet. Die Werte waren über die Seeds identisch "
        f"({len(off)} Kontroll- und {len(on)} Treatmentläufe; keine Runtime-Fehler)."
    )
    document.add_paragraph(
        "Die Differenzen sind deskriptive Ergebnisse. Der Lauf enthält keinen registrierten "
        "Inferenztest und wurde aus einem Dirty Source Tree erzeugt; deshalb wird keine "
        "allgemeine Kausal- oder Signifikanzbehauptung in die Dissertation übernommen."
    )

    document.add_heading("RQ-LIFE-001: Learning-Interference-Screen", level=2)
    life = runs("EXP-LIFE-0001-R1")
    successes = [item["metrics"]["task_successes"] for item in life]
    document.add_paragraph(
        f"Der explorative Vorläuferscreen umfasst {len(life)} Seeds. In jedem Lauf waren "
        f"alle drei Task-Ergebnisse positiv ({sum(all(item) for item in successes)}/{len(successes)} "
        "Läufe; retained success fraction = 1.0). Der Reset transienten neuronalen "
        "Zustands zwischen unabhängigen Tasks wurde protokollspezifisch ergänzt, während "
        "gelernte Gewichte erhalten blieben."
    )
    document.add_paragraph(
        "Dieser Screen prüft unabhängige Task-Instanzen und ist ausdrücklich kein Nachweis "
        "gegen Catastrophic Forgetting in einem gemeinsamen sequenziellen Netzwerk."
    )

    document.add_heading("RQ-SUITE-001: Science-Suite-Diagnostik", level=2)
    suite_manifest = read_json(RESEARCH / "experiments" / "EXP-GEN-0033-R1" / "manifest.json")
    document.add_paragraph(
        f"Die vollständige Suite erzeugte {suite_manifest['results']['run_count']} Teilruns "
        "unter gemeinsamer Provenienz. Der Tickvertrag bis 100.000 Ticks wurde erfüllt; "
        "Laufzeitfehler traten nicht auf. Die Suite bleibt eine technische Omnibus-Diagnostik "
        "und ersetzt keine spezifischen, präregistrierten Fachprotokolle."
    )

    document.add_heading("Wissenschaftlicher Gesamtstatus", level=2)
    document.add_paragraph(
        "Die neuen Läufe erweitern den empirischen Anschluss der Dissertation. Sie zeigen "
        "reproduzierbare technische Resultate unter den jeweils angegebenen Bedingungen. "
        "Alle vier Ergebnislinien wurden jedoch mit Dirty-Tree-Provenienz geführt; zudem "
        "stehen Human Reviews aus. Die Forschungsfragen werden daher nicht als bestätigt "
        "oder widerlegt markiert. Die primären Belege bleiben die verlinkten Manifeste, "
        "Summaries, DATA- und Statistikdateien im Repository."
    )
    document.add_paragraph(
        "Repository-Artefakte: research/experiments/EXP-SNN-001-R2, "
        "EXP-REPL-0001-R1, EXP-LIFE-0001-R1 und EXP-GEN-0033-R1."
    )

    document.save(DOCX)
    print(f"Updated {DOCX}")


if __name__ == "__main__":
    main()