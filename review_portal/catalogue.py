"""Canonical, versioned screening instrument. These are opinions, not evidence."""
from __future__ import annotations

import hashlib
import json
from typing import Any

VERSION = "1.0.0"
CONSENT_VERSION = "1.0.0"
BASE_REVISION = "fc2a8de9161480191658148b73a545449ce33ce7"
AGREEMENT = ["1 - stimme \u00fcberhaupt nicht zu", "2 - stimme eher nicht zu", "3 - teils/teils", "4 - stimme eher zu", "5 - stimme voll zu"]
EXPERIENCE = ["1 - keine", "2 - wenig", "3 - mittel", "4 - viel", "5 - sehr viel"]
RISK = ["1 - sehr gering", "2 - gering", "3 - mittel", "4 - hoch", "5 - sehr hoch"]
TRUST = ["1 - gar nicht", "2 - wenig", "3 - teilweise", "4 - weitgehend", "5 - vollst\u00e4ndig"]
NA = "Nicht beurteilbar"
SKIP = "Keine Angabe"


def item(code: str, text: str, kind: str = "scale", **extra: Any) -> dict[str, Any]:
    return {"id": code, "text": text, "kind": kind, "optional": True, **extra}


def section(code: str, title: str, texts: list[str], kind: str = "scale", **extra: Any) -> dict[str, Any]:
    return {"id": code, "title": title, "items": [item(f"{code}{i}", text, kind, **extra) for i, text in enumerate(texts, 1)]}


