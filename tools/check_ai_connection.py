from pathlib import Path
import sys
import os

(
    "Check the configured provider with s"
    "ynthetic data, without printing secr"
    "ets."
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import project_paths  # noqa: E402,F401
import django  # noqa: E402

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from ai_assistant.services.ai_client import (
    AIError,
    generate_json,
)  # noqa: E402

try:
    result = generate_json(
        "Return only a JSON object with a greeting string in Vietnamese.",
        {"request": "Say hello. This is synthetic connectivity test data."},
    )
    if not isinstance(result.get("greeting"), str) or not result["greeting"]:
        raise AIError("Phản hồi thiếu lời chào.")
    print("PASS: API returned a valid greeting.")
except AIError as exc:
    print(str(exc))
    sys.exit(1)
