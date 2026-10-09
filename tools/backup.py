"""Criar e conferir backup local dos presets e da configuracao do M-EFCS."""

import argparse
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from atkm import load


TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent.parent
BACKUPS = TOOL_DIR.parent / "backups"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(folder: Path, require_original_match: bool = False) -> None:
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    changed = []
    for item in manifest["files"]:
        original = ROOT / item["source"]
        saved = folder / item["copy"]
        if digest(saved) != item["sha256"]:
            raise ValueError(f"copia alterada: {saved}")
        if not original.exists() or digest(original) != item["sha256"]:
            changed.append(str(original))
    if require_original_match and changed:
        raise ValueError(f"originais divergentes durante criacao: {changed}")
    if "device_export" in manifest:
        item = manifest["device_export"]
        if digest(folder / item["copy"]) != item["sha256"]:
            raise ValueError("exportacao do pedal alterada")
    print(f"backup conferido: {folder}; arquivos: {len(manifest['files'])}; exportacao do pedal: {'sim' if 'device_export' in manifest else 'nao'}; originais alterados desde o backup: {len(changed)}")


def attach_export(folder: Path, source: Path) -> None:
    data, count, kind = load(source)
    if kind != "atkm" or count != 21:
        raise ValueError("exportacao deve ser ATKM com 21 presets")
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if "device_export" in manifest:
        raise ValueError("backup ja possui exportacao do pedal")
    target = folder / "device" / "export-all.atkm"
    target.parent.mkdir(exist_ok=True)
    shutil.copy2(source, target)
    manifest["device_export"] = {"copy": str(target.relative_to(folder)), "bytes": len(data), "sha256": digest(target)}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    verify(folder)


def create() -> None:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = BACKUPS / f"seguranca-{stamp}"
    folder.mkdir(parents=True, exist_ok=False)
    files = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in {".atkm", ".tkm"} and TOOL_DIR not in p.parents]
    cab_folder = ROOT / "CAB 16-21"
    if cab_folder.exists():
        files.extend(p for p in cab_folder.rglob("*") if p.is_file())
    files.append(TOOL_DIR.parent / "AppConfig.ini")
    previous = TOOL_DIR / "AppConfig.ini.before"
    if previous.exists():
        files.append(previous)
    entries = []
    for source in sorted(set(files)):
        rel = source.relative_to(ROOT)
        target = folder / "files" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        entries.append({"source": str(rel), "copy": str(target.relative_to(folder)), "bytes": source.stat().st_size, "sha256": digest(source)})
    (folder / "manifest.json").write_text(json.dumps({"created": datetime.now().isoformat(), "scope": "arquivos locais; nao inclui memoria do pedal", "files": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    verify(folder, require_original_match=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("create")
    check = sub.add_parser("verify")
    check.add_argument("folder", type=Path)
    attach = sub.add_parser("attach-device-export")
    attach.add_argument("folder", type=Path)
    attach.add_argument("source", type=Path)
    args = parser.parse_args()
    if args.command == "create":
        create()
    elif args.command == "verify":
        verify(args.folder)
    else:
        attach_export(args.folder, args.source)


if __name__ == "__main__":
    main()
