import sys, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from ui import app

def client():
    app.config["TESTING"] = True
    return app.test_client()

def test_backup_ok(monkeypatch):
    import ui
    visto = {}
    def fake(args):
        visto["args"] = args
        return subprocess.CompletedProcess(args, 0, stdout="backup: ok\n", stderr="")
    monkeypatch.setattr(ui, "run_tool", fake)
    r = client().post("/api/device", json={"command": "backup"})
    assert r.status_code == 200 and r.get_json()["ok"] is True
    assert visto["args"][:2] == ["tools/m_efcs_automation.py", "backup"]

def test_import_preset_exige_slot_e_path(monkeypatch):
    import ui
    monkeypatch.setattr(ui, "run_tool", lambda args: subprocess.CompletedProcess(args, 0, stdout="", stderr=""))
    r = client().post("/api/device", json={"command": "import-preset"})
    assert r.status_code == 400
    r = client().post("/api/device", json={"command": "import-preset", "slot": "1A", "path": "x.tkm"})
    assert r.status_code == 200

def test_comando_desconhecido():
    r = client().post("/api/device", json={"command": "format-c:"})
    assert r.status_code == 400

def test_pedal_desconectado(monkeypatch):
    import ui
    monkeypatch.setattr(ui, "run_tool", lambda args: subprocess.CompletedProcess(args, 1, stdout="", stderr="M-EFCS nao abriu o Tank Mini"))
    r = client().post("/api/device", json={"command": "backup"})
    assert r.status_code == 400 and "M-EFCS nao abriu" in r.get_json()["error"]

def test_timeout_vira_400(monkeypatch):
    # O contrato: TimeoutExpired nunca escapa como 500 — o run_tool real converte
    # para CompletedProcess falho. O mock simula esse contrato.
    import ui
    def fake(args):
        return subprocess.CompletedProcess(args, 1, stdout="", stderr="tempo limite de 120s esgotado em tools/m_efcs_automation.py")
    monkeypatch.setattr(ui, "run_tool", fake)
    r = client().post("/api/device", json={"command": "backup"})
    assert r.status_code == 400 and "tempo" in r.get_json()["error"].lower()
