from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

BASE_URL = os.environ.get("PREVIEW_BASE_URL", "http://127.0.0.1:8000")
ARTIFACT_DIR = Path(os.environ.get("PREVIEW_ARTIFACT_DIR", "preview-artifacts"))
PREVIEW_EMAIL = "preview@listerine.local"
PREVIEW_PASSWORD = "preview-secret"


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    with httpx.Client(base_url=BASE_URL, follow_redirects=True, timeout=30.0) as client:
        pages = {
            "health.json": client.get("/health").json(),
            "preview.html": client.get("/preview").text,
            "login.html": client.get("/login").text,
        }

        token = client.post(
            "/api/v1/auth/login",
            json={"email": PREVIEW_EMAIL, "password": PREVIEW_PASSWORD},
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        me = client.get("/api/v1/auth/me", headers=headers).json()
        households = client.get("/api/v1/households", headers=headers).json()
        lists = client.get(
            f"/api/v1/households/{households[0]['id']}/lists", headers=headers
        ).json()
        items = client.get(f"/api/v1/lists/{lists[0]['id']}/items", headers=headers).json()

    for filename, payload in pages.items():
        target = ARTIFACT_DIR / filename
        if filename.endswith(".json"):
            target.write_text(json.dumps(payload, indent=2) + "\n")
        else:
            target.write_text(str(payload))

    (ARTIFACT_DIR / "api-me.json").write_text(json.dumps(me, indent=2) + "\n")
    (ARTIFACT_DIR / "api-households.json").write_text(json.dumps(households, indent=2) + "\n")
    (ARTIFACT_DIR / "api-lists.json").write_text(json.dumps(lists, indent=2) + "\n")
    (ARTIFACT_DIR / "api-items.json").write_text(json.dumps(items, indent=2) + "\n")

    summary = """# PR preview bundle\n\nThis artifact was generated from a locally booted FastAPI app in preview mode.\n\nIncluded files:\n- `preview.html`: rendered seeded preview page\n- `login.html`: login page snapshot\n- `health.json`: health endpoint response\n- `api-*.json`: authenticated API responses for the seeded account\n"""
    (ARTIFACT_DIR / "README.md").write_text(summary)


if __name__ == "__main__":
    main()
