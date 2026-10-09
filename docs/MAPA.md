# Mapa do formato ATKM

Status: estrutura e parte dos parâmetros confirmadas pela comparação entre os binários e as tabelas `1a.txt` até `3a.txt` em `Preset modificadov1`. Algumas tabelas posteriores divergem do binário e não foram usadas como prova.

| Região | Offset absoluto | Tamanho | Evidência |
| --- | ---: | ---: | --- |
| Registros | 0 | 1.932 | 21 × 92 bytes nos arquivos `.atkm` locais examinados |
| Rodapé | 1.932 | 10 | `PATCHEND\x00\x00` |

Cada `.tkm` encontrado tem exatamente 92 bytes e corresponde a um registro. Os registros do `.atkm` seguem a ordem `1A, 1B, 1C, 2A, ... 7C`. Correspondências exatas comprovadas com arquivos locais: `2a.tkm` = registro 3, `3a.tkm` = 6, `3b.tkm` = 7, `3c.tkm` = 8, `4a.tkm` = 9, `4b.tkm` = 10, `4c.tkm` = 11 de `padrao.atkm`.

Dentro de cada registro, o offset local vai de 0 a 91. O primeiro byte varia entre registros; sua função é desconhecida.

## Campos mapeados no registro de 92 bytes

| Offset local | Tamanho | Campo | Evidência |
| ---: | ---: | --- | --- |
| 0 | 1 | volume geral bruto, função provável | valores 70–100; não aparece nas tabelas |
| 3–7 | 1 cada | ordem bruta da cadeia | nas 84 posições examinadas, cada grupo é uma permutação de 1..5; significado dos números não confirmado |
| 8–13 | 1 cada | FX, AMP, MOD, DLY, CAB, REV ligados | coincide com módulos ON/OFF nas tabelas |
| 14 | 1 | tipo FX: 0 Gate, 1 Boost, 2 Compress | tabelas 1A, 2B e 2C |
| 15 | 1 | índice do modelo AMP | tabela `AM2` embutida no `M-EFCS.exe`, numeração começando em 1; arquivo começa em 0 |
| 16–18 | 1 cada | índices de tipo MOD, DLY, REV | listas da interface no EXE; 1C confirma Chorus 0, Analog 0, Hall 1; 1B confirma Spring 3 |
| 19 | 1 | slot CAB menos 1 | 1A: 17→16, 1B: 12→11, 1C: 20→19 |
| 20, 22, 24, 26 | 2 cada, LE | quatro controles FX | Compress em 1A/1B: Gate, Sustain, Attack, Level |
| 32, 34, 36, 38, 40 | 2 cada, LE | AMP Gain, Level, Bass, Mid, Treble | comparação direta 1A–3A |
| 44–54 | 2 cada, LE | seis controles MOD | Chorus em 1C: primeiros três = Speed, Depth, Mix |
| 56–66 | 2 cada, LE | seis controles DLY | Analog em 1C: primeiros valores próximos de Time, Fb, Mix |
| 68–78 | 2 cada, LE | seis controles REV | primeiros cinco acompanham Decay, Mix, HPass, LPass, Depth/Combs |
| 80 | 2, LE | CAB Level | 100 nas tabelas e arquivos comparados |
| 82, 84 | 2 cada, LE | cortes baixo e alto CAB, escala bruta | acompanham Lcut/Hcut, conversão Hz/kHz ainda desconhecida |

Os campos ainda não explicados são preservados ao aplicar alterações por `preset_config.py`. Os nomes `paramN` no JSON significam apenas posição dentro do módulo. Valores físicos de frequência, ordem da cadeia e compatibilidade da tabela de modelos com o firmware conectado exigem validação no M-EFCS.

Os nomes dos 20 modelos AMP e dos 20 CABs de fábrica foram encontrados nas tabelas `AM2` e `CAB` embutidas no `M-EFCS.exe`. Para os modelos AMP, o índice armazenado no preset é o número exibido nessa tabela menos 1. Os slots CAB 16–20 podem ter IRs personalizados carregados no pedal; `cab_nome_de_fabrica` em `show` indica apenas o nome original daquele slot, não o IR atual.

As quatro amostras encontradas (`backup.atkm`, `padrao.atkm`, `1 preset.atkm` e `presets modificados 1A_4C.atkm`) têm 1.942 bytes e passam na validação estrutural. `backup.atkm` e `padrao.atkm` diferem em 352 bytes distribuídos por 17 registros. `padrao.atkm` e `1 preset.atkm` diferem em 118 bytes distribuídos por 6 registros. Portanto, os nomes dos arquivos não bastam para identificar controles individuais.

## Experimentos

| Controle no M-EFCS | Valor original | Valor alterado | Arquivos comparados | Offsets afetados | Interpretação |
| --- | --- | --- | --- | --- | --- |

