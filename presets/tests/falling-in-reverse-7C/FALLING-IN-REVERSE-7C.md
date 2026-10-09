# Falling in Reverse — timbre pesado, banco 7C

Criado a partir da exportação atual da pedaleira, salva no backup `seguranca-20261009-102130`. Os outros 20 presets não foram alterados.

## Arquivos

- `falling-in-reverse-7C.tkm`: importe como preset individual no slot **7C**.
- `falling-in-reverse-7C.atkm`: conjunto completo para conferir ou restaurar o banco com a alteração em 7C. Evite importar o conjunto inteiro se quiser mudar apenas 7C.
- `falling-in-reverse-7C-plano.json`: parâmetros usados para gerar os arquivos.

## No M-EFCS

1. Conecte a Tank Mini e abra o M-EFCS.
2. Selecione **7C**.
3. Use **Import current preset** e escolha `falling-in-reverse-7C.tkm`.
4. Use **Save preset to device** para gravar em 7C.
5. Use **Export all presets** e salve como `falling-in-reverse-7C-lido.atkm` nesta pasta. Isso permite conferir o que ficou no pedal.

## Ajuste proposto

AMP ligado no slot 9 (índice interno 8), boost com gate 55 e ganho 24, amp gain 78, bass 46, mid 61, treble 61, CAB ligado no slot 10 (Mesa Rect V30 no catálogo original), modulação e delay desligados, reverb desligado. O volume do preset e do amp ficaram nos valores originais de 7C. A interpretação física dos cortes da caixa ainda não foi confirmada no M-EFCS; use o ouvido e ajuste após a importação, se necessário.

O arquivo `.tkm` referencia os slots AMP 9 e CAB 10; ele não contém um arquivo AMX/AM2 de captura de amplificador nem o áudio WAV do IR. A tabela antiga AM2 embutida no M-EFCS chama o AMP 9 de `PvEV5150`, mas `G:\Meu Drive\Tank mini\2026\AMPS 2026.txt` lista o slot 9 como `MS_HIGAIN` após a atualização AM4. O nome que aparece no pedal deve ser conferido no M-EFCS. Nenhum AMX/AM2 local foi encontrado para anexar a este preset.

O arquivo passou na validação estrutural local. O timbre ainda não foi ouvido nem testado na pedaleira.
