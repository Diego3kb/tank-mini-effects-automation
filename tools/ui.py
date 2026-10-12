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

from flask import Flask, jsonify, render_template, request

TOOLS = Path(__file__).resolve().parent
PROJECT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from atkm import SLOTS, load  # noqa: E402
from preset_config import show  # noqa: E402

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.get("/")
def index():
    return render_template("index.html")


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


DEVICE_COMMANDS = {
    "backup": [],
    "export-all": [],
    "export-preset": ["slot", "path"],
    "import-preset": ["slot", "path"],
    "import-all": ["path"],
}


@app.post("/api/device")
def api_device():
    body = request.get_json(silent=True) or {}
    command = body.get("command")
    if command not in DEVICE_COMMANDS:
        return jsonify(error=f"comando desconhecido: {command}"), 400
    required = DEVICE_COMMANDS[command]
    missing = [field for field in required if not body.get(field)]
    if missing:
        return jsonify(error=f"campos obrigatorios ausentes: {missing}"), 400
    argv = ["tools/m_efcs_automation.py", command]
    for field in required:
        argv.append(str(body[field]))
    result = run_tool(argv)
    if result.returncode != 0:
        return jsonify(ok=False, error=(result.stdout + result.stderr).strip()), 400
    return jsonify(ok=True, log=result.stdout.strip())


LIBRARY_COMMANDS = {"cab": "open-cab", "amp": "open-amp"}
SAVE_COMMANDS = {"cab": "save-cab", "amp": "save-amp"}


@app.get("/api/library")
def api_library():
    cabs, amps = [], []
    for path in (PROJECT / "assets").rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(PROJECT).as_posix()
        suffix = path.suffix.lower()
        if suffix == ".wav":
            cabs.append(relative)
        elif suffix == ".am2data":
            amps.append(relative)
    return jsonify(cabs=sorted(cabs), amps=sorted(amps))


def run_library(argv: list[str]):
    result = run_tool(argv)
    if result.returncode != 0:
        return jsonify(ok=False, error=(result.stdout + result.stderr).strip()), 400
    return jsonify(ok=True, log=result.stdout.strip())


@app.post("/api/library/open")
def api_library_open():
    body = request.get_json(silent=True) or {}
    kind, path = body.get("kind"), body.get("path")
    if kind not in LIBRARY_COMMANDS or not path:
        return jsonify(error="informe kind (cab|amp) e path"), 400
    return run_library(["tools/m_efcs_automation.py", LIBRARY_COMMANDS[kind], str(path)])


@app.post("/api/library/save")
def api_library_save():
    body = request.get_json(silent=True) or {}
    kind, item = body.get("kind"), body.get("item")
    if kind not in SAVE_COMMANDS or not isinstance(item, int):
        return jsonify(error="informe kind (cab|amp) e item (numero)"), 400
    if body.get("confirm") is not True:
        return jsonify(error="confirmacao obrigatoria: envie confirm: true"), 400
    return run_library(["tools/m_efcs_automation.py", SAVE_COMMANDS[kind], str(item)])


if __name__ == "__main__":
    import threading
    import webbrowser

    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:8517")).start()
    app.run(host="127.0.0.1", port=8517, debug=False)
