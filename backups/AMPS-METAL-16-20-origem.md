# Capturas metal para AMP 16 a 20

Cinco arquivos `.am2Data` foram baixados da comunidade M-VAVE em 09/10/2026. Todos têm cabeçalho `AM2\0` e tamanho observado em capturas AM2 locais (6.204 ou 14.140 bytes). Isso valida o contêiner, não o som nem a importação no pedal.

| Slot | Arquivo em `M-EFCS/AMPS METAL 16-20` | Artigo | SHA-256 |
| ---: | --- | --- | --- |
| 16 | `16 - Bogner Uberschall.am2Data` | [814](https://community.m-vave.com/bbs/api/getdetail?id=814) | `24E283B08B5CF1EF8142FAE6C08770FBC55C9D2EADC2119F61F865F6CD01B3DC` |
| 17 | `17 - Diezel VH4 HiGain.am2Data` | [706](https://community.m-vave.com/bbs/api/getdetail?id=706) | `C5E48217C202CDFAD9E5C8F841826AD90CED536BCAF74742CA73E893C595C5BB` |
| 18 | `18 - Marshall JVM410.am2Data` | [33](https://community.m-vave.com/bbs/api/getdetail?id=33) | `12CF98738A3BE6AC41C6274490D6F49122C496321556389E3092DE46908CFB1D` |
| 19 | `19 - EVH 5150 TS9 HiGain.am2Data` | [3278](https://community.m-vave.com/bbs/api/getdetail?id=3278) | `B7440B9541C4C1559587BCCFC0D4D8EE296B1114AFDC2801F812F3D728695EBD` |
| 20 | `20 - Fortin Cali OD2.am2Data` | [734](https://community.m-vave.com/bbs/api/getdetail?id=734) | `FCA5B7606206D90B502BB1D7F67011EA5958D6B34A9AA022D27221A97B556AE8` |

Um candidato Fortin do artigo 423 veio sem cabeçalho AM2 e foi retirado da pasta de importação. A cópia recebida está em `backups/candidatos-fortin/423-FortinCali3-estrutura-diferente.am2Data` para análise, sem indicação de importação.

Esses arquivos ainda não foram enviados ao pedal. O backup `.atkm` conserva apenas os números dos slots usados pelos presets. Ele não guarda os modelos AMP 16 a 20. Para reverter a troca de modelos, exporte cada conteúdo original pelo M-EFCS antes de gravar as capturas novas. Na exportação dos presets de 09/10/2026, o slot 16 era usado por 6A e o 18 por 6C; os arquivos ativos atuais de 7A e 7B usam AMP 8.
