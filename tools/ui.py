"""UI web local para bancos ATKM da Tank Mini.

Leitura offline importa as ferramentas direto; escrita e operacoes de
dispositivo vao por subprocess da CLI testada em tools/.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

from flask import Flask, jsonify, request

TOOLS = Path(__file__).resolve().parent
PROJECT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from atkm import SLOTS, load  # noqa: E402
from preset_config import show  # noqa: E402

app = Flask(__name__, template_folder="templates", static_folder="static")


def run_tool(args: list[str]) -> subprocess.CompletedProcess:
    """Roda um script de tools/ em subprocess com a CLI testada."""
    return subprocess.run(
        [sys.executable, *args],
        cwd=PROJECT, capture_output=True, text=True, timeout=120,
    )


def resolve_path(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else PROJECT / path


@app.get("/api/bundle")
def api_bundle():
    raw = request.args.get("path", "")
    if not raw:
        return jsonify(error="informe path"), 400
    path = resolve_path(raw)
    try:
        data, _, _ = load(path)
    except (FileNotFoundError, ValueError) as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(
        path=str(path),
        sha256=hashlib.sha256(data).hexdigest(),
        slots={slot: show(data, slot) for slot in SLOTS},
    )
