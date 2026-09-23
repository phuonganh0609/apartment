"""Offline static checks; does not replace Django's system checks and tests."""

import ast
from pathlib import Path

root = Path(__file__).resolve().parent.parent
files = [p for p in root.rglob("*.py") if ".venv" not in p.parts]
for path in files:
    ast.parse(
        path.read_text(encoding="utf-8"), filename=str(path.relative_to(root))
    )
apps = [
    "accounts",
    "buildings",
    "tenants",
    "contracts",
    "payments",
    "maintenance",
    "alerts",
    "reports",
    "regulations",
    "ai_assistant",
]
for app in apps:
    for name in ["__init__.py", "apps.py", "urls.py", "views.py"]:
        assert (
            root
            / ("chatbot" if app == "ai_assistant" else "backend")
            / app
            / name
        ).exists(), f"Missing {app}/{name}"
models = []
for app in apps:
    path = root / "models" / (app + ".py")
    if path.exists():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        models.extend(
            node.name for node in tree.body if isinstance(node, ast.ClassDef)
        )
expected = {
    "User",
    "Building",
    "Apartment",
    "Amenity",
    "ApartmentAmenity",
    "Tenant",
    "Contact",
    "Contract",
    "Payment",
    "MaintenanceRequest",
    "Regulation",
    "RegulationDocument",
}
assert set(models) == expected, models
for path in root.rglob("*.html"):
    if ".venv" in path.parts:
        continue
    content = path.read_text(encoding="utf-8")
    if 'method="post"' in content:
        assert "{% csrf_token %}" in content, f"Missing CSRF: {path}"
print(
    (
        "PASS: syntax of "
        f"{len(files)}"
        " Python files, 10 apps, exactly 12 "
        "domain models, CSRF tags in POST fo"
        "rms."
    )
)
