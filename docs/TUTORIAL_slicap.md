# Tutorial Completo: SLiCAP - Symbolic Linear Circuit Analysis Program

**Autor:** Leonardo
**Versão:** 2.0
**Data:** 2026-01-03
**Público-alvo:** Estudantes de Engenharia Eletrônica

---

## Índice

1. [Introdução](#introdução)
2. [Instalação](#instalação)
3. [Conceitos Fundamentais](#conceitos-fundamentais)
4. [Estrutura de Projeto SLiCAP](#estrutura-de-projeto-slicap)
5. [Criando Netlists SPICE](#criando-netlists-spice)
6. [Tutorial Prático: Passo a Passo](#tutorial-prático-passo-a-passo)
   - [Exemplo 1: Divisor de Tensão](#exemplo-1-divisor-de-tensão)
   - [Exemplo 2: Filtro RC Passa-Baixa](#exemplo-2-filtro-rc-passa-baixa)
   - [Exemplo 3: Amplificador JFET](#exemplo-3-amplificador-jfet-classe-a)
7. [Análise de Matrizes do Circuito (MNA)](#análise-de-matrizes-do-circuito-mna)
8. [Visualização de Funções de Transferência](#visualização-de-funções-de-transferência)
9. [Tipos de Análise Disponíveis](#tipos-de-análise-disponíveis)
10. [Projetos para Estudantes](#projetos-para-estudantes)
11. [Troubleshooting e Dicas](#troubleshooting-e-dicas)
12. [Referências](#referências)

---

## Introdução

### O que é SLiCAP?

**SLiCAP** (Symbolic Linear Circuit Analysis Program) é uma ferramenta Python para análise **simbólica e numérica** de circuitos lineares. Diferente de simuladores como ngspice que fornecem apenas resultados numéricos, SLiCAP calcula **expressões algébricas** exatas.

### Por que usar SLiCAP?

| Vantagem | Descrição |
|----------|-----------|
| **Insight matemático** | Veja as equações exatas, não apenas números |
| **Projeto otimizado** | Identifique quais componentes afetam cada característica |
| **Documentação automática** | Gere relatórios HTML/LaTeX profissionais |
| **Ensino** | Excelente para aprender teoria de circuitos |
| **Verificação** | Confirme resultados de simulações numéricas |

### SLiCAP vs ngspice

```
┌─────────────────┬──────────────────┬──────────────────┐
│ Característica  │ SLiCAP           │ ngspice          │
├─────────────────┼──────────────────┼──────────────────┤
│ Análise         │ Simbólica        │ Numérica         │
│ Saída           │ H(s) = 1/(RC*s)  │ Vout = 0.707V    │
│ Não-linearidade │ ❌ Não suporta   │ ✅ Suporta       │
│ Documentação    │ ✅ Automática    │ ❌ Manual        │
│ Velocidade      │ ⚠️ Lenta (>50 nós)│ ✅ Rápida        │
│ Uso ideal       │ Entendimento     │ Validação final  │
└─────────────────┴──────────────────┴──────────────────┘
```

**Estratégia recomendada:** Use SLiCAP para projeto e entendimento, ngspice para validação final.

### Limitações Importantes

⚠️ **SLiCAP é apenas para circuitos LINEARES:**
- ✅ Resistores, capacitores, indutores
- ✅ Amplificadores operacionais ideais
- ✅ Transistores em **pequenos sinais** (modelo linearizado)
- ❌ Diodos (não-linear)
- ❌ Transistores em grande sinal
- ❌ Análise transiente não-linear

---

## Instalação

### Pré-requisitos

- **Python:** 3.8 ou superior
- **pip** ou **uv**: Gerenciador de pacotes Python
- **LaTeX** (opcional): Para renderização de equações em gráficos

### Instalar SLiCAP

#### Opção 1: pip

```bash
pip install SLiCAP
```

#### Opção 2: uv (recomendado para este projeto)

```bash
# Instalar uv se necessário
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar SLiCAP
uv pip install SLiCAP
```

### Verificar Instalação

```bash
python -c "import SLiCAP; print(f'SLiCAP versão: {SLiCAP.__version__}')"
```

**Saída esperada:**
```
SLiCAP versão: 3.x.x
```

### Instalar LaTeX (Opcional)

Para gráficos com equações renderizadas:

**Ubuntu/Debian:**
```bash
sudo apt install texlive texlive-latex-extra dvipng
```

**macOS:**
```bash
brew install --cask mactex
```

**Windows:**
- Baixar MiKTeX: https://miktex.org/download

---

## Conceitos Fundamentais

### 1. Análise Nodal Modificada (MNA)

SLiCAP usa **Modified Nodal Analysis (MNA)** para montar as equações do circuito em forma matricial:

```
┌─────┬─────┐ ┌───┐   ┌───┐
│  M  │     │ │Dv │ = │Iv │
└─────┴─────┘ └───┘   └───┘
```

Onde:
- **M**: Matriz MNA (system matrix)
- **Dv**: Vetor de variáveis dependentes (tensões nodais e correntes de ramo)
- **Iv**: Vetor de variáveis independentes (fontes)

**Exemplo para um divisor de tensão:**

```
M = │ 0      1        0      │
    │ 1     1/R1    -1/R1    │
    │ 0    -1/R1   1/R1+1/R2 │

Dv = │ I_V1  │  (corrente na fonte)
     │ V_in  │  (tensão de entrada)
     │ V_out │  (tensão de saída)

Iv = │ V_in │  (valor da fonte)
     │  0   │
     │  0   │
```

### 2. Análise Laplace

SLiCAP trabalha no domínio de Laplace (variável complexa `s`), permitindo análise simbólica em frequência:

```
H(s) = Vout(s) / Vin(s)
```

**Substituições importantes:**
- **DC (s = 0):** Capacitores = circuito aberto, Indutores = curto-circuito
- **AC (s = jω):** Análise em frequência
- **Polos e zeros:** Raízes do denominador e numerador de H(s)

**Exemplo RC:**
```
H(s) = 1 / (1 + R*C*s)
```

### 3. Funções de Transferência

SLiCAP pode calcular diversos tipos:

- **Ganho de tensão:** `V_out / V_in`
- **Ganho de corrente:** `I_out / I_in`
- **Transimpedância:** `V_out / I_in`
- **Transadmitância:** `I_out / V_in`
- **Impedância:** `V / I`

### 4. Pequenos Sinais

Para transistores (BJT, JFET, MOSFET), SLiCAP usa **modelos de pequenos sinais**:

**JFET (modelo J):**
- `gm`: Transcondutância (S)
- `go`: Condutância de saída (S)
- `cgs`: Capacitância gate-source (F)
- `cdg`: Capacitância drain-gate (F)

Esses parâmetros são calculados a partir do ponto de operação DC (que deve ser calculado separadamente).

---

## Estrutura de Projeto SLiCAP

### Estrutura de Diretórios Recomendada

```
meu_projeto/
├── cir/                    # Netlists SPICE (.cir)
│   ├── circuito1.cir
│   └── circuito2.cir
├── lib/                    # Bibliotecas de modelos (opcional)
│   └── meus_modelos.lib
├── img/                    # Imagens e esquemáticos
│   └── schematic.svg
├── html/                   # Saída HTML (gerado automaticamente)
├── tex/                    # Saída LaTeX (gerado automaticamente)
├── csv/                    # Dados CSV (gerado automaticamente)
├── SLiCAP.ini             # Configuração do projeto
├── analyze_circuit.py      # Script de análise
└── README.md              # Documentação
```

### Inicialização do Projeto

Todo script SLiCAP começa com:

```python
import SLiCAP as sl

# Inicializar projeto
prj = sl.initProject("Nome do Projeto")
```

Isso cria automaticamente a estrutura de diretórios necessária.

---

## Criando Netlists SPICE

### Sintaxe Básica SPICE para SLiCAP

**Estrutura geral:**

```spice
"Título do Circuito"
* Comentários começam com *

* Componentes passivos
R<nome> <nó+> <nó-> <valor ou {parâmetro}>
C<nome> <nó+> <nó-> <valor ou {parâmetro}>
L<nome> <nó+> <nó-> <valor ou {parâmetro}>

* Fontes
V<nome> <nó+> <nó-> <valor ou {parâmetro}>
I<nome> <nó+> <nó-> <valor ou {parâmetro}>

* Fontes controladas
E<nome> <nó+ out> <nó- out> <nó+ ctrl> <nó- ctrl> <ganho>  ; VCVS
G<nome> <nó+ out> <nó- out> <nó+ ctrl> <nó- ctrl> <ganho>  ; VCCS

* JFET (modelo de pequenos sinais)
J<nome> <drain> <gate> <source> <modelo>
.model <modelo> J gm={gm} go={go} cgs={cgs} cdg={cdg}

.end
```

### Convenções Importantes

1. **Nó de referência (terra):** Sempre use `0`
2. **Nomes de nós:** Use nomes descritivos (`input`, `output`, `drain`, etc.)
3. **Primeira linha:** Deve ser o título (entre aspas)
4. **Última linha:** Deve ser `.end`
5. **Parâmetros:** Use `{nome_parametro}` para valores que serão definidos no Python
6. **Comentários:** Use `*` no início da linha

### Unidades SPICE

SLiCAP/SPICE usa unidades SI por padrão:

| Sufixo | Multiplicador | Exemplo |
|--------|---------------|---------|
| `T` | 10¹² | 1T = 1e12 |
| `G` | 10⁹ | 1G = 1e9 |
| `Meg` | 10⁶ | 1Meg = 1e6 |
| `k` | 10³ | 1k = 1000 |
| `m` | 10⁻³ | 1m = 0.001 |
| `u` | 10⁻⁶ | 1u = 1e-6 |
| `n` | 10⁻⁹ | 1n = 1e-9 |
| `p` | 10⁻¹² | 1p = 1e-12 |
| `f` | 10⁻¹⁵ | 1f = 1e-15 |

### Exemplos de Netlists

#### Divisor de Tensão

```spice
"Voltage Divider Circuit"
* Simple voltage divider with 2 resistors

V1 in 0 {V_in}
R1 in out {R1}
R2 out 0 {R2}

.end
```

#### Filtro RC Passa-Baixa

```spice
"RC Low Pass Filter"
* First-order RC low pass filter
* Cutoff frequency fc = 1/(2*pi*R*C)

V1 in 0 {V_in}
R1 in out {R}
C1 out 0 {C}

.end
```

#### Amplificador JFET

```spice
"Self-Biased JFET Class-A Amplifier"
* N-channel JFET common-source amplifier

* Input signal
V_in in 0 {V_sig}

* Input coupling capacitor
C_in in gate {C_in}

* Gate bias resistor
R_g gate 0 {R_g}

* JFET (N-channel)
J1 drain gate source jfet_model

* Drain resistor
R_d vdd drain {R_d}

* Source resistor (sets bias point)
R_s source 0 {R_s}

* Source bypass capacitor
C_s source 0 {C_s}

* Output coupling capacitor
C_out drain out {C_out}

* Load resistor
R_load out 0 {R_load}

* Power supply
V_dd vdd 0 {V_DD}

* JFET small-signal model
.model jfet_model J gm={gm} go={go} cgs={cgs} cdg={cdg}

.end
```

---

## Tutorial Prático: Passo a Passo

### Exemplo 1: Divisor de Tensão

Um divisor de tensão é o circuito mais básico. Vamos analisá-lo completamente.

#### Teoria

```
      V_in
         |
        R1
         |
    out o--------> V_out
         |
        R2
         |
        GND
```

**Fórmula:**
```
V_out = V_in × R2/(R1 + R2)
```

#### Passo 1: Criar Diretório do Projeto

```bash
mkdir ~/voltage_divider_project
cd ~/voltage_divider_project
```

#### Passo 2: Criar Netlist SPICE

Crie `cir/voltage_divider.cir`:

```spice
"Voltage Divider Circuit"
* Simple voltage divider with 2 resistors
* Output voltage = Vin * R2/(R1+R2)

V1 in 0 {V_in}
R1 in out {R1}
R2 out 0 {R2}

.end
```

#### Passo 3: Script Python de Análise

Crie `analyze_divider.py`:

```python
#!/usr/bin/env python3
"""
Análise completa de divisor de tensão
"""

import SLiCAP as sl
import numpy as np
import matplotlib.pyplot as plt

# Inicializar projeto
print("="*70)
print("ANÁLISE DE DIVISOR DE TENSÃO")
print("="*70)

prj = sl.initProject("Voltage Divider Analysis")

# Carregar circuito
cir = sl.makeCircuit("voltage_divider.cir")

print(f"\nCircuito: {cir.title}")
print(f"Nós: {cir.nodes}")
print(f"Elementos: {list(cir.elements.keys())}")

# Definir parâmetros
R1_val = 1000   # 1kΩ
R2_val = 2000   # 2kΩ
V_in_val = 10   # 10V

cir.defPar('R1', R1_val)
cir.defPar('R2', R2_val)
cir.defPar('V_in', V_in_val)

print(f"\nParâmetros:")
print(f"  R1 = {R1_val} Ω")
print(f"  R2 = {R2_val} Ω")
print(f"  V_in = {V_in_val} V")

# Análise simbólica
print("\n" + "-"*70)
print("ANÁLISE SIMBÓLICA")
print("-"*70)

result = sl.doLaplace(cir, source='V1', detector='V_out')
H = result.laplace

print(f"\nFunção de transferência H(s) = V_out/V_in:")
print(f"  {H}")

print(f"\nNumerador: {result.numer}")
print(f"\nDenominador: {result.denom}")

# Análise numérica
print("\n" + "-"*70)
print("ANÁLISE NUMÉRICA")
print("-"*70)

# Substituir valores
dc_gain = H.subs([('R1', R1_val), ('R2', R2_val)])
v_out = V_in_val * float(dc_gain)

print(f"\nGanho DC: {float(dc_gain):.4f}")
print(f"Tensão de saída: {v_out:.4f} V")

# Verificação
v_out_formula = V_in_val * R2_val / (R1_val + R2_val)
print(f"\nVerificação (fórmula): {v_out_formula:.4f} V")
print(f"Match: {abs(v_out - v_out_formula) < 0.001} ✓")

# Análise paramétrica - varrer R2
print("\n" + "-"*70)
print("ANÁLISE PARAMÉTRICA: Variando R2")
print("-"*70)

R2_values = np.logspace(2, 4, 50)  # 100Ω a 10kΩ
v_out_values = []

for R2 in R2_values:
    gain = R2 / (R1_val + R2)
    v_out_values.append(V_in_val * gain)

# Plotar
plt.figure(figsize=(10, 6))
plt.semilogx(R2_values, v_out_values, 'b-', linewidth=2)
plt.axhline(V_in_val, color='r', linestyle='--', alpha=0.5, label='V_in')
plt.axhline(V_in_val/2, color='g', linestyle='--', alpha=0.5, label='V_in/2')
plt.axvline(R1_val, color='orange', linestyle='--', alpha=0.5, label=f'R1={R1_val}Ω')
plt.grid(True, which='both', alpha=0.3)
plt.xlabel('R2 (Ω)', fontsize=12)
plt.ylabel('V_out (V)', fontsize=12)
plt.title('Tensão de Saída vs R2', fontsize=14, fontweight='bold')
plt.legend()
plt.tight_layout()
plt.savefig('voltage_divider_sweep.png', dpi=150)
print("\n✓ Gráfico salvo: voltage_divider_sweep.png")

print("\n" + "="*70)
print("ANÁLISE COMPLETA")
print("="*70)
```

#### Passo 4: Executar

```bash
python analyze_divider.py
```

#### Resultados Esperados

```
======================================================================
ANÁLISE DE DIVISOR DE TENSÃO
======================================================================

Circuito: Voltage Divider Circuit
Nós: ['0', 'in', 'out']
Elementos: ['V1', 'R1', 'R2']

Parâmetros:
  R1 = 1000 Ω
  R2 = 2000 Ω
  V_in = 10 V

----------------------------------------------------------------------
ANÁLISE SIMBÓLICA
----------------------------------------------------------------------

Função de transferência H(s) = V_out/V_in:
  R2/(R1 + R2)

Numerador: R2

Denominador: R1 + R2

----------------------------------------------------------------------
ANÁLISE NUMÉRICA
----------------------------------------------------------------------

Ganho DC: 0.6667
Tensão de saída: 6.6667 V

Verificação (fórmula): 6.6667 V
Match: True ✓
```

#### Observações Importantes

1. **Função de transferência independente de s:** Circuito puramente resistivo não tem dependência de frequência
2. **Ganho sempre < 1:** Divisor de tensão sempre atenua
3. **Quando R2 = R1:** V_out = V_in/2
4. **Quando R2 >> R1:** V_out ≈ V_in

---

### Exemplo 2: Filtro RC Passa-Baixa

Agora vamos analisar um circuito com elementos reativos (capacitores).

#### Teoria

```
       V_in
          |
         R
          |
     out o--------> V_out
          |
         C
          |
         GND
```

**Função de transferência:**
```
H(s) = 1/(1 + sRC) = 1/(1 + s/ωc)

onde ωc = 1/(RC) é a frequência de corte angular
     fc = ωc/(2π) = 1/(2πRC) é a frequência de corte em Hz
```

**Características:**
- **Ganho DC (s=0):** H(0) = 1 (0 dB)
- **Frequência de corte:** |H(jωc)| = 1/√2 ≈ 0.707 (-3 dB)
- **Fase em fc:** ∠H(jωc) = -45°
- **Atenuação:** -20 dB/década
- **Polo:** p = -ωc = -1/(RC)

#### Passo 1: Criar Netlist

Crie `cir/rc_lowpass.cir`:

```spice
"RC Low Pass Filter"
* First-order RC low pass filter
* Cutoff frequency fc = 1/(2*pi*R*C)
* Input signal at node 'in', output at node 'out'

V1 in 0 {V_in}
R1 in out {R}
C1 out 0 {C}

.end
```

#### Passo 2: Script de Análise Completa

Crie `analyze_rc_filter.py`:

```python
#!/usr/bin/env python3
"""
Análise completa de filtro RC passa-baixa
Inclui: transfer function, Bode plots, pole-zero analysis
"""

import SLiCAP as sl
import numpy as np
import matplotlib.pyplot as plt

print("="*70)
print("FILTRO RC PASSA-BAIXA - ANÁLISE COMPLETA")
print("="*70)

# Inicializar
prj = sl.initProject("RC Low Pass Filter")
cir = sl.makeCircuit("rc_lowpass.cir")

# Parâmetros do circuito
R_value = 1000      # 1kΩ
C_value = 100e-9    # 100nF
V_in_value = 1      # 1V AC

# Calcular frequência de corte
fc = 1 / (2 * np.pi * R_value * C_value)
omega_c = 2 * np.pi * fc

print(f"\nParâmetros do Circuito:")
print(f"  R = {R_value} Ω = {R_value/1000} kΩ")
print(f"  C = {C_value*1e9} nF")
print(f"  V_in = {V_in_value} V")
print(f"\nFrequência de corte calculada:")
print(f"  fc = 1/(2πRC) = {fc:.2f} Hz")
print(f"  ωc = {omega_c:.2f} rad/s")

# Definir parâmetros
cir.defPar("R", R_value)
cir.defPar("C", C_value)
cir.defPar("V_in", V_in_value)

# Análise simbólica
print("\n" + "-"*70)
print("ANÁLISE SIMBÓLICA")
print("-"*70)

result = sl.doLaplace(cir, source='V1', detector='V_out')
H = result.laplace

print(f"\nFunção de transferência H(s):")
print(f"  {H}")
print(f"\nNumerador: {result.numer}")
print(f"Denominador: {result.denom}")

# Análise de resposta em frequência
print("\n" + "-"*70)
print("RESPOSTA EM FREQUÊNCIA")
print("-"*70)

# Frequências de teste
test_freqs = [10, 100, fc, 1000, 10000]
print(f"\n{'Freq [Hz]':<12} {'|H(jω)|':<12} {'|H| [dB]':<12} {'∠H [°]':<12}")
print("-"*70)

for f in test_freqs:
    omega = 2 * np.pi * f
    s_val = 1j * omega
    H_val = H.subs([('R', R_value), ('C', C_value), ('s', s_val)])
    H_complex = complex(H_val)

    mag = abs(H_complex)
    mag_dB = 20 * np.log10(mag)
    phase = np.angle(H_complex, deg=True)

    freq_str = f"{f:.2f}" if f == fc else f"{f:.0f}"
    print(f"{freq_str:<12} {mag:<12.4f} {mag_dB:<12.2f} {phase:<12.2f}")

# Análise de polos e zeros
print("\n" + "-"*70)
print("ANÁLISE DE POLOS E ZEROS")
print("-"*70)

pole = -1 / (R_value * C_value)
print(f"\nPolo: p = -1/(RC) = {pole:.2f} rad/s")
print(f"Polo em Hz: fp = |p|/(2π) = {abs(pole)/(2*np.pi):.2f} Hz")
print(f"Zeros: Nenhum (sem zeros finitos)")

# Gerar gráficos de Bode
print("\n" + "-"*70)
print("GERANDO DIAGRAMAS DE BODE")
print("-"*70)

# Range de frequências: 1Hz a 100kHz
freqs = np.logspace(0, 5, 500)
magnitudes = []
phases = []

for f in freqs:
    omega = 2 * np.pi * f
    s_val = 1j * omega
    H_val = H.subs([('R', R_value), ('C', C_value), ('s', s_val)])
    H_complex = complex(H_val)

    magnitudes.append(abs(H_complex))
    phases.append(np.angle(H_complex, deg=True))

magnitudes = np.array(magnitudes)
phases = np.array(phases)
magnitudes_dB = 20 * np.log10(magnitudes)

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Magnitude
ax1.semilogx(freqs, magnitudes_dB, 'b-', linewidth=2, label='|H(jω)|')
ax1.axhline(0, color='k', linestyle='-', linewidth=0.5)
ax1.axhline(-3, color='r', linestyle='--', alpha=0.7, label='-3 dB')
ax1.axvline(fc, color='g', linestyle='--', alpha=0.7, label=f'fc = {fc:.0f} Hz')
ax1.grid(True, which='both', alpha=0.3)
ax1.set_xlabel('Frequência (Hz)', fontsize=12)
ax1.set_ylabel('Magnitude (dB)', fontsize=12)
ax1.set_title('Diagrama de Bode - Magnitude', fontsize=14, fontweight='bold')
ax1.legend()
ax1.set_ylim([-60, 5])

# Fase
ax2.semilogx(freqs, phases, 'b-', linewidth=2, label='∠H(jω)')
ax2.axhline(-45, color='r', linestyle='--', alpha=0.7, label='-45°')
ax2.axvline(fc, color='g', linestyle='--', alpha=0.7, label=f'fc = {fc:.0f} Hz')
ax2.grid(True, which='both', alpha=0.3)
ax2.set_xlabel('Frequência (Hz)', fontsize=12)
ax2.set_ylabel('Fase (graus)', fontsize=12)
ax2.set_title('Diagrama de Bode - Fase', fontsize=14, fontweight='bold')
ax2.legend()
ax2.set_ylim([-100, 5])

plt.tight_layout()
plt.savefig('rc_filter_bode.png', dpi=150)
print("✓ Diagrama de Bode salvo: rc_filter_bode.png")

# Resposta ao degrau
print("\n" + "-"*70)
print("RESPOSTA AO DEGRAU")
print("-"*70)

tau = R_value * C_value  # Constante de tempo
print(f"\nConstante de tempo τ = RC = {tau*1e6:.2f} µs")
print(f"Tempo para 63.2% do valor final: t = τ = {tau*1e6:.2f} µs")
print(f"Tempo para 99% do valor final: t ≈ 5τ = {5*tau*1e6:.2f} µs")

# Calcular resposta ao degrau: v_out(t) = V_in * (1 - e^(-t/τ))
t = np.linspace(0, 5*tau, 500)
v_out_step = V_in_value * (1 - np.exp(-t/tau))

plt.figure(figsize=(10, 6))
plt.plot(t*1e6, v_out_step, 'b-', linewidth=2, label='v_out(t)')
plt.axhline(V_in_value, color='r', linestyle='--', alpha=0.5, label=f'V_in = {V_in_value}V')
plt.axhline(0.632*V_in_value, color='g', linestyle='--', alpha=0.5, label='63.2% de V_in')
plt.axvline(tau*1e6, color='orange', linestyle='--', alpha=0.5, label=f'τ = {tau*1e6:.1f}µs')
plt.grid(True, alpha=0.3)
plt.xlabel('Tempo (µs)', fontsize=12)
plt.ylabel('V_out (V)', fontsize=12)
plt.title('Resposta ao Degrau', fontsize=14, fontweight='bold')
plt.legend()
plt.tight_layout()
plt.savefig('rc_filter_step.png', dpi=150)
print("✓ Resposta ao degrau salva: rc_filter_step.png")

print("\n" + "="*70)
print("ANÁLISE COMPLETA")
print("="*70)
print(f"\nResumo do Filtro RC Passa-Baixa:")
print(f"  • Tipo: Primeira ordem")
print(f"  • Frequência de corte: {fc:.2f} Hz")
print(f"  • Ganho DC: 0 dB (1.0)")
print(f"  • Atenuação em fc: -3 dB (0.707)")
print(f"  • Fase em fc: -45°")
print(f"  • Taxa de atenuação: -20 dB/década")
print(f"  • Constante de tempo: {tau*1e6:.2f} µs")
```

#### Passo 3: Executar

```bash
python analyze_rc_filter.py
```

#### Interpretando os Resultados

**Diagrama de Bode - Magnitude:**
- Em baixas frequências (f << fc): Ganho ≈ 0 dB (passa tudo)
- Em f = fc: Ganho = -3 dB (70.7% da amplitude)
- Em altas frequências (f >> fc): Ganho cai -20 dB/década

**Diagrama de Bode - Fase:**
- Em baixas frequências: Fase ≈ 0°
- Em f = fc: Fase = -45°
- Em altas frequências: Fase → -90°

**Resposta ao Degrau:**
- O capacitor carrega exponencialmente
- Após τ = RC: v_out atinge 63.2% do valor final
- Após 5τ: v_out ≈ 99% do valor final

---

### Exemplo 3: Amplificador JFET Classe-A

Este é o exemplo mais complexo, envolvendo um transistor em configuração de pequenos sinais.

#### Teoria

**Configuração:** Common-source amplifier com auto-polarização

```
        VDD (+12V)
         |
         Rd
         |
    Cout|--- Output
         |
     Drain
         |
   JFET  Gate --- Rg (1MΩ)
         |        |
      Source    Cin
         |        |
    Rs ===Cs    Input
         |
        GND
```

**Características:**
- **Ganho de tensão:** Av ≈ -gm × Rd (negativo = inversão de fase)
- **Auto-polarização:** Rs define VGS através da corrente de dreno
- **Cs (bypass cap):** Curto-circuita Rs em AC, aumentando ganho
- **Cin e Cout:** Acoplamento AC (bloqueiam DC)

#### Passo 1: Criar Netlist

Já vimos o netlist `cir/jfet_amplifier.cir` anteriormente.

#### Passo 2: Script de Análise

Crie `analyze_jfet_amplifier.py`:

```python
#!/usr/bin/env python3
"""
Análise completa de amplificador JFET Classe-A
"""

import SLiCAP as sl
import numpy as np
import matplotlib.pyplot as plt
from sympy import latex, simplify

print("="*70)
print("AMPLIFICADOR JFET CLASSE-A - ANÁLISE COMPLETA")
print("="*70)

# Inicializar
prj = sl.initProject("JFET Amplifier Analysis")
cir = sl.makeCircuit("jfet_amplifier.cir")

print(f"\nCircuito: {cir.title}")
print(f"Nós: {cir.nodes}")
print(f"Elementos: {list(cir.elements.keys())}")

# Especificações do projeto
print("\n" + "-"*70)
print("ESPECIFICAÇÕES DO PROJETO")
print("-"*70)

V_DD = 12          # 12V supply
V_sig = 0.1        # 100mV input signal
f_signal = 100e3   # 100kHz

# Parâmetros do JFET (N-channel, ex: 2N5457)
IDSS = 10e-3       # 10mA
V_P = -3.0         # -3V pinch-off
Lambda = 0.001     # Channel-length modulation

# Ponto de polarização (escolher VGS para operação classe-A)
V_GS = -1.5
I_D = IDSS * (1 - V_GS/V_P)**2

# Parâmetros de pequenos sinais
gm = -2 * IDSS / V_P * (1 - V_GS/V_P)  # Transcondutância
go = Lambda * I_D                       # Condutância de saída
cgs = 5e-12                            # 5pF
cdg = 2e-12                            # 2pF

# Componentes do circuito
R_s = abs(V_GS) / I_D  # Resistor de source (define polarização)
R_d = 2000             # 2kΩ
R_g = 1e6              # 1MΩ
R_load = 10e3          # 10kΩ

# Tensão DC de dreno
V_DS = V_DD - I_D * R_d - abs(V_GS)

# Capacitores (escolhidos para fc_low = 10Hz)
f_low = 10
C_in = 1 / (2 * np.pi * f_low * R_g)
C_out = 1 / (2 * np.pi * f_low * R_load)
C_s = 10 / (2 * np.pi * f_low * R_s)  # 10x maior para bypass efetivo

print(f"\nAlimentação:")
print(f"  VDD = {V_DD} V")

print(f"\nPonto de operação DC:")
print(f"  VGS = {V_GS} V")
print(f"  ID = {I_D*1000:.2f} mA")
print(f"  VDS = {V_DS:.2f} V")

print(f"\nParâmetros de pequenos sinais:")
print(f"  gm = {gm*1000:.2f} mS")
print(f"  go = {go*1e6:.2f} µS")
print(f"  cgs = {cgs*1e12:.1f} pF")
print(f"  cdg = {cdg*1e12:.1f} pF")

print(f"\nResistores:")
print(f"  Rs = {R_s:.0f} Ω")
print(f"  Rd = {R_d} Ω")
print(f"  Rg = {R_g/1e6:.0f} MΩ")
print(f"  Rload = {R_load/1e3:.0f} kΩ")

print(f"\nCapacitores:")
print(f"  Cin = {C_in*1e6:.2f} µF")
print(f"  Cout = {C_out*1e6:.2f} µF")
print(f"  Cs = {C_s*1e6:.1f} µF")

print(f"\nGanho esperado (mid-band):")
A_v_expected = -gm * R_d
print(f"  Av ≈ -gm × Rd = -{gm*1000:.2f}mS × {R_d}Ω")
print(f"  Av = {A_v_expected:.2f} ({20*np.log10(abs(A_v_expected)):.2f} dB)")

# Definir parâmetros no circuito
cir.defPar('V_DD', V_DD)
cir.defPar('V_sig', V_sig)
cir.defPar('R_d', R_d)
cir.defPar('R_s', R_s)
cir.defPar('R_g', R_g)
cir.defPar('R_load', R_load)
cir.defPar('C_in', C_in)
cir.defPar('C_out', C_out)
cir.defPar('C_s', C_s)
cir.defPar('gm', gm)
cir.defPar('go', go)
cir.defPar('cgs', cgs)
cir.defPar('cdg', cdg)

# Análise da função de transferência
print("\n" + "-"*70)
print("FUNÇÃO DE TRANSFERÊNCIA")
print("-"*70)

result = sl.doLaplace(cir, source='V_in', detector='V_out')
H = result.laplace

print(f"\nFunção de transferência H(s) = V_out/V_in:")
print(f"  (expressão muito longa - simplificando...)")

# A expressão completa é muito longa, então vamos avaliar no ponto de operação
omega_signal = 2 * np.pi * f_signal
s_at_signal = 1j * omega_signal

params = [
    ('R_d', R_d), ('R_s', R_s), ('R_g', R_g), ('R_load', R_load),
    ('C_in', C_in), ('C_out', C_out), ('C_s', C_s),
    ('gm', gm), ('go', go), ('cgs', cgs), ('cdg', cdg),
    ('s', s_at_signal)
]

H_at_signal = H.subs(params)
H_complex = complex(H_at_signal)

gain_mag = abs(H_complex)
gain_dB = 20 * np.log10(gain_mag)
gain_phase = np.angle(H_complex, deg=True)

print(f"\nGanho em {f_signal/1000} kHz:")
print(f"  |Av| = {gain_mag:.2f}")
print(f"  Av [dB] = {gain_dB:.2f} dB")
print(f"  Fase = {gain_phase:.1f}°")

# Resposta em frequência
print("\n" + "-"*70)
print("RESPOSTA EM FREQUÊNCIA")
print("-"*70)

freqs = np.logspace(0, 7, 300)  # 1Hz a 10MHz
magnitudes = []
phases = []

print("Calculando resposta em frequência...")

for f in freqs:
    omega = 2 * np.pi * f
    s_val = 1j * omega

    params_freq = [
        ('R_d', R_d), ('R_s', R_s), ('R_g', R_g), ('R_load', R_load),
        ('C_in', C_in), ('C_out', C_out), ('C_s', C_s),
        ('gm', gm), ('go', go), ('cgs', cgs), ('cdg', cdg),
        ('s', s_val)
    ]

    H_val = H.subs(params_freq)
    H_c = complex(H_val)

    magnitudes.append(abs(H_c))
    phases.append(np.angle(H_c, deg=True))

magnitudes = np.array(magnitudes)
phases = np.array(phases)
magnitudes_dB = 20 * np.log10(magnitudes + 1e-10)

print("✓ Resposta calculada")

# Plot Bode
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Magnitude
ax1.semilogx(freqs, magnitudes_dB, 'b-', linewidth=2)
ax1.axhline(gain_dB, color='r', linestyle='--', alpha=0.5,
           label=f'Mid-band: {gain_dB:.1f} dB')
ax1.axhline(gain_dB - 3, color='orange', linestyle='--', alpha=0.5,
           label='-3 dB')
ax1.axvline(f_signal, color='g', linestyle='--', alpha=0.5,
           label=f'Signal: {f_signal/1e3:.0f} kHz')
ax1.grid(True, which='both', alpha=0.3)
ax1.set_xlabel('Frequência (Hz)', fontsize=12)
ax1.set_ylabel('Magnitude (dB)', fontsize=12)
ax1.set_title('Amplificador JFET - Magnitude', fontsize=14, fontweight='bold')
ax1.legend()

# Fase
ax2.semilogx(freqs, phases, 'b-', linewidth=2)
ax2.axhline(180, color='r', linestyle='--', alpha=0.5,
           label='180° (inversão)')
ax2.axvline(f_signal, color='g', linestyle='--', alpha=0.5,
           label=f'Signal: {f_signal/1e3:.0f} kHz')
ax2.grid(True, which='both', alpha=0.3)
ax2.set_xlabel('Frequência (Hz)', fontsize=12)
ax2.set_ylabel('Fase (graus)', fontsize=12)
ax2.set_title('Amplificador JFET - Fase', fontsize=14, fontweight='bold')
ax2.legend()

plt.tight_layout()
plt.savefig('jfet_amplifier_bode.png', dpi=150)
print("✓ Diagrama de Bode salvo: jfet_amplifier_bode.png")

# Ganho vs Rd
print("\n" + "-"*70)
print("ANÁLISE PARAMÉTRICA: Ganho vs Rd")
print("-"*70)

Rd_values = np.linspace(500, 5000, 50)
gains_vs_Rd = []

for Rd_val in Rd_values:
    params_rd = [
        ('R_d', Rd_val), ('R_s', R_s), ('R_g', R_g), ('R_load', R_load),
        ('C_in', C_in), ('C_out', C_out), ('C_s', C_s),
        ('gm', gm), ('go', go), ('cgs', cgs), ('cdg', cdg),
        ('s', s_at_signal)
    ]
    H_val = H.subs(params_rd)
    gains_vs_Rd.append(abs(complex(H_val)))

gains_vs_Rd = np.array(gains_vs_Rd)

plt.figure(figsize=(10, 6))
plt.plot(Rd_values, gains_vs_Rd, 'b-', linewidth=2)
plt.axvline(R_d, color='r', linestyle='--', alpha=0.7,
           label=f'Projeto: {R_d}Ω')
plt.axhline(gain_mag, color='g', linestyle='--', alpha=0.7,
           label=f'Ganho: {gain_mag:.1f}')
plt.grid(True, alpha=0.3)
plt.xlabel('Rd (Ω)', fontsize=12)
plt.ylabel('Ganho |Av|', fontsize=12)
plt.title('Ganho vs Resistor de Dreno', fontsize=14, fontweight='bold')
plt.legend()
plt.tight_layout()
plt.savefig('jfet_gain_vs_rd.png', dpi=150)
print("✓ Ganho vs Rd salvo: jfet_gain_vs_rd.png")

print("\n" + "="*70)
print("RESUMO DO AMPLIFICADOR")
print("="*70)
print(f"\n✓ Ganho de tensão: {gain_mag:.2f} ({gain_dB:.2f} dB)")
print(f"✓ Inversão de fase: {gain_phase:.0f}° (classe-A)")
print(f"✓ Frequência de sinal: {f_signal/1e3:.0f} kHz (dentro da banda)")
print(f"✓ Saída para {V_sig*1000}mV entrada: {V_sig*gain_mag*1000:.1f}mV")
print(f"\nO amplificador está funcionando corretamente!")
```

#### Passo 3: Executar

```bash
python analyze_jfet_amplifier.py
```

#### Conceitos Importantes

1. **Ponto de Operação DC:**
   - Calculado fora do SLiCAP (usando equações do JFET)
   - Define os parâmetros de pequenos sinais

2. **Modelo de Pequenos Sinais (Modelo J):**
   - `gm`: Controla o ganho de tensão
   - `go`: Resistência de saída do JFET
   - `cgs`, `cdg`: Limitam resposta em alta frequência

3. **Capacitores de Acoplamento:**
   - Bloqueiam DC
   - Definem frequência de corte inferior

4. **Capacitor de Bypass (Cs):**
   - Curto-circuita Rs em AC
   - Aumenta ganho significativamente

---

## Análise de Matrizes do Circuito (MNA)

A Análise Nodal Modificada (MNA) é fundamental para entender como SLiCAP resolve circuitos.

### O que é MNA?

MNA monta as equações do circuito em forma matricial:

```
M · Dv = Iv
```

- **M**: Matriz MNA (system matrix) - contém condutâncias e relações dos elementos
- **Dv**: Vetor de variáveis dependentes - tensões nodais e correntes de ramo (INCÓGNITAS)
- **Iv**: Vetor de variáveis independentes - valores das fontes (CONHECIDAS)

### Extraindo Matrizes com SLiCAP

```python
import SLiCAP as sl

# Carregar circuito
cir = sl.makeCircuit("voltage_divider.cir")

# Extrair matrizes
matrix_result = sl.doMatrix(cir)

M = matrix_result.M      # MNA matrix
Iv = matrix_result.Iv    # Independent variables
Dv = matrix_result.Dv    # Dependent variables

# Exibir
print("Matriz M:")
print(M)

print("\nVetor Dv (incógnitas):")
print(Dv)

print("\nVetor Iv (fontes):")
print(Iv)
```

### Exemplo: Divisor de Tensão

```python
# Para o divisor de tensão visto anteriormente:

M = Matrix([
    [0,     1,           0      ],
    [1,    1/R1,       -1/R1    ],
    [0,   -1/R1,   1/R1 + 1/R2  ]
])

Dv = Matrix([
    [ I_V1  ],    # Corrente através da fonte V1
    [ V_in  ],    # Tensão no nó 'in'
    [ V_out ]     # Tensão no nó 'out'
])

Iv = Matrix([
    [V_in],       # Valor da fonte V1
    [  0  ],      # KCL no nó 'in'
    [  0  ]       # KCL no nó 'out'
])
```

### Interpretação da Matriz M

**Estrutura geral:**

```
     I_V1      V_in         V_out
┌─────────┬──────────┬────────────────┐
│    0    │    1     │       0        │  ← Equação da fonte V1
│    1    │   1/R1   │     -1/R1      │  ← KCL no nó 'in'
│    0    │  -1/R1   │  1/R1 + 1/R2   │  ← KCL no nó 'out'
└─────────┴──────────┴────────────────┘
```

**Linha 1:** Equação da fonte de tensão (V_in = V_in)
**Linha 2:** KCL no nó 'in': I_V1 + V_in/R1 - V_out/R1 = 0
**Linha 3:** KCL no nó 'out': -V_in/R1 + V_out(1/R1 + 1/R2) = 0

### Solucionando o Sistema

```python
# Solução: Dv = M^(-1) · Iv
solution = M.inv() * Iv

print("Solução:")
for i, var in enumerate(Dv):
    print(f"{var} = {solution[i]}")
```

**Resultado:**
```
I_V1 = -V_in/(R1 + R2)
V_in = V_in
V_out = R2*V_in/(R1 + R2)  ← Esta é a fórmula do divisor!
```

### Exemplo: Filtro RC

Para o filtro RC, a matriz MNA inclui termos com `s` (variável de Laplace):

```python
M = Matrix([
    [0,    1,         0      ],
    [1,   1/R,      -1/R     ],
    [0,  -1/R,   C*s + 1/R   ]  ← Note o termo C*s!
])
```

A presença de `s` na matriz indica dependência de frequência.

### Visualizando Matrizes no Jupyter

```python
from IPython.display import display, Math
from sympy import latex

# Exibir em LaTeX
display(Math(latex(M)))

# Pretty print
from sympy import pprint
pprint(M)
```

---

## Visualização de Funções de Transferência

### Formas de Visualizar H(s)

SLiCAP oferece várias formas de visualizar e analisar funções de transferência:

#### 1. Expressão Simbólica

```python
result = sl.doLaplace(cir, source='V1', detector='V_out')
H = result.laplace

print(f"H(s) = {H}")
print(f"Numerador: {result.numer}")
print(f"Denominador: {result.denom}")
```

#### 2. Simplificação Simbólica

```python
from sympy import simplify, factor, expand, cancel

H_simplified = simplify(H)
H_factored = factor(H)
H_expanded = expand(H)
H_canceled = cancel(H)

print(f"Simplificado: {H_simplified}")
print(f"Fatorado: {H_factored}")
```

#### 3. Diagrama de Bode (Magnitude e Fase)

```python
import numpy as np
import matplotlib.pyplot as plt

# Range de frequências
freqs = np.logspace(0, 6, 500)  # 1Hz a 1MHz

magnitudes_dB = []
phases = []

for f in freqs:
    omega = 2 * np.pi * f
    s_val = 1j * omega

    # Substituir s e parâmetros
    H_val = H.subs([('R', 1000), ('C', 100e-9), ('s', s_val)])
    H_complex = complex(H_val)

    mag = abs(H_complex)
    magnitudes_dB.append(20 * np.log10(mag))
    phases.append(np.angle(H_complex, deg=True))

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

ax1.semilogx(freqs, magnitudes_dB, 'b-', linewidth=2)
ax1.set_ylabel('Magnitude (dB)')
ax1.set_title('Bode Plot - Magnitude')
ax1.grid(True)

ax2.semilogx(freqs, phases, 'r-', linewidth=2)
ax2.set_xlabel('Frequency (Hz)')
ax2.set_ylabel('Phase (degrees)')
ax2.set_title('Bode Plot - Phase')
ax2.grid(True)

plt.tight_layout()
plt.show()
```

#### 4. Diagrama de Polos e Zeros

```python
# Encontrar polos e zeros
from sympy import solve, symbols

s = symbols('s')

# Polos: raízes do denominador
poles = solve(result.denom, s)
print(f"Polos: {poles}")

# Zeros: raízes do numerador
zeros = solve(result.numer, s)
print(f"Zeros: {zeros}")

# Plot no plano complexo
plt.figure(figsize=(8, 8))

# Plot polos (X)
for pole in poles:
    if pole.is_real:
        plt.plot(float(pole), 0, 'rx', markersize=15, markeredgewidth=3)
    else:
        plt.plot(float(pole.as_real_imag()[0]),
                float(pole.as_real_imag()[1]),
                'rx', markersize=15, markeredgewidth=3)

# Plot zeros (O)
for zero in zeros:
    if zero.is_real:
        plt.plot(float(zero), 0, 'bo', markersize=12, fillstyle='none',
                markeredgewidth=2)
    else:
        plt.plot(float(zero.as_real_imag()[0]),
                float(zero.as_real_imag()[1]),
                'bo', markersize=12, fillstyle='none', markeredgewidth=2)

plt.axhline(0, color='k', linewidth=0.5)
plt.axvline(0, color='k', linewidth=0.5)
plt.grid(True, alpha=0.3)
plt.xlabel('Real', fontsize=12)
plt.ylabel('Imaginário', fontsize=12)
plt.title('Diagrama de Polos e Zeros', fontsize=14, fontweight='bold')
plt.legend(['Polos (×)', 'Zeros (○)'])
plt.show()
```

#### 5. Resposta ao Degrau e Impulso

```python
# Para sistemas de 1ª ordem: H(s) = K/(s + a)
# Resposta ao degrau: h_step(t) = K/a * (1 - e^(-at))
# Resposta ao impulso: h_impulse(t) = K * e^(-at)

from sympy import inverse_laplace_transform, symbols

s, t = symbols('s t')

# Transformada inversa de Laplace
h_impulse = inverse_laplace_transform(H, s, t)
h_step = inverse_laplace_transform(H/s, s, t)

print(f"Resposta ao impulso h(t): {h_impulse}")
print(f"Resposta ao degrau g(t): {h_step}")
```

#### 6. Análise de Ganho em Frequências Específicas

```python
# Ganho DC
H_dc = H.subs(s, 0)
print(f"Ganho DC: {H_dc}")

# Ganho em frequência específica (ex: 1kHz)
f_test = 1000
omega_test = 2 * np.pi * f_test
H_at_1kHz = H.subs([('R', 1000), ('C', 100e-9), ('s', 1j*omega_test)])
print(f"Ganho em 1kHz: {abs(complex(H_at_1kHz)):.4f}")

# Ganho em infinito
from sympy import limit, oo
H_inf = limit(H, s, oo)
print(f"Ganho em f→∞: {H_inf}")
```

---

## Tipos de Análise Disponíveis

SLiCAP oferece diversos tipos de análise:

### 1. Análise DC

```python
dc_result = sl.doDC(cir, source='V1', detector='V_out')
print(f"Ganho DC: {dc_result.DCvalue}")
```

### 2. Análise AC (Laplace)

```python
# Simbólica
result_sym = sl.doLaplace(cir, source='V1', detector='V_out')

# Numérica (com valores dos componentes)
result_num = sl.doLaplace(cir, source='V1', detector='V_out', pardefs='circuit')
```

### 3. Análise de Polos e Zeros

```python
pz_result = sl.doPZ(cir, source='V1', detector='V_out', pardefs='circuit')

print(f"Polos: {pz_result.poles}")
print(f"Zeros: {pz_result.zeros}")
print(f"Ganho DC: {pz_result.DCvalue}")
```

### 4. Análise de Ruído

```python
noise_result = sl.doNoise(cir, source='V1', detector='V_out', pardefs='circuit')

# Plotar densidade espectral de ruído
fig = sl.plotSweep('noise', 'Noise Spectral Density', noise_result,
                   1, '1G', 100, funcType='onoise', show=True)
```

### 5. Análise de Impedância

```python
# Impedância de entrada
Zin_result = sl.doLaplace(cir, source='V1', detector='I_V1', pardefs='circuit')
Zin = 1 / Zin_result.laplace  # Z = V/I

print(f"Impedância de entrada: {Zin}")
```

### 6. Análise Paramétrica

```python
# Varrer valores de um componente
import numpy as np

R_values = np.logspace(2, 4, 20)  # 100Ω a 10kΩ

for R_val in R_values:
    cir.defPar('R', R_val)
    result = sl.doLaplace(cir, source='V1', detector='V_out', pardefs='circuit')
    # Processar resultado...
```

### 7. Análise de Matrizes

```python
matrix_result = sl.doMatrix(cir)

M = matrix_result.M
Dv = matrix_result.Dv
Iv = matrix_result.Iv

print(f"Matriz MNA: {M}")
```

---

## Projetos para Estudantes

Aqui estão projetos progressivos para praticar SLiCAP:

### Nível Iniciante

#### Projeto 1: Divisor de Tensão Ajustável
- **Objetivo:** Criar divisor com ganho variável
- **Tarefas:**
  1. Netlist com parâmetro `{ratio}` para ajustar R2/R1
  2. Script que varia `ratio` de 0.1 a 10
  3. Plot de V_out vs ratio
  4. Encontrar ratio para V_out = 3.3V (dado V_in = 5V)

#### Projeto 2: Filtro RC com Frequência de Corte Especificada
- **Objetivo:** Projetar filtro para fc = 10kHz
- **Tarefas:**
  1. Escolher R = 1kΩ, calcular C necessário
  2. Criar netlist e script de análise
  3. Verificar fc com diagrama de Bode
  4. Medir -3dB point
  5. Verificar roll-off de -20dB/década

### Nível Intermediário

#### Projeto 3: Filtro Passa-Banda RLC
- **Objetivo:** Projetar filtro passa-banda para f0 = 1kHz, Q = 10
- **Tarefas:**
  1. Calcular L, C, R para especificações dadas
  2. Criar netlist RLC série
  3. Análise simbólica de H(s)
  4. Encontrar polos complexos conjugados
  5. Plotar resposta em frequência
  6. Medir largura de banda a -3dB

#### Projeto 4: Amplificador Multi-Estágio
- **Objetivo:** Cascata de 2 amplificadores
- **Tarefas:**
  1. Projetar dois estágios com Av1 = 5 e Av2 = 10
  2. Analisar cada estágio separadamente
  3. Combinar em cascata
  4. Verificar ganho total ≈ Av1 × Av2
  5. Analisar efeito de carga entre estágios

### Nível Avançado

#### Projeto 5: Filtro Ativo com Op-Amp
- **Objetivo:** Filtro Sallen-Key passa-baixa de 2ª ordem
- **Tarefas:**
  1. Topologia Sallen-Key com op-amp ideal
  2. Projeto para fc = 1kHz, Q = 0.707 (Butterworth)
  3. Análise simbólica completa
  4. Encontrar 2 polos complexos
  5. Comparar com filtro RC passivo
  6. Documentação HTML completa

#### Projeto 6: Amplificador Diferencial
- **Objetivo:** Amp diff com rejeição de modo comum
- **Tarefas:**
  1. Netlist de par diferencial com carga ativa
  2. Análise de ganho diferencial
  3. Análise de ganho de modo comum
  4. Calcular CMRR (Common Mode Rejection Ratio)
  5. Análise de impedância de entrada

#### Projeto 7: Oscilador Wien Bridge
- **Objetivo:** Projeto de oscilador com frequência específica
- **Tarefas:**
  1. Análise de ganho de malha
  2. Encontrar condição de oscilação (ganho de malha = 1, fase = 0°)
  3. Determinar frequência de oscilação
  4. Calcular valores de componentes
  5. Análise de estabilidade

### Projeto Final: Sistema Completo

#### Projeto 8: Sistema de Aquisição de Sinais
- **Objetivo:** Cadeia completa de processamento de sinal
- **Componentes:**
  1. Filtro anti-aliasing (passa-baixa)
  2. Amplificador de instrumentação
  3. Filtro passa-banda para banda de interesse
  4. Buffer de saída
- **Tarefas:**
  1. Especificar cada bloco
  2. Projetar individualmente
  3. Análise cascata completa
  4. Função de transferência do sistema
  5. Resposta em frequência total
  6. Análise de ruído
  7. Documentação técnica completa

---

## Troubleshooting e Dicas

### Problemas Comuns

#### 1. "No module named 'SLiCAP'"

**Solução:**
```bash
pip install SLiCAP
# ou
uv pip install SLiCAP
```

#### 2. "Cannot find circuit file"

**Causa:** Arquivo .cir não está em `cir/` subdirectory

**Solução:**
```python
# Estrutura correta:
meu_projeto/
├── cir/
│   └── circuito.cir  ← Aqui!
└── analyze.py

# No script:
cir = sl.makeCircuit("circuito.cir")  # SLiCAP procura em cir/
```

#### 3. Expressões muito longas/complexas

**Solução:**
```python
from sympy import simplify, factor

H = result.laplace
H_simplified = simplify(H)
H_factored = factor(H)

# Ou use análise numérica diretamente:
result_num = sl.doLaplace(cir, source='V1', detector='V_out',
                          pardefs='circuit')
```

#### 4. Análise muito lenta (circuitos grandes)

**Causa:** Análise simbólica cresce exponencialmente

**Soluções:**
1. Usar `pardefs='circuit'` para análise numérica direta
2. Dividir circuito em blocos menores
3. Para circuitos >30 nós, considere ngspice
4. Simplificar modelos de componentes

#### 5. Resultados não batem com expectativa

**Checklist:**
```python
# 1. Verificar valores dos parâmetros
print(cir.parDefs)

# 2. Verificar conexões dos nós
print(cir.elements)

# 3. Verificar detector correto
# Detector de tensão: 'V_<nome_do_nó>'
result = sl.doLaplace(cir, source='V1', detector='V_out')  # Nó 'out'

# 4. Verificar netlist
# Nó 0 deve ser terra
# Polaridade das fontes
```

#### 6. LaTeX warnings

**Causa:** SLiCAP usa LaTeX para renderização

**Solução 1:** Instalar LaTeX (veja seção Instalação)

**Solução 2:** Ignorar warnings (não afeta funcionalidade)

### Dicas de Boas Práticas

#### 1. Estrutura de Projeto Organizada

```
projeto/
├── cir/              # Netlists
├── img/              # Esquemáticos
├── docs/             # Documentação
├── scripts/          # Scripts de análise
├── results/          # Gráficos e resultados
├── README.md
└── requirements.txt
```

#### 2. Documentar Netlists

```spice
"Título Descritivo"
* Autor: Seu Nome
* Data: 2026-01-03
* Descrição: Este circuito faz...
* Especificações:
*   - Frequência de corte: 1kHz
*   - Ganho: 20dB
*   - Impedância de entrada: >1MΩ

* Componentes principais
R1 in out {R}  * Resistor de entrada
C1 out 0 {C}   * Capacitor de saída

.end
```

#### 3. Scripts Modulares

```python
def analyze_transfer_function(circuit, source, detector):
    """Analisa função de transferência"""
    result = sl.doLaplace(circuit, source=source, detector=detector)
    return result

def plot_bode(circuit, source, detector, freq_range):
    """Gera diagrama de Bode"""
    # ...
    return fig

def generate_report(circuit, results):
    """Gera relatório HTML"""
    # ...

# Main
if __name__ == "__main__":
    cir = sl.makeCircuit("meu_circuito.cir")
    result = analyze_transfer_function(cir, 'V1', 'V_out')
    fig = plot_bode(cir, 'V1', 'V_out', (1, 1e6))
    generate_report(cir, result)
```

#### 4. Versionamento

Use git para controlar versões:

```bash
git init
git add cir/ scripts/ README.md
git commit -m "Initial circuit design"
```

#### 5. Validação com ngspice

Sempre valide resultados críticos com simulação ngspice:

```python
# SLiCAP (simbólico/linear)
result_slicap = sl.doLaplace(cir, ...)

# ngspice (numérico/validação)
# Criar netlist ngspice e simular
```

---

## Referências

### Documentação Oficial

- **Site oficial:** https://www.analog-electronics.eu/slicap/slicap.html
- **User Guide:** https://www.analog-electronics.eu/slicap/userguide/userguide.html
- **Syntax Reference:** https://www.analog-electronics.eu/slicap/syntax/syntax.html
- **Examples:** https://www.analog-electronics.eu/slicap/examples/examples.html
- **GitHub:** https://github.com/SLiCAP/SLiCAP_python

### Livros Recomendados

1. **Structured Electronic Design** - Anton Verhoeven
   _O livro do criador do SLiCAP, excelente para metodologia de projeto_

2. **Design of Analog Circuits** - Verhoeven et al.
   _Teoria de circuitos com foco em análise sistemática_

3. **Analysis and Design of Analog Integrated Circuits** - Gray, Hurst, Lewis, Meyer
   _Clássico de circuitos analógicos integrados_

4. **Microelectronic Circuits** - Sedra & Smith
   _Texto fundamental para eletrônica analógica_

### Recursos Online

- **SLiCAP Tutorial Videos:** YouTube "SLiCAP tutorial"
- **Analog Electronics Blog:** https://www.analog-electronics.eu/
- **Repositório de Exemplos:** https://github.com/SLiCAP/SLiCAP_python/tree/master/examples

### Comunidade

- **Issues GitHub:** https://github.com/SLiCAP/SLiCAP_python/issues
- **Discussões:** https://github.com/SLiCAP/SLiCAP_python/discussions

### Teoria de Circuitos

- **Modified Nodal Analysis:** https://en.wikipedia.org/wiki/Modified_nodal_analysis
- **Laplace Transform:** https://en.wikipedia.org/wiki/Laplace_transform
- **Bode Plots:** https://en.wikipedia.org/wiki/Bode_plot
- **Pole-Zero Analysis:** https://en.wikipedia.org/wiki/Pole%E2%80%93zero_plot

---

## Conclusão

### O que você aprendeu

✅ **Fundamentos de SLiCAP** - Instalação, conceitos, e workflow
✅ **Criação de Netlists** - Sintaxe SPICE para SLiCAP
✅ **Análise de Circuitos** - Divisores, filtros, amplificadores
✅ **Matrizes MNA** - Entendimento profundo de como SLiCAP funciona
✅ **Funções de Transferência** - Visualização e interpretação
✅ **Tipos de Análise** - DC, AC, polos-zeros, ruído, impedância
✅ **Projetos Práticos** - Exemplos progressivos para aprendizado

### Próximos Passos

1. **Execute os exemplos** deste tutorial
2. **Modifique os circuitos** e veja o que acontece
3. **Complete os projetos** para estudantes
4. **Explore os exemplos** em `exercises/slicap_exercises/`
5. **Integre com ngspice** para validação completa
6. **Crie seus próprios projetos** de engenharia

### Lembre-se

- SLiCAP é para circuitos **LINEARES** (ou linearizados)
- Use análise **simbólica** para entendimento
- Use análise **numérica** quando expressões ficarem muito longas
- **Valide sempre** com ngspice para circuitos reais
- **Documente** seus projetos para referência futura

### Mensagem Final

SLiCAP é uma ferramenta poderosa que transforma sua forma de pensar sobre circuitos. Ao invés de apenas obter números, você obtém **equações** que revelam as relações fundamentais entre componentes.

Use SLiCAP para:
- 📚 **Aprender** - Veja exatamente como cada componente afeta o circuito
- 🎯 **Projetar** - Otimize analyticamente antes de simular
- 📝 **Documentar** - Gere relatórios profissionais automaticamente
- ✅ **Verificar** - Confirme sua intuição com matemática exata

**Boa sorte em seus projetos de eletrônica!**

---

**Autor:** Leonardo
**Contato:** leonardo.araujo.santos@gmail.com
**Licença:** MIT
**Versão do tutorial:** 2.0
**Última atualização:** 2026-01-03
**Baseado em:** SLiCAP 3.x

---

## Apêndice A: Referência Rápida de Comandos

```python
# Inicialização
import SLiCAP as sl
prj = sl.initProject("Nome")
cir = sl.makeCircuit("arquivo.cir")

# Definir parâmetros
cir.defPar('R', 1000)

# Análises
result = sl.doLaplace(cir, source='V1', detector='V_out')
dc = sl.doDC(cir, source='V1', detector='V_out')
pz = sl.doPZ(cir, source='V1', detector='V_out', pardefs='circuit')
matrix = sl.doMatrix(cir)

# Acessar resultados
H = result.laplace      # Função de transferência
num = result.numer      # Numerador
den = result.denom      # Denominador
M = matrix.M            # Matriz MNA
Dv = matrix.Dv          # Variáveis dependentes
Iv = matrix.Iv          # Variáveis independentes

# Plotagem
fig = sl.plotSweep('nome', 'título', result, f_start, f_stop,
                   num_points, funcType='dBmag', show=True)
```

## Apêndice B: Modelos de Componentes

### Resistor
```spice
R<nome> <nó+> <nó-> <valor>
R1 in out 1k
```

### Capacitor
```spice
C<nome> <nó+> <nó-> <valor>
C1 out 0 100n
```

### Indutor
```spice
L<nome> <nó+> <nó-> <valor>
L1 in out 10m
```

### Fonte de Tensão
```spice
V<nome> <nó+> <nó-> <valor>
V1 in 0 10        # DC
V1 in 0 AC 1      # AC
```

### Fonte de Corrente
```spice
I<nome> <nó+> <nó-> <valor>
I1 0 out 1m
```

### VCVS (Voltage Controlled Voltage Source)
```spice
E<nome> <out+> <out-> <in+> <in-> <ganho>
E1 out 0 in 0 100
```

### VCCS (Voltage Controlled Current Source)
```spice
G<nome> <out+> <out-> <in+> <in-> <gm>
G1 out 0 in 0 0.01
```

### JFET (Modelo de Pequenos Sinais)
```spice
J<nome> <drain> <gate> <source> <modelo>
.model <modelo> J gm={gm} go={go} cgs={cgs} cdg={cdg}
```
