# Opção AMP + CAB da comunidade M-VAVE para 7C

Os arquivos desta pasta são candidatos separados. Nada aqui foi enviado à Tank Mini. O `falling-in-reverse-7C.tkm` anterior continua igual.

## Arquivos e origem

| Arquivo local | Conteúdo | Artigo da comunidade | SHA-256 |
| --- | --- | --- | --- |
| `EVH-5150-comunidade.am2Data` | captura AMP `9EVH 5150.am2Data`, cabeçalho `AM2`, 14.140 bytes | `9238`, “evh 5150” | `D56CFC609270F92425006E6A576A62ADF40211FF9ECB589D50A291722CCB4464` |
| `Mesa-Rectifier-OS-4x12-V30-comunidade.wav` | IR mono, 48 kHz, PCM 24 bits, 10.000 amostras (208 ms) | `7944`, “Mesa Rectifier Oversized Cab - V30s” | `F96A159AE2DE16953E0122F6D1D62DF4543EEBF4FCFC42EEEC513CDC10CE70D8` |

Origem: `https://community.m-vave.com/#/home`. Os dados dos artigos são públicos em `https://community.m-vave.com/bbs/api/getdetail?id=9238` e `https://community.m-vave.com/bbs/api/getdetail?id=7944`.

## Preset alternativo

`falling-in-reverse-7C-amp-comunidade.tkm` mantém todos os ajustes do 7C anterior, mas aponta para AMP **slot 10** (índice interno 9) e CAB **slot 10**. O arquivo `.atkm` correspondente modifica somente o registro 7C.

Na exportação original usada para gerar o preset, nenhum dos 21 presets usava AMP 10 ou CAB 10. O 7C anterior passou a usar CAB 10. Confirme novamente depois de qualquer alteração feita no pedal.

**Antes de importar as capturas ao pedal**, exporte/guarde o conteúdo atual dos slots AMP 10 e CAB 10 no M-EFCS. O backup `.atkm` guarda as referências dos presets, não os dados AMP/IR instalados nesses slots. Importar as capturas pode substituir o conteúdo dos slots. Depois, carregue o AM2 no AMP 10, o WAV no CAB 10 e importe o `.tkm` alternativo em 7C. A compatibilidade e o timbre final ainda precisam ser conferidos no M-EFCS e ouvindo o pedal.
