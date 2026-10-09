# Guia completo: editar a Tank Mini com um agente

Este documento registra o que foi descoberto e como outro agente pode continuar
o trabalho sem depender de tentativa e erro.

## O que existe neste projeto

Este projeto contém apenas as ferramentas de automação e os arquivos de
engenharia reversa específicos da Tank Mini.

As ferramentas específicas da pedaleira estão na pasta principal:

- `tools/atkm.py`: valida, extrai, compara e substitui presets `.tkm` e `.atkm`.
- `tools/preset_config.py`: edita campos conhecidos de um banco `.atkm` usando JSON.
- `tools/backup.py`: cria e verifica cópias com SHA-256.
- `tools/device_probe.py`: lista as portas MIDI USB.
- `tools/m_efcs_automation.py`: controla o M-EFCS para importar e exportar arquivos.
- `docs/MAPA.md`: mapa dos bytes conhecidos.
- `docs/AUTOMACAO.md`: comandos rápidos de automação.

## Formatos

Um preset individual `.tkm` tem 92 bytes. Um banco `.atkm` tem 21 registros de
92 bytes, na ordem `1A, 1B, 1C, 2A ... 7C`, seguido de `PATCHEND` e dois bytes
zero. Não se deve editar o executável para alterar esses valores.

Campos confirmados dentro de cada registro:

| Offset | Campo |
|---:|---|
| 0 | volume geral |
| 8 a 13 | FX, AMP, MOD, delay, CAB e reverb ligados |
| 14 | tipo de FX |
| 15 | modelo AMP, índice começando em zero |
| 16 a 18 | tipos de MOD, delay e reverb |
| 19 | slot CAB menos 1 |
| 32 a 40 | ganho, nível, graves, médios e agudos do AMP |
| 44 a 78 | parâmetros de MOD, delay e reverb |
| 80 | nível do CAB |
| 82 e 84 | cortes baixo e alto do CAB |

## Como editar um banco

Sempre comece exportando o estado atual da pedaleira:

```powershell
py tools\m_efcs_automation.py backup
```

O backup fica em `backups/automation-AAAAmmdd-HHMMSS/export-all.atkm`.

Consulte um slot:

```powershell
py tools\preset_config.py show backups\automation-AAAAmmdd-HHMMSS\export-all.atkm --slot 1A
```

Crie um plano JSON com o hash do banco original e os campos que deseja mudar.
Um exemplo pronto está em `scar_tissue_1A_plano.json`. Gere um novo banco:

```powershell
py tools\preset_config.py apply banco-original.atkm plans\plano.json banco-editado.atkm
```

O programa recusa hash errado, valores fora da faixa e destino já existente.
Extraia o slot que será testado:

```powershell
py tools\atkm.py extract banco-editado.atkm preset-1A.tkm --slot 1A
```

## Como importar e gravar um preset

Com a Tank Mini conectada e o M-EFCS aberto:

```powershell
py tools\m_efcs_automation.py import-preset 1A preset-1A.tkm
```

Esse comando cria um backup antes da importação. Para gravar no dispositivo,
no M-EFCS use `Save preset to`, confirme o slot exibido e aceite a confirmação.
Depois exporte o slot e compare os arquivos:

```powershell
py tools\m_efcs_automation.py export-preset 1A preset-1A-depois.tkm
py tools\atkm.py diff preset-1A.tkm preset-1A-depois.tkm
```

No teste confirmado, o preset “Scar Tissue” foi gravado no 1A e o arquivo
exportado de volta ficou byte a byte igual ao enviado.

Para um banco completo:

```powershell
py tools\m_efcs_automation.py import-all banco-editado.atkm
py tools\m_efcs_automation.py export-all banco-depois.atkm
```

## De onde vêm os CABs

CAB é a captura de caixa em WAV, também chamada de IR. O arquivo usado nos
testes foi:

`assets/cabs/not-installed/user-and-community/A7X-Self-Titled-IR-mono-48k-automation.wav`

Ele veio do arquivo fornecido pelo usuário e preservado em
`archive/old-presets/afterlife-7B/A7X-Self-Titled-IR-mono-48k.wav`.

Outro CAB comunitário está em:

`archive/community-candidates/falling-in-reverse/Mesa-Rectifier-OS-4x12-V30-comunidade.wav`

O M-EFCS mostra os CABs carregados na aba **Cab**. O arquivo precisa ser aberto
na biblioteca, ouvido com **Audition** e só depois enviado ao slot escolhido
com **Save to device**. O nome exibido no preset não prova sozinho que o IR foi
gravado; confirme exportando o preset e conferindo o slot CAB.

## De onde vêm os AMPs

AMPs capturados usam arquivos `.am2Data`. As fontes locais são:

- `assets/amps/not-installed/metal-16-20/`: cinco capturas preparadas para os slots 16 a 20, ainda não instaladas.
- `assets/amps/not-installed/imported/`: arquivo AMX/AM2 recebido anteriormente, ainda não instalado.
- `archive/community-candidates/falling-in-reverse/EVH-5150-comunidade.am2Data`.
- `archive/old-presets/afterlife-7B/Bogner-Uberschall-comunidade.am2Data`.
- `archive/community-candidates/fortin/`: candidatos Fortin preservados para análise.

Para carregar um AMP na biblioteca:

```powershell
py tools\m_efcs_automation.py open-amp "assets\amps\metal-16-20\16 - Bogner Uberschall.am2Data"
```

Depois selecione o item na aba **Amx**, confira o nome e use **Save to device**.
O arquivo do AMP não muda o modelo armazenado no `.tkm` automaticamente: o
`.tkm` guarda o índice do modelo, enquanto o `.am2Data` altera a captura que o
pedal associa àquele espaço.

## Automação e limites atuais

O M-EFCS continua original. A automação opera a interface e os arquivos; ela
já foi testada para exportar o banco, importar presets e carregar CAB/AMP na
biblioteca. A gravação direta com o software fechado ainda não foi concluída:
para isso será necessário descobrir e implementar o protocolo USB-MIDI/SysEx
proprietário da Tank Mini.

Antes de qualquer gravação física, mantenha uma exportação ATKM atualizada em
`backups/` e valide o arquivo gerado com:

```powershell
py tools\atkm.py info banco.atkm
py tools\preset_config.py validate banco.atkm
```

