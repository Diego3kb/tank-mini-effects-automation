# Afterlife — Avenged Sevenfold — banco 7B

Dois presets individuais para o slot 7B. O 7C anterior foi preservado. `7B-antes.tkm` é a cópia do 7B da exportação do pedal de 09/10/2026. Os `.atkm` foram usados para gerar e validar os `.tkm`; para mudar só 7B, importe um `.tkm`, nunca o conjunto inteiro.

## Atualização: IR carregado no CAB 11

O usuário informou que colocou o IR no **CAB 11**. Foram geradas duas versões corrigidas que diferem das anteriores por apenas um byte no slot 7B (referência do CAB):

- `afterlife-7B-CAB11-AMP8.tkm`: use se o Bogner AM2 foi carregado no **AMP 8**.
- `afterlife-7B-CAB11-AMP9.tkm`: use o amplificador já presente no **AMP 9**. É a opção para testar sem carregar outro AM2.

Selecione 7B, importe **um** desses arquivos e salve no dispositivo. O arquivo `.atkm` exportado antes da alteração mostra que **2A também usa CAB 11** com o bloco CAB ligado; substituir o IR nesse slot muda o som de 2A. A exportação de presets não revela o conteúdo de áudio atual de CAB 11, então a carga do WAV precisa ser confirmada no M-EFCS ou ouvindo o pedal.

## Opção para testar agora

`afterlife-7B-sem-cargas-extras.tkm`: usa AMP **9** e CAB **10**, os mesmos slots escolhidos no 7C anterior. Ajustei o 7B para solo: boost leve, AMP gain 72, médios 66, delay analógico discreto e reverb Room baixo. O resultado depende do AMP e do IR que estão instalados nesses slots no pedal. Se 7C já está bom, esta opção evita importar um novo AMP e um novo IR.

No M-EFCS: selecione **7B**, use **Import current preset**, escolha esse `.tkm` e depois **Save preset to device**. Exporte novamente todos os presets para verificar a gravação.

## Opção com Bogner e IR A7X

`afterlife-7B.tkm`: os mesmos ajustes de 7B, mas aponta para AMP **8** e CAB **8**.

- `Bogner-Uberschall-comunidade.am2Data`: captura AM2 obtida do artigo `814`, “BOGNER UBERSCHALL MKI (AMP+CAB)”, em `https://community.m-vave.com/bbs/api/getdetail?id=814`. SHA-256 `24E283B08B5CF1EF8142FAE6C08770FBC55C9D2EADC2119F61F865F6CD01B3DC`.
- `A7X-Self-Titled-IR-mono-48k.wav`: convertido para mono, 48 kHz, PCM 24 bits a partir de `G:\Meu Drive\Tank mini\IR A7X\Self-Titled.wav` (SHA-256 original `B533745CB84993E596B6C8DF58C6788F70AEC0DF2A80C4BC30E76E0C5E755F35`). SHA-256 convertido `D21F8FB905031481989A90FB85F5590507CC3D06A972F651F122BAE12DB04ECC`.

Na exportação usada como base, nenhum preset apontava para AMP 8 ou CAB 8. Antes de importar o AM2 ou o WAV, exporte/guarde os conteúdos atuais desses slots no M-EFCS; o backup `.atkm` contém só referências, não as capturas. Depois importe o AM2 no AMP 8, o WAV no CAB 8, selecione 7B, importe `afterlife-7B.tkm` e salve no dispositivo. Exporte todos os presets para conferir.

## Parâmetros

Ambas as opções: volume bruto 78; FX Boost ligado, gate 45, boost gain 16; AMP gain 72, level 69, bass 46, mid 66, treble 61; CAB ligado, level 100, cortes brutos 25/40; modulação desligada; delay Analog ligado com parâmetros brutos 45/25/17; reverb Room ligado, decay 25, mix 10. Os valores de delay e de cortes da caixa ainda precisam ser confirmados em unidades físicas no M-EFCS.

Os arquivos passaram na validação estrutural local. O timbre não foi ouvido nem testado na pedaleira nesta sessão.
