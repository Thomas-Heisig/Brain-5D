from pathlib import Path

path = Path("src/dashboard/file_rendering.py")
text = path.read_text(encoding="utf-8")
old = '''    streams_object = payload.get("streams")
    if isinstance(streams_object, list):
        stream_items: list[dict[str, object]] = []
        codec_names: set[str] = set()
        for stream_object in streams_object:
'''
new = '''    streams_object = payload.get("streams")
    if isinstance(streams_object, list):
        stream_objects = cast(list[object], streams_object)
        stream_items: list[dict[str, object]] = []
        codec_names: set[str] = set()
        for stream_object in stream_objects:
'''
if old not in text:
    raise RuntimeError("ffprobe stream narrowing anchor missing")
path.write_text(text.replace(old, new), encoding="utf-8")
