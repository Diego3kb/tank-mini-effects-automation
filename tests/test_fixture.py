import subprocess, sys
from pathlib import Path

def test_make_bundle_passa_no_validate(tmp_path):
    from conftest import make_bundle
    bundle = tmp_path / "sintetico.atkm"
    sha = make_bundle(bundle)
    assert bundle.stat().st_size == 1942
    r = subprocess.run(
        [sys.executable, "tools/preset_config.py", "validate", str(bundle)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert sha == __import__("hashlib").sha256(bundle.read_bytes()).hexdigest()
