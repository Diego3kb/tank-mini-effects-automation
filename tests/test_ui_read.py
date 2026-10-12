import sys, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from ui import app

def client():
    app.config["TESTING"] = True
    return app.test_client()

def test_bundle_ok(tmp_path):
    from conftest import make_bundle
    bundle = tmp_path / "b.atkm"; make_bundle(bundle)
    r = client().get(f"/api/bundle?path={bundle}")
    assert r.status_code == 200
    body = r.get_json()
    assert body["sha256"] == hashlib.sha256(bundle.read_bytes()).hexdigest()
    assert set(body["slots"]) == {f"{b}{l}" for b in range(1, 8) for l in "ABC"}
    assert body["slots"]["1A"]["cab_nome_de_fabrica"] == "EAGLProV30s"

def test_bundle_arquivo_invalido(tmp_path):
    lixo = tmp_path / "lixo.atkm"; lixo.write_bytes(b"x" * 100)
    r = client().get(f"/api/bundle?path={lixo}")
    assert r.status_code == 400 and "error" in r.get_json()

def test_bundle_ausente(tmp_path):
    r = client().get(f"/api/bundle?path={tmp_path/'naoexiste.atkm'}")
    assert r.status_code == 400
