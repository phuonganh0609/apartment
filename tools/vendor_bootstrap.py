"""Vendor a pinned Bootstrap stylesheet locally for offline UI."""

from pathlib import Path
from urllib.request import urlopen

target = (
    Path(__file__).resolve().parent.parent
    / "frontend"
    / "static"
    / "vendor"
    / "bootstrap.min.css"
)
if not target.exists():
    with urlopen(
        (
            "https://cdn.jsdelivr.net/npm/bootstr"
            "ap@5.3.8/dist/css/bootstrap.min.css"
        ),
        timeout=30,
    ) as response:
        data = response.read(400000)
    if (
        b"Bootstrap v5.3.8" not in b" ".join(data[:300].split())
        or len(data) < 100000
    ):
        raise RuntimeError("Unexpected Bootstrap content")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
print("Bootstrap stylesheet ready.")
