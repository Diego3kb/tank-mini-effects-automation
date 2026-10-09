"""Configuracao em lote de presets ATKM por campos conhecidos e valores brutos."""

import argparse
import hashlib
import json
from pathlib import Path

from atkm import RECORD_SIZE, SLOTS, load


# Cada campo ocupa 1 byte ou um inteiro de 16 bits little-endian.
# Os grupos paramN preservam os valores nativos quando a funcao depende do tipo.
FIELDS: dict[str, tuple[int, int, int, int]] = {
    "preset_volume_raw": (0, 1, 0, 100),
    "fx.enabled": (8, 1, 0, 1),
    "amp.enabled": (9, 1, 0, 1),
    "mod.enabled": (10, 1, 0, 1),
    "delay.enabled": (11, 1, 0, 1),
    "cab.enabled": (12, 1, 0, 1),
    "reverb.enabled": (13, 1, 0, 1),
    "fx.type_id": (14, 1, 0, 255),
    "amp.model_id": (15, 1, 0, 255),
    "mod.type_id": (16, 1, 0, 255),
    "delay.type_id": (17, 1, 0, 255),
    "reverb.type_id": (18, 1, 0, 255),
    "cab.slot": (19, 1, 1, 20),
    "amp.gain": (32, 2, 0, 100),
    "amp.level": (34, 2, 0, 100),
    "amp.bass": (36, 2, 0, 100),
    "amp.mid": (38, 2, 0, 100),
    "amp.treble": (40, 2, 0, 100),
    "cab.level": (80, 2, 0, 100),
    "cab.low_cut_raw": (82, 2, 0, 100),
    "cab.high_cut_raw": (84, 2, 0, 100),
}
for module, start, count in (("fx", 20, 4), ("mod", 44, 6), ("delay", 56, 6), ("reverb", 68, 6)):
    for n in range(count):
        FIELDS[f"{module}.param{n + 1}"] = (start + n * 2, 2, 0, 100)

TYPE_LABELS = {
    "fx": {0: "Noise Gate", 1: "Boost", 2: "Compress"},
    "mod": {0: "Chorus", 1: "Phaser", 2: "Tremolo", 3: "Flanger", 4: "Vibrato", 5: "Univibe", 6: "Autofilter"},
    "delay": {0: "Analog", 1: "Duck", 2: "dTape", 3: "Dual", 4: "Lofi"},
    "reverb": {0: "Room", 1: "Hall", 2: "Swell", 3: "Spring", 4: "Shimmer", 5: "Cloud"},
}
AMP_LABELS = {
    0: "UWE-Twins",
    1: "UK-C30Normal",
    2: "MarsVM410",
    3: "Victor_Mars",
    4: "BritPLEX_100",
    5: "MarsFD100",
    6: "Eagle_SAVAGE",
    7: "TH_DiselHgn",
    8: "PvEV5150",
    9: "FORTIN_CALI",
    10: "MessMktCln2",
    11: "CA-tweed",
    12: "BogSV20",
    13: "Juice_JIM",
    14: "Sur_SL68",
    15: "BasADAtube",
    16: "BasAlmbic",
    17: "BasG800K_7",
    18: "BasTR-Trad",
    19: "BasMarkT501",
}
CAB_FACTORY_LABELS = {
    1: "EAGLProV30s",
    2: "Sperimental",
    3: "Juice4x12V30",
    4: "Mess Bog",
    5: "FdChamp",
    6: "FdPrJunir",
    7: "Mar960BV30",
    8: "DizzlV30",
    9: "Elctrovoice",
    10: "MessRectV30",
    11: "TwinJensenC",
    12: "TwedDlx1X12",
    13: "FendShowman",
    14: "J120Rolnd",
    15: "AC30Silvers",
    16: "BassAgula25",
    17: "BassJensn10",
    18: "BassStdio22",
    19: "BassAmpg410",
    20: "BassEDN300",
}
ENUM_NAMES = {
    "amp.model": ("amp.model_id", AMP_LABELS),
    "fx.type": ("fx.type_id", TYPE_LABELS["fx"]),
    "mod.type": ("mod.type_id", TYPE_LABELS["mod"]),
    "delay.type": ("delay.type_id", TYPE_LABELS["delay"]),
    "reverb.type": ("reverb.type_id", TYPE_LABELS["reverb"]),
}
ALIASES = {
    "fx.gate": ("fx.param1", "fx.type_id", {0, 1, 2}),
    "fx.boost_gain": ("fx.param2", "fx.type_id", {1}),
    "fx.sustain": ("fx.param2", "fx.type_id", {2}),
    "fx.attack": ("fx.param3", "fx.type_id", {2}),
    "fx.level": ("fx.param4", "fx.type_id", {2}),
    "mod.speed": ("mod.param1", "mod.type_id", {0}),
    "mod.depth": ("mod.param2", "mod.type_id", {0}),
    "mod.mix": ("mod.param3", "mod.type_id", {0}),
    "reverb.decay": ("reverb.param1", "reverb.type_id", {0, 1, 3}),
    "reverb.mix": ("reverb.param2", "reverb.type_id", {0, 1, 3}),
    "reverb.high_pass": ("reverb.param3", "reverb.type_id", {0, 1, 3}),
    "reverb.low_pass": ("reverb.param4", "reverb.type_id", {0, 1, 3}),
    "reverb.depth": ("reverb.param5", "reverb.type_id", {0, 1}),
    "reverb.combs": ("reverb.param5", "reverb.type_id", {3}),
}


