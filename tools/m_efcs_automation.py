"""Automacao segura do M-EFCS para Tank Mini.

O programa usa os botoes do M-EFCS, sempre exporta um backup antes de
importar e nao envia nada ao pedal sem um comando explicito.
Requer Python 3 e pywinauto (ja instalado neste computador).
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from pywinauto import Desktop
from pywinauto.application import Application

from update_effects_md import update as update_effects_document


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "tank-mini-effects-automation"
EXE = ROOT / "M-EFCS.exe"
DEVICE_TITLE = "Tank Mini [Firmware Version:9]"
PRESET_COMBO = (
    "QApplication.TankMini.tabWidget_2.qt_tabwidget_stackedwidget."
    "tab_3.groupBox.combox_preset"
)


def app_window() -> tuple[Application, object]:
    windows = [w for w in Desktop(backend="uia").windows() if DEVICE_TITLE in w.window_text()]
    if windows:
        return Application(backend="uia").connect(process=windows[0].element_info.process_id), windows[0]
    app = Application(backend="uia").start(str(EXE), work_dir=str(ROOT))
    deadline = time.time() + 15
    while time.time() < deadline:
        windows = [w for w in Desktop(backend="uia").windows() if DEVICE_TITLE in w.window_text()]
        if windows:
            return app, windows[0]
        time.sleep(0.25)
    raise RuntimeError("M-EFCS nao abriu o Tank Mini")


def dialog_path(window, path: Path, save: bool) -> None:
    """Preenche o dialogo nativo sem depender da pasta atualmente aberta."""
    deadline = time.time() + 5
    while time.time() < deadline:
        dialogs = [w for w in Desktop(backend="uia").windows() if w.element_info.process_id == window.element_info.process_id]
        dialog = next((w for w in dialogs if any(c.element_info.automation_id in {"1001", "1148"} for c in w.descendants())), None)
        if dialog:
            edit = next(c for c in dialog.descendants() if c.element_info.control_type == "Edit" and c.element_info.automation_id in {"1001", "1148"})
            edit.set_edit_text(str(path))
            button_name = "Salvar" if save else "Abrir"
            button = next(c for c in dialog.descendants() if c.element_info.control_type == "Button" and c.element_info.automation_id == "1")
            if button_name == "Salvar" or button:
                button.invoke()
            return
        time.sleep(0.1)
    raise RuntimeError("dialogo de arquivo nao apareceu")


def combo(window):
    return next(c for c in window.descendants() if c.element_info.control_type == "ComboBox" and c.element_info.automation_id == PRESET_COMBO)


def control(window, *, title: str | None = None, control_type: str | None = None, auto_id: str | None = None):
    return next(
        c for c in window.descendants()
        if (title is None or c.element_info.name == title)
        and (control_type is None or c.element_info.control_type == control_type)
        and (auto_id is None or c.element_info.automation_id == auto_id)
    )


def close_auxiliary_dialogs(window) -> None:
    """Fecha diálogos internos deixados abertos por operações de lote."""
    for item in list(window.descendants()):
        if item.element_info.control_type == "Button" and item.element_info.name in {"Cancel", "Cancelar"}:
            if "SwapDialog" in item.element_info.automation_id:
                item.invoke()
                time.sleep(0.2)


def select_preset(window, slot: str) -> None:
    slot = slot.upper()
    box = combo(window)
    box.expand()
    # A lista Qt e uma janela popup. Selecionar pelo texto evita depender do indice.
    deadline = time.time() + 3
    while time.time() < deadline:
        item = next((x for x in window.descendants() if x.element_info.control_type == "ListItem" and x.element_info.name == slot), None)
        if item:
            item.invoke()
            time.sleep(0.4)
            if box.legacy_properties().get("Value") == slot:
                return
        time.sleep(0.1)
    raise RuntimeError(f"nao consegui selecionar o preset {slot}")


def export_all(window, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    control(window, title="Export all presets", control_type="Button").invoke()
    dialog_path(window, destination, save=True)
    time.sleep(0.4)
    if not destination.exists() or destination.stat().st_size != 1942:
        raise RuntimeError(f"exportacao ATKM invalida: {destination}")
    digest = update_effects_document(destination)
    print(f"efeitos ativos atualizados; sha256 ATKM: {digest}")


def export_current(window, slot: str, destination: Path) -> None:
    select_preset(window, slot)
    destination.parent.mkdir(parents=True, exist_ok=True)
    control(window, title="Export current preset", control_type="Button").invoke()
    dialog_path(window, destination, save=True)
    time.sleep(0.3)
    if not destination.exists() or destination.stat().st_size != 92:
        raise RuntimeError(f"exportacao TKM invalida: {destination}")


def import_current(window, slot: str, source: Path) -> None:
    if source.stat().st_size != 92:
        raise ValueError("preset atual deve ser um arquivo TKM de 92 bytes")
    select_preset(window, slot)
    control(window, title="Import current preset", control_type="Button").invoke()
    dialog_path(window, source, save=False)
    time.sleep(0.6)


def import_all(window, source: Path) -> None:
    if source.stat().st_size != 1942:
        raise ValueError("banco deve ser um arquivo ATKM de 1942 bytes")
    control(window, title="Import all presets", control_type="Button").invoke()
    dialog_path(window, source, save=False)
    time.sleep(0.8)


def safety_backup(window) -> Path:
    destination = PROJECT / "backups" / f"automation-before-{time.strftime('%Y%m%d-%H%M%S')}" / "export-all.atkm"
    export_all(window, destination)
    return destination


def open_module_file(window, tab: str, source: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(source)
    control(window, title=tab, control_type="TabItem").select()
    button = control(window, title="Open local file", control_type="Button")
    button.invoke()
    dialog_path(window, source, save=False)
    time.sleep(0.7)


def save_module_to_device(window, tab: str, item_index: int) -> None:
    """Audiciona o item e envia o modulo selecionado ao pedal.

    A interface Qt expõe a lista como controles customizados. O primeiro
    clique abre a audicao; o segundo comando usa o botao Save to device.
    """
    control(window, title=tab, control_type="TabItem").select()
    items = [x for x in window.descendants() if x.element_info.control_type == "ListItem" and ("tab_4" in x.element_info.automation_id or "tab_5" in x.element_info.automation_id)]
    if item_index < 1 or item_index > len(items):
        raise ValueError(f"item {item_index} fora da lista; existem {len(items)}")
    item = items[item_index - 1]
    item.invoke()
    time.sleep(0.8)
    control(window, title="Save to device", control_type="Button").invoke()
    time.sleep(0.8)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("backup", help="exporta todos os presets atuais")
    p = sub.add_parser("export-preset")
    p.add_argument("slot")
    p.add_argument("destination", type=Path)
    p = sub.add_parser("import-preset")
    p.add_argument("slot")
    p.add_argument("source", type=Path)
    p = sub.add_parser("export-all")
    p.add_argument("destination", type=Path)
    p = sub.add_parser("import-all")
    p.add_argument("source", type=Path)
    p = sub.add_parser("open-cab")
    p.add_argument("source", type=Path)
    p = sub.add_parser("open-amp")
    p.add_argument("source", type=Path)
    p = sub.add_parser("save-cab")
    p.add_argument("item", type=int)
    p = sub.add_parser("save-amp")
    p.add_argument("item", type=int)
    args = parser.parse_args()

    _, window = app_window()
    try:
        if args.command == "backup":
            destination = PROJECT / "backups" / f"automation-{time.strftime('%Y%m%d-%H%M%S')}" / "export-all.atkm"
            export_all(window, destination)
            print(f"backup: {destination}")
        elif args.command == "export-preset":
            export_current(window, args.slot, args.destination)
            print(f"exportado: {args.destination}")
        elif args.command == "import-preset":
            safety_backup(window)
            import_current(window, args.slot, args.source)
            print(f"importado no {args.slot.upper()}: {args.source}")
        elif args.command == "export-all":
            export_all(window, args.destination)
            print(f"exportado: {args.destination}")
        elif args.command == "import-all":
            safety_backup(window)
            import_all(window, args.source)
            print(f"banco importado: {args.source}")
        elif args.command == "open-cab":
            open_module_file(window, "Cab", args.source)
            print(f"CAB carregado na biblioteca: {args.source}")
        elif args.command == "open-amp":
            open_module_file(window, "Amx", args.source)
            print(f"AMP carregado na biblioteca: {args.source}")
        else:
            save_module_to_device(window, "Cab" if args.command == "save-cab" else "Amx", args.item)
            print("modulo enviado; confirme o slot exibido no M-EFCS")
    finally:
        close_auxiliary_dialogs(window)


if __name__ == "__main__":
    main()
