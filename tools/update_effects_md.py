"""Atualiza docs/EFEITOS-ATIVOS.md a partir de um ATKM exportado."""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime
from pathlib import Path

from atkm import SLOTS, load
from preset_config import AMP_LABELS, CAB_FACTORY_LABELS, TYPE_LABELS, read_field


TOOL_DIR = Path(__file__).resolve().parent
PROJECT = TOOL_DIR.parent
DOC = PROJECT / "EFEITOS-ATIVOS.md"


def module_state(record: bytes, module: str, labels: dict[int, str]) -> str:
    enabled = read_field(record, f"{module}.enabled")
    kind = read_field(record, f"{module}.type_id")
    return f"{'ligado' if enabled else 'desligado'}: {labels.get(kind, f'tipo {kind}') }"


def update(bundle: Path, output: Path = DOC) -> str:
    data, count, kind = load(bundle)
    if kind != "atkm" or count != len(SLOTS):
        raise ValueError("o arquivo precisa ser um ATKM completo com 21 presets")

    rows: list[str] = []
    used_amps: set[int] = set()
    used_cabs: set[int] = set()
    for index, slot in enumerate(SLOTS):
        record = data[index * 92 : (index + 1) * 92]
        amp_id = read_field(record, "amp.model_id")
        cab_id = read_field(record, "cab.slot")
        used_amps.add(amp_id)
        used_cabs.add(cab_id)
        rows.append(
            "| {slot} | {amp} | {cab} | {fx} | {mod} | {delay} | {reverb} |".format(
                slot=slot,
                amp=AMP_LABELS.get(amp_id, f"índice {amp_id}"),
                cab=f"{cab_id}: {CAB_FACTORY_LABELS.get(cab_id, 'personalizado')}",
                fx=module_state(record, "fx", TYPE_LABELS["fx"]),
                mod=module_state(record, "mod", TYPE_LABELS["mod"]),
                delay=module_state(record, "delay", TYPE_LABELS["delay"]),
                reverb=module_state(record, "reverb", TYPE_LABELS["reverb"]),
            )
        )

    custom_cabs = sorted(
        p.relative_to(PROJECT).as_posix()
        for p in (PROJECT / "assets" / "cabs" / "not-installed").rglob("*")
        if p.is_file()
    )
    custom_amps = sorted(
        p.relative_to(PROJECT).as_posix()
        for p in (PROJECT / "assets" / "amps" / "not-installed").rglob("*")
        if p.is_file() and p.suffix.lower() in {".am2data", ".amx"}
    )
    digest = hashlib.sha256(data).hexdigest()
    content = [
        "# Efeitos ativos na Tank Mini",
        "",
        f"Fonte: `{bundle}`  ",
        f"Atualizado: {datetime.now().isoformat(timespec='seconds')}  ",
        f"SHA-256 do ATKM: `{digest}`",
        "",
        "Este arquivo é gerado por `tools/update_effects_md.py`. Sempre rode o comando depois de editar, importar ou gravar um preset.",
        "",
        "## Presets e módulos",
        "",
        "| Slot | AMP | CAB | FX | MOD | Delay | Reverb |",
        "|---|---|---|---|---|---|---|",
        *rows,
        "",
        "## Modelos AMP usados",
        "",
        *[f"- `{number}`: {AMP_LABELS[number]}" for number in sorted(used_amps)],
        "",
        "## Slots CAB usados",
        "",
        *[f"- `{number}`: {CAB_FACTORY_LABELS.get(number, 'personalizado')}" for number in sorted(used_cabs)],
        "",
        "## Arquivos CAB disponíveis localmente (não significa instalados)",
        "",
        *([f"- `{name}`" for name in custom_cabs] or ["- Nenhum arquivo CAB local encontrado."]),
        "",
        "## Arquivos AMP/AMX disponíveis localmente (não significa instalados)",
        "",
        *([f"- `{name}`" for name in custom_amps] or ["- Nenhum arquivo AMP local encontrado."]),
        "",
    ]
    # Mantém a seção de arquivos locais organizada e com caminhos completos.
    local_start = next((i for i, line in enumerate(content) if line.startswith("## Arquivos CAB")), len(content))
    content = content[:local_start] + [
        "## Biblioteca local — não instalada na pedaleira",
        "",
        "Os arquivos abaixo estão disponíveis no computador para testes e futuras instalações. Eles não fazem parte do estado atual da Tank Mini.",
        "",
        "### CAB/IR",
        "",
        *([f"- `{name}`" for name in custom_cabs] or ["- Nenhum arquivo CAB local encontrado."]),
        "",
        "### AMP/AM2Data",
        "",
        *([f"- `{name}`" for name in custom_amps] or ["- Nenhum arquivo AMP local encontrado."]),
        "",
        "### Registro",
        "",
        "- `assets/amps/MANIFESTO.md`: hashes SHA-256 e histórico dos arquivos AMP.",
        "",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(content), encoding="utf-8")
    return digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="ATKM exportado do estado atual da pedaleira")
    parser.add_argument("--output", type=Path, default=DOC)
    args = parser.parse_args()
    digest = update(args.bundle, args.output)
    print(f"atualizado: {args.output}; sha256 ATKM: {digest}")


if __name__ == "__main__":
    main()
