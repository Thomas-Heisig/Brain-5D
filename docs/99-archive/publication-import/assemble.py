"""Restore the authorized publication, checking every byte before integration."""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import subprocess
import tempfile
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from xml.etree import ElementTree as ET

REPO = "Thomas-Heisig/Brain-5D"
ROOT = Path.cwd()
IMPORT = ROOT / ".publication-import"
DEST = ROOT / "research/publications/2026-09-07_ki-die-geliehene-intelligenz"
ARCHIVE = ROOT / "research/publications/archives/Brain5D_Wissenschaftliche_Abhandlung_2026-09-07.zip"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def safe(root: Path, name: str) -> Path:
    path = root / name
    require(not Path(name).is_absolute() and ".." not in Path(name).parts, name)
    require(path.resolve().is_relative_to(root.resolve()), name)
    return path


def fetch_part(part: dict) -> bytes:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/git/blobs/{part['blob']}",
        headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                 "Accept": "application/vnd.github+json", "User-Agent": "Brain5D-publication-import"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = base64.b64decode(json.load(response)["content"])
    data = data[:part["size"]]
    if sha(data) != part["sha256"]:
        actual = [sha(data[i:i+256]) for i in range(0, len(data), 256)]
        print("CHUNK_DIAGNOSTIC", part["offset"], json.dumps(actual), flush=True)
        raise ValueError(f"Transport chunk mismatch at offset {part['offset']}")
    print("CHUNK VERIFIED", part["offset"], len(data), flush=True)
    return data


def zip_info(info: dict) -> zipfile.ZipInfo:
    result = zipfile.ZipInfo(info["filename"], tuple(info["date_time"]))
    for key, value in info.items():
        if key not in {"filename", "date_time"}:
            setattr(result, key, base64.b64decode(value) if key in {"extra", "comment"} else value)
    return result


def main() -> None:
    ready = json.loads((IMPORT / "READY.json").read_text())
    with ThreadPoolExecutor(max_workers=6) as pool:
        compressed = b"".join(pool.map(fetch_part, ready["chunks"]))
    require(sha(compressed) == ready["transport_sha256"], "Whole transport mismatch")
    sources = []
    for spec in ready["sources"]:
        data = safe(ROOT, spec["path"]).read_bytes()
        require(sha(data) == spec["sha256"], "Original source mismatch: " + spec["path"])
        sources.append(data)
    dictionaries = []
    for index in (2, 1, 0):
        with zipfile.ZipFile(io.BytesIO(sources[index])) as source:
            for name in sorted(source.namelist()):
                if not name.endswith((".xml", ".rels")):
                    continue
                raw = source.read(name)
                dictionaries.extend([raw, json.dumps(raw.decode(), ensure_ascii=False).encode()])
                try:
                    document = ET.fromstring(raw)
                    paragraphs = ["".join(p.itertext()) for p in document.findall(
                        ".//w:p", {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"})]
                    text = "\n\n".join(paragraphs)
                    dictionaries.extend([text.encode(), json.dumps(text, ensure_ascii=False).encode()])
                except ET.ParseError:
                    pass
    dictionary = b"\n".join(dictionaries)
    require(sha(dictionary) == ready["dictionary_sha256"], "Source dictionary mismatch")
    with tempfile.TemporaryDirectory() as work:
        temp = Path(work)
        (temp / "dictionary").write_bytes(dictionary)
        (temp / "transport.zst").write_bytes(compressed)
        subprocess.run(["zstd", "-d", "--long", "--patch-from=" + str(temp / "dictionary"),
                        str(temp / "transport.zst"), "-o", str(temp / "payload.json")], check=True)
        raw = (temp / "payload.json").read_bytes()
    require(sha(raw) == ready["payload_sha256"], "Payload mismatch")
    payload = json.loads(raw)
    archives = [zipfile.ZipFile(io.BytesIO(data)) for data in sources]

    def decode(data: dict) -> bytes:
        if "copy" in data:
            return sources[data["copy"]]
        if "source" in data:
            return archives[data["source"]].read(data["member"])
        if "text" in data:
            return data["text"].encode()
        if "base64" in data:
            return base64.b64decode(data["base64"])
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as target:
            target.comment = base64.b64decode(data["comment"])
            for member in data["zip"]:
                target.writestr(zip_info(member["info"]), decode(member["data"]))
        return output.getvalue()

    restored = {}
    for file in payload["files"]:
        data = decode(file["data"])
        require(len(data) == file["size"] and sha(data) == file["sha256"], "File mismatch: " + file["path"])
        restored[file["path"]] = data
    require(len(restored) == 41, "Expected exactly 41 publication files")
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
        target.comment = base64.b64decode(payload["archive"]["comment"])
        for member in payload["archive"]["entries"]:
            info = zip_info(member)
            info._compresslevel = 9
            target.writestr(info, restored[member["filename"].split("/", 1)[1]])
    archive = output.getvalue()
    require(sha(archive) == payload["archive"]["sha256"], "Whole original ZIP mismatch")
    for name, data in restored.items():
        path = safe(DEST, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            require(path.read_bytes() == data, "Refusing to overwrite divergent publication: " + name)
        path.write_bytes(data)
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_bytes(archive)
    inventory = [{key: file[key] for key in ("path", "size", "sha256")} for file in payload["files"]]
    (DEST.parent / "integrity.json").write_text(json.dumps({
        "package": DEST.name, "file_count": 41, "files": inventory,
        "archive": {"path": str(ARCHIVE.relative_to(DEST.parent)),
                    "sha256": sha(archive), "size": len(archive)},
        "publication_source_commit": "661681981458bc69fea5fce096e27f2b85b6c9d2",
        "authority": "interpretation_only", "automatic_evidence_promotion": False,
    }, ensure_ascii=False, indent=2) + "\n")
    subprocess.run(["python", str(DEST / "pruefsummen_pruefen.py")], check=True)
    print("VERIFIED: 41 byte-exact files and original archive", sha(archive), flush=True)


if __name__ == "__main__":
    main()
