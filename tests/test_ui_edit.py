import sys, json, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from ui import app
from atkm import TRAILER

def client():
    app.config["TESTING"] = True
    return app.test_client()

def test_edit_cria_plano_e_banco(tmp_path):
    from conftest import make_bundle
    bundle = tmp_path / "b.atkm"; sha = make_bundle(bundle)
    plans_dir = tmp_path / "plans"; plans_dir.mkdir()
    app.config["PLANS_DIR"] = plans_dir
    r = client().post("/api/edit", json={
        "path": str(bundle),
        "edits": {"1A": {"amp.gain": 80, "reverb.enabled": 0}}})
    assert r.status_code == 200, r.get_json()
    out = Path(r.get_json()["output"])
    assert out.exists() and out.read_bytes().endswith(TRAILER)
    plano = json.loads(Path(r.get_json()["plan"]).read_text(encoding="utf-8"))
    assert plano["expected_sha256"] == sha
    assert plano["edits"] == {"1A": {"amp.gain": 80, "reverb.enabled": 0}}
    assert Path(r.get_json()["plan"]).parent == plans_dir

def test_edit_arquivo_ausente(tmp_path):
    app.config["PLANS_DIR"] = tmp_path / "plans"; app.config["PLANS_DIR"].mkdir()
    r = client().post("/api/edit", json={"path": str(tmp_path / "naoexiste.atkm"), "edits": {"1A": {"amp.gain": 10}}})
    assert r.status_code == 400
    assert list((tmp_path / "plans").iterdir()) == []  # nenhum plano gravado

def test_edit_apply_falha(tmp_path, monkeypatch):
    import ui
    from conftest import make_bundle
    bundle = tmp_path / "b.atkm"; make_bundle(bundle)
    app.config["PLANS_DIR"] = tmp_path / "plans"; app.config["PLANS_DIR"].mkdir()
    monkeypatch.setattr(ui, "run_tool", lambda args: __import__("subprocess").CompletedProcess(args, 1, stdout="", stderr="hash original diferente ou ausente"))
    r = client().post("/api/edit", json={"path": str(bundle), "edits": {"1A": {"amp.gain": 10}}})
    assert r.status_code == 400 and "hash original diferente" in r.get_json()["error"]
