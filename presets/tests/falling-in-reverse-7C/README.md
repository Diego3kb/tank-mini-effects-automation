# Teste de importação sem mudança de som

O arquivo `7C-atual.tkm` foi extraído do `export-all.atkm` salvo no backup verificado em `backups/seguranca-20261009-102130/device/`. Ele contém exatamente os 92 bytes do slot `7C` exportado do pedal em 09/10/2026.

Na exportação atual, os 21 slots passaram na validação; em comparação com `backup.atkm` de agosto, somente 8 bytes do slot `7C` são diferentes. A janela do M-EFCS identificou o equipamento como `Tank Mini [Firmware Version:9]`.

No M-EFCS conectado ao Tank Mini:

1. Selecione o preset `7C`.
2. Use **Import current preset** e escolha `7C-atual.tkm` desta pasta.
3. Se o aplicativo exigir **Save preset to device**, execute essa etapa no mesmo slot `7C`.
4. Use **Export all presets** e salve nesta pasta como `roundtrip-depois.atkm`.

Depois, o comando `py ..\atkm.py diff ..\backups\seguranca-20261009-102130\device\export-all.atkm roundtrip-depois.atkm` deve mostrar `bytes alterados: 0`. Uma diferença será investigada antes de criar presets modificados.

O controle de interface do M-EFCS não abriu nesta sessão, então esses cliques precisam ser feitos manualmente. O arquivo de teste não contém valores novos.
