# Tank Mini Effects Automation

Tools for M-VAVE Tank Mini owners to create, edit, validate, import and
export presets, CABs and AMP captures.

## Start here

- [INDEX.md](INDEX.md): project structure.
- [docs/GUIA-COMPLETO.md](docs/GUIA-COMPLETO.md): complete workflow guide.
- [docs/REGRAS.md](docs/REGRAS.md): safety and documentation rules.
- [docs/ESTADO-DE-FABRICA.md](docs/ESTADO-DE-FABRICA.md): factory reset reference.
- [docs/FONTES-CABS-AMPS.md](docs/FONTES-CABS-AMPS.md): CAB and AMP sources.
- [EFEITOS-ATIVOS.md](EFEITOS-ATIVOS.md): current pedal state.

## What this project does

This project automates backups, validation, editing, importing and exporting
of Tank Mini presets through M-EFCS. It also tracks local CAB/IR files and AMP
captures, separating installed items from files that are only available for
testing.

## Current state

- The factory reference is documented in [docs/ESTADO-DE-FABRICA.md](docs/ESTADO-DE-FABRICA.md).
- The confirmed pedal state is documented in [EFEITOS-ATIVOS.md](EFEITOS-ATIVOS.md).
- Presets are organized from clean sounds to heavier guitar tones, with bass
  presets grouped before the final heavy guitar slots.
- Custom CABs and AMPs remain in `assets/*/not-installed/` until explicitly
  sent to the pedal.

## Recommended workflow

1. Read [INDEX.md](INDEX.md), [docs/REGRAS.md](docs/REGRAS.md) and
   [docs/GUIA-COMPLETO.md](docs/GUIA-COMPLETO.md).
2. Create an ATKM backup before every change.
3. Edit a copy using a JSON plan and validate the result.
4. Import or write to the M-EFCS only with an explicit command.
5. Export the bank again after writing the change to the pedal.
6. Update `EFEITOS-ATIVOS.md` and confirm that no auxiliary dialog remains
   open.

## Tools

- `tools/m_efcs_automation.py`: backup, import, export and library actions.
- `tools/preset_config.py`: read, validate and edit known preset fields.
- `tools/atkm.py`: inspect, compare, extract and replace preset records.
- `tools/reorder_bank.py`: reorder all 21 slots without changing record data.
- `tools/update_effects_md.py`: generate the documented active-effects list.

## Main commands

Run them from `G:\Meu Drive\Tank mini\M-EFCS`:

```powershell
py tank-mini-effects-automation\tools\m_efcs_automation.py backup
py tank-mini-effects-automation\tools\m_efcs_automation.py export-all destination.atkm
py tank-mini-effects-automation\tools\m_efcs_automation.py import-preset 1A preset.tkm
py tank-mini-effects-automation\tools\update_effects_md.py destination.atkm
```

## Safety

Backups are stored in `backups/`. The `M-EFCS.exe` executable is not modified.
Old files are moved to `archive/` instead of being deleted during cleanup.
Always use CABs and AMP captures that you are authorized to use.
