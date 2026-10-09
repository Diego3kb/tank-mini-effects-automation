# Automação do M-EFCS

O script `m_efcs_automation.py` controla o M-EFCS conectado ao Tank Mini.
Antes de importar banco ou preset ele exporta um backup ATKM em `backups/`.
Ao finalizar, a ferramenta fecha diálogos internos deixados pela interface,
como `Swap preset`, e a conferência final deve mostrar somente a janela
principal do M-EFCS.

```powershell
py tools\m_efcs_automation.py backup
py tools\m_efcs_automation.py export-preset 7A .\backups\7A-atual.tkm
py tools\m_efcs_automation.py import-preset 7A .\presets\active\afterlife-7A\7A HEAVY - AMP 8 CAB 11.tkm
py tools\m_efcs_automation.py export-all .\backups\export-atual.atkm
py tools\m_efcs_automation.py import-all .\backups\export-atual.atkm
py tools\m_efcs_automation.py open-cab caminho\captura.wav
py tools\m_efcs_automation.py open-amp caminho\captura.am2Data
```

`open-cab` e `open-amp` carregam arquivos na biblioteca do aplicativo. Depois
de conferir a lista no M-EFCS, `save-cab N` ou `save-amp N` envia o item N ao
dispositivo. O slot de destino deve ser conferido na própria tela antes do
envio.

Os comandos de exportação foram testados com a pedaleira conectada: o backup
gerado tem 1.942 bytes. O CAB A7X e o AMP Bogner também foram carregados na
biblioteca pelo script.
