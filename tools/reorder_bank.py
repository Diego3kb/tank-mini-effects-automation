"""Reorganiza os 21 presets de um ATKM sem alterar o conteúdo de cada registro."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from atkm import RECORD_SIZE, SLOTS, TRAILER, load, write_new


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("order", nargs=len(SLOTS), choices=SLOTS)
    args = parser.parse_args()
    data, count, kind = load(args.source)
    if kind != "atkm" or count != len(SLOTS):
        parser.error("a origem deve ser um ATKM completo")
    if len(set(args.order)) != len(SLOTS):
        parser.error("a ordem deve usar cada slot original uma única vez")
    records = {slot: data[i * RECORD_SIZE:(i + 1) * RECORD_SIZE] for i, slot in enumerate(SLOTS)}
    output_data = b"".join(records[slot] for slot in args.order) + TRAILER
    write_new(parser, args.output, output_data)


if __name__ == "__main__":
    main()
