import sys, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from ui import app

def client():
    app.config["TESTING"] = True
    return app.test_client()

def test_lista_biblioteca_real():
    r = client().get("/api/library")
    body = r.get_json()
    assert any("A7X-Self-Titled" in p for p in body["cabs"])
    assert any("Bogner Uberschall" in p for p in body["amps"])

def test_open_cab_argv(monkeypatch):
    import ui
    visto = {}
    def fake(args):
        visto["args"] = args
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
    monkeypatch.setattr(ui, "run_tool", fake)
    r = client().post("/api/library/open", json={"kind": "cab", "path": "assets/cabs/x.wav"})
    assert r.status_code == 200
    assert visto["args"] == ["tools/m_efcs_automation.py", "open-cab", "assets/cabs/x.wav"]

def test_save_sem_confirmacao(monkeypatch):
    import ui
    monkeypatch.setattr(ui, "run_tool", lambda a: subprocess.CompletedProcess(a, 0, stdout="", stderr=""))
    r = client().post("/api/library/save", json={"kind": "amp", "item": 3})
    assert r.status_code == 400 and "confirma" in r.get_json()["error"]
    r = client().post("/api/library/save", json={"kind": "amp", "item": 3, "confirm": True})
    assert r.status_code == 200
