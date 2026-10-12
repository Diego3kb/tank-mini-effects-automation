# ui.js deve enviar path ao chamar export-preset (CLI exige slot + destination)
import re
from pathlib import Path

def test_export_preset_envia_path():
    js = (Path(__file__).resolve().parents[1] / "tools/static/ui.js").read_text(encoding="utf-8")
    assert re.search(r'device\("export-preset",\s*\{[^}]*path', js, re.S), "export-preset sem path"

def test_index_descreve_pastas_existentes():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    index = (root / "INDEX.md").read_text(encoding="utf-8")
    for folder in ["plans", "backups", "archive", "presets"]:
        assert folder in index, f"INDEX.md nao menciona {folder}/ que existe"
    for folder in ["docs", "tools", "assets", "plans", "backups", "archive", "presets"]:
        assert (root / folder).is_dir(), f"{folder}/ deveria existir"
