# Tutorial Completo da Linguagem SPICE

Este tutorial cobre a linguagem SPICE (Simulation Program with Integrated Circuit Emphasis) usada no ngspice para simulacao de circuitos eletronicos.

## Indice

1. [Estrutura Basica de um Arquivo SPICE](#1-estrutura-basica-de-um-arquivo-spice)
2. [Componentes Passivos](#2-componentes-passivos)
3. [Fontes de Alimentacao](#3-fontes-de-alimentacao)
4. [Semicondutores](#4-semicondutores)
5. [Tipos de Analise](#5-tipos-de-analise)
6. [Bloco .control](#6-bloco-control)
7. [Subcircuitos](#7-subcircuitos)
8. [Parametros e Expressoes](#8-parametros-e-expressoes)
9. [Modelos de Componentes](#9-modelos-de-componentes)
10. [Comandos de Plotagem e Exportacao](#10-comandos-de-plotagem-e-exportacao)
11. [Dicas e Boas Praticas](#11-dicas-e-boas-praticas)

---

## 1. Estrutura Basica de um Arquivo SPICE

### Formato geral

```spice
* Titulo do circuito (primeira linha SEMPRE e o titulo)

* Comentarios comecam com asterisco
; Comentarios tambem podem usar ponto-e-virgula

* Definicao dos componentes
R1 no1 no2 1k
C1 no2 0 100n

* Comandos de analise
.tran 1u 10m

* Bloco de controle (opcional, especifico do ngspice)
.control
  run
  plot v(no2)
.endc

* Fim do arquivo (obrigatorio)
.end
```

### Regras importantes

1. **Primeira linha**: Sempre e tratada como titulo (mesmo sem `*`)
2. **No 0 (zero)**: E sempre o terra/ground/referencia
3. **Case insensitive**: `R1`, `r1` e `R1` sao identicos
4. **Continuacao de linha**: Use `+` no inicio da proxima linha
5. **`.end`**: Obrigatorio no final do arquivo

---

## 2. Componentes Passivos

### Resistores (R)

```spice
* Sintaxe: Rnome no+ no- valor

R1 in out 1k          ; 1 kilo-ohm
R2 a b 4.7k           ; 4.7 kilo-ohms
R3 vcc base 47000     ; 47k (valor numerico)
R4 x y 1meg           ; 1 mega-ohm
R5 p q 0.1            ; 0.1 ohm (100 mili-ohms)
```

### Capacitores (C)

```spice
* Sintaxe: Cnome no+ no- valor [IC=tensao_inicial]

C1 in out 100n        ; 100 nanofarads
C2 a b 10u            ; 10 microfarads
C3 vcc 0 1000p        ; 1000 picofarads = 1nF
C4 x y 100n IC=5      ; com condicao inicial de 5V
```

### Indutores (L)

```spice
* Sintaxe: Lnome no+ no- valor [IC=corrente_inicial]

L1 in out 10m         ; 10 mili-henrys
L2 a b 470u           ; 470 micro-henrys
L3 x y 1u IC=0.1      ; com corrente inicial de 100mA
```

### Acoplamento Magnetico (K)

```spice
* Para transformadores e indutores acoplados
* Sintaxe: Knome Lnome1 Lnome2 coeficiente

L1 a b 10m
L2 c d 10m
K1 L1 L2 0.99         ; acoplamento de 99%
```

### Sufixos de Escala

| Sufixo | Multiplicador | Exemplo |
|--------|---------------|---------|
| T | 10^12 (tera) | 1T = 1e12 |
| G | 10^9 (giga) | 1G = 1e9 |
| MEG | 10^6 (mega) | 1MEG = 1e6 |
| K | 10^3 (kilo) | 1K = 1e3 |
| M | 10^-3 (mili) | 1M = 1e-3 |
| U | 10^-6 (micro) | 1U = 1e-6 |
| N | 10^-9 (nano) | 1N = 1e-9 |
| P | 10^-12 (pico) | 1P = 1e-12 |
| F | 10^-15 (femto) | 1F = 1e-15 |

**Atencao**: `M` significa mili (10^-3), nao mega! Use `MEG` para mega.

---

## 3. Fontes de Alimentacao

### Fontes de Tensao DC (V)

```spice
* Sintaxe: Vnome no+ no- [DC] valor

V1 vcc 0 DC 12        ; 12V DC
V2 in 0 5             ; 5V DC (DC e opcional)
V3 a b DC -3.3        ; -3.3V (polaridade invertida)
```

### Fontes de Corrente DC (I)

```spice
* Sintaxe: Inome no+ no- [DC] valor
* A corrente flui do no+ para o no-

I1 0 vcc DC 10m       ; fonte de 10mA
I2 a b 1u             ; fonte de 1uA
```

### Fonte AC (para analise de frequencia)

```spice
* Sintaxe: Vnome no+ no- DC valor_dc AC magnitude [fase]

V1 in 0 DC 0 AC 1     ; 1V AC, 0V DC, fase 0
V2 in 0 DC 2.5 AC 1 0 ; 1V AC, 2.5V DC offset, fase 0
V3 in 0 AC 1 90       ; 1V AC com fase de 90 graus
```

### Fonte Senoidal (SIN)

```spice
* Sintaxe: Vnome no+ no- SIN(Voffset Vampl Freq [Td] [Theta] [Fase])
* Td = atraso inicial
* Theta = fator de amortecimento (1/s)
* Fase = fase inicial em graus

V1 in 0 SIN(0 1 1k)              ; seno 1Vpp, 1kHz, sem offset
V2 in 0 SIN(2.5 1 1k)            ; seno 1Vpp, 1kHz, offset 2.5V
V3 in 0 SIN(0 5 60 0 0 90)       ; seno 5Vpp, 60Hz, fase 90 graus
V4 in 0 SIN(0 1 1k 1m 100)       ; com atraso de 1ms e amortecimento
```

### Fonte de Pulso (PULSE)

```spice
* Sintaxe: Vnome no+ no- PULSE(V1 V2 Td Tr Tf Pw Per [Np])
* V1 = nivel baixo
* V2 = nivel alto
* Td = atraso inicial
* Tr = tempo de subida
* Tf = tempo de descida
* Pw = largura do pulso
* Per = periodo
* Np = numero de pulsos (opcional)

* Onda quadrada 5V, 1kHz, duty cycle 50%
V1 in 0 PULSE(0 5 0 1n 1n 0.5m 1m)

* Pulso unico de 10us
V2 trig 0 PULSE(0 3.3 1u 10n 10n 10u 1)

* Clock 10MHz
V3 clk 0 PULSE(0 5 0 1n 1n 50n 100n)
```

### Fonte PWL (Piecewise Linear)

```spice
* Sintaxe: Vnome no+ no- PWL(t1 v1 t2 v2 t3 v3 ...)
* Define pontos (tempo, tensao) e interpola linearmente

* Rampa de 0V a 5V em 1ms
V1 in 0 PWL(0 0 1m 5)

* Forma de onda customizada
V2 in 0 PWL(0 0 1m 5 2m 5 3m 0 4m 0)

* Degrau em t=1ms
V3 in 0 PWL(0 0 1m 0 1.001m 5 10m 5)
```

### Fonte Exponencial (EXP)

```spice
* Sintaxe: Vnome no+ no- EXP(V1 V2 Td1 Tau1 Td2 Tau2)
* V1 = valor inicial
* V2 = valor de pico
* Td1 = atraso para subida
* Tau1 = constante de tempo de subida
* Td2 = atraso para descida
* Tau2 = constante de tempo de descida

V1 in 0 EXP(0 5 1u 1u 5u 2u)
```

---

## 4. Semicondutores

### Diodos (D)

```spice
* Sintaxe: Dnome anodo catodo modelo

D1 in out 1N4148      ; diodo de sinal
D2 a b DMOD           ; usando modelo customizado

* Modelo basico de diodo
.model 1N4148 D(IS=2.52e-9 RS=0.568 N=1.752 BV=100 IBV=100u)

* Modelo simplificado
.model DMOD D(IS=1e-14 N=1)
```

### Diodo Zener

```spice
D1 catodo anodo ZENER5V1

.model ZENER5V1 D(IS=1e-14 BV=5.1 IBV=5m RS=10)
```

### Transistores Bipolares (Q) - BJT

```spice
* Sintaxe: Qnome coletor base emissor [substrato] modelo

* NPN
Q1 c b e BC548
Q2 vcc base gnd 0 2N2222   ; com substrato

* PNP
Q3 e b c BC558

* Modelos
.model BC548 NPN(IS=1e-14 BF=200 VAF=100 CJE=8p CJC=3p TF=0.35n)
.model BC558 PNP(IS=1e-14 BF=200 VAF=100)
.model 2N2222 NPN(IS=14.34f BF=255 VAF=74.03 NE=1.307 IKF=0.2847)
```

### Transistores MOSFET (M)

```spice
* Sintaxe: Mnome drain gate source [bulk] modelo [L=valor] [W=valor]

* NMOS
M1 d g s 0 NMOS W=10u L=1u

* PMOS (bulk conectado ao source geralmente)
M2 d g s vdd PMOS W=20u L=1u

* Modelos nivel 1 (simplificado)
.model NMOS NMOS(VTO=0.7 KP=110u GAMMA=0.4 LAMBDA=0.04 PHI=0.65)
.model PMOS PMOS(VTO=-0.7 KP=50u GAMMA=0.4 LAMBDA=0.05 PHI=0.65)
```

### Transistores JFET (J)

```spice
* Sintaxe: Jnome drain gate source modelo

J1 d g s 2N5457

.model 2N5457 NJF(VTO=-1.5 BETA=1m LAMBDA=2m IS=1f)
```

---

## 5. Tipos de Analise

### Analise DC - Ponto de Operacao (.op)

```spice
* Calcula o ponto de operacao DC do circuito
.op
```

### Analise DC - Varredura (.dc)

```spice
* Sintaxe: .dc fonte inicio fim passo

* Varrer V1 de 0V a 10V em passos de 0.1V
.dc V1 0 10 0.1

* Varredura dupla (curvas de um BJT)
.dc Vce 0 10 0.1 Ib 10u 50u 10u
```

### Analise AC - Frequencia (.ac)

```spice
* Sintaxe: .ac tipo pontos f_inicio f_fim
* tipo: DEC (decada), OCT (oitava), LIN (linear)

* 100 pontos por decada, de 1Hz a 1MHz
.ac dec 100 1 1meg

* 1000 pontos lineares de 1kHz a 10kHz
.ac lin 1000 1k 10k

* 10 pontos por oitava de 20Hz a 20kHz
.ac oct 10 20 20k
```

### Analise Transiente (.tran)

```spice
* Sintaxe: .tran passo tempo_final [tempo_inicio] [tempo_max] [uic]
* uic = use initial conditions (nao calcula .op antes)

* Simular 10ms com passo de 1us
.tran 1u 10m

* Comecar a salvar a partir de 1ms
.tran 1u 10m 1m

* Usar condicoes iniciais (importante para osciladores)
.tran 0.1u 1m uic
```

### Analise de Sensibilidade (.sens)

```spice
* Sintaxe: .sens variavel_saida

.sens v(out)          ; sensibilidade da tensao no no 'out'
.sens i(R1)           ; sensibilidade da corrente em R1
```

### Analise de Ruido (.noise)

```spice
* Sintaxe: .noise v(saida) fonte_entrada tipo pontos f_inicio f_fim

.noise v(out) V1 dec 10 1k 1meg
```

### Analise de Temperatura

```spice
* A temperatura padrao e 27C (300K)
.temp 25              ; define temperatura para 25C

* Varredura de temperatura
.step temp 0 100 25   ; de 0C a 100C em passos de 25C
```

---

## 6. Bloco .control

O bloco `.control` e especifico do ngspice e permite controle programatico da simulacao.

### Estrutura basica

```spice
.control
  * Comandos aqui
  run
  plot v(out)
.endc
```

### Comandos principais

```spice
.control
  * Executar simulacao
  run

  * Plotar graficos
  plot v(in) v(out)                    ; tensoes
  plot i(V1)                           ; corrente na fonte V1
  plot v(out) vs v(in)                 ; grafico XY
  plot db(v(out))                      ; magnitude em dB
  plot phase(v(out))                   ; fase em graus
  plot v(out) xlimit 0 1m ylimit -1 6  ; com limites

  * Imprimir valores
  print v(out) i(R1)
  print all                            ; todos os valores

  * Mostrar mensagens
  echo "Simulacao concluida"

  * Medidas automaticas
  meas tran vmax MAX v(out)            ; valor maximo
  meas tran vmin MIN v(out)            ; valor minimo
  meas tran vpp PP v(out)              ; pico a pico
  meas tran vavg AVG v(out)            ; media
  meas tran vrms RMS v(out)            ; valor RMS

  * Medir tempo de subida
  meas tran trise TRIG v(out) VAL=0.1 RISE=1 TARG v(out) VAL=0.9 RISE=1

  * Medir frequencia
  meas tran periodo TRIG v(out) VAL=0 RISE=1 TARG v(out) VAL=0 RISE=2
  meas tran freq PARAM='1/periodo'
.endc
```

### Variaveis e expressoes

```spice
.control
  * Definir variaveis
  let vref = 2.5
  let ganho = v(out)/v(in)

  * Operacoes matematicas
  let potencia = v(out) * i(R1)

  * Imprimir resultado
  print ganho potencia
.endc
```

### Controle de fluxo

```spice
.control
  * Loop foreach
  foreach val 1k 2k 5k 10k
    alter R1 = $val
    run
    plot v(out)
  end

  * Loop while
  let x = 0
  while x < 10
    let x = x + 1
    echo "Iteracao $&x"
  end

  * Condicional if
  if v(out) > 2.5
    echo "Saida acima de 2.5V"
  else
    echo "Saida abaixo de 2.5V"
  end
.endc
```

### Alterar parametros em tempo de execucao

```spice
.control
  * Alterar valor de componente
  alter R1 = 2k
  alter C1 = 200n

  * Alterar fonte
  alter V1 DC 10
  alter V1 PULSE(0 5 0 1n 1n 1u 2u)

  * Alterar parametro
  alterparam R = 5k
  reset                    ; necessario apos alterparam

  run
.endc
```

---

## 7. Subcircuitos

### Definicao de subcircuito

```spice
* Sintaxe: .subckt nome no1 no2 ... [params: p1=val1 ...]
* ...componentes...
* .ends [nome]

* Subcircuito de um amplificador inversor
.subckt amp_inv in out vcc vee
R1 in n1 10k
R2 n1 out 100k
X1 0 n1 vcc vee out LM741
.ends amp_inv
```

### Usando subcircuitos

```spice
* Sintaxe: Xnome no1 no2 ... nome_subckt [params]

X1 entrada saida vcc gnd amp_inv
X2 saida saida2 vcc gnd amp_inv     ; cascateando
```

### Subcircuito com parametros

```spice
.subckt filtro_rc in out gnd params: R=1k C=100n
R1 in out {R}
C1 out gnd {C}
.ends

* Usando com valores padrao
X1 in out1 0 filtro_rc

* Usando com valores customizados
X2 in out2 0 filtro_rc params: R=2.2k C=47n
```

### Subcircuitos hierarquicos

```spice
* Subcircuito basico
.subckt resistor_par a b params: R1=1k R2=1k
Ra a b {R1}
Rb a b {R2}
.ends

* Subcircuito que usa outro subcircuito
.subckt divisor in out gnd
X1 in mid gnd resistor_par params: R1=10k R2=10k
X2 mid out gnd resistor_par params: R1=5k R2=5k
.ends
```

---

## 8. Parametros e Expressoes

### Definindo parametros

```spice
* Sintaxe: .param nome=valor

.param Vcc=12
.param R_base=10k
.param freq=1k
.param pi=3.14159

* Parametros podem referenciar outros parametros
.param periodo=1/freq
.param omega=2*pi*freq
```

### Usando parametros

```spice
.param R=1k C=100n

R1 in out {R}
C1 out 0 {C}

* Em expressoes
R2 a b {R*2}              ; 2k
C2 c d {C/10}             ; 10n
```

### Expressoes em valores de componentes

```spice
* Operadores: + - * / ** (potencia)
* Funcoes: sin, cos, tan, exp, ln, log, sqrt, abs, min, max

R1 a b {10k * 1.5}
C1 c d {1/(2*3.14159*1000*10k)}    ; para f = 1kHz

* Condicional
R2 e f {(Vcc > 10) ? 10k : 5k}
```

### Funcoes disponiveis

| Funcao | Descricao |
|--------|-----------|
| `abs(x)` | Valor absoluto |
| `sqrt(x)` | Raiz quadrada |
| `exp(x)` | Exponencial (e^x) |
| `ln(x)` | Logaritmo natural |
| `log(x)` | Logaritmo base 10 |
| `sin(x)` | Seno (x em radianos) |
| `cos(x)` | Cosseno |
| `tan(x)` | Tangente |
| `asin(x)` | Arco seno |
| `acos(x)` | Arco cosseno |
| `atan(x)` | Arco tangente |
| `min(x,y)` | Minimo |
| `max(x,y)` | Maximo |
| `pow(x,y)` | x elevado a y |

---

## 9. Modelos de Componentes

### Estrutura do .model

```spice
* Sintaxe: .model nome tipo (parametros)

.model DMOD D(IS=1e-14 RS=10 N=1.8 BV=100)
```

### Modelo de Diodo (D)

```spice
.model nome D(parametros)

* Parametros principais:
* IS  = corrente de saturacao (A)
* RS  = resistencia serie (ohm)
* N   = coeficiente de emissao
* BV  = tensao de ruptura reversa (V)
* IBV = corrente na ruptura (A)
* CJO = capacitancia de juncao (F)
* VJ  = potencial de juncao (V)
* TT  = tempo de transito (s)

.model 1N4148 D(IS=2.52e-9 RS=0.568 N=1.752 BV=100 IBV=100u CJO=4p VJ=0.5 TT=6n)
```

### Modelo de BJT (NPN/PNP)

```spice
.model nome NPN(parametros)  ; ou PNP

* Parametros principais:
* IS  = corrente de saturacao (A)
* BF  = ganho de corrente (beta) direto
* BR  = ganho reverso
* VAF = tensao Early direta (V)
* VAR = tensao Early reversa (V)
* NF  = coeficiente de emissao direto
* NR  = coeficiente de emissao reverso
* IKF = corrente de joelho (A)
* ISE = corrente de saturacao B-E
* ISC = corrente de saturacao B-C
* CJE = capacitancia B-E (F)
* CJC = capacitancia B-C (F)
* TF  = tempo de transito direto (s)
* TR  = tempo de transito reverso (s)
* RB  = resistencia de base (ohm)
* RC  = resistencia de coletor (ohm)
* RE  = resistencia de emissor (ohm)

.model 2N2222 NPN(IS=14.34f BF=255 NF=1 VAF=74.03 IKF=0.2847 ISE=14.34f
+ NE=1.307 BR=6.092 NR=1 VAR=28 IKR=0 ISC=0 NC=2 RB=10 RC=1 RE=0
+ CJE=22.01p VJE=0.75 MJE=0.377 CJC=7.306p VJC=0.75 MJC=0.3416 TF=411.1p TR=46.91n)
```

### Modelo de MOSFET (NMOS/PMOS)

```spice
.model nome NMOS(parametros) LEVEL=1  ; ou PMOS

* Parametros nivel 1:
* VTO    = tensao de threshold (V)
* KP     = transcondutancia (A/V^2)
* GAMMA  = coeficiente de body effect (V^0.5)
* PHI    = potencial de superficie (V)
* LAMBDA = modulacao de canal (1/V)
* CBD    = capacitancia drain-bulk (F)
* CBS    = capacitancia source-bulk (F)
* TOX    = espessura do oxido (m)

.model NMOS_3V3 NMOS(VTO=0.5 KP=120u GAMMA=0.4 PHI=0.65 LAMBDA=0.06
+ CBD=20f CBS=20f TOX=7.5n)

* Para modelos mais precisos, use LEVEL=2, 3, ou BSIM3/4
```

### Modelo de JFET (NJF/PJF)

```spice
.model nome NJF(parametros)  ; ou PJF

* VTO   = tensao de pinch-off (V)
* BETA  = coeficiente de transcondutancia (A/V^2)
* LAMBDA = modulacao de canal (1/V)
* IS    = corrente de saturacao do gate (A)

.model 2N5457 NJF(VTO=-1.5 BETA=1m LAMBDA=2m IS=1f CGS=4.5p CGD=1.5p)
```

---

## 10. Comandos de Plotagem e Exportacao

### Plotagem

```spice
.control
  run

  * Grafico basico
  plot v(out)

  * Multiplas curvas
  plot v(in) v(out) v(ref)

  * Grafico XY (curva caracteristica)
  plot i(D1) vs v(D1)

  * Com titulo
  plot v(out) title 'Tensao de Saida'

  * Com limites de eixo
  plot v(out) xlimit 0 10m ylimit -5 5

  * Em escala logaritmica
  plot v(out) xlog          ; eixo X log
  plot v(out) ylog          ; eixo Y log

  * Magnitude em dB (para analise AC)
  plot db(v(out))
  plot vdb(out)             ; sintaxe alternativa

  * Fase em graus
  plot phase(v(out))
  plot vp(out)              ; sintaxe alternativa

  * Magnitude e fase juntos
  plot db(v(out)) phase(v(out))
.endc
```

### Exportacao de graficos

```spice
.control
  run

  * Definir tipo de arquivo
  set hcopydevtype=png      ; ou svg, ps, eps

  * Exportar grafico
  hardcopy saida.png v(out)
  hardcopy bode.png db(v(out)) phase(v(out))

  * Definir tamanho (em pixels para PNG)
  set hcopywidth=1024
  set hcopyheight=768
.endc
```

### Exportacao de dados

```spice
.control
  run

  * Configurar formato
  set filetype=ascii        ; arquivo texto legivel
  set wr_vecnames           ; incluir nomes das colunas
  set wr_singlescale        ; escala unica (tempo/frequencia)

  * Exportar para arquivo
  wrdata dados.csv v(in) v(out)
  wrdata transiente.txt time v(out) i(R1)

  * Exportar raw data (formato binario ngspice)
  write simulacao.raw v(out)
.endc
```

### Medidas automaticas (.meas)

```spice
* Medidas em analise transiente
.meas tran v_max MAX v(out)
.meas tran v_min MIN v(out)
.meas tran v_pp PP v(out)
.meas tran v_avg AVG v(out) from=1m to=5m
.meas tran v_rms RMS v(out)

* Medir quando atinge um valor
.meas tran t_rise WHEN v(out)=2.5 RISE=1
.meas tran t_fall WHEN v(out)=2.5 FALL=1

* Medir intervalo de tempo
.meas tran t_delay TRIG v(in) VAL=2.5 RISE=1 TARG v(out) VAL=2.5 RISE=1

* Calcular expressao
.meas tran freq PARAM='1/periodo'
.meas tran ganho PARAM='v_out_pp/v_in_pp'

* Medidas em analise AC
.meas ac bw WHEN db(v(out))=-3 FALL=1
.meas ac f_polo WHEN phase(v(out))=-45
.meas ac ganho_max MAX db(v(out))
```

---

## 11. Dicas e Boas Praticas

### Convergencia

```spice
* Se a simulacao nao converge, tente:

* Relaxar tolerancias
.options reltol=1e-3       ; tolerancia relativa (padrao: 1e-3)
.options abstol=1e-9       ; tolerancia absoluta de corrente (padrao: 1e-12)
.options vntol=1e-4        ; tolerancia de tensao (padrao: 1e-6)
.options gmin=1e-10        ; condutancia minima (padrao: 1e-12)

* Aumentar iteracoes
.options itl1=500          ; iteracoes DC (padrao: 100)
.options itl2=200          ; iteracoes DC transfer curve
.options itl4=100          ; iteracoes transiente (padrao: 10)

* Para osciladores - pular ponto de operacao
.tran 1n 1m uic
```

### Performance

```spice
* Para simulacoes longas
.options method=gear       ; metodo de integracao (gear ou trap)
.options maxord=4          ; ordem maxima do metodo

* Controle de passo
.options trtol=1           ; tolerancia de truncamento
.tran 1n 1m 0 10n          ; tempo_max_passo = 10n
```

### Organizacao do codigo

```spice
* ==========================
* CABECALHO COM TITULO
* ==========================

* ---------- Secao: Parametros ----------
.param Vcc=12
.param freq=1k

* ---------- Secao: Alimentacao ----------
V1 vcc 0 DC {Vcc}

* ---------- Secao: Circuito Principal ----------
R1 vcc out 1k
C1 out 0 100n

* ---------- Secao: Analise ----------
.tran 1u 10m

* ---------- Secao: Controle ----------
.control
  run
  plot v(out)
.endc

.end
```

### Debug

```spice
.control
  * Ver todos os nos do circuito
  display

  * Ver opcoes atuais
  options

  * Ver dispositivos
  show all

  * Ver modelo de um componente
  showmod R1
  showmod Q1

  * Verificar circuito sem simular
  op
  show Q1         ; parametros DC do transistor
.endc
```

### Mensagens de erro comuns

| Erro | Causa | Solucao |
|------|-------|---------|
| `no DC path to ground` | No flutuante | Adicione resistor de alta impedancia para terra |
| `singular matrix` | Malha de tensao ou no de corrente | Verifique conexoes |
| `timestep too small` | Descontinuidade forte | Reduza tolerancias ou suavize transicoes |
| `doAnalyses: iteration limit` | Nao convergiu | Ajuste .options ou condicoes iniciais |

### Exemplo de circuito completo bem estruturado

```spice
* =========================================================
* AMPLIFICADOR EMISSOR COMUM - BC548
* Autor: Seu Nome
* Data: 2024
* =========================================================

* ---------- Parametros Globais ----------
.param Vcc=12
.param Ic=1m
.param Beta=200
.param freq_sinal=1k

* ---------- Alimentacao ----------
VCC vcc 0 DC {Vcc}
Vin in 0 SIN(0 10m {freq_sinal}) AC 1

* ---------- Polarizacao ----------
* Divisor de tensao para base
R1 vcc base 47k
R2 base 0 10k

* Resistores de emissor e coletor
RC vcc col 4.7k
RE emi 0 1k

* Capacitor de bypass do emissor
CE emi 0 100u

* ---------- Transistor ----------
Q1 col base emi BC548

* ---------- Acoplamento ----------
Cin in base 10u
Cout col out 10u
RL out 0 10k

* ---------- Modelo ----------
.model BC548 NPN(IS=1e-14 BF={Beta} VAF=100 CJE=8p CJC=3p)

* ---------- Analises ----------
.op
.ac dec 100 10 10meg
.tran 10u 10m

* ---------- Controle ----------
.control
  * Ponto de operacao
  op
  echo "=== Ponto de Operacao ==="
  print v(base) v(col) v(emi)
  print @Q1[ic] @Q1[vbe] @Q1[vce]

  * Resposta em frequencia
  ac dec 100 10 10meg
  plot db(v(out)) title 'Resposta em Frequencia'
  meas ac bw_3db WHEN db(v(out))=db(v(out))-3 FALL=1

  * Transiente
  tran 10u 10m
  plot v(in)*100 v(out) title 'Entrada (x100) e Saida'

  * Calcular ganho
  meas tran vin_pp PP v(in)
  meas tran vout_pp PP v(out)
  let ganho = vout_pp/vin_pp
  print ganho
.endc

.end
```

---

## 12. Modo Batch e Armadilhas Comuns

### Modo Batch vs Modo Interativo

O ngspice pode ser executado de duas formas:

**Modo Interativo:**
```bash
ngspice circuito.spice
# Abre interface grafica com plots
```

**Modo Batch:**
```bash
ngspice -b circuito.spice -o saida.log
# Executa sem interface, salva log
```

### Limitacoes do Modo Batch

```spice
.control
  run

  * ESTES COMANDOS NAO FUNCIONAM EM BATCH MODE:
  plot v(out)              ; ✗ Nao tem interface grafica
  hardcopy saida.png       ; ✗ Dispositivo PNG nao disponivel

  * ALTERNATIVAS QUE FUNCIONAM:
  print v(out)             ; ✓ Imprime valores no log
  wrdata saida.csv v(out)  ; ✓ Exporta para CSV
  echo "Resultado: " v(out) ; ✓ Mostra no log
.endc
```

### Armadilha 1: Analises Duplicadas

**ERRADO** - Define analises fora E dentro do .control:
```spice
* Analises fora do .control
.op
.tran 1u 10m
.ac dec 100 1 1meg

.control
  * ERRO: Chama as mesmas analises novamente!
  op
  tran 1u 10m
  ac dec 100 1 1meg

  plot v(out)
.endc
```

**CORRETO** - Opcao 1: Apenas dentro do .control
```spice
* Nao definir analises fora!

.control
  * Chamar analises diretamente
  op
  tran 1u 10m
  ac dec 100 1 1meg

  plot v(out)
.endc
```

**CORRETO** - Opcao 2: Usar 'run' (recomendado)
```spice
* Definir analises fora
.op
.tran 1u 10m
.ac dec 100 1 1meg

.control
  * Usar 'run' para executar TODAS as analises
  run

  plot v(out)
.endc
```

### Armadilha 2: Sintaxe PARAM (obsoleta)

**ERRADO** - Usando PARAM em .meas:
```spice
.control
  tran 1u 10m

  meas tran vmax MAX v(out)
  meas tran vmin MIN v(out)
  meas tran vpp PARAM='vmax - vmin'    ; ✗ ERRO!
  meas tran ganho PARAM='vpp/vin'      ; ✗ ERRO!
.endc
```

**CORRETO** - Usar 'let' para calculos:
```spice
.control
  tran 1u 10m

  meas tran vmax MAX v(out)
  meas tran vmin MIN v(out)
  let vpp = vmax - vmin                ; ✓ Correto
  let ganho = vpp / vin                ; ✓ Correto

  print vpp ganho
.endc
```

### Armadilha 3: Plot Switching em wrdata

Quando voce tem multiplas analises (tran, ac, dc), precisa mudar o plot ativo antes de exportar dados:

**ERRADO** - Nao muda o plot:
```spice
.control
  run

  * Apos 'run', o plot atual pode ser qualquer um
  wrdata time_data.csv time v(out)        ; ✗ Pode falhar
  wrdata freq_data.csv frequency vdb(out) ; ✗ Pode falhar
.endc
```

**CORRETO** - Muda o plot antes de wrdata:
```spice
.control
  run

  * Mudar para plot transiente
  set curplot = tran1
  wrdata time_data.csv time v(out)

  * Mudar para plot AC
  set curplot = ac1
  wrdata freq_data.csv frequency vdb(out)
.endc
```

### Armadilha 4: Hardcopy em Batch Mode

**ERRADO** - Tentar usar hardcopy em batch:
```spice
.control
  run

  set hcopydevtype=png
  hardcopy saida.png v(out)  ; ✗ ERRO: dispositivo PNG nao disponivel
.endc
```

**CORRETO** - Exportar CSV e converter depois:
```spice
.control
  run

  * Exportar dados em CSV
  wrdata saida.csv time v(out)

  * Converter para PNG fora do ngspice:
  * python csv_to_png.py saida.csv
.endc
```

### Armadilha 5: Nomes de Modelos Case-Sensitive

**ERRADO** - Nome do modelo nao bate:
```spice
* Definir modelo
.model VSWITCH SW (RON=10 ROFF=10meg)

* Usar modelo (nome diferente!)
S1 in out ctrl 0 vswitch    ; ✗ ERRO: 'vswitch' != 'VSWITCH'
```

**CORRETO** - Nome exato:
```spice
* Definir modelo
.model SWMOD SW (RON=10 ROFF=10meg)

* Usar modelo
S1 in out ctrl 0 SWMOD       ; ✓ Correto
```

**NOTA**: O tipo de modelo correto para switches de tensao e `SW`, nao `VSWITCH`!

### Armadilha 6: Osciladores sem Perturbacao

Osciladores podem ficar "travados" no ponto DC se nao houver uma perturbacao inicial:

**PROBLEMA** - Oscilador nao inicia:
```spice
* Oscilador Colpitts
C1 coletor emissor 100p
C2 emissor 0 100p
L1 coletor 0 10u

* Condicoes iniciais zeradas - pode nao oscilar!
.tran 1n 1m
```

**SOLUCAO** - Adicionar perturbacao inicial:
```spice
* Oscilador Colpitts
C1 coletor emissor 100p IC=0.1    ; Pequena tensao inicial
C2 emissor 0 100p
L1 coletor 0 10u

* Usar 'uic' para pular .op e usar IC
.tran 1n 1m uic
```

### Armadilha 7: Caminhos Relativos em wrdata

**ERRADO** - Caminho relativo pode falhar:
```spice
.control
  run
  wrdata circuits/dados/saida.csv v(out)  ; ✗ Pode nao encontrar diretorio
.endc
```

**CORRETO** - Usar caminho absoluto ou diretorio atual:
```spice
.control
  run
  wrdata saida.csv v(out)  ; ✓ Salva no diretorio atual
.endc
```

---

## 13. Referencias de Dispositivos e Hierarquia

### Acessando Parametros de Dispositivos

```spice
.control
  op

  * Sintaxe: @dispositivo[parametro]
  print @Q1[ic]      ; Corrente de coletor
  print @Q1[vbe]     ; Tensao base-emissor
  print @Q1[vce]     ; Tensao coletor-emissor
  print @Q1[gm]      ; Transcondutancia

  print @R1[i]       ; Corrente no resistor
  print @C1[i]       ; Corrente no capacitor

  print @M1[vgs]     ; MOSFET: tensao gate-source
  print @M1[id]      ; MOSFET: corrente de drain
  print @M1[vth]     ; MOSFET: tensao de threshold
.endc
```

### Dispositivos em Subcircuitos (Hierarquia)

**Dispositivos em subcircuitos** precisam de referencias hierarquicas:

```spice
* Subcircuito simples
.subckt amplificador in out vcc gnd
  Q1 out in gnd BC548
  R1 vcc out 10k
.ends

* Instanciar subcircuito
X1 entrada saida vcc 0 amplificador

.control
  op

  * ERRADO - Dispositivo esta dentro de X1:
  print @Q1[ic]           ; ✗ ERRO: Q1 nao existe no top-level

  * CORRETO - Referencia hierarquica:
  print @q.x1.q1[ic]      ; ✓ BJT dentro de subcircuito
  print @r.x1.r1[i]       ; ✓ Resistor dentro de subcircuito
.endc
```

### Regras de Referencias Hierarquicas

**Top-level (fora de subcircuitos):**
```spice
Q1 c b e BC548
R1 vcc out 1k

.control
  print @q1[ic]           ; ✓ Dispositivo no top-level
  print @r1[i]            ; ✓ Resistor no top-level
.endc
```

**Dentro de subcircuito:**
```spice
.subckt amp in out
  Q1 out in 0 BC548
  R1 vcc out 1k
.ends

X1 entrada saida amp

.control
  * Formato: @tipo.instancia.dispositivo[parametro]
  print @q.x1.q1[ic]      ; ✓ BJT: prefixo 'q.'
  print @r.x1.r1[i]       ; ✓ Resistor: prefixo 'r.'
  print @c.x1.c1[i]       ; ✓ Capacitor: prefixo 'c.'
  print @m.x1.m1[id]      ; ✓ MOSFET: prefixo 'm.'
  print @j.x1.j1[id]      ; ✓ JFET: prefixo 'j.'
  print @d.x1.d1[id]      ; ✓ Diodo: prefixo 'd.'
.endc
```

### Hierarquia com Multiplos Niveis

```spice
.subckt bloco_interno in out
  Q1 out in 0 BC548
.ends

.subckt bloco_externo in out
  X_interno in mid bloco_interno
  R1 mid out 1k
.ends

X_sistema entrada saida bloco_externo

.control
  * Referencia com 3 niveis:
  print @q.x_sistema.x_interno.q1[ic]

  * 2 niveis:
  print @r.x_sistema.r1[i]
.endc
```

### Parametros Disponiveis por Tipo

**BJT (Q):**
```spice
@Q1[ic]     ; Corrente de coletor
@Q1[ib]     ; Corrente de base
@Q1[ie]     ; Corrente de emissor
@Q1[vbe]    ; Tensao base-emissor
@Q1[vbc]    ; Tensao base-coletor
@Q1[vce]    ; Tensao coletor-emissor
@Q1[gm]     ; Transcondutancia
@Q1[gpi]    ; Condutancia de entrada
@Q1[gmu]    ; Condutancia de Miller
@Q1[beta]   ; Ganho de corrente (hfe)
```

**MOSFET (M):**
```spice
@M1[id]     ; Corrente de drain
@M1[ig]     ; Corrente de gate
@M1[is]     ; Corrente de source
@M1[vgs]    ; Tensao gate-source
@M1[vds]    ; Tensao drain-source
@M1[vth]    ; Tensao de threshold
@M1[gm]     ; Transcondutancia
@M1[gds]    ; Condutancia drain-source
@M1[cgs]    ; Capacitancia gate-source
```

**JFET (J):**
```spice
@J1[id]     ; Corrente de drain
@J1[ig]     ; Corrente de gate
@J1[vgs]    ; Tensao gate-source
@J1[vgd]    ; Tensao gate-drain
@J1[gm]     ; Transcondutancia
@J1[gds]    ; Condutancia drain-source
```

**Diodo (D):**
```spice
@D1[id]     ; Corrente no diodo
@D1[vd]     ; Tensao no diodo
@D1[cd]     ; Capacitancia de juncao
@D1[gd]     ; Condutancia
```

**Resistor (R):**
```spice
@R1[i]      ; Corrente
@R1[p]      ; Potencia dissipada
@R1[resistance] ; Resistencia
```

**Capacitor (C):**
```spice
@C1[i]      ; Corrente
@C1[p]      ; Potencia
@C1[capacitance] ; Capacitancia
```

**Indutor (L):**
```spice
@L1[i]      ; Corrente
@L1[p]      ; Potencia
@L1[flux]   ; Fluxo magnetico
```

---

## Referencias Adicionais

- [ngspice User Manual](http://ngspice.sourceforge.net/docs/ngspice-manual.pdf)
- [SPICE Quick Reference - Berkeley](http://bwrcs.eecs.berkeley.edu/Classes/IcBook/SPICE/)
- [LTspice Getting Started Guide](https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html)
- [Troubleshooting Guide](troubleshooting.md) - Guia de resolucao de problemas comuns

---

*Tutorial criado para o projeto learning_ngspice*
