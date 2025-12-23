# Tutorial SLiCAP - Symbolic Linear Circuit Analysis Program

**Autor:** Leonardo
**Versão:** 1.0
**Data:** 2025-12-23

---

## Índice

1. [Introdução](#introdução)
2. [Instalação](#instalação)
3. [Conceitos Fundamentais](#conceitos-fundamentais)
4. [Tutorial Passo a Passo](#tutorial-passo-a-passo)
5. [Tipos de Análise](#tipos-de-análise)
6. [Exemplos Práticos](#exemplos-práticos)
7. [Referências](#referências)

---

## Introdução

### O que é SLiCAP?

**SLiCAP** (Symbolic Linear Circuit Analysis Program) é uma ferramenta Python para análise simbólica e numérica de circuitos lineares. Diferente de simuladores como ngspice que fornecem apenas resultados numéricos, SLiCAP calcula **expressões algébricas** das funções de transferência, impedâncias, e outras características do circuito.

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

#### Opção 2: uv (recomendado)

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

SLiCAP usa MNA (Modified Nodal Analysis) para montar as equações do circuito:

```
┌─────┬─────┐ ┌───┐   ┌───┐
│  G  │  B  │ │ V │ = │ I │
│     │     │ │   │   │   │
│  C  │  D  │ │ J │   │ E │
└─────┴─────┘ └───┘   └───┘
```

Onde:
- **G**: Matriz de condutâncias (nós)
- **B**: Matriz de fontes de tensão
- **C**: Transposta de B
- **D**: Matriz das fontes de tensão
- **V**: Vetor de tensões nodais
- **J**: Vetor de correntes através das fontes de tensão
- **I**: Vetor de correntes injetadas
- **E**: Vetor de tensões das fontes

### 2. Análise Laplace

SLiCAP trabalha no domínio de Laplace (variável `s`), permitindo análise simbólica:

```
H(s) = Vout(s) / Vin(s)
```

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

---

## Tutorial Passo a Passo

### Exemplo 1: Filtro RC Passa-Baixa

Vamos criar um filtro RC completo do zero.

#### Passo 1: Criar Diretório do Projeto

```bash
mkdir ~/meu_filtro_rc
cd ~/meu_filtro_rc
```

#### Passo 2: Criar Netlist SPICE

Crie o arquivo `rc_filter.cir`:

```spice
"Filtro RC Passa-Baixa - fc=159Hz"
* R = 1kΩ, C = 1µF
* fc = 1/(2*pi*R*C) = 159.15 Hz

Vin input 0 AC 1
R1 input output 1k
C1 output 0 1u

.end
```

**Convenções importantes:**
- Primeira linha é o título (entre aspas)
- Nó 0 é sempre o terra (ground)
- Use nomes descritivos para os nós (`input`, `output`)
- Comentários começam com `*`

#### Passo 3: Criar Script Python

Crie o arquivo `analyze_rc.py`:

```python
#!/usr/bin/env python3
"""
Análise completa de filtro RC passa-baixa usando SLiCAP
"""

import SLiCAP as sl

# 1. Inicializar projeto
print("Inicializando projeto SLiCAP...")
prj = sl.initProject("RC_Filter_Analysis")

# 2. Importar circuito
print("Importando circuito...")
cir = sl.makeCircuit("rc_filter.cir")

# 3. Exibir informações do circuito
print("\n=== Informações do Circuito ===")
print(f"Título: {cir.title}")
print(f"Nós: {cir.nodes}")
print(f"Elementos: {list(cir.elements.keys())}")

# 4. Análise MNA (Matriz de Equações)
print("\n=== Análise MNA ===")
MNA = sl.doMatrix(cir, source='Vin', detector='V_output')

# Exportar para HTML
sl.htmlPage('Análise Matricial')
sl.text2html('Equações da Análise Nodal Modificada:')
sl.matrices2html(MNA, label='MNA', labelText='Matriz MNA do filtro RC')

# 5. Função de transferência simbólica
print("\n=== Função de Transferência Simbólica ===")
gain = sl.doLaplace(cir, source='Vin', detector='V_output')

print(f"H(s) = {gain.laplace}")

# Exportar para HTML
sl.htmlPage('Função de Transferência')
sl.head2html('Análise Simbólica')
sl.eqn2html('H(s)', gain.laplace, label='transferFunction',
           labelText='Função de transferência do filtro RC')

# 6. Análise numérica (substituir valores dos componentes)
print("\n=== Análise Numérica ===")
numGain = sl.doLaplace(cir, source='Vin', detector='V_output', pardefs='circuit')

# 7. Plotar resposta em frequência
print("\n=== Gerando Gráficos de Bode ===")
sl.htmlPage('Diagramas de Bode')
sl.head2html('Resposta em Frequência')

# Magnitude linear
figMag = sl.plotSweep('magnitude', 'Magnitude Linear', numGain,
                     10, '100k', 200, yUnits='-', show=False)
sl.fig2html(figMag, 700, caption='Magnitude da resposta em frequência',
           label='figMagnitude')

# Magnitude em dB
figdB = sl.plotSweep('magnitude_dB', 'Magnitude (dB)', numGain,
                    10, '100k', 200, funcType='dBmag', show=False)
sl.fig2html(figdB, 700, caption='Magnitude em dB',
           label='figMagnitudedB')

# Fase
figPhase = sl.plotSweep('phase', 'Fase', numGain,
                       10, '100k', 200, funcType='phase', show=False)
sl.fig2html(figPhase, 700, caption='Fase da resposta em frequência',
           label='figPhase')

# 8. Análise de Polos e Zeros
print("\n=== Análise de Polos e Zeros ===")
pzResult = sl.doPZ(cir, source='Vin', detector='V_output', pardefs='circuit')

print(f"Polos: {pzResult.poles}")
print(f"Zeros: {pzResult.zeros}")
print(f"Ganho DC: {pzResult.DCvalue}")

# Exportar para HTML
sl.htmlPage('Polos e Zeros')
sl.pz2html(pzResult, label='PZanalysis',
          labelText='Polos e zeros do filtro RC')

# Plot de polos/zeros no plano complexo
figPZ = sl.plotPZ('pz_plot', 'Diagrama de Polos e Zeros', pzResult, show=False)
sl.fig2html(figPZ, 600, caption='Polos (×) e zeros (○) no plano s',
           label='figPZ')

# 9. Resposta ao degrau
print("\n=== Resposta ao Degrau ===")
stepResult = sl.doStep(cir, source='Vin', detector='V_output', pardefs='circuit')

sl.htmlPage('Resposta Temporal')
sl.head2html('Resposta ao Degrau Unitário')

figStep = sl.plotSweep('step_response', 'Resposta ao Degrau', stepResult,
                      0, 10, 100, sweepScale='m', show=False)
sl.fig2html(figStep, 700, caption='Resposta ao degrau unitário (tempo em ms)',
           label='figStep')

# 10. Gerar índice de navegação
sl.htmlPage('Índice')
sl.head1html('Análise Completa do Filtro RC')
sl.text2html('Este relatório contém a análise completa do filtro RC passa-baixa.')
sl.links2html()

print("\n✅ Análise completa!")
print(f"📄 Abra o relatório em: {prj.htmlPath}index.html")
```

#### Passo 4: Executar

```bash
python analyze_rc.py
```

#### Passo 5: Visualizar Resultados

```bash
# Linux
xdg-open html/index.html

# macOS
open html/index.html

# Windows
start html/index.html
```

**Você verá:**
- Equações MNA matriciais
- H(s) = 1/(1 + 0.001·s) simbólico
- Diagramas de Bode (magnitude e fase)
- Polos: s = -1000 rad/s
- Resposta ao degrau

---

## Tipos de Análise

### 1. Análise DC

```python
dcResult = sl.doDC(cir, source='Vin', detector='V_output')
print(f"Ganho DC: {dcResult.DCvalue}")
```

### 2. Análise AC (Laplace)

```python
gain = sl.doLaplace(cir, source='Vin', detector='V_output', pardefs='circuit')
```

### 3. Análise de Ruído

```python
noise = sl.doNoise(cir, source='Vin', detector='V_output', pardefs='circuit')
figNoise = sl.plotSweep('noise', 'Densidade Espectral de Ruído', noise,
                       1, '1G', 100, funcType='onoise', show=True)
```

### 4. Análise de Impedância

```python
# Impedância de entrada
Zin = sl.doLaplace(cir, source='Vin', detector='I_Vin', pardefs='circuit')
Zin_expr = 1 / Zin.laplace  # Z = V/I
```

### 5. Análise Paramétrica

```python
# Varrer valores de R1
import numpy as np

for R in np.logspace(2, 4, 5):  # 100Ω a 10kΩ
    cir.defPar('R1', R)
    gain = sl.doLaplace(cir, source='Vin', detector='V_output', pardefs='circuit')
    # ... plotar resultados
```

---

## Exemplos Práticos

### Exemplo 2: Filtro Passa-Alta RC

**Circuito (`hp_filter.cir`):**
```spice
"Filtro RC Passa-Alta"

Vin input 0 AC 1
C1 input node1 1u
R1 node1 0 1k
.model VCVS out node1 0 1  ; Buffer

.end
```

**Análise:**
```python
import SLiCAP as sl

prj = sl.initProject("HighPass_Filter")
cir = sl.makeCircuit("hp_filter.cir")

# H(s) para passa-alta: H(s) = (R*C*s) / (1 + R*C*s)
gain = sl.doLaplace(cir, source='Vin', detector='V_node1')
print(f"H(s) = {gain.laplace}")

# Bode plot
numGain = sl.doLaplace(cir, source='Vin', detector='V_node1', pardefs='circuit')
fig = sl.plotSweep('hp_bode', 'Passa-Alta Bode', numGain, 1, '100k', 200,
                  funcType='dBmag', show=True)
```

### Exemplo 3: Divisor de Tensão

**Circuito (`voltage_divider.cir`):**
```spice
"Divisor de Tensão 2:1"

Vin input 0 AC 1
R1 input output 1k
R2 output 0 1k

.end
```

**Análise:**
```python
import SLiCAP as sl

prj = sl.initProject("Voltage_Divider")
cir = sl.makeCircuit("voltage_divider.cir")

# Ganho simbólico
gain = sl.doLaplace(cir, source='Vin', detector='V_output')
print(f"Vout/Vin = {gain.laplace}")
# Esperado: Vout/Vin = R2/(R1+R2) = 0.5

# Ganho numérico
numGain = sl.doLaplace(cir, source='Vin', detector='V_output', pardefs='circuit')
print(f"Ganho DC = {numGain.DCvalue}")
# Esperado: 0.5
```

### Exemplo 4: Amplificador Inversor (Op-Amp)

**Circuito (`inverting_amp.cir`):**
```spice
"Amplificador Inversor - Ganho = -10"

Vin input 0 AC 1
R1 input inv 1k
R2 inv output 10k
E1 output 0 0 inv 1e6  ; Op-amp ideal (ganho 1e6)

.end
```

**Análise:**
```python
import SLiCAP as sl

prj = sl.initProject("Inverting_Amplifier")
cir = sl.makeCircuit("inverting_amp.cir")

# Ganho simbólico
gain = sl.doLaplace(cir, source='Vin', detector='V_output')
print(f"H(s) = {gain.laplace}")
# Esperado: H(s) ≈ -R2/R1 = -10

# Verificar polo dominante
pz = sl.doPZ(cir, source='Vin', detector='V_output', pardefs='circuit')
print(f"Polos: {pz.poles}")
```

### Exemplo 5: Filtro RLC Passa-Banda

**Circuito (`rlc_bandpass.cir`):**
```spice
"Filtro RLC Passa-Banda - Q=10"

Vin input 0 AC 1
R1 input 0 100
L1 input output 10m
C1 output 0 10u

.end
```

**Análise:**
```python
import SLiCAP as sl

prj = sl.initProject("RLC_BandPass")
cir = sl.makeCircuit("rlc_bandpass.cir")

# Função de transferência
gain = sl.doLaplace(cir, source='Vin', detector='V_output')
print(f"H(s) = {gain.laplace}")

# Calcular frequência de ressonância e Q
pz = sl.doPZ(cir, source='Vin', detector='V_output', pardefs='circuit')
print(f"Polos: {pz.poles}")

# Plotar resposta em frequência
numGain = sl.doLaplace(cir, source='Vin', detector='V_output', pardefs='circuit')
fig = sl.plotSweep('rlc_response', 'Resposta RLC', numGain,
                  100, '100k', 500, funcType='dBmag', show=True)

# Frequência de ressonância esperada
# f0 = 1/(2*pi*sqrt(L*C)) = 1/(2*pi*sqrt(10m*10u)) = 503 Hz
```

---

## Comandos e Funções Úteis

### Inicialização e Circuitos

```python
# Criar projeto
prj = sl.initProject("MeuProjeto")

# Importar circuito
cir = sl.makeCircuit("circuito.cir")
cir = sl.makeCircuit("circuito.cir", circuitName="Nome Customizado")

# Ver elementos do circuito
print(cir.elements)
print(cir.nodes)
print(cir.params)
```

### Análises

```python
# Análise MNA
MNA = sl.doMatrix(cir, source='V1', detector='Vout')

# Laplace (simbólico)
result = sl.doLaplace(cir, source='V1', detector='Vout')

# Laplace (numérico)
result = sl.doLaplace(cir, source='V1', detector='Vout', pardefs='circuit')

# Polos e zeros
pz = sl.doPZ(cir, source='V1', detector='Vout', pardefs='circuit')

# DC
dc = sl.doDC(cir, source='V1', detector='Vout')

# Ruído
noise = sl.doNoise(cir, source='V1', detector='Vout', pardefs='circuit')

# Resposta ao degrau
step = sl.doStep(cir, source='V1', detector='Vout', pardefs='circuit')
```

### Plotagem

```python
# Sweep de frequência
fig = sl.plotSweep(fileName, title, result, fStart, fStop, numPoints,
                   funcType='mag', sweepScale='log', show=True)

# Tipos de função (funcType):
# 'mag'     - magnitude linear
# 'dBmag'   - magnitude em dB
# 'phase'   - fase em graus
# 'delay'   - atraso de grupo
# 'onoise'  - ruído de saída
# 'inoise'  - ruído de entrada

# Polos e zeros
fig = sl.plotPZ(fileName, title, pzResult, show=True)
```

### HTML e Documentação

```python
# Criar nova página HTML
sl.htmlPage('Título da Página')

# Adicionar títulos
sl.head1html('Título Principal')
sl.head2html('Subtítulo')

# Adicionar texto
sl.text2html('Texto explicativo aqui.')

# Adicionar equação
sl.eqn2html('H(s)', gain.laplace, label='eq1', labelText='Descrição')

# Adicionar matriz
sl.matrices2html(MNA, label='mna1', labelText='Matriz MNA')

# Adicionar figura
sl.fig2html(fig, width=700, caption='Legenda da figura', label='fig1')

# Adicionar tabela de polos/zeros
sl.pz2html(pzResult, label='pz1', labelText='Polos e zeros')

# Gerar índice de navegação
sl.links2html()
```

---

## Dicas e Boas Práticas

### 1. Nomear Nós de Forma Significativa

```spice
✅ Bom:
Vin input 0 AC 1
R1 input output 1k

❌ Ruim:
Vin 1 0 AC 1
R1 1 2 1k
```

### 2. Usar Parâmetros para Facilitar Variações

```spice
.param Rval=1k
.param Cval=1u

R1 in out {Rval}
C1 out 0 {Cval}
```

No Python:
```python
cir.defPar('Rval', 2000)  # Alterar para 2kΩ
```

### 3. Documentar no Netlist

```spice
"Filtro RC - Projeto para fc=1kHz"
* Componentes:
* - R1: Resistor de entrada (1kΩ)
* - C1: Capacitor de filtragem (159nF)
* - fc = 1/(2*pi*R*C) = 1000 Hz
```

### 4. Verificar Unidades

SLiCAP/SPICE usam unidades SI por padrão:

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

### 5. Salvar Figuras para Uso Externo

```python
# Plotar e salvar
fig = sl.plotSweep('bode', 'Diagrama de Bode', gain,
                   10, '100k', 200, funcType='dBmag', show=False)

# Figuras são salvas automaticamente em:
# - html/img/bode.svg (para web)
# - html/img/bode.pdf (alta resolução)
```

---

## Troubleshooting

### Problema: "No module named 'SLiCAP'"

**Solução:**
```bash
pip install SLiCAP
# ou
uv pip install SLiCAP
```

### Problema: "Cannot find circuit file"

**Causa:** Caminho do arquivo .cir incorreto

**Solução:**
```python
# Opção 1: Usar caminho relativo correto
cir = sl.makeCircuit("cir/meu_circuito.cir")

# Opção 2: Usar caminho absoluto
cir = sl.makeCircuit("/home/user/projetos/meu_circuito.cir")

# Opção 3: Verificar diretório atual
import os
print(os.getcwd())
```

### Problema: Equações muito complexas/longas

**Solução:** Usar simplificação simbólica:

```python
from sympy import simplify, factor

# Obter função de transferência
gain = sl.doLaplace(cir, source='Vin', detector='Vout')

# Simplificar
H_simplified = simplify(gain.laplace)
H_factored = factor(gain.laplace)

print(f"Simplificado: {H_simplified}")
print(f"Fatorado: {H_factored}")
```

### Problema: Análise muito lenta (circuitos grandes)

**Causa:** Análise simbólica cresce exponencialmente com número de nós

**Soluções:**
1. Usar análise numérica diretamente: `pardefs='circuit'`
2. Dividir circuito em blocos menores
3. Usar ngspice para circuitos >30 nós
4. Simplificar modelos (usar equivalentes mais simples)

### Problema: LaTeX warnings

SLiCAP usa LaTeX para renderizar equações. Se não tiver LaTeX, verá warnings.

**Solução 1:** Instalar LaTeX (veja seção Instalação)

**Solução 2:** Ignorar warnings (funcionalidade não é afetada)

---

## Recursos Avançados

### 1. Criar Bibliotecas de Modelos

Crie `lib/my_models.lib`:

```spice
* Biblioteca de modelos customizados

.subckt opamp_ideal in out
E1 out 0 in 0 1e6
.ends

.subckt rc_filter in out {R=1k} {C=1u}
R1 in out {R}
C1 out 0 {C}
.ends
```

Use no circuito principal:

```spice
"Circuito com subcircuitos"

.include lib/my_models.lib

Vin input 0 AC 1
X1 input output rc_filter R=2k C=500n

.end
```

### 2. Análise de Sensibilidade

```python
# Calcular sensibilidade de H(s) em relação a R1
from sympy import diff

gain = sl.doLaplace(cir, source='Vin', detector='Vout')
H = gain.laplace

# Sensibilidade: S = (∂H/∂R1) * (R1/H)
R1 = cir.getParValue('R1')
sens = diff(H, R1) * (R1 / H)

print(f"Sensibilidade de H em relação a R1: {sens}")
```

### 3. Exportar para LaTeX

```python
# Gerar documento LaTeX completo
sl.latexPage('Relatório LaTeX')
sl.head2latex('Análise do Circuito')
sl.eqn2latex('H(s)', gain.laplace, label='transfer')
sl.fig2latex(fig, caption='Bode plot', label='figBode')

# Arquivo gerado em: tex/documento.tex
```

### 4. Integração com Jupyter Notebooks

```python
# No Jupyter Notebook
import SLiCAP as sl
from IPython.display import Image, Math

# Inicializar
prj = sl.initProject("Notebook_Analysis")
cir = sl.makeCircuit("circuito.cir")

# Análise
gain = sl.doLaplace(cir, source='Vin', detector='Vout')

# Exibir equação renderizada
display(Math(f"H(s) = {sl.latex(gain.laplace)}"))

# Plotar inline
fig = sl.plotSweep('bode', 'Bode', gain, 10, '100k', 200, show=True)
```

---

## Referências

### Documentação Oficial

- **Site oficial:** https://www.analog-electronics.eu/slicap/slicap.html
- **User Guide:** https://www.analog-electronics.eu/slicap/userguide/userguide.html
- **Syntax Reference:** https://www.analog-electronics.eu/slicap/syntax/syntax.html
- **Examples:** https://www.analog-electronics.eu/slicap/examples/examples.html
- **GitHub:** https://github.com/SLiCAP/SLiCAP_python

### Livros

1. **Structured Electronic Design** - Anton Verhoeven
   _O livro do criador do SLiCAP, excelente para metodologia de projeto_

2. **Design of Analog Circuits** - Verhoeven, Van Staveren, Monna, Kouwenhoven, Yildiz
   _Teoria de circuitos com foco em análise sistemática_

3. **Analysis and Design of Analog Integrated Circuits** - Gray, Hurst, Lewis, Meyer
   _Clássico de circuitos analógicos integrados_

### Tutoriais Online

- **Canal YouTube:** Buscar "SLiCAP tutorial"
- **Analog Electronics (blog do criador):** https://www.analog-electronics.eu/
- **Repositório de Exemplos:** https://github.com/SLiCAP/SLiCAP_python/tree/master/examples

### Comunidade

- **Issues GitHub:** https://github.com/SLiCAP/SLiCAP_python/issues
- **Discussões:** https://github.com/SLiCAP/SLiCAP_python/discussions

---

## Conclusão

SLiCAP é uma ferramenta poderosa para:

✅ Entender circuitos através de equações algébricas
✅ Otimizar projetos analiticamente
✅ Gerar documentação profissional automaticamente
✅ Ensinar e aprender teoria de circuitos

**Próximos passos:**

1. Execute o exemplo RC do tutorial
2. Modifique o circuito e veja as equações mudarem
3. Experimente com seus próprios circuitos
4. Explore os exemplos em `circuits/17_slicap/`

**Lembre-se:** SLiCAP é para circuitos **lineares**. Para não-lineares, use ngspice!

---

**Autor:** Leonardo
**Contato:** [Adicione seu contato]
**Licença:** MIT
**Versão do tutorial:** 1.0
**Última atualização:** 2025-12-23