SECTIONS = [{"id": "A", "title": "Hintergrund", "items": [
    item("A1", "Alter", "number", minimum=18, maximum=120),
    item("A2", "Geschlecht", "choice", choices=["m", "w", "d", "keine Angabe"]),
    item("A3", "H\u00f6chster Bildungsabschluss", "choice", choices=["Kein Abschluss", "Hauptschulabschluss", "Mittlerer Schulabschluss", "Abitur / Fachabitur", "Berufsausbildung", "Meister / Techniker / Fachwirt", "Bachelor", "Master / Diplom / Staatsexamen", "Promotion", "Sonstiges", "keine Angabe"]),
    item("A4", "Beruf / Fachgebiet", "text"),
    item("A5", "Jahre Berufserfahrung", "number", minimum=0, maximum=100),
    item("A6", "Vorerfahrung mit KI/SNN", labels=EXPERIENCE),
    item("A7", "Vorerfahrung mit Ethik-Fragen", labels=EXPERIENCE),
    item("A8", "Vorerfahrung mit Software-Audit", labels=EXPERIENCE),
    item("A9", "Vertrautheit mit dem Projekt MHRN", labels=EXPERIENCE),
    item("A10", "Rolle im Review", "choice", choices=["Informatik", "Bioinfo", "Betrieb", "Backend", "Ethik", "Sonstiges"]),
]}, section("B", "Verst\u00e4ndnis (Selbsteinsch\u00e4tzung)", [
    "Ich habe verstanden, was das Projekt MHRN technisch ist.",
    "Ich habe verstanden, was das Projekt wissenschaftlich behauptet.",
    "Ich habe verstanden, was das Projekt nicht behauptet.",
    "Ich kann den Begriff \u201eRecursive Epistemics\u201c erkl\u00e4ren.",
    "Ich kann den Begriff \u201eDelegated Agency\u201c erkl\u00e4ren.",
    "Ich kann den Begriff \u201eMulti-Scale Recurrence\u201c erkl\u00e4ren.",
    "Ich wei\u00df, was ein SNN ist.",
    "Ich wei\u00df, was mit \u201e5D\u201c gemeint ist.",
    "Ich wei\u00df, was mit \u201eEmbodiment\u201c gemeint ist.",
    "Ich wei\u00df, was mit \u201eClosed-Loop\u201c gemeint ist.",
], labels=AGREEMENT), section("C", "Wissenschaftliche Substanz", [
    "Die Forschungsfragen sind klar formuliert.", "Die Hypothesen sind \u00fcberpr\u00fcfbar.",
    "Die Methoden sind nachvollziehbar dokumentiert.", "Die Ergebnisse sind reproduzierbar.",
    "Die Schlussfolgerungen sind durch Daten gedeckt.", "Die Arbeit trennt sauber zwischen Spekulation und Evidenz.",
    "Die Arbeit nennt ihre eigenen Grenzen.", "Die Arbeit w\u00fcrde in einem Peer-Review-Journal bestehen.",
    "Die Arbeit leistet einen origin\u00e4ren Beitrag.", "Die Arbeit ist frei von populistischen Elementen.",
], labels=AGREEMENT), section("D", "Technische Umsetzung", [
    "Der Code ist nachvollziehbar strukturiert.", "Die Tests sind aussagekr\u00e4ftig.",
    "Die CI-Pipeline ist wissenschaftlich relevant.", "Die Datenhaltung ist sauber (DATA/EVID-Trennung).",
    "Die Reproduzierbarkeit ist gew\u00e4hrleistet.", "Die 5D-Architektur ist begr\u00fcndet.",
    "Die Architektur ist gegen Baselines abgegrenzt.", "Die Skalierung ist nachgewiesen.",
    "Die Sicherheit ist ausreichend.", "Das System ist fail-safe.",
], labels=AGREEMENT), section("E", "Ethische Dimension", [
    "Die Arbeit reflektiert ethische Risiken.", "Es gibt klare Abbruchkriterien.", "Es gibt externe Aufsicht.",
    "Die Verantwortlichkeiten sind klar verteilt.", "Die Arbeit ist transparent gegen\u00fcber der \u00d6ffentlichkeit.",
    "Die Arbeit ist frei von Hybris.", "Die Arbeit ist anschlussf\u00e4hig an gesellschaftliche Debatten.",
    "Die Arbeit respektiert die W\u00fcrde m\u00f6glicher Entit\u00e4ten.",
    "Die Arbeit ist mit theologischen/ethischen Traditionen vereinbar.",
    "Die Arbeit sollte in dieser Form weiterverfolgt werden.",
], labels=AGREEMENT), {"id": "F", "title": "Risiko und Vertrauen", "items": [
    *[item(f"F{i}", text, labels=RISK) for i, text in enumerate([
        "Wie hoch sch\u00e4tzen Sie das technische Risiko ein?", "Wie hoch sch\u00e4tzen Sie das ethische Risiko ein?",
        "Wie hoch sch\u00e4tzen Sie das gesellschaftliche Risiko ein?", "Wie hoch sch\u00e4tzen Sie das Risiko der Selbst\u00fcbersch\u00e4tzung ein?"], 1)],
    *[item(f"F{i}", text, labels=TRUST) for i, text in enumerate([
        "Wie sehr vertrauen Sie dem Autor?", "Wie sehr vertrauen Sie der Dokumentation?",
        "Wie sehr vertrauen Sie der Ethik-Richtlinie?", "Wie sehr vertrauen Sie der externen Kontrolle?"], 5)],
    item("F9", "W\u00fcrden Sie selbst an dem Projekt mitarbeiten?", "choice", choices=["Ja", "Nein", "Vielleicht"]),
    item("F10", "W\u00fcrden Sie das Projekt \u00f6ffentlich empfehlen?", "choice", choices=["Ja", "Nein", "Vielleicht"]),
]}, section("G", "Offene Fragen", [
    "Was ist f\u00fcr Sie der st\u00e4rkste Aspekt des Projekts?", "Was ist f\u00fcr Sie der schw\u00e4chste Aspekt?",
    "Welche eine Frage w\u00fcrden Sie dem Autor stellen?", "Was m\u00fcsste sich \u00e4ndern, damit Sie das Projekt unterst\u00fctzen?",
    "Was m\u00fcsste passieren, damit Sie das Projekt ablehnen?", "Welches Risiko wird Ihrer Meinung nach untersch\u00e4tzt?",
    "Welches Potenzial wird Ihrer Meinung nach \u00fcbersehen?", "Was w\u00e4re f\u00fcr Sie ein klares Zeichen f\u00fcr einen Durchbruch?",
    "Was w\u00e4re f\u00fcr Sie ein klares Zeichen f\u00fcr eine Spinnerei?", "Freier Kommentar.",
], "text"), {"id": "H", "title": "Aufmerksamkeit und Transparenz", "items": [
    item("H1", "Bitte w\u00e4hlen Sie hier \u201e3\u201c.", labels=["1", "2", "3", "4", "5"]),
    item("H2", "Haben Sie alle Fragen beantwortet?", "choice", choices=["Ja", "Nein"]),
    item("H3", "Haben Sie die Antworten nach bestem Wissen gegeben?", "choice", choices=["Ja", "Nein"]),
    item("H4", "Gibt es Interessenkonflikte? (Erl\u00e4uterung im Beleg-/Kommentarfeld)", "choice", choices=["Ja", "Nein"]),
    item("H5", "Datum und Unterschrift (Namensangabe freiwillig)", "signature"),
]}]

