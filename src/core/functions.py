import re

_filename_safe_re = re.compile(r"[^A-Za-z0-9._-]+")

def _safe_name(name: str) -> str:
    name = (name or "unnamed.bin").strip().replace(" ", "_")
    name = _filename_safe_re.sub("_", name)
    return name[:255]