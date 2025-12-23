# SLiCAP - Symbolic Linear Circuit Analysis Program

Este diretório contém exemplos de análise simbólica de circuitos usando **SLiCAP** (Symbolic Linear Circuit Analysis Program), uma ferramenta Python para análise analítica e simbólica de circuitos lineares.

## O que é SLiCAP?

**SLiCAP** é um programa Python para análise simbólica de circuitos eletrônicos lineares que permite:

- **Análise simbólica**: Obter expressões algébricas de funções de transferência, impedâncias, etc.
- **Análise MNA**: Visualizar equações matriciais da análise nodal modificada
- **Análise de polos e zeros**: Calcular e plotar polos/zeros de funções de transferência
- **Resposta em frequência**: Gerar diagramas de Bode automaticamente
- **Resposta no tempo**: Calcular resposta ao degrau, impulso, etc.
- **Documentação automática**: Gerar relatórios HTML, LaTeX, Sphinx com todos os resultados

**Site oficial:** https://www.analog-electronics.eu/slicap/slicap.html
**Repositório GitHub:** https://github.com/SLiCAP/SLiCAP_python

## Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip ou uv (gerenciador de pacotes)

### Instalar SLiCAP

```bash
# Usando pip
pip install SLiCAP

# Ou usando uv (recomendado)
uv pip install SLiCAP
```

### Verificar instalação

```bash
python -c "import SLiCAP; print(SLiCAP.__version__)"
```

## Estrutura do Diretório

```
17_slicap/
├── rc_lp_slicap.py        # Script principal: análise RC passa-baixa
├── SLiCAP.ini             # Arquivo de configuração do projeto
├── cir/                   # Netlists SPICE dos circuitos
│   └── rc_lp.cir          # Filtro RC passa-baixa
├── html/                  # Relatórios HTML gerados
│   ├── index.html         # Página inicial do relatório
│   ├── RC-Low-Pass-Filter_*.html  # Páginas do relatório
│   ├── css/               # Estilos CSS
│   └── img/               # Gráficos SVG gerados
├── sphinx/                # Documentação Sphinx (opcional)
│   └── source/
│       ├── conf.py
│       └── index.rst
├── tex/                   # Saída LaTeX (opcional)
├── csv/                   # Dados exportados em CSV
├── txt/                   # Dados em formato texto
├── lib/                   # Bibliotecas de modelos customizados
├── img/                   # Imagens adicionais
└── README.md              # Este arquivo
```

## Exemplo: Filtro RC Passa-Baixa

### Circuito (`cir/rc_lp.cir`)

```spice
"RC Low-Pass Filter"
* Simple RC network

V1 in 0 1
R1 in out 1k
C1 out 0 1u

.end
```

### Script de Análise (`rc_lp_slicap.py`)

O script demonstra as principais funcionalidades do SLiCAP:

1. **Inicialização do projeto**
   ```python
   import SLiCAP as sl
   prj = sl.initProject("RC_LowPass_SLiCAP")
   ```

2. **Importar circuito SPICE**
   ```python
   cir = sl.makeCircuit("rc_lp.cir")
   ```

3. **Análise MNA (Matriz de Equações)**
   ```python
   MNA = sl.doMatrix(cir, source='V1', detector='V_out')
   ```

4. **Função de transferência simbólica H(s)**
   ```python
   gain = sl.doLaplace(cir, source='V1', detector='V_out')
   print(gain.laplace)  # Expressão algébrica de H(s)
   ```

5. **Resposta em frequência (Bode)**
   ```python
   numGain = sl.doLaplace(cir, source='V1', detector='V_out', pardefs='circuit')
   figMag = sl.plotSweep('RCmag', 'Magnitude', numGain, 10, '100k', 100)
   figdB = sl.plotSweep('RCdBmag', 'Magnitude dB', numGain, 10, '100k', 100, funcType='dBmag')
   figPhase = sl.plotSweep('RCphase', 'Phase', numGain, 10, '100k', 100, funcType='phase')
   ```

6. **Análise de polos e zeros**
   ```python
   pzResult = sl.doPZ(cir, source='V1', detector='V_out', pardefs='circuit')
   figPZ = sl.plotPZ('PZ', 'Polos e zeros', pzResult)
   ```

7. **Resposta ao degrau**
   ```python
   numStep = sl.doStep(cir, source='V1', detector='V_out', pardefs="circuit")
   figStep = sl.plotSweep('step', 'Step response', numStep, 0, 1, 50, sweepScale='m')
   ```

### Executar o Exemplo

```bash
cd circuits/17_slicap
python rc_lp_slicap.py
```

**Saída:**
- Função de transferência H(s) impressa no terminal
- Relatório HTML completo em `html/index.html`
- Gráficos SVG em `html/img/`
- Equações LaTeX em `tex/`

### Visualizar Resultados

```bash
# Abrir relatório HTML no navegador
xdg-open html/index.html  # Linux
open html/index.html      # macOS
start html/index.html     # Windows
```

## Resultados Esperados

### Função de Transferência Simbólica

Para o filtro RC (R=1kΩ, C=1µF):

```
H(s) = 1 / (1 + R*C*s)
     = 1 / (1 + 0.001*s)
```

Frequência de corte: **fc = 1/(2πRC) = 159.15 Hz**

### Análise de Polos e Zeros

- **Polo:** s = -1000 rad/s (ou f = -159.15 Hz)
- **Zeros:** nenhum
- Filtro de 1ª ordem: -20 dB/década após fc

### Diagramas de Bode