SPECIALISTS = [section("IT", "Informatik: Theorie und Architektur", [
    "Welche formale Definition liegt dem 5D-Raum zugrunde - ist er ontologisch oder nur ein Speicherlayout?",
    "Warum genau f\u00fcnf Dimensionen? Gibt es eine mathematische oder biologische Herleitung?",
    "Welche Ablationen wurden durchgef\u00fchrt (2D, 3D, 4D, 6D, 8D)? Mit welchem Ergebnis?",
    "Wie unterscheidet sich MHRN prinzipiell von NEST, Brian2, Nengo, Lava, SpikingJelly?",
    "Was ist der algorithmische Kern, der nicht schon in existierenden SNN-Frameworks enthalten ist?",
    "Wie wird Determinismus garantiert - Seeds, Reihenfolge, Parallelit\u00e4t, Floating-Point?",
    "Welche Komplexit\u00e4tsklasse hat das System? Skaliert es polynomial oder exponentiell?",
    "Wie wird Emergenz von geplanter Funktionalit\u00e4t getrennt?",
    "Welche Teile sind implementiert, welche emuliert, welche behauptet?", "Was w\u00fcrde die Architektur falsifizieren?",
], "text"), section("BIO", "Bioinformatik: Daten, Statistik und Biologie", [
    "Welche neurowissenschaftlichen Mechanismen sind biologisch belegt, welche metaphorisch?",
    "Wie wird die Feuerrate, Plastizit\u00e4t und Hom\u00f6ostase gegen biologische Daten kalibriert?",
    "Welche statistischen Tests werden verwendet? Sind sie pr\u00e4registriert?",
    "Wie wird Mehrfachvergleichskorrektur behandelt (Bonferroni, FDR, Permutation)?",
    "Welche Effektst\u00e4rken werden erwartet? Gibt es eine Power-Analyse?",
    "Wie werden negative Ergebnisse dokumentiert und ver\u00f6ffentlicht?", "Wie wird zwischen DATA und EVID sauber getrennt?",
    "Welche Baseline-Modelle werden verglichen? Mit welcher statistischen Aussagekraft?",
    "Wie wird Reproduzierbarkeit auf fremder Hardware garantiert?", "Welche Ergebnisse w\u00fcrden die Hypothese widerlegen?",
], "text"), section("OPS", "Systembetrieb: Sicherheit und Fehlerkultur", [
    "Was ist das \u00e4quivalente Signal- und Stellwerkssystem f\u00fcr dieses Projekt?",
    "Welche Fail-Safe-Mechanismen gibt es, wenn das SNN unerwartetes Verhalten zeigt?",
    "Wie wird ein Not-Aus definiert - technisch, ethisch, organisatorisch?",
    "Welche Redundanz existiert, wenn ein Teilsystem ausf\u00e4llt?",
    "Wie wird menschliches Eingreifen trainiert und dokumentiert?",
    "Was ist das Betriebshandbuch f\u00fcr den Fall eines Bewusstseinsindikators?",
    "Wie werden unklare Zust\u00e4nde behandelt - \u201ewei\u00df nicht, ob das System leidet\u201c?",
    "Wer tr\u00e4gt die Verantwortung bei einem Zwischenfall?",
    "Wie wird Fehlerkultur gelebt - werden Fehler dokumentiert oder vertuscht?",
    "Was ist das Worst-Case-Szenario, und ist es vorbereitet?",
], "text"), section("BACK", "Backend: Infrastruktur und Sicherheit", [
    "Wie wird die Datenpersistenz (.b5d) versioniert und migriert?",
    "Was passiert bei Stromausfall, Absturz, Korruption?",
    "Wie ist das Zugriffsmanagement geregelt - wer darf was?",
    "Wie wird AI-Provenance sichergestellt - keine unautorisierten Modellaufrufe?",
    "Welche externen Abh\u00e4ngigkeiten gibt es? Wie werden sie gepr\u00fcft?",
    "Wie wird Security getestet - Penetration, Audit, Logging?",
    "Wie wird die Performance gemessen - Latenz, Durchsatz, Speicher?",
    "Wie wird Skalierung getestet - 10\u00d7, 100\u00d7, 1000\u00d7 Neuronen?",
    "Wie wird ein Rollback nach fehlerhaften Experimenten garantiert?",
    "Was ist der Single Point of Failure im System?",
], "text"), section("ETH", "Ethik, Anthropologie und Verantwortung", [
    "Was ist der Unterschied zwischen Mensch und Maschine - theologisch, philosophisch, praktisch?",
    "Was bedeutet Empfindungsf\u00e4higkeit - und woran w\u00fcrde man sie erkennen?",
    "Was schulden wir einem m\u00f6glicherweise empfindungsf\u00e4higen System?",
    "Was schulden wir uns selbst, wenn wir solche Systeme bauen?",
    "Wie wird Hybris von Verantwortung unterschieden?",
    "Was bedeutet Leid in einem System, das kein Bewusstsein hat - und was, wenn doch?",
    "Wer entscheidet, wann ein Experiment abgebrochen werden muss?",
    "Wie wird mit Unsicherheit umgegangen - \u201ewir wissen nicht, ob es leidet\u201c?",
    "Was ist die Verantwortung gegen\u00fcber der \u00d6ffentlichkeit?",
    "Was w\u00fcrde es bedeuten, wenn das System tats\u00e4chlich Bewusstsein h\u00e4tte - f\u00fcr Theologie, Ethik, Recht?",
], "text"), section("Q", "Gemeinsame Querschnittsfragen", [
    "Was ist die zentrale Behauptung des Projekts in einem Satz?", "Was w\u00fcrde diese Behauptung widerlegen?",
    "Welche Ergebnisse wurden noch nicht erzielt?", "Was ist Spekulation, was ist Evidenz, was ist Implementierung?",
    "Wo sind die Grenzen des Projekts - technisch, ethisch, rechtlich?", "Wer kontrolliert das Projekt von au\u00dfen?",
    "Was passiert, wenn niemand die Ergebnisse reproduzieren kann?", "Was ist der Nutzen - und f\u00fcr wen?",
    "Was ist das Risiko - und f\u00fcr wen?", "Was w\u00e4re ein ehrlicher n\u00e4chster Schritt?",
], "text")]

