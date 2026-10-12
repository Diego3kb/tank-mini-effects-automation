"""UI web local para bancos ATKM da Tank Mini.

Leitura offline importa as ferramentas direto; escrita e operacoes de
dispositivo vao por subprocess da CLI testada em tools/.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
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


@app.post("/api/edit")
def api_edit():
    body = request.get_json(silent=True) or {}
    raw, edits = body.get("path"), body.get("edits")
    if not raw or not isinstance(edits, dict) or not edits:
        return jsonify(error="informe path e edits"), 400
    path = resolve_path(raw)
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        return jsonify(error=str(exc)), 400
    plans_dir = Path(app.config.setdefault("PLANS_DIR", PROJECT / "plans"))
    plans_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    plan_path = plans_dir / f"plano-{stamp}.json"
    plan_path.write_text(
        json.dumps({"expected_sha256": hashlib.sha256(data).hexdigest(), "edits": edits},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    output = path.with_name(f"{path.stem}-edit-{stamp}.atkm")
    result = run_tool(["tools/preset_config.py", "apply", str(path), str(plan_path), str(output)])
    if result.returncode != 0:
        return jsonify(error=(result.stdout + result.stderr).strip()), 400
    return jsonify(
        output=str(output),
        sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        plan=str(plan_path),
        log=result.stdout.strip(),
    )
