# Tank Mini Effects Automation

Ferramentas para proprietários da M-VAVE Tank Mini criarem, editarem,
validarem, importarem e exportarem presets, CABs e AMPs.

Leia primeiro:

- [INDEX.md](INDEX.md): estrutura do projeto.
- [docs/GUIA-COMPLETO.md](docs/GUIA-COMPLETO.md): fluxo de trabalho.
- [docs/REGRAS.md](docs/REGRAS.md): regras de segurança.
- [docs/ESTADO-DE-FABRICA.md](docs/ESTADO-DE-FABRICA.md): exportação-base após o reset.
- [EFEITOS-ATIVOS.md](EFEITOS-ATIVOS.md): estado atual dos presets.

## O que este projeto faz

Este projeto automatiza backups, validação, edição, importação e exportação de
presets da M-VAVE Tank Mini pelo M-EFCS. Também mantém o inventário dos CABs,
IRs e capturas AMP locais, separando arquivos instalados dos arquivos que estão
apenas disponíveis para testes.

## Estado atual

- A referência de fábrica está em [docs/ESTADO-DE-FABRICA.md](docs/ESTADO-DE-FABRICA.md).
- O estado confirmado na pedaleira está em [EFEITOS-ATIVOS.md](EFEITOS-ATIVOS.md).
- A ordem dos presets segue a intensidade: limpos, baixos e guitarras pesadas.
- CABs e AMPs personalizados ficam em `assets/*/not-installed/` até serem
  enviados explicitamente para a pedaleira.

## Fluxo recomendado

1. Leia [INDEX.md](INDEX.md), [docs/REGRAS.md](docs/REGRAS.md) e
   [docs/GUIA-COMPLETO.md](docs/GUIA-COMPLETO.md).
2. Faça um backup ATKM antes de qualquer alteração.
3. Edite uma cópia usando um plano JSON e valide o resultado.
4. Importe ou grave no M-EFCS somente com um comando explícito.
5. Exporte novamente o banco depois da gravação.
6. Atualize `EFEITOS-ATIVOS.md` e confirme que nenhum diálogo auxiliar ficou
   aberto.

## Ferramentas

- `tools/m_efcs_automation.py`: backup, importação, exportação e biblioteca.
- `tools/preset_config.py`: leitura, validação e edição de campos de preset.
- `tools/atkm.py`: inspeção, comparação, extração e substituição de registros.
- `tools/reorder_bank.py`: reorganização dos 21 slots sem alterar o conteúdo.
- `tools/update_effects_md.py`: geração do inventário documentado dos efeitos.

## Segurança

Os backups ficam em `backups/`. O executável `M-EFCS.exe` não é modificado.
Arquivos antigos devem ser movidos para `archive/`, nunca apagados durante uma
limpeza.

## Comandos principais

Execute a partir de `G:\Meu Drive\Tank mini\M-EFCS`:

```powershell
py tank-mini-effects-automation\tools\m_efcs_automation.py backup
py tank-mini-effects-automation\tools\m_efcs_automation.py export-all destino.atkm
py tank-mini-effects-automation\tools\m_efcs_automation.py import-preset 1A preset.tkm
py tank-mini-effects-automation\tools\update_effects_md.py destino.atkm
```

Os arquivos de trabalho ficam em `presets/active/`, os CABs em
`assets/cabs/`, os AMPs em `assets/amps/`, e versões antigas em `archive/`.