- **Magnitude:** 0 dB em baixas frequências, -3 dB em fc, -20 dB/década após
- **Fase:** 0° em baixas frequências, -45° em fc, -90° em altas frequências

## Recursos Avançados do SLiCAP

### 1. Análise de Ruído

```python
noise = sl.doNoise(cir, source='V1', detector='V_out', pardefs='circuit')
figNoise = sl.plotSweep('noise', 'Noise Analysis', noise, 1, '1G', 100)
```

### 2. Análise DC

```python
dcResult = sl.doDC(cir, source='V1', detector='V_out')
```

### 3. Análise Paramétrica

```python
# Varrer valores de R1 de 100Ω a 10kΩ
results = []
for R in [100, 1000, 10000]:
    cir.setParameter('R1', R)
    gain = sl.doLaplace(cir, source='V1', detector='V_out', pardefs='circuit')
    results.append(gain)
```

### 4. Análise de Circuitos Complexos

SLiCAP suporta:
- Amplificadores operacionais
- Transistores (modelos lineares)
- Transformadores
- Girators
- Fontes controladas (VCVS, VCCS, CCVS, CCCS)

## Comparação: SLiCAP vs ngspice

| Característica | SLiCAP | ngspice |
|----------------|--------|---------|
| **Tipo de análise** | Simbólica/analítica | Numérica |
| **Saída** | Expressões algébricas | Valores numéricos |
| **Circuitos** | Lineares | Lineares e não-lineares |
| **Transiente não-linear** | ❌ Não | ✅ Sim |
| **Documentação automática** | ✅ HTML/LaTeX | ❌ Não |
| **Insight matemático** | ✅✅✅ Excelente | ⚠️ Limitado |
| **Velocidade (grandes circuitos)** | ⚠️ Pode ser lento | ✅ Rápido |

**Quando usar cada um:**
- **SLiCAP**: Entender comportamento, derivar equações, ensino, otimização analítica
- **ngspice**: Simulação precisa, circuitos não-lineares, validação final de projeto

## Dicas de Uso

### 1. Nomear nós claramente

```spice
* Ruim (nós genéricos)
V1 1 0 AC 1
R1 1 2 1k
C1 2 0 1u

* Bom (nós descritivos)
V1 input 0 AC 1
R1 input output 1k
C1 output 0 1u
```

### 2. Usar unidades consistentes

```spice
* Preferir notação de engenharia
R1 in out 1k     ; 1 kΩ
C1 out 0 1u      ; 1 µF
L1 out 0 1m      ; 1 mH
```

### 3. Documentar no netlist

```spice
"RC Low-Pass Filter - fc=159Hz"
* Components:
* R1: 1kΩ resistor
* C1: 1µF capacitor
...
```

## Referências e Recursos

### Documentação Oficial
- [SLiCAP User Guide](https://www.analog-electronics.eu/slicap/userguide/userguide.html)
- [SLiCAP Syntax](https://www.analog-electronics.eu/slicap/syntax/syntax.html)
- [SLiCAP Examples](https://www.analog-electronics.eu/slicap/examples/examples.html)

### Livros Recomendados
- **Structured Electronic Design** - Anton J.M. Verhoeven (criador do SLiCAP)
- **Analog Circuit Design** - Arthur van Roermund

### Tutoriais
- Ver `docs/TUTORIAL_slicap.md` na raiz do repositório para tutorial completo
- [YouTube: SLiCAP Tutorials](https://www.youtube.com/results?search_query=slicap+tutorial)

## Criando Novos Projetos SLiCAP

### 1. Criar estrutura de diretórios

```bash
mkdir meu_projeto_slicap
cd meu_projeto_slicap
```

### 2. Criar script Python

```python
#!/usr/bin/env python3
import SLiCAP as sl

# Inicializar projeto
prj = sl.initProject("MeuProjeto")

# Importar circuito
cir = sl.makeCircuit("meu_circuito.cir")

# Realizar análises
gain = sl.doLaplace(cir, source='Vin', detector='Vout')
print(gain.laplace)

# Gerar relatório HTML
sl.htmlPage('Resultados')
sl.eqn2html('H(s)', gain.laplace)
```

### 3. Criar netlist SPICE

```spice
"Meu Circuito"

Vin input 0 AC 1
* ... componentes ...

.end
```

### 4. Executar

```bash
python meu_script.py
xdg-open html/index.html
```

## Troubleshooting

### Erro: "Module SLiCAP not found"

**Solução:**
```bash
pip install SLiCAP
# ou
uv pip install SLiCAP
```

### Erro: "Cannot find circuit file"

**Causa:** Caminho incorreto para o arquivo .cir

**Solução:**
```python
# Usar caminho relativo correto
cir = sl.makeCircuit("cir/meu_circuito.cir")

# Ou caminho absoluto
cir = sl.makeCircuit("/path/completo/meu_circuito.cir")
```

### LaTeX não instalado (avisos durante plotagem)

SLiCAP usa LaTeX para renderizar equações nos gráficos. Se não tiver LaTeX instalado, os gráficos ainda funcionarão mas sem formatação matemática.

**Instalar LaTeX (opcional):**
```bash
# Ubuntu/Debian
sudo apt install texlive texlive-latex-extra dvipng

# macOS
brew install --cask mactex
```

### Gráficos não aparecem

**Solução:** Usar `show=True` nas funções de plot:
```python
figMag = sl.plotSweep('mag', 'Magnitude', gain, 10, '100k', 100, show=True)
```

## Licença

SLiCAP é software livre distribuído sob a licença GPL v3.

Este repositório de exemplos segue a licença MIT - veja [LICENSE](../../LICENSE).
