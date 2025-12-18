# Guia de Troubleshooting - ngspice

Guia rápido de resolução de problemas comuns encontrados ao trabalhar com ngspice e arquivos SPICE.

## Índice

1. [Erros de Sintaxe](#1-erros-de-sintaxe)
2. [Erros de Convergência](#2-erros-de-convergência)
3. [Erros em Modo Batch](#3-erros-em-modo-batch)
4. [Erros de Medição](#4-erros-de-medição)
5. [Erros de Referência de Dispositivos](#5-erros-de-referência-de-dispositivos)
6. [Problemas com Modelos](#6-problemas-com-modelos)
7. [Problemas com Osciladores](#7-problemas-com-osciladores)
8. [Problemas de Exportação](#8-problemas-de-exportação)

---

## 1. Erros de Sintaxe

### Erro: "no such vector"

**Sintoma:**
```
Error: no such vector time
Error: no such vector frequency
```

**Causa:** Tentando acessar vetor de um plot diferente do atual.

**Solução:**
```spice
* Mudar o plot ativo antes de acessar vetores
.control
  run

  * Para dados transientes
  set curplot = tran1
  wrdata time_data.csv time v(out)

  * Para dados AC
  set curplot = ac1
  wrdata freq_data.csv frequency vdb(out)
.endc
```

---

### Erro: "RHS invalid" ou "Expression err"

**Sintoma:**
```
Error: RHS "vout_pp/vin_pp" invalid
Netlist line: meas tran ganho PARAM='vout_pp/vin_pp'
```

**Causa:** Sintaxe `PARAM='...'` não é suportada em versões modernas do ngspice.

**Solução:**
```spice
* ERRADO:
meas tran ganho PARAM='vout_pp/vin_pp'

* CORRETO:
meas tran vout_pp PP v(out)
meas tran vin_pp PP v(in)
let ganho = vout_pp / vin_pp
print ganho
```

---

### Erro: "incomplete or empty netlist"

**Sintoma:**
```
Error: incomplete or empty netlist
       or no ".plot", ".print", or ".fourier" lines in batch mode;
no simulations run!
```

**Causa:** Arquivo SPICE vazio, sem análises definidas, ou problema no modelo.

**Solução:**
1. Verificar se o arquivo tem `.end` no final
2. Verificar se há pelo menos uma análise (`.op`, `.tran`, `.ac`, ou `.dc`)
3. Verificar se todos os modelos estão corretamente definidos
4. Verificar se não há erros de sintaxe que impeçam o parsing

---

## 2. Erros de Convergência

### Erro: "Timestep too small"

**Sintoma:**
```
doAnalyses: TRAN: Timestep too small; time = 7.56e-11, timestep = 1.25e-20:
trouble with node "x_nand.n1"
```

**Causa:**
- Descontinuidades muito abruptas no circuito
- Modelos de componentes com parâmetros parasitários complexos
- Capacitâncias muito pequenas

**Solução 1:** Relaxar tolerâncias
```spice
.options reltol=1e-3 abstol=1e-9 vntol=1e-4
```

**Solução 2:** Simplificar modelos
```spice
* ANTES (muitos parâmetros):
.model NMOS_5V NMOS (
+ LEVEL=1 VTO=0.7 KP=200u LAMBDA=0.01
+ PHI=0.65 GAMMA=0.4 CBD=20f CBS=20f
+ CGSO=0.1p CGDO=0.1p CGBO=1p
+ CJ=0.5m CJSW=0.3n MJ=0.5 MJSW=0.3
+ PB=0.9 TOX=7.5n LD=0.1u )

* DEPOIS (simplificado):
.model NMOS_5V NMOS (
+ LEVEL=1
+ VTO=0.7
+ KP=200u
+ LAMBDA=0.01 )
```

**Solução 3:** Suavizar transições
```spice
* ANTES (transição abrupta - 1ns):
V1 in 0 PULSE(0 5 0 1n 1n 100n 200n)

* DEPOIS (transição mais suave - 10ns):
V1 in 0 PULSE(0 5 0 10n 10n 100n 200n)
```

---

### Erro: "doAnalyses: iteration limit"

**Sintoma:**
```
doAnalyses: iteration limit reached
```

**Causa:** Simulação não converge no ponto de operação DC.

**Solução:**
```spice
* Aumentar limites de iteração
.options itl1=500 itl2=200 itl4=100

* Ou pular o ponto de operação (osciladores)
.tran 1n 1m uic
```

---

### Erro: "singular matrix"

**Sintoma:**
```
Error: singular matrix: check node ...
```

**Causa:**
- Loop de fontes de tensão
- Nó flutuante sem caminho para terra
- Componentes em curto-circuito

**Solução:**
```spice
* Adicionar resistor de alta impedância para terra
R_pulldown node_flutuante 0 10MEG

* Verificar se não há fontes de tensão em série
* (remover uma ou adicionar resistor pequeno entre elas)
```

---

## 3. Erros em Modo Batch

### Erro: "Can't find device png"

**Sintoma:**
```
ERROR: (internal) Can't find device png.
ERROR: (internal) no hardcopy device
```

**Causa:** Comando `hardcopy` não funciona em modo batch (sem suporte PNG compilado).

**Solução:**
```spice
* ERRADO em batch mode:
.control
  run
  set hcopydevtype=png
  hardcopy saida.png v(out)
.endc

* CORRETO:
.control
  run
  * Exportar CSV e converter fora do ngspice
  wrdata saida.csv time v(out)
.endc
```

Depois, usar script Python:
```bash
python csv_to_png.py saida.csv
```

---

### Erro: "plot: not available during batch simulation"

**Sintoma:**
```
Warning: command 'plot' is not available during batch simulation, ignored!
```

**Causa:** Comando `plot` só funciona em modo interativo.

**Solução:**
```spice
* Comentar ou remover comandos plot em batch
.control
  run
  * plot v(out)  ; Comentar para batch mode

  * Usar print ou wrdata ao invés
  print v(out)
  wrdata dados.csv time v(out)
.endc
```

---

## 4. Erros de Medição

### Erro: "measure: out of interval" ou "TRIG/TARG out of interval"

**Sintoma:**
```
Error: measure tper trig(TRIG) : out of interval
meas tran tper trig v(c) val=0 rise=1 targ v(c) val=0 rise=2 from=50u failed!
```

**Causa:**
- Sinal não cruza o valor especificado no intervalo dado
- Sinal não tem transições (RISE/FALL) suficientes
- Valor de threshold incorreto

**Solução 1:** Ajustar valor de threshold
```spice
* Verificar o nível DC do sinal primeiro
* Se Vdc = 1.76V, usar esse valor:
meas tran TPER TRIG v(c) VAL=1.76 RISE=1 TARG v(c) VAL=1.76 RISE=2
```

**Solução 2:** Estender o intervalo
```spice
* ANTES:
meas tran delay TRIG v(in) VAL=2.5 RISE=1 FROM=0 TO=1u

* DEPOIS (intervalo maior):
meas tran delay TRIG v(in) VAL=2.5 RISE=1 FROM=0 TO=10u
```

**Solução 3:** Remover FROM/TO para buscar em todo o intervalo
```spice
* Buscar em toda a simulação
meas tran delay TRIG v(in) VAL=2.5 RISE=1
```

---

### Erro: "argument out of range for db"

**Sintoma:**
```
Error: argument out of range for db
  in term: vdb(vo1,vo2)
```

**Causa:** Tentando calcular dB de um valor muito pequeno (próximo de zero) ou negativo.

**Solução:**
- Este erro geralmente é não-crítico (apenas warning)
- O ngspice pula esses pontos e continua
- Se for crítico, verificar se o sinal diferencial está correto

---

## 5. Erros de Referência de Dispositivos

### Erro: "no such device or model name"

**Sintoma:**
```
Error: no such device or model name q1
Error: no such device or model name x1.j1
```

**Causa:** Referência incorreta de dispositivo (hierarquia errada).

**Solução:**

**Top-level (sem subcircuito):**
```spice
Q1 c b e BC548

.control
  op
  print @q1[ic]    ; ✓ Correto (minúscula OK)
.endc
```

**Dentro de subcircuito:**
```spice
.subckt amp in out
  Q1 out in 0 BC548
.ends

X1 entrada saida amp

.control
  op
  * ERRADO:
  print @q1[ic]        ; ✗ Q1 está dentro de X1
  print @x1.q1[ic]     ; ✗ Falta prefixo do tipo

  * CORRETO:
  print @q.x1.q1[ic]   ; ✓ Formato: @tipo.instancia.dispositivo[param]
.endc
```

**Tabela de prefixos hierárquicos:**
| Tipo | Prefixo | Exemplo |
|------|---------|---------|
| BJT | `q.` | `@q.x1.q1[ic]` |
| MOSFET | `m.` | `@m.x1.m1[id]` |
| JFET | `j.` | `@j.x1.j1[id]` |
| Diodo | `d.` | `@d.x1.d1[id]` |
| Resistor | `r.` | `@r.x1.r1[i]` |
| Capacitor | `c.` | `@c.x1.c1[i]` |
| Indutor | `l.` | `@l.x1.l1[i]` |

---

## 6. Problemas com Modelos

### Erro: "Unknown model type"

**Sintoma:**
```
Warning: Model issue on line 173 :
  .model swmod vswitch (ron=10 roff=10meg von=2.5 voff=0.5)
Unknown model type vswitch - ignored
```

**Causa:** Nome de tipo de modelo incorreto.

**Solução:**
```spice
* ERRADO:
.model SWMOD VSWITCH (RON=10 ROFF=10MEG VON=2.5 VOFF=0.5)

* CORRETO:
.model SWMOD SW (RON=10 ROFF=10MEG VON=2.5 VOFF=0.5)
```

**Tipos de modelo corretos:**
- Diodo: `D`
- BJT NPN: `NPN`
- BJT PNP: `PNP`
- MOSFET N: `NMOS`
- MOSFET P: `PMOS`
- JFET N: `NJF`
- JFET P: `PJF`
- Switch: `SW` (não VSWITCH!)

---

### Erro: "Unable to find definition of model"

**Sintoma:**
```
Error: Unable to find definition of model bc548
```

**Causa:**
- Modelo não definido
- Nome do modelo não bate (case-sensitive)
- Arquivo .lib não encontrado

**Solução:**
```spice
* ERRADO (nome não bate):
Q1 c b e BC548
.model bc548 NPN (...)    ; ✗ 'bc548' != 'BC548'

* CORRETO:
Q1 c b e BC548
.model BC548 NPN (...)    ; ✓ Nome exato

* Ou usando .include:
.include modelos/BC548.lib
```

---

## 7. Problemas com Osciladores

### Problema: Oscilador não inicia

**Sintoma:** Circuito oscilador permanece no ponto DC, sem oscilar.

**Causa:**
- Sem perturbação inicial
- Ponto DC estável demais
- Ganho de malha insuficiente

**Solução 1:** Adicionar condições iniciais
```spice
* Oscilador Colpitts
C1 coletor emissor 100p IC=0.1    ; Pequena tensão inicial
C2 emissor 0 100p
L1 coletor 0 10u

.tran 1n 1m uic    ; Usar 'uic' para pular .op
```

**Solução 2:** Adicionar capacitor com IC na base
```spice
* Para osciladores BJT
CB base 0 100n IC=1.75    ; Bias correto
```

---

### Problema: Frequência errada no oscilador

**Sintoma:** Oscilador funciona mas frequência está errada.

**Causa:**
- Valores L/C incorretos
- Indutor de choke em paralelo afetando frequência
- Capacitâncias parasitas não consideradas

**Solução:** Ajustar empiricamente valores de L e C
```spice
* Frequência teórica para Colpitts:
* f = 1 / (2π√(L×Ceq))
* onde Ceq = (C1×C2)/(C1+C2)

* Se calculou para 1MHz mas oscila em 3MHz:
* Aumentar C1 e C2 proporcionalmente

* ANTES (3 MHz):
C1 c e 100p
C2 e 0 120p

* DEPOIS (1 MHz):
C1 c e 390p
C2 e 0 470p
```

---

## 8. Problemas de Exportação

### Problema: wrdata cria arquivo vazio ou com erro

**Sintoma:** Arquivo CSV vazio ou com erro "no such vector".

**Causa:** Plot ativo errado ou análise não executada.

**Solução:**
```spice
.control
  * Executar análise
  run

  * IMPORTANTE: Mudar para o plot correto
  set curplot = tran1     ; Para dados transientes
  wrdata tran.csv time v(out)

  set curplot = ac1       ; Para dados AC
  wrdata ac.csv frequency vdb(out)
.endc
```

---

### Problema: Caminho de arquivo não encontrado

**Sintoma:**
```
circuits/dados/saida.csv: No such file or directory
```

**Causa:** Diretório não existe ou caminho relativo incorreto.

**Solução:**
```spice
* EVITAR caminhos relativos complexos
* ERRADO:
wrdata circuits/12_amp_diff/dados.csv v(out)

* CORRETO (diretório atual):
wrdata dados.csv v(out)

* Ou criar diretório antes:
* mkdir -p circuits/12_amp_diff/
```

---

## 9. Checklist de Debug

Quando um circuito não funciona, seguir esta ordem:

### ✅ Passo 1: Verificar sintaxe básica
- [ ] Arquivo tem `.end` no final?
- [ ] Primeira linha é o título?
- [ ] Todos os nós estão conectados?
- [ ] Há caminho para terra (nó 0)?

### ✅ Passo 2: Verificar modelos
- [ ] Todos os modelos estão definidos?
- [ ] Nomes dos modelos batem (case-sensitive)?
- [ ] Arquivos `.include` existem?

### ✅ Passo 3: Verificar análises
- [ ] Análises definidas (`.op`, `.tran`, `.ac`)?
- [ ] Sem duplicação de análises?
- [ ] Usando `run` ou chamando diretamente no `.control`?

### ✅ Passo 4: Verificar convergência
- [ ] Simulação converge?
- [ ] Precisa relaxar tolerâncias?
- [ ] Oscilador precisa de `uic` e `IC=`?

### ✅ Passo 5: Verificar modo batch
- [ ] Removeu comandos `plot`?
- [ ] Removeu comandos `hardcopy`?
- [ ] Usando `wrdata` corretamente?
- [ ] Plot switching correto?

---

## 10. Comandos Úteis de Debug

```spice
.control
  * Listar todos os nós
  display

  * Listar todos os dispositivos
  show all

  * Mostrar modelo de um componente
  showmod Q1

  * Ver parâmetros de um dispositivo após .op
  op
  show Q1

  * Listar opções ativas
  options

  * Habilitar output verboso
  set printverbose
.endc
```

---

## 11. Mensagens de Erro por Categoria

### 🔴 Erros Críticos (bloqueiam simulação)
- `incomplete or empty netlist`
- `singular matrix`
- `Unable to find definition of model`
- `doAnalyses: iteration limit reached`

### 🟡 Erros Não-Críticos (simulação continua)
- `measure: out of interval`
- `argument out of range for db`
- `Can't find device png` (apenas afeta export)

### ⚪ Avisos (warnings - geralmente OK)
- `plot: not available during batch simulation`
- `No compatibility mode selected`
- `vector ... is not available` (em medições que falharam)

---

## 12. Recursos Adicionais

- [Tutorial SPICE Completo](tutorial_spice.md)
- [ngspice Manual](http://ngspice.sourceforge.net/docs/ngspice-manual.pdf)
- [README do Projeto](../README.md)

---

*Guia criado baseado em experiência real consertando 29 circuitos do projeto learning_ngspice.*
