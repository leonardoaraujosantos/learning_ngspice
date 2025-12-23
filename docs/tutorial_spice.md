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
12. [FFT e Analise no Dominio da Frequencia](#12-fft-e-analise-no-dominio-da-frequencia)
13. [Fontes Comportamentais](#13-fontes-comportamentais)
14. [Chaves e Fontes Controladas](#14-chaves-e-fontes-controladas)
15. [Modo Batch e Armadilhas Comuns](#15-modo-batch-e-armadilhas-comuns)
16. [Referencias de Dispositivos e Hierarquia](#16-referencias-de-dispositivos-e-hierarquia)
17. [Modo Interativo Avancado](#17-modo-interativo-avancado)
18. [Verilog-A e OpenVAF - Modelos Customizados](#18-verilog-a-e-openvaf---modelos-customizados)

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

* Usando FIND para encontrar valor em ponto especifico
.meas ac ganho_1khz FIND vdb(out) AT=1k
.meas ac ganho_10khz FIND vdb(out) AT=10k
.meas ac fase_1khz FIND vp(out) AT=1k

* FIND com condicao WHEN
.meas ac fase_fc FIND vp(out) WHEN vdb(out)=-3

* Exemplo completo de medidas AC
.meas ac ganho_dc FIND vdb(out) AT=1
.meas ac fc WHEN vdb(out)=ganho_dc-3 FALL=1
.meas ac ganho_fc FIND vdb(out) WHEN vdb(out)=ganho_dc-3
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

## 12. FFT e Analise no Dominio da Frequencia

A Transformada Rapida de Fourier (FFT - Fast Fourier Transform) permite analisar o conteudo espectral de sinais no dominio do tempo, sendo essencial para analise de osciladores, mixers, e distorcao harmonica.

### Comando linearize

Antes de executar a FFT, e necessario **linearizar** os dados, ou seja, reamostrar para uma grade de tempo uniforme.

```spice
.control
  * Executar analise transiente
  tran 1u 100u

  * Linearizar dados antes da FFT
  linearize v(output)

  * Agora pode executar FFT
  fft v(output)
.endc
```

**Por que linearize e necessario?**
- A analise transiente usa passo adaptativo (passos variaveis)
- FFT requer pontos igualmente espacados no tempo
- `linearize` reamostra os dados para grade uniforme

### Executando FFT

```spice
.control
  * Simular sinal periodico
  tran 0.1u 100u

  * Linearizar e executar FFT
  linearize v(signal)
  fft v(signal)

  * Plotar magnitude do espectro
  plot mag(v(signal)) xlimit 0 10MEG

  * Plotar em dB
  let signal_db = db(v(signal))
  plot signal_db xlimit 0 10MEG title 'Espectro de Frequencia (dB)'
.endc
```

### Exemplo Completo - Oscilador com FFT

```spice
* Oscilador Colpitts com analise FFT

* Circuito oscilador
V1 vcc 0 DC 9
Q1 coll base emit BC548
L1 coll 0 10u IC=0.1
C1 coll emit 100p
C2 emit 0 100p
R1 vcc base 47k
R2 base 0 10k
RE emit 0 1k

.model BC548 NPN(IS=1e-14 BF=200 VAF=100)

* Analise transiente (100us = ~10 periodos @ 100kHz)
.tran 0.1u 100u uic

.control
  run

  * Plotar forma de onda no tempo
  plot v(coll) title 'Oscilador - Dominio do Tempo'

  * Preparar para FFT
  linearize v(coll)
  fft v(coll)

  * Converter para dB
  let coll_db = db(v(coll))

  * Plotar espectro
  plot coll_db xlimit 0 1MEG ylimit -80 0 title 'Espectro de Frequencia'

  * Encontrar frequencia fundamental
  meas sp fund_freq WHEN coll_db=MAX(coll_db) FROM=50k TO=200k
  echo "Frequencia fundamental: " $&fund_freq " Hz"

  * Exportar dados espectrais
  set curplot = fft1
  wrdata espectro.csv frequency mag(v(coll))
.endc

.end
```

### Medidas no Dominio da Frequencia

```spice
.control
  tran 0.1u 100u
  linearize v(out)
  fft v(out)

  * Mudar para plot FFT
  set curplot = fft1

  * Medir pico fundamental
  meas sp fund_mag MAX mag(v(out)) FROM=900 TO=1100

  * Medir harmonica (2x freq fundamental)
  meas sp harm2_mag MAX mag(v(out)) FROM=1900 TO=2100

  * Calcular THD (Total Harmonic Distortion)
  let thd_pct = (harm2_mag / fund_mag) * 100
  print thd_pct
.endc
```

### Analise de Mixers e Modulacao

```spice
* Mixer simples - multiplica dois sinais

* Sinal RF (10MHz)
Vrf rf 0 SIN(0 1 10MEG)

* Oscilador Local (9MHz)
Vlo lo 0 SIN(0 1 9MEG)

* Mixer comportamental (produto)
Bmixer out 0 V={v(rf) * v(lo)}
Rload out 0 1k

.tran 1n 10u

.control
  run

  * Linearizar e FFT
  linearize v(out)
  fft v(out)

  * Plotar espectro - deve mostrar:
  * - 1MHz (diferenca: 10M - 9M)
  * - 19MHz (soma: 10M + 9M)
  let out_db = db(v(out))
  plot out_db xlimit 0 25MEG title 'Saida do Mixer'

  * Medir frequencia IF (intermediaria)
  set curplot = fft1
  meas sp if_freq WHEN out_db=MAX(out_db) FROM=500k TO=1.5MEG
  echo "Frequencia IF: " $&if_freq " Hz"
.endc

.end
```

### Janelamento (Windowing)

Para reduzir "vazamento espectral" (spectral leakage), pode-se aplicar janelas:

```spice
.control
  tran 0.1u 100u

  * Aplicar janela de Hanning antes da FFT
  let window = hanning(length(v(signal)))
  let signal_windowed = v(signal) * window

  * FFT com janelamento
  linearize signal_windowed
  fft signal_windowed

  plot db(signal_windowed) xlimit 0 1MEG
.endc
```

**Funcoes de janela disponiveis:**
- `hanning(n)` - Janela de Hanning (mais comum)
- `hamming(n)` - Janela de Hamming
- `blackman(n)` - Janela de Blackman

### Resolucao em Frequencia

A resolucao da FFT depende do tempo total de simulacao:

```
Resolucao = 1 / tempo_total

Exemplos:
- 1ms simulado   → resolucao = 1kHz
- 100us simulado → resolucao = 10kHz
- 10us simulado  → resolucao = 100kHz
```

**Dica**: Para melhor resolucao, aumente o tempo de simulacao (mais periodos).

### Plot Switching para FFT

Quando houver multiplas analises, use `set curplot`:

```spice
.control
  * Analise AC
  ac dec 100 1 1MEG

  * Analise transiente
  tran 1u 100u
  linearize v(out)
  fft v(out)

  * Mudar para plot transiente
  set curplot = tran1
  wrdata time_domain.csv time v(out)

  * Mudar para plot FFT
  set curplot = fft1
  wrdata freq_domain.csv frequency mag(v(out))
.endc
```

### Exemplo - Analise de Distorcao Harmonica

```spice
* Amplificador com analise de distorcao

Vin in 0 SIN(0 0.5 1k)
R1 in base 10k
Q1 vcc base 0 BC548
RC vcc coll 4.7k
RE 0 emit 1k
Vcc vcc 0 DC 12

.model BC548 NPN(IS=1e-14 BF=200)

.tran 1u 10m

.control
  run

  * FFT do sinal de saida
  linearize v(coll)
  fft v(coll)

  set curplot = fft1
  let coll_db = db(v(coll))

  * Plotar espectro
  plot coll_db xlimit 0 10k ylimit -100 0 title 'Distorcao Harmonica'

  * Medir fundamental (1kHz) e harmonicas
  meas sp fund MAX mag(v(coll)) FROM=900 TO=1100
  meas sp h2 MAX mag(v(coll)) FROM=1900 TO=2100     ; 2a harmonica
  meas sp h3 MAX mag(v(coll)) FROM=2900 TO=3100     ; 3a harmonica

  * Calcular THD
  let thd = sqrt(h2^2 + h3^2) / fund * 100
  echo "THD = " $&thd "%"
.endc

.end
```

### Limitacoes da FFT

1. **Frequencia de Nyquist**: Frequencia maxima = 1/(2*passo_tempo)
2. **Sinais nao periodicos**: FFT funciona melhor com sinais periodicos
3. **Tempo de simulacao**: Deve capturar varios periodos completos
4. **Memoria**: FFT de sinais longos pode consumir muita memoria

---

## 13. Fontes Comportamentais

Fontes comportamentais (B-sources) permitem criar fontes de tensao ou corrente com expressoes matematicas arbitrarias, sendo essenciais para modelar sistemas complexos.

### Sintaxe Basica

```spice
* Fonte de tensao comportamental
* Sintaxe: Bnome no+ no- V={expressao}

Bvco out 0 V={5*sin(2*3.14159*1MEG*time)}

* Fonte de corrente comportamental
* Sintaxe: Bnome no+ no- I={expressao}

Bisrc out 0 I={v(ctrl) * 1m}
```

### Expressoes Matematicas

```spice
* Operadores aritmeticos: + - * / **
B1 out 0 V={v(in) * 10 + 2.5}          ; ganho e offset

* Funcoes trigonometricas
B2 out 0 V={sin(2*pi*1k*time)}         ; seno
B3 out 0 V={cos(2*pi*1k*time)}         ; cosseno

* Funcoes exponenciais
B4 out 0 V={exp(-time/1m)}             ; decaimento exponencial
B5 out 0 V={log10(v(in))}              ; logaritmo

* Funcoes matematicas
B6 out 0 V={sqrt(v(in))}               ; raiz quadrada
B7 out 0 V={abs(v(in))}                ; valor absoluto
B8 out 0 V={pow(v(in), 2)}             ; potencia
```

### Operador Condicional (Ternario)

```spice
* Sintaxe: {condicao ? valor_se_true : valor_se_false}

* Comparador simples
Bcomp out 0 V={v(in) > 2.5 ? 5 : 0}

* Retificador ideal
Brect out 0 V={v(in) > 0 ? v(in) : 0}

* Limitador
Blimit out 0 V={v(in) > 5 ? 5 : (v(in) < -5 ? -5 : v(in))}
```

### Operadores Logicos e Relacionais

```spice
* Operadores relacionais: > < >= <= == !=
* Operadores logicos: && (AND), || (OR), ! (NOT)

* Porta AND comportamental
Band out 0 V={v(a) > 2.5 && v(b) > 2.5 ? 5 : 0}

* Porta OR comportamental
Bor out 0 V={v(a) > 2.5 || v(b) > 2.5 ? 5 : 0}

* Porta XOR comportamental
Bxor out 0 V={abs(v(a) - v(b)) > 2.5 ? 5 : 0}
```

### Variavel time

A variavel especial `time` representa o tempo atual da simulacao:

```spice
* Rampa linear
Bramp out 0 V={time * 1000}            ; 1V/ms

* Sinal senoidal customizado
Bsin out 0 V={2.5 + 2.5*sin(2*3.14159*1k*time)}

* VCO (Voltage Controlled Oscillator)
* Frequencia varia com tensao de controle
Bvco out 0 V={sin(2*3.14159*(1MEG + 100k*v(tune))*time)}
```

### Exemplo - Multiplicador Analogico

```spice
* Multiplicador de 4 quadrantes

Vin1 in1 0 SIN(0 1 1k)
Vin2 in2 0 SIN(0 0.5 10k)

* Multiplicador: Vout = Vin1 * Vin2
Bmult out 0 V={v(in1) * v(in2)}
Rload out 0 10k

.tran 10u 10m

.control
  run
  plot v(in1) v(in2) v(out)
.endc

.end
```

### Exemplo - Mixer RF

```spice
* Mixer RF com oscilador local

* Sinal RF (100MHz)
Vrf rf 0 SIN(0 1 100MEG)

* Oscilador local (90MHz)
Vlo lo 0 SIN(0 1 90MEG)

* Mixer (multiplicador)
Bmixer mix 0 V={v(rf) * v(lo)}

* Filtro passa-baixas para extrair IF (10MHz)
Rmix mix out 1k
Cout out 0 16n              ; fc ~= 10MHz

.tran 0.1n 1u

.control
  run
  plot v(rf) v(out)

  * FFT para ver componentes espectrais
  linearize v(out)
  fft v(out)
  let out_db = db(v(out))
  plot out_db xlimit 0 200MEG
.endc

.end
```

### Exemplo - PLL Simples (Phase-Locked Loop)

```spice
* PLL comportamental simplificado

* Sinal de referencia (1MHz)
Vref ref 0 PULSE(0 5 0 1n 1n 500n 1u)

* Detector de fase (XOR)
Bxor phase_err 0 V={abs(v(ref) - v(feedback))}

* Filtro de loop (passa-baixas)
Rloop phase_err vtune 10k
Cloop vtune 0 1u

* VCO (Voltage Controlled Oscillator)
* Frequencia central: 1MHz, ganho: 100kHz/V
Bvco vco_out 0 V={5*sin(2*3.14159*(1MEG + 100k*v(vtune))*time)}

* Comparador para gerar feedback digital
Bcomp feedback 0 V={v(vco_out) > 0 ? 5 : 0}

.tran 0.1u 100u

.control
  run
  plot v(ref) v(feedback) v(vtune)
  echo "Tensao de sintonia final: " v(vtune)
.endc

.end
```

### Exemplo - Funcao de Transferencia Customizada

```spice
* Amplificador com ganho variavel

Vin in 0 AC 1
Vctrl ctrl 0 DC 2.5        ; controle de ganho

* Ganho = 1 + ctrl_voltage (de 1x a 6x)
Bamp out 0 V={v(in) * (1 + v(ctrl))}
Rload out 0 10k

.ac dec 100 1 1MEG

.control
  run
  plot db(v(out)) title 'Ganho Variavel'
.endc

.end
```

### Limitacoes e Cuidados

```spice
* CUIDADO: Expressoes muito complexas podem causar problemas de convergencia

* BOM - Simples e claro
Bgood out 0 V={v(in) * 10}

* RUIM - Muito complexo, pode nao convergir
Bbad out 0 V={sqrt(abs(sin(v(in)*time))) / (1 + exp(-v(in)))}

* Solucao: Dividir em etapas
B1 temp 0 V={sin(v(in) * time)}
B2 out 0 V={sqrt(abs(v(temp)))}
```

### Funcoes Disponiveis em B-sources

| Funcao | Descricao |
|--------|-----------|
| `sin(x)`, `cos(x)`, `tan(x)` | Trigonometricas (radianos) |
| `asin(x)`, `acos(x)`, `atan(x)` | Arco-trigonometricas |
| `exp(x)` | Exponencial (e^x) |
| `ln(x)`, `log(x)` | Logaritmo natural e base 10 |
| `sqrt(x)` | Raiz quadrada |
| `abs(x)` | Valor absoluto |
| `pow(x,y)` | x elevado a y |
| `min(x,y)`, `max(x,y)` | Minimo e maximo |
| `time` | Tempo atual da simulacao |

---

## 14. Chaves e Fontes Controladas

Alem dos componentes passivos e ativos, o SPICE oferece chaves controladas e fontes dependentes (controladas) que sao essenciais para modelar circuitos complexos.

### Chaves Controladas por Tensao (S)

```spice
* Sintaxe: Snome no+ no- nctrl+ nctrl- modelo

* Chave controlada por tensao
S1 in out ctrl 0 SWMOD

* Modelo de chave
.model SWMOD SW(Ron=10 Roff=10MEG Vt=2.5 Vh=0.1)

* Parametros:
* Ron  = resistencia quando fechada (ohms)
* Roff = resistencia quando aberta (ohms)
* Vt   = tensao de threshold (V)
* Vh   = histerese (V)
```

**Operacao:**
- Fecha quando `V(ctrl) - V(0) > Vt + Vh`
- Abre quando `V(ctrl) - V(0) < Vt - Vh`

### Chaves Controladas por Corrente (W)

```spice
* Sintaxe: Wnome no+ no- Vsense modelo

* Fonte de corrente para sensoriamento
Vsense ctrl 0 DC 0

* Chave controlada por corrente
W1 in out Vsense SWMOD

.model SWMOD CSW(Ron=1 Roff=1MEG It=10m Ih=1m)

* Parametros:
* Ron  = resistencia quando fechada
* Roff = resistencia quando aberta
* It   = corrente de threshold (A)
* Ih   = histerese (A)
```

### Exemplo - Timer 555 com Chaves

```spice
* Modelo simplificado do 555 usando chaves

* Pinos
Vcc VCC 0 DC 5
Rtrig TRIG 0 10k
Ctrig TRIG 0 100n
Vtrig_pulse TRIG 0 PULSE(5 0 1m 1n 1n 1u 10m)

* Capacitor de tempo
Ctime DISCH GND 100n
Rtime VCC DISCH 10k

* Comparadores implementados com chaves
* Comparador superior (threshold = 2/3 Vcc)
Scomp_upper n_upper GND DISCH GND SW_UPPER
.model SW_UPPER SW(Ron=100 Roff=10MEG Vt=3.33 Vh=0.1)

* Comparador inferior (threshold = 1/3 Vcc)
Scomp_lower GND n_lower TRIG GND SW_LOWER
.model SW_LOWER SW(Ron=100 Roff=10MEG Vt=1.67 Vh=0.1)

* Flip-flop SR simplificado e chave de descarga
* (modelo muito simplificado para demonstracao)
Sdisch DISCH GND n_dctl GND SW_555
.model SW_555 SW(Ron=100 Roff=100MEG Vt=1.7 Vh=0.1)

Rload OUT GND 10k
Vout OUT 0 DC 2.5

.tran 10u 20m

.control
  run
  plot v(DISCH) v(OUT) v(TRIG)
.endc

.end
```

### Fontes Controladas por Tensao

#### VCVS - Fonte de Tensao Controlada por Tensao (E)

```spice
* Sintaxe: Enome no+ no- nctrl+ nctrl- ganho

* Amplificador de tensao simples
E1 out 0 in 0 10            ; ganho = 10

* Buffer diferencial
E2 out 0 inp inn 1          ; Vout = Vinp - Vinn

* Com offset
E3 out 0 in 0 5             ; Vout = 5 * Vin
```

**Aplicacoes:**
- Amplificadores ideais
- Buffers
- Amplificadores diferenciais
- Instrumentacao

#### VCCS - Fonte de Corrente Controlada por Tensao (G)

```spice
* Sintaxe: Gnome no+ no- nctrl+ nctrl- transcondutancia

* Transcondutancia simples
G1 out 0 in 0 0.001         ; gm = 1mS (1mA/V)

* OTA (Operational Transconductance Amplifier)
Gota out 0 inp inn 10m      ; Iout = 10m * (Vinp - Vinn)
```

**Aplicacoes:**
- OTAs
- Conversores tensao-corrente
- Filtros gm-C

### Fontes Controladas por Corrente

#### CCVS - Fonte de Tensao Controlada por Corrente (H)

```spice
* Sintaxe: Hnome no+ no- Vsense ganho_transresistencia

* Fonte de corrente para medir
Vsense in node2 DC 0

* Transresistencia
H1 out 0 Vsense 1k          ; Vout = 1k * Iin
```

**Aplicacoes:**
- Transimpedancia
- Conversores corrente-tensao
- Sensores de corrente

#### CCCS - Fonte de Corrente Controlada por Corrente (F)

```spice
* Sintaxe: Fnome no+ no- Vsense ganho_corrente

* Fonte de corrente para medir
Vsense in node2 DC 0

* Espelho de corrente ideal
F1 out 0 Vsense 1           ; Iout = Iin

* Amplificador de corrente
F2 out 0 Vsense 10          ; Iout = 10 * Iin
```

**Aplicacoes:**
- Espelhos de corrente ideais
- Amplificadores de corrente
- Multiplicadores de corrente

### Exemplo - Amplificador Diferencial Ideal

```spice
* Amp-op ideal usando fontes controladas

.subckt AMPOP_IDEAL inp inn out vcc vee
  * Resistencia de entrada infinita (implicit)
  * Ganho diferencial muito alto
  Edif out 0 inp inn 1MEG

  * Limitadores de saida
  Dlim_p out vcc DLIM
  Dlim_n vee out DLIM
  .model DLIM D(IS=1e-14)

  * Resistencia de saida baixa
  Rout out 0 0.01
.ends

* Usar o amp-op
Vin1 inp 0 AC 1
Vin2 inn 0 DC 0
Vcc vcc 0 DC 15
Vee vee 0 DC -15

X1 inp inn out vcc vee AMPOP_IDEAL
Rload out 0 10k

.ac dec 100 1 1MEG

.control
  run
  plot db(v(out)) phase(v(out))
.endc

.end
```

### Exemplo - Conversor Howland (Fonte de Corrente)

```spice
* Fonte de corrente controlada por tensao usando amp-op

* Amp-op ideal
.subckt OPAMP in+ in- out
  Rin in+ in- 10MEG
  Eamp out 0 in+ in- 100k
  Rout out 0 10
.ends

* Circuito Howland
Vin ctrl 0 DC 1
R1 ctrl n1 10k
R2 n1 out 10k
R3 out n2 10k
R4 n2 0 10k
Rload out 0 1k

X1 n1 n2 out OPAMP

.dc Vin 0 5 0.1

.control
  run
  plot i(Rload)
  * Corrente deve ser constante independente da carga
.endc

.end
```

### Exemplo - Girador (Simula Indutor com Capacitor)

```spice
* Girador - converte capacitor em indutor equivalente

* Dois amp-ops ideais
.subckt OPAMP in+ in- out
  E1 out 0 in+ in- 100k
  Rout out 0 1
.ends

Vin in 0 AC 1

* Girador
R1 in n1 1k
X1 n1 0 n2 OPAMP
R2 n2 n3 1k
C1 n3 0 100n
X2 n3 0 out OPAMP
R3 out 0 1k

* Leq = R1 * R2 * C1 = 1k * 1k * 100n = 100mH

.ac dec 100 10 10k

.control
  run
  plot db(v(out)) phase(v(out))
.endc

.end
```

### Tabela Resumo - Fontes Controladas

| Elemento | Nome | Controle | Saida | Parametro | Unidade |
|----------|------|----------|-------|-----------|---------|
| **E** | VCVS | Tensao | Tensao | Ganho de tensao | V/V |
| **F** | CCCS | Corrente | Corrente | Ganho de corrente | A/A |
| **G** | VCCS | Tensao | Corrente | Transcondutancia | A/V (S) |
| **H** | CCVS | Corrente | Tensao | Transresistencia | V/A (Ω) |

### Tabela Resumo - Chaves

| Elemento | Nome | Controle | Modelo | Parametros Principais |
|----------|------|----------|--------|---------------------|
| **S** | Chave de tensao | Tensao | SW | Ron, Roff, Vt, Vh |
| **W** | Chave de corrente | Corrente | CSW | Ron, Roff, It, Ih |

### Aplicacoes Praticas

**Chaves:**
- Timers (555, monostaveis)
- Conversores DC-DC (Buck, Boost)
- Multiplexadores
- Sample-and-hold

**Fontes Controladas:**
- Modelagem de amp-ops ideais
- Giradores e conversores de impedancia
- Amplificadores de instrumentacao
- Fontes de corrente programaveis
- Filtros ativos

---

## 15. Modo Batch e Armadilhas Comuns

### Modo Batch vs Modo Interativo

O ngspice pode ser executado de duas formas:

**Modo Interativo:**
```bash
ngspice circuito.cir
# Abre interface grafica com plots
```

**Modo Batch:**
```bash
ngspice -b circuito.cir -o saida.log
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

## 16. Referencias de Dispositivos e Hierarquia

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

## 17. Modo Interativo Avancado

O ngspice oferece um modo interativo poderoso que permite controlar simulacoes, explorar circuitos e depurar problemas em tempo real.

### Iniciando o Modo Interativo

```bash
# Iniciar ngspice sem arquivo
ngspice

# Iniciar com arquivo de circuito
ngspice circuito.cir

# Iniciar e executar comandos
ngspice -i circuito.cir
```

### Carregando Circuitos

```
ngspice 1 -> source circuito.cir
Circuit: * Titulo do Circuito

ngspice 2 -> listing
  * Lista o circuito carregado
```

**Comandos de arquivo:**
- `source arquivo.cir` - Carrega circuito
- `listing` - Mostra netlist do circuito
- `listing deck` - Mostra netlist completo com expansao de subcircuitos
- `listing logical` - Mostra estrutura logica

### Executando Analises Interativamente

```
ngspice 1 -> source amplificador.cir

ngspice 2 -> op
Operating point analysis...

ngspice 3 -> print all
  * Mostra todas as tensoes e correntes

ngspice 4 -> print v(out)
v(out) = 2.456000e+00

ngspice 5 -> tran 1u 10m
Transient analysis...

ngspice 6 -> plot v(in) v(out)
  * Abre janela grafica

ngspice 7 -> ac dec 100 1 1meg
AC analysis...

ngspice 8 -> plot db(v(out))
```

### Comandos de Informacao

```
ngspice 1 -> display
  * Lista todos os vetores (variaveis) disponiveis

ngspice 2 -> print v(base) v(coll) @Q1[ic]
v(base) = 6.500000e-01
v(coll) = 5.234000e+00
q1[ic] = 1.234000e-03

ngspice 3 -> show Q1
  * Mostra parametros do transistor Q1

ngspice 4 -> showmod BC548
  * Mostra parametros do modelo BC548

ngspice 5 -> where
  * Mostra o circuito atual (plot atual)
```

### Modificando Circuitos Interativamente

```
ngspice 1 -> alter R1 = 2.2k
  * Muda valor de R1

ngspice 2 -> alter V1 DC 15
  * Muda tensao de V1

ngspice 3 -> alter @Q1[bf] = 300
  * Muda beta do transistor

ngspice 4 -> op
  * Recalcula ponto de operacao

ngspice 5 -> print v(out)
v(out) = 3.124000e+00
```

### Variaveis e Calculos

```
ngspice 1 -> tran 1u 10m

ngspice 2 -> let ganho = v(out) / v(in)

ngspice 3 -> plot ganho

ngspice 4 -> let ganho_db = db(ganho)

ngspice 5 -> print mean(ganho_db)
mean(ganho_db) = 2.034000e+01

ngspice 6 -> let potencia = v(out) * i(R1)

ngspice 7 -> plot potencia
```

### Salvando e Carregando Dados

```
ngspice 1 -> tran 1u 10m

ngspice 2 -> write dados.raw
  * Salva dados em formato binario

ngspice 3 -> wrdata saida.txt v(in) v(out)
  * Salva em formato texto

ngspice 4 -> quit
  * Sai do ngspice

# Em uma nova sessao
$ ngspice

ngspice 1 -> load dados.raw
  * Carrega dados salvos

ngspice 2 -> display
  * Mostra vetores carregados

ngspice 3 -> plot v(out)
```

### Controle de Plots

Quando ha multiplas analises, ngspice cria multiplos "plots":

```
ngspice 1 -> source circuito.cir

ngspice 2 -> op
ngspice 3 -> ac dec 100 1 1meg
ngspice 4 -> tran 1u 10m

ngspice 5 -> setplot
Current plots:
 new
 op1
 ac1
 tran1

ngspice 6 -> setplot ac1
  * Muda para plot AC

ngspice 7 -> plot db(v(out))

ngspice 8 -> setplot tran1
  * Muda para plot transiente

ngspice 9 -> plot v(out)
```

### Depuracao Avancada

```
ngspice 1 -> source circuito.cir

ngspice 2 -> listing
  * Verifica netlist

ngspice 3 -> show all
  * Mostra todos os dispositivos

ngspice 4 -> op

ngspice 5 -> show Q1
  * Parametros DC do transistor
  model: bc548
  ib = 1.234e-05
  ic = 2.468e-03
  vbe = 6.500e-01
  vce = 5.234e+00

ngspice 6 -> print @Q1[gm]
  * Transcondutancia

ngspice 7 -> print @Q1[beta]
  * Beta (hfe)
```

### Opcoes de Simulacao

```
ngspice 1 -> set
  * Mostra todas as opcoes

ngspice 2 -> set hcopydevtype = png

ngspice 3 -> set color0 = white
  * Muda cor de fundo

ngspice 4 -> option
  * Mostra opcoes de simulacao

ngspice 5 -> set reltol = 1e-4
  * Muda tolerancia relativa
```

### Script de Inicializacao (.spiceinit)

Crie arquivo `~/.spiceinit` (Linux/Mac) ou `spice.rc` (Windows) para configuracao automatica:

```spice
* Arquivo .spiceinit - configuracoes do ngspice

* Opcoes de simulacao
set num_threads=4
set reltol=1e-4

* Opcoes de interface
set color0=white
set color1=black
set hcopydevtype=png

* Alias para comandos comuns
alias ls listing
alias r run
alias q quit
alias disp display

* Mensagem de boas-vindas
echo "ngspice configurado!"
```

### Comandos de Ajuda

```
ngspice 1 -> help
  * Lista todos os comandos

ngspice 2 -> help tran
  * Ajuda sobre comando especifico

ngspice 3 -> help plot
  * Ajuda sobre plotagem
```

### Exemplo de Sessao Interativa Completa

```
$ ngspice

ngspice 1 -> source amplificador.cir
Circuit: * Amplificador Emissor Comum

ngspice 2 -> listing
  * Verifica o circuito

ngspice 3 -> op
Operating point analysis...

ngspice 4 -> print v(base) v(coll) @Q1[ic]
v(base) = 6.500000e-01
v(coll) = 5.234000e+00
q1[ic] = 1.234000e-03

ngspice 5 -> echo "Ic = " @Q1[ic] " A"
Ic = 1.234000e-03 A

ngspice 6 -> ac dec 100 10 10meg
AC analysis...

ngspice 7 -> let ganho_db = db(v(out)/v(in))

ngspice 8 -> plot ganho_db

ngspice 9 -> meas ac bw_3db when ganho_db=ganho_db[1]-3
bw_3db = 1.234567e+05

ngspice 10 -> echo "Largura de banda: " $&bw_3db " Hz"
Largura de banda: 1.234567e+05 Hz

ngspice 11 -> tran 1u 10m

ngspice 12 -> plot v(in) v(out)

ngspice 13 -> hardcopy saida.png v(out)

ngspice 14 -> wrdata dados.csv time v(in) v(out)

ngspice 15 -> quit
```

### Comandos Uteis - Resumo

| Comando | Descricao |
|---------|-----------|
| `source arquivo.cir` | Carrega circuito |
| `listing` | Mostra netlist |
| `op`, `ac`, `tran`, `dc` | Executa analises |
| `run` | Executa analises definidas no circuito |
| `print variavel` | Imprime valor |
| `plot variavel` | Plota grafico |
| `display` | Lista variaveis disponiveis |
| `show dispositivo` | Mostra parametros de dispositivo |
| `showmod modelo` | Mostra parametros de modelo |
| `alter componente = valor` | Modifica componente |
| `let var = expressao` | Cria variavel |
| `meas` | Faz medicoes |
| `write arquivo.raw` | Salva dados binarios |
| `wrdata arquivo.txt` | Salva dados texto |
| `load arquivo.raw` | Carrega dados salvos |
| `setplot` | Lista/muda plots |
| `set opcao = valor` | Define opcao |
| `help` | Ajuda |
| `quit` | Sai |

### Vantagens do Modo Interativo

1. **Depuracao rapida**: Testar mudancas sem editar arquivo
2. **Exploracao**: Investigar circuito interativamente
3. **Analise incremental**: Executar apenas analises necessarias
4. **Aprendizado**: Experimentar comandos e ver resultados imediatos
5. **Prototipagem**: Ajustar valores ate obter resultado desejado

### Modo Interativo vs Modo Batch

**Use Modo Interativo quando:**
- Depurando circuito
- Aprendendo ngspice
- Ajustando valores experimentalmente
- Explorando resultados interativamente

**Use Modo Batch quando:**
- Simulacoes automatizadas
- Scripts de teste
- Integraçao com outras ferramentas
- Simulacoes longas sem supervisao

---

## 18. Verilog-A e OpenVAF - Modelos Customizados

Verilog-A permite criar modelos comportamentais customizados de dispositivos eletrônicos usando uma linguagem de descrição de hardware (HDL). OpenVAF compila esses modelos para uso no ngspice.

### O que e Verilog-A?

**Verilog-A** é uma linguagem para modelagem analógica que permite:
- Criar modelos de dispositivos customizados
- Implementar equações físicas complexas
- Modelar efeitos não disponíveis em SPICE padrão
- Reutilizar modelos em diferentes simuladores

**OpenVAF** é um compilador open-source que transforma código Verilog-A em módulos OSDI (Open Simulation Device Interface) carregáveis pelo ngspice.

### Instalacao do OpenVAF

#### Linux
```bash
# Baixar release
wget https://github.com/pascalkuthe/OpenVAF/releases/download/v23.5.0/openvaf_23.5.0_linux_amd64.tar.gz

# Extrair e instalar
tar -xzf openvaf_23.5.0_linux_amd64.tar.gz
sudo mv openvaf /usr/local/bin/

# Verificar
openvaf --version
```

#### Windows/Mac
Baixar binário de: https://openvaf.semimod.de/

### Estrutura Basica de um Modelo

```verilog
// resistor_simples.va
`include "constants.vams"
`include "disciplines.vams"

module resistor_simples(p, n);
    // Declaracao dos terminais
    inout p, n;
    electrical p, n;

    // Parametros do modelo
    parameter real R = 1k from (0:inf);

    analog begin
        // Lei de Ohm: I = V/R
        I(p, n) <+ V(p, n) / R;
    end
endmodule
```

### Compilando e Usando

```bash
# 1. Compilar modelo Verilog-A
openvaf resistor_simples.va
# Gera: resistor_simples.osdi

# 2. Criar circuito SPICE
cat > teste.cir << EOF
.title Teste Resistor Verilog-A

* Carregar modelo compilado
.pre_osdi resistor_simples.osdi

* Usar o modelo
Vin in 0 DC 5
R1 in out resistor_simples R=1k
Rload out 0 1k

.op

.control
  run
  print v(out)
.endc

.end
EOF

# 3. Executar simulacao
ngspice teste.cir
```

### Exemplo 1 - Resistor Nao-Linear

Modelo com resistência dependente da tensão: R(V) = R₀ × (1 + α×V²)

```verilog
// resistor_naolinear.va
`include "constants.vams"
`include "disciplines.vams"

module resistor_naolinear(p, n);
    inout p, n;
    electrical p, n;

    // Parametros
    parameter real R0 = 1k from (0:inf);
    parameter real alpha = 0.001 from [0:inf);

    // Variaveis
    real R;
    real V;

    analog begin
        V = V(p, n);
        R = R0 * (1 + alpha * V * V);
        I(p, n) <+ V / R;
    end
endmodule
```

**Circuito de teste:**
```spice
.title Teste Resistor Nao-Linear

.pre_osdi resistor_naolinear.osdi

Vin in 0 DC 0
Rnl in out resistor_naolinear R0=1k alpha=0.001
Rload out 0 10k

.dc Vin -10 10 0.1

.control
  run
  let I = v(out) / 10k
  let R = abs((v(in) - v(out)) / I)
  plot R vs v(in) title 'Resistencia vs Tensao'
.endc

.end
```

### Exemplo 2 - Diodo com Equacao de Shockley

```verilog
// diodo_simples.va
`include "constants.vams"
`include "disciplines.vams"

module diodo_simples(anode, cathode);
    inout anode, cathode;
    electrical anode, cathode;

    parameter real Is = 1e-14 from (0:inf);
    parameter real n = 1.0 from (0:inf);
    parameter real Rs = 0 from [0:inf);

    real Vd, Id, Vt;

    analog begin
        // Tensao termica kT/q
        Vt = $vt($temperature);

        // Tensao no diodo
        Vd = V(anode, cathode) - I(anode, cathode) * Rs;

        // Equacao de Shockley com limexp (evita overflow)
        Id = Is * (limexp(Vd / (n * Vt)) - 1);

        I(anode, cathode) <+ Id;
    end
endmodule
```

**Uso:**
```spice
.pre_osdi diodo_simples.osdi

Vin in 0 SIN(0 5 60)
D1 in out diodo_simples Is=1e-14 n=1.0
Rload out 0 1k

.tran 1m 50m
```

### Exemplo 3 - Capacitor Variavel (Varactor)

```verilog
// varactor.va
`include "constants.vams"
`include "disciplines.vams"

module varactor(plus, minus);
    inout plus, minus;
    electrical plus, minus;

    parameter real C0 = 10p from (0:inf);
    parameter real Vj = 0.7 from (0:inf);
    parameter real m = 0.5 from (0:1];

    real V, C;

    analog begin
        V = V(plus, minus);

        // Modelo de capacitancia variavel
        if (V >= 0)
            C = C0 * (1 + m*V/Vj);
        else
            C = C0 / pow(1 - V/Vj, m);

        // I = C * dV/dt
        I(plus, minus) <+ C * ddt(V);
    end
endmodule
```

### Operadores e Funcoes Importantes

#### Operadores de Contribuicao

```verilog
// Contribuicao aditiva (correntes se somam)
I(p, n) <+ expressao;

// Contribuicao capacitiva (derivada)
I(p, n) <+ C * ddt(V(p, n));

// Contribuicao indutiva (integral)
V(p, n) <+ L * ddt(I(p, n));
```

#### Funcoes do Sistema

| Funcao | Descricao |
|--------|-----------|
| `V(n1, n2)` | Tensao entre nos |
| `I(n1, n2)` | Corrente através do ramo |
| `ddt(x)` | Derivada temporal (dx/dt) |
| `idt(x)` | Integral temporal |
| `$temperature` | Temperatura de simulacao (K) |
| `$vt(T)` | Tensao termica kT/q |
| `limexp(x)` | Exponencial limitada |
| `abs(x)` | Valor absoluto |
| `pow(x, y)` | Potencia (x^y) |
| `sqrt(x)` | Raiz quadrada |
| `ln(x)`, `log(x)` | Logaritmos |
| `sin(x)`, `cos(x)` | Trigonometricas |

#### Funcoes de Analise

```verilog
// Ruido termico de resistor
I(p, n) <+ white_noise(4 * `P_K * $temperature / R);

// Ruido flicker (1/f)
I(p, n) <+ flicker_noise(Kf * pow(I, af), af);
```

### Includes Padrao

```verilog
// Constantes fisicas
`include "constants.vams"
// Define: `P_Q (carga eletron), `P_K (Boltzmann), etc

// Disciplinas eletricas
`include "disciplines.vams"
// Define: electrical, voltage, current, etc
```

### Parametros

```verilog
// Parametro basico
parameter real R = 1k;

// Com limites
parameter real R = 1k from (0:inf);     // R > 0
parameter real C = 10p from [0:inf);    // C >= 0

// Com unidades
parameter real R = 1k from (0:inf) (* units = "Ohms" *);

// Parametro inteiro
parameter integer N = 10 from [1:100];
```

### Variaveis

```verilog
// Variaveis analogicas
real V, I, R;
integer count;

analog begin
    V = V(p, n);
    I = V / R;
end
```

### Controle de Fluxo

```verilog
analog begin
    // Condicional
    if (V > 0)
        I = V / R1;
    else
        I = V / R2;

    // Case
    case (modo)
        0: I = 0;
        1: I = V / R;
        default: I = V / (R * 2);
    endcase
end
```

### Exemplo Completo - Modelo de MOSFET Simplificado

```verilog
// mosfet_simples.va
`include "constants.vams"
`include "disciplines.vams"

module mosfet_nmos(drain, gate, source, bulk);
    inout drain, gate, source, bulk;
    electrical drain, gate, source, bulk;

    // Parametros
    parameter real W = 10u from (0:inf);
    parameter real L = 1u from (0:inf);
    parameter real Vth = 0.7 from (-inf:inf);
    parameter real Kp = 110u from (0:inf);
    parameter real lambda = 0.04 from [0:inf);

    // Variaveis
    real Vgs, Vds, Vgd, Vbs;
    real Id;
    real beta;

    analog begin
        // Tensoes
        Vgs = V(gate, source);
        Vds = V(drain, source);
        Vgd = V(gate, drain);
        Vbs = V(bulk, source);

        // Transcondutancia
        beta = Kp * W / L;

        // Modelo simplificado
        if (Vgs < Vth) begin
            // Regiao de corte
            Id = 0;
        end else if (Vds < (Vgs - Vth)) begin
            // Regiao triodo
            Id = beta * ((Vgs - Vth) * Vds - 0.5 * Vds * Vds);
        end else begin
            // Regiao de saturacao
            Id = 0.5 * beta * pow(Vgs - Vth, 2) * (1 + lambda * Vds);
        end

        // Corrente drain-source
        I(drain, source) <+ Id;

        // Capacitancias parasitas (simplificado)
        I(gate, source) <+ ddt(1e-15 * V(gate, source));
        I(gate, drain) <+ ddt(1e-15 * V(gate, drain));
    end
endmodule
```

### Boas Praticas

#### 1. Use limexp() para exponenciais

```verilog
// RUIM - pode dar overflow
I <+ Is * (exp(V/Vt) - 1);

// BOM - limitado automaticamente
I <+ Is * (limexp(V/Vt) - 1);
```

#### 2. Adicione pequena condutancia para convergencia

```verilog
// Evita matriz singular
I(p, n) <+ V(p, n) / 1e12;  // Gmin = 1pS
```

#### 3. Limite valores extremos

```verilog
if (C < 1e-18) C = 1e-18;   // Cmin
if (C > 1e-9) C = 1e-9;     // Cmax
```

#### 4. Use @(initial_step) para inicializacao

```verilog
analog begin
    @(initial_step) begin
        // Codigo executado apenas no inicio
        var_init = valor_inicial;
    end

    // Codigo normal
    I(p, n) <+ expressao;
end
```

### Compilacao e Debug

```bash
# Compilar com mensagens detalhadas
openvaf --verbose modelo.va

# Verificar apenas (nao gera .osdi)
openvaf --check modelo.va

# Gerar codigo intermediario para debug
openvaf --emit=llvm modelo.va
```

### Exemplo de Sessao Completa

```bash
# 1. Criar modelo
cat > resistor.va << 'EOF'
`include "disciplines.vams"
module resistor(p, n);
    inout p, n;
    electrical p, n;
    parameter real R = 1k;
    analog I(p, n) <+ V(p, n) / R;
endmodule
EOF

# 2. Compilar
openvaf resistor.va

# 3. Criar circuito
cat > teste.cir << 'EOF'
Teste Resistor Verilog-A
.pre_osdi resistor.osdi
Vin in 0 DC 5
R1 in out resistor R=2.2k
Rload out 0 1k
.op
.control
  run
  print v(out)
.endc
.end
EOF

# 4. Simular
ngspice -b teste.cir
```

### Vantagens do Verilog-A

1. **Portabilidade**: Mesmo modelo funciona em diferentes simuladores
2. **Expressividade**: Sintaxe matemática clara e direta
3. **Modularidade**: Modelos reutilizáveis
4. **Precisão**: Pode incluir efeitos físicos complexos
5. **Open-Source**: OpenVAF é gratuito e código aberto

### Limitacoes

1. **Performance**: Mais lento que modelos SPICE nativos compilados
2. **Convergencia**: Modelos mal escritos podem causar problemas
3. **Debug**: Erros podem ser difíceis de rastrear
4. **Aprendizado**: Curva de aprendizado mais íngreme

### Recursos Adicionais

**Exemplos incluídos em:** `circuits/17_eletricidade_vlsi/`
- `resistor_naolinear.va` - Resistor não-linear
- `diodo_simples.va` - Diodo com Shockley
- `varactor.va` - Capacitor variável
- `teste_*.cir` - Circuitos de teste
- `README_VERILOG_A.md` - Guia detalhado

**Links úteis:**
- [OpenVAF](https://openvaf.semimod.de/)
- [Verilog-AMS Reference](http://www.verilog-ams.com/)
- [Designer's Guide](https://designers-guide.org/verilog-ams/)
- [VA-Models Repository](https://github.com/Xyce/VA-Models)

### Proximo Passo

Para aprender mais:
1. Compile e teste os exemplos em `circuits/17_eletricidade_vlsi/`
2. Modifique parâmetros e observe o comportamento
3. Crie seus próprios modelos simples
4. Estude modelos complexos disponíveis online

**Dica**: Comece com modelos simples (resistor, capacitor) antes de tentar dispositivos complexos (transistores, amplificadores operacionais).

---

## Referencias Adicionais

- [ngspice User Manual](http://ngspice.sourceforge.net/docs/ngspice-manual.pdf)
- [SPICE Quick Reference - Berkeley](http://bwrcs.eecs.berkeley.edu/Classes/IcBook/SPICE/)
- [LTspice Getting Started Guide](https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html)
- [Troubleshooting Guide](troubleshooting.md) - Guia de resolucao de problemas comuns
- [OpenVAF Documentation](https://openvaf.semimod.de/)
- [Verilog-A Language Reference Manual](http://www.verilog-ams.com/)
- [Designer's Guide to Verilog-AMS](https://designers-guide.org/verilog-ams/)

---

*Tutorial criado para o projeto learning_ngspice*