def resolved_field(record: bytes, name: str) -> str:
    if name in FIELDS:
        return name
    if name in ENUM_NAMES:
        return ENUM_NAMES[name][0]
    if name in ALIASES:
        base, selector, allowed = ALIASES[name]
        current_type = read_field(record, selector)
        if current_type not in allowed:
            raise ValueError(f"{name} exige {selector} em {sorted(allowed)}; atual: {current_type}")
        return base
    raise ValueError(f"campo desconhecido: {name}")


def read_field(record: bytes, name: str) -> int:
    offset, width, _, _ = FIELDS[resolved_field(record, name)]
    value = int.from_bytes(record[offset : offset + width], "little")
    return value + 1 if name == "cab.slot" else value


def write_field(record: bytearray, name: str, value: int | str) -> None:
    base = resolved_field(record, name)
    if name in ENUM_NAMES and isinstance(value, str):
        labels = ENUM_NAMES[name][1]
        match = next((key for key, label in labels.items() if label.casefold() == value.casefold()), None)
        if match is None:
            raise ValueError(f"{name}: nome desconhecido: {value}")
        value = match
    if type(value) is not int:
        raise ValueError(f"{name}: use numero inteiro")
    offset, width, minimum, maximum = FIELDS[base]
    if not minimum <= value <= maximum:
        raise ValueError(f"{name}: valor deve estar entre {minimum} e {maximum}")
    stored = value - 1 if name == "cab.slot" else value
    record[offset : offset + width] = stored.to_bytes(width, "little")