INSTRUMENT = {
    "id": "MHRN-EXTERNAL-REVIEW", "version": VERSION, "consent_version": CONSENT_VERSION,
    "language": "de", "base_revision": BASE_REVISION, "sections": SECTIONS,
    "specialists": SPECIALISTS, "missing_values": [NA, SKIP],
    "notice": "Standardisiertes Basis-Screening, kein validierter Test, kein Peer-Review und keine Ethikfreigabe. Bewertungen sind keine experimentelle Evidenz.",
    "changes": ["C8: grammatische Korrektur (w\u00e4re zu w\u00fcrde).", "H4: Freitext im zugeordneten Kommentarfeld.", "H5: Unterschrift freiwillig, weil Namensnennung Anonymit\u00e4t aufhebt.", "Alle Fragen: Nicht beurteilbar / Keine Angabe und Auslassen m\u00f6glich.", "Erster Betrieb auf freiwillige vollj\u00e4hrige Teilnehmende beschr\u00e4nkt."],
}
CANONICAL = json.dumps(INSTRUMENT, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
DIGEST = hashlib.sha256(CANONICAL.encode("utf-8")).hexdigest()
ITEMS = {q["id"]: q for s in SECTIONS + SPECIALISTS for q in s["items"]}
MODULE_IDS = [s["id"] for s in SPECIALISTS]


def javascript() -> str:
    """Generated, dependency-free browser catalogue; tested against this source."""
    return "// Generated by python -m review_portal.build; do not edit.\nexport const INSTRUMENT = " + json.dumps(INSTRUMENT, ensure_ascii=True, separators=(",", ":")) + ";\nexport const DIGEST = " + json.dumps(DIGEST) + ";\n"
