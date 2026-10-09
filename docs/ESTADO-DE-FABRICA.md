# Estado de fábrica

## Referência atual

A Tank Mini foi restaurada para os presets e a biblioteca AMP/IR de fábrica em
09/10/2026. A exportação completa feita imediatamente depois do reset é a
referência oficial para qualquer trabalho futuro:

- Arquivo: `backups/factory-reset-20261009/export-all-factory.atkm`
- Tamanho: 1942 bytes
- Presets: 21 (1A a 7C)
- SHA-256: `9fab22aca5d93eb81d608297555cbde52d4452dce63cd35dbbe993a664879ba3`
- Validação: `tools/preset_config.py validate` concluída sem erro

Os presets e módulos listados em [EFEITOS-ATIVOS.md](../EFEITOS-ATIVOS.md)
correspondem a essa exportação de fábrica.

## Arquivos personalizados

Os CABs e AMPs usados nos testes anteriores continuam guardados em
`assets/cabs/not-installed/` e `assets/amps/not-installed/`. Eles estão
disponíveis localmente para uma futura instalação, mas **não estão instalados
na pedaleira após o reset**.

## Regra de manutenção

Esta exportação não deve ser sobrescrita. Depois de qualquer alteração no
dispositivo, crie uma nova exportação em `backups/`, valide-a e regenere
`EFEITOS-ATIVOS.md`.