def show(data: bytes, slot: str) -> dict:
    if slot not in SLOTS:
        raise ValueError(f"slot invalido: {slot}")
    start = SLOTS.index(slot) * RECORD_SIZE
    record = data[start : start + RECORD_SIZE]
    result = {name: read_field(record, name) for name in FIELDS}
    result["slot"] = slot
    result["chain_order_raw"] = list(record[3:8])
    result["controles_nomeados"] = {
        name: read_field(record, name)
        for name in ALIASES
        if read_field(record, f"{name.split('.')[0]}.enabled")
        and read_field(record, ALIASES[name][1]) in ALIASES[name][2]
    }
    result["labels_observados"] = {
        module: labels[result[f"{module}.type_id"]]
        for module, labels in TYPE_LABELS.items()
        if result[f"{module}.type_id"] in labels
    }
    if result["amp.model_id"] in AMP_LABELS:
        result["amp_nome_tabela_am2_original"] = AMP_LABELS[result["amp.model_id"]]
    result["cab_nome_de_fabrica"] = CAB_FACTORY_LABELS[result["cab.slot"]]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    view = sub.add_parser("show", help="mostrar campos de um slot em JSON")
    view.add_argument("bundle", type=Path)
    selection = view.add_mutually_exclusive_group(required=True)
    selection.add_argument("--slot")
    selection.add_argument("--all", action="store_true")
    check = sub.add_parser("validate", help="conferir estrutura e faixas observadas nos 21 slots")
    check.add_argument("bundle", type=Path)
    apply = sub.add_parser("apply", help="aplicar plano JSON e criar novo ATKM")
    apply.add_argument("bundle", type=Path)
    apply.add_argument("plan", type=Path)
    apply.add_argument("output", type=Path)
    args = parser.parse_args()

    data, count, _ = load(args.bundle)
    if count != len(SLOTS):
        parser.error("informe um ATKM de 21 presets")
    if args.command == "show":
        result = {slot: show(data, slot) for slot in SLOTS} if args.all else show(data, args.slot.upper())
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if args.command == "validate":
        errors = []
        for slot in SLOTS:
            record = data[SLOTS.index(slot) * RECORD_SIZE : (SLOTS.index(slot) + 1) * RECORD_SIZE]
            if sorted(record[3:8]) != [1, 2, 3, 4, 5]:
                errors.append(f"{slot}: ordem da cadeia invalida")
            for name, (_, _, minimum, maximum) in FIELDS.items():
                value = read_field(record, name)
                if not minimum <= value <= maximum:
                    errors.append(f"{slot}: {name}={value} fora de {minimum}..{maximum}")
            if read_field(record, "amp.model_id") not in AMP_LABELS:
                errors.append(f"{slot}: modelo AMP desconhecido")
            for module, labels in TYPE_LABELS.items():
                if read_field(record, f"{module}.type_id") not in labels:
                    errors.append(f"{slot}: tipo {module} desconhecido")
        if errors:
            for error in errors:
                print(error)
            parser.exit(1, f"falhas: {len(errors)}\n")
        print(f"OK: {len(SLOTS)} slots; estrutura, ordem e faixas observadas validas")
        return

    if args.output.exists():
        parser.error("destino ja existe; escolha um novo nome")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    digest = hashlib.sha256(data).hexdigest()
    if plan.get("expected_sha256", "").lower() != digest:
        parser.error(f"hash original diferente ou ausente; atual: {digest}")
    edits = plan.get("edits")
    if not isinstance(edits, dict) or not edits:
        parser.error("plano deve ter objeto 'edits' nao vazio")
    result = bytearray(data)
    for slot, changes in edits.items():
        slot = slot.upper()
        if slot not in SLOTS or not isinstance(changes, dict) or not changes:
            parser.error(f"slot ou mudancas invalidas: {slot}")
        start = SLOTS.index(slot) * RECORD_SIZE
        record = bytearray(result[start : start + RECORD_SIZE])
        for field, value in sorted(changes.items(), key=lambda item: not (item[0].endswith("type_id") or item[0] in ENUM_NAMES)):
            if field == "chain_order_raw":
                if not isinstance(value, list) or sorted(value) != [1, 2, 3, 4, 5]:
                    parser.error("chain_order_raw deve ser uma permutacao de 1..5")
                old = list(record[3:8])
                record[3:8] = bytes(value)
                print(f"{slot} {field}: {old} -> {value}")
                continue
            old = read_field(record, resolved_field(record, field))
            write_field(record, field, value)
            print(f"{slot} {field}: {old} -> {value}")
        result[start : start + RECORD_SIZE] = record
    if result[-10:] != data[-10:]:
        raise AssertionError("rodape alterado")
    args.output.write_bytes(result)
    print(f"criado: {args.output}; sha256: {hashlib.sha256(result).hexdigest()}")


if __name__ == "__main__":
    main()
