"""Inspecionar e manipular presets TKM/ATKM do M-EFCS sem usar o pedal."""

import argparse
import hashlib
from pathlib import Path


RECORD_SIZE = 92
TRAILER = b"PATCHEND\x00\x00"
SLOTS = tuple(f"{bank}{letter}" for bank in range(1, 8) for letter in "ABC")


def load(path: Path) -> tuple[bytes, int, str]:
    data = path.read_bytes()
    if len(data) == RECORD_SIZE:
        return data, 1, "tkm"
    if data.endswith(TRAILER):
        body_size = len(data) - len(TRAILER)
        if body_size == len(SLOTS) * RECORD_SIZE:
            return data, len(SLOTS), "atkm"
    raise ValueError(f"formato nao reconhecido: {path}")


def index_for_slot(parser: argparse.ArgumentParser, slot: str, count: int) -> int:
    name = slot.upper()
    if count == 1:
        parser.error("esta operacao exige um arquivo ATKM completo")
    if name not in SLOTS:
        parser.error("slot deve estar entre 1A e 7C")
    return SLOTS.index(name)


def write_new(parser: argparse.ArgumentParser, output: Path, data: bytes) -> None:
    if output.exists():
        parser.error("destino ja existe; escolha um novo nome")
    output.write_bytes(data)
    print(f"criado: {output}; sha256: {hashlib.sha256(data).hexdigest()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    info = sub.add_parser("info", help="resumo e hash")
    info.add_argument("file", type=Path)
    dump = sub.add_parser("dump", help="bytes de um preset")
    dump.add_argument("file", type=Path)
    dump.add_argument("--slot", help="posicao no arquivo ATKM, por exemplo 2A")
    diff = sub.add_parser("diff", help="comparar dois arquivos byte a byte")
    diff.add_argument("original", type=Path)
    diff.add_argument("changed", type=Path)
    audit = sub.add_parser("audit", help="comparar slots ATKM com arquivos TKM nomeados por slot")
    audit.add_argument("bundle", type=Path)
    audit.add_argument("folder", type=Path)
    extract = sub.add_parser("extract", help="extrair um slot como arquivo TKM")
    extract.add_argument("source", type=Path)
    extract.add_argument("output", type=Path)
    extract.add_argument("--slot", required=True)
    replace = sub.add_parser("replace", help="substituir um slot ATKM por arquivo TKM")
    replace.add_argument("source", type=Path)
    replace.add_argument("patch", type=Path)
    replace.add_argument("output", type=Path)
    replace.add_argument("--slot", required=True)
    replace.add_argument("--sha256", help="hash esperado do arquivo ATKM original")
    edit = sub.add_parser("set-byte", help="criar copia com um byte alterado")
    edit.add_argument("source", type=Path)
    edit.add_argument("output", type=Path)
    edit.add_argument("--slot", help="posicao no arquivo ATKM")
    edit.add_argument("--offset", type=int, required=True)
    edit.add_argument("--expect", type=int, required=True)
    edit.add_argument("--value", type=int, required=True)
    edit.add_argument("--sha256", help="hash esperado do arquivo de entrada")
    args = parser.parse_args()

    if args.command == "info":
        data, count, kind = load(args.file)
        print(f"tipo: {kind}; bytes: {len(data)}; presets: {count}; bytes por preset: {RECORD_SIZE}")
        print(f"sha256: {hashlib.sha256(data).hexdigest()}")
    elif args.command == "dump":
        data, count, _ = load(args.file)
        if count > 1 and not args.slot:
            parser.error("informe --slot para arquivos ATKM")
        start = index_for_slot(parser, args.slot, count) * RECORD_SIZE if count > 1 else 0
        for offset in range(0, RECORD_SIZE, 16):
            chunk = data[start + offset : start + min(offset + 16, RECORD_SIZE)]
            print(f"{offset:02d}: {chunk.hex(' ')}")
    elif args.command == "diff":
        before, a_count, _ = load(args.original)
        after, b_count, _ = load(args.changed)
        if a_count != b_count:
            parser.error(f"numero de presets diferente: {a_count} vs {b_count}")
        changes = [(i, a, b) for i, (a, b) in enumerate(zip(before, after)) if a != b]
        print(f"bytes alterados: {len(changes)}")
        for i, a, b in changes:
            where = f"slot {SLOTS[i // RECORD_SIZE]}, " if a_count > 1 else ""
            print(f"{where}offset {i % RECORD_SIZE:02d}: {a:02x} -> {b:02x}")
    elif args.command == "audit":
        data, count, _ = load(args.bundle)
        if count != len(SLOTS):
            parser.error("audit exige um arquivo ATKM completo")
        files = {p.stem.upper(): p for p in args.folder.glob("*.tkm") if p.stem.upper() in SLOTS}
        if not files:
            parser.error("nenhum TKM com nome de slot encontrado")
        matched = 0
        mismatched = 0
        for slot in SLOTS:
            if slot not in files:
                continue
            patch, patch_count, _ = load(files[slot])
            if patch_count != 1:
                parser.error(f"TKM invalido: {files[slot]}")
            index = SLOTS.index(slot)
            equal = data[index * RECORD_SIZE : (index + 1) * RECORD_SIZE] == patch
            print(f"{slot}: {'IGUAL' if equal else 'DIFERENTE'} ({files[slot].name})")
            matched += equal
            mismatched += not equal
        print(f"conferidos: {matched + mismatched}; iguais: {matched}; diferentes: {mismatched}")
        if mismatched:
            parser.exit(1)
    elif args.command == "extract":
        data, count, _ = load(args.source)
        index = index_for_slot(parser, args.slot, count)
        write_new(parser, args.output, data[index * RECORD_SIZE : (index + 1) * RECORD_SIZE])
    elif args.command == "replace":
        data, count, _ = load(args.source)
        index = index_for_slot(parser, args.slot, count)
        patch, patch_count, _ = load(args.patch)
        if patch_count != 1:
            parser.error("patch deve ser um arquivo TKM de 92 bytes")
        if args.sha256 and hashlib.sha256(data).hexdigest() != args.sha256.lower():
            parser.error("hash do ATKM original diferente")
        start = index * RECORD_SIZE
        result = data[:start] + patch + data[start + RECORD_SIZE :]
        write_new(parser, args.output, result)
    else:
        data, count, _ = load(args.source)
        if count > 1 and not args.slot:
            parser.error("informe --slot para arquivos ATKM")
        index = index_for_slot(parser, args.slot, count) if count > 1 else 0
        if not 0 <= args.offset < RECORD_SIZE:
            parser.error("offset fora de 0..91")
        if not 0 <= args.expect <= 255 or not 0 <= args.value <= 255:
            parser.error("valores devem estar entre 0 e 255")
        if args.sha256 and hashlib.sha256(data).hexdigest() != args.sha256.lower():
            parser.error("hash do arquivo original diferente")
        position = index * RECORD_SIZE + args.offset
        if data[position] != args.expect:
            parser.error(f"valor antigo diferente: {data[position]} (0x{data[position]:02x})")
        result = bytearray(data)
        result[position] = args.value
        write_new(parser, args.output, bytes(result))


if __name__ == "__main__":
    main()
