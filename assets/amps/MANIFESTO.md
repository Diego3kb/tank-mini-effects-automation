# AMP 16–20: estado e hashes

Estes cinco arquivos são capturas `.am2Data` preparadas para possível uso nos
slots 16–20. Eles foram apenas organizados na pasta do projeto e carregados na
biblioteca do M-EFCS durante o teste. Não foram enviados ao pedal.

| Slot | Arquivo | SHA-256 |
|---:|---|---|
| 16 | `not-installed/metal-16-20/16 - Bogner Uberschall.am2Data` | `24E283B08B5CF1EF8142FAE6C08770FBC55C9D2EADC2119F61F865F6CD01B3DC` |
| 17 | `not-installed/metal-16-20/17 - Diezel VH4 HiGain.am2Data` | `C5E48217C202CDFAD9E5C8F841826AD90CED536BCAF74742CA73E893C595C5BB` |
| 18 | `not-installed/metal-16-20/18 - Marshall JVM410.am2Data` | `12CF98738A3BE6AC41C6274490D6F49122C496321556389E3092DE46908CFB1D` |
| 19 | `not-installed/metal-16-20/19 - EVH 5150 TS9 HiGain.am2Data` | `B7440B9541C4C1559587BCCFC0D4D8EE296B1114AFDC2801F812F3D728695EBD` |
| 20 | `not-installed/metal-16-20/20 - Fortin Cali OD2.am2Data` | `FCA5B7606206D90B502BB1D7F67011EA5958D6B34A9AA022D27221A97B556AE8` |

Para conferir novamente:

```powershell
Get-FileHash tank-mini-effects-automation\assets\amps\not-installed\metal-16-20\*.am2Data -Algorithm SHA256
```

O banco exportado antes e depois do Scar Tissue só diferiu no registro 1A.
Os AMP 16–20 não aparecem como dados dentro do `.atkm`; o banco guarda apenas
o índice do modelo selecionado.
