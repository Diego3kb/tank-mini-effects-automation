# Regras de trabalho da Tank Mini

1. Antes de importar, gravar ou trocar CAB/AMP, exportar um ATKM atual e
   guardar em `backups/`.
2. Nunca editar o executável `M-EFCS.exe` para alterar um preset. Editar uma
   cópia `.tkm` ou `.atkm` e manter o original intacto.
3. Um preset ativo só pode ter uma cópia de trabalho em
   `presets/active/<nome>/`. Versões antigas ficam em `archive/` ou `backups/`.
4. Toda alteração deve ter um plano JSON com o hash do ATKM de origem.
5. Validar o ATKM com `tools/atkm.py info` e
   `tools/preset_config.py validate` antes de importar.
6. Depois de importar e salvar no dispositivo, exportar o preset ou o banco de
   volta e comparar com o arquivo enviado.
7. Depois de qualquer mudança em FX, MOD, delay, reverb, AMP ou CAB, regenerar
   `EFEITOS-ATIVOS.md` na raiz com `tools/update_effects_md.py`.
8. CAB é arquivo WAV de IR; AMP capturado é `.am2Data`. O slot numérico do
   preset e o arquivo carregado na biblioteca são coisas diferentes e devem ser
   registrados separadamente.
9. Não apagar arquivos de trabalho ou backups durante uma limpeza. Mover para
   `archive/` com o motivo e a data.
10. Um agente novo deve ler `INDEX.md`, este arquivo e
    `docs/GUIA-COMPLETO.md` antes de editar qualquer coisa.
11. Toda alteração de preset, AMP, CAB ou efeito exige a atualização da
    documentação na mesma operação. Sem atualizar `EFEITOS-ATIVOS.md`, o
    trabalho fica incompleto.
12. Depois de gravar uma alteração no pedal, a documentação deve usar uma
    nova exportação do pedal, nunca apenas o arquivo planejado no computador.
13. Ao terminar uma operação, fechar ou cancelar qualquer diálogo auxiliar do
    M-EFCS, inclusive `Swap preset` e diálogos de arquivo. A tela deve voltar à
    janela principal antes de considerar a operação concluída.
14. A automação deve verificar que não há diálogo auxiliar aberto e registrar
    essa verificação no resultado da operação. Um seletor parado em um slot não
    substitui essa conferência.

## Comando padrão após uma alteração

```powershell
py tank-mini-effects-automation\tools\update_effects_md.py caminho\export-atual.atkm
```

`tools/m_efcs_automation.py export-all ...` já executa essa atualização
automaticamente depois de validar a exportação. A exportação completa deve ser
feita novamente depois de salvar a mudança no pedal; o backup anterior mostra o
estado antes da alteração.
