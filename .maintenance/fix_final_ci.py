from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor missing in {path}")
    target.write_text(text.replace(old, new), encoding="utf-8")


replace(
    "src/dashboard/file_rendering.py",
    '''        payload = json.loads(completed.stdout[:PDF_TEXT_BYTES])
    except (OSError, subprocess.SubprocessError, ValueError, TypeError):
        return {}
    result: dict[str, Any] = {}
    format_info = payload.get("format") if isinstance(payload, dict) else None
    if isinstance(format_info, dict):
        if format_info.get("duration") is not None:
            try:
                result["duration_seconds"] = round(float(format_info["duration"]), 3)
            except (TypeError, ValueError):
                pass
        if format_info.get("format_name"):
            result["container"] = str(format_info["format_name"])
    streams = payload.get("streams") if isinstance(payload, dict) else None
    if isinstance(streams, list):
        codecs = sorted(
            {
                str(item.get("codec_name"))
                for item in streams
                if isinstance(item, dict) and item.get("codec_name")
            }
        )
        if codecs:
            result["codecs"] = codecs
        for item in streams:
            if isinstance(item, dict) and item.get("codec_type") == "video":
                if item.get("width") is not None:
                    result["width"] = int(item["width"])
                if item.get("height") is not None:
                    result["height"] = int(item["height"])
                break
    return result
''',
    '''        payload_object: object = json.loads(completed.stdout[:PDF_TEXT_BYTES])
    except (OSError, subprocess.SubprocessError, ValueError, TypeError):
        return {}
    if not isinstance(payload_object, dict):
        return {}
    payload = cast(dict[str, object], payload_object)
    result: dict[str, Any] = {}
    format_object = payload.get("format")
    if isinstance(format_object, dict):
        format_info = cast(dict[str, object], format_object)
        duration = format_info.get("duration")
        if duration is not None:
            try:
                result["duration_seconds"] = round(float(str(duration)), 3)
            except (TypeError, ValueError):
                pass
        format_name = format_info.get("format_name")
        if format_name:
            result["container"] = str(format_name)
    streams_object = payload.get("streams")
    if isinstance(streams_object, list):
        stream_items: list[dict[str, object]] = []
        codec_names: set[str] = set()
        for stream_object in streams_object:
            if not isinstance(stream_object, dict):
                continue
            item = cast(dict[str, object], stream_object)
            stream_items.append(item)
            codec_name = item.get("codec_name")
            if codec_name:
                codec_names.add(str(codec_name))
        if codec_names:
            result["codecs"] = sorted(codec_names)
        for item in stream_items:
            if item.get("codec_type") == "video":
                width = item.get("width")
                height = item.get("height")
                if width is not None:
                    result["width"] = int(str(width))
                if height is not None:
                    result["height"] = int(str(height))
                break
    return result
''',
)

replace(
    "tests/test_file_rendering.py",
    '''    graph = service.roots["docs"] / "flow.dot"
    graph.write_text("digraph G { a -> b; }")
    monkeypatch.setattr(
        file_rendering.shutil,
        "which",
        lambda name: "/usr/bin/dot" if name == "dot" else None,
    )
    monkeypatch.setattr(
        file_rendering.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout='<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>'
        ),
    )
''',
    '''    graph = service.roots["docs"] / "flow.dot"
    graph.write_text("digraph G { a -> b; }")

    def fake_which(name: str) -> str | None:
        return "/usr/bin/dot" if name == "dot" else None

    def fake_run(*args: object, **kwargs: object) -> SimpleNamespace:
        del args, kwargs
        return SimpleNamespace(
            stdout='<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>'
        )

    monkeypatch.setattr(file_rendering.shutil, "which", fake_which)
    monkeypatch.setattr(file_rendering.subprocess, "run", fake_run)
''',
)

replace(
    "tests/test_msba_experiment_runner.py",
    "from dataclasses import asdict\n",
    "from dataclasses import asdict\nfrom pathlib import Path\n",
)
replace(
    "tests/test_msba_experiment_runner.py",
    "def test_gateway_state_persists_to_separate_sidecar(tmp_path) -> None:",
    "def test_gateway_state_persists_to_separate_sidecar(tmp_path: Path) -> None:",
)
