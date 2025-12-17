# Learning ngspice

Repositorio para aprendizado de simulacao de circuitos eletronicos usando **ngspice** e a linguagem **SPICE**.

## Estrutura do Projeto

```
learning_ngspice/
├── circuits/
│   ├── 00_esquematicos/                    # Circuitos simples para gerar esquematicos
│   │   ├── divisor_tensao.spice
│   │   ├── divisor_corrente.spice
│   │   ├── filtro_rc.spice
│   │   └── amplificador_ec.spice
│   ├── 01_fundamentos/                     # Circuitos didaticos com teoria
│   │   ├── 01_divisor_tensao.spice
│   │   └── 02_divisor_corrente.spice
│   ├── 02_filtros/                         # Filtros passivos e ativos
│   │   └── filtro_rc_passa_baixa.spice
│   ├── 03_osciladores/                     # Osciladores (6 circuitos)
│   │   ├── colpitts_bc548.spice
│   │   ├── oscilador_ring.spice            # CMOS (3 e 5 estágios)
│   │   ├── oscilador_hartley.spice         # BJT com tanque LC
│   │   ├── oscilador_pierce_jfet.spice     # JFET + cristal 10MHz
│   │   ├── vco_senoidal.spice              # VCO com varactor
│   │   └── multivibrador_astavel_10hz.spice # Multivibrador clássico
│   ├── 04_amplificadores/                  # Amplificadores (3 circuitos)
│   │   ├── classe_ab_push_pull.spice       # Classe A/B com BJT
│   │   └── amplificador_jfet_self_bias.spice # JFET (3 configurações)
│   ├── 05_amplificadores_operacionais/     # Amp-ops (5 circuitos)
│   │   ├── 01_amp_op_inversor.spice
│   │   ├── 02_amp_op_nao_inversor.spice
│   │   ├── 03_amp_op_somador.spice         # Mixer, DAC 3-bit
│   │   ├── 04_amp_op_integrador.spice      # Com reset
│   │   └── 05_amp_op_comparador.spice      # Schmitt, janela
│   ├── 06_rf_comunicacoes/                 # RF (3 circuitos)
│   │   ├── mixer_diodo.spice               # Mixer de frequência
│   │   ├── modulador_am.spice              # AM (3 topologias)
│   │   └── pll_completo.spice              # Phase-Locked Loop
│   └── 07_logica_digital_cmos/             # Lógica CMOS (1 circuito)
│       └── portas_logicas_cmos.spice       # 7 portas (NOT a XNOR)
├── docs/
│   ├── tutorial_spice.md                   # Tutorial completo SPICE
│   └── circuitikzmanual.pdf                # Manual CircuiTikZ
├── scripts/
│   ├── csv_to_png.py                       # Converte CSV para PNG
│   └── spice_to_schematic.py               # Gera esquemático PNG
├── justfile                                # Comandos de automação
├── pyproject.toml                          # Dependências Python (uv)
└── README.md
```

## Quick Start

```bash
# 1. Instalar dependencias
just setup

# 2. Verificar instalacao
just check

# 3. Rodar um exemplo completo (simula + graficos + esquematico)
just exemplo-divisor
```

## Pre-requisitos

### ngspice

**macOS:**
```bash
brew install ngspice
```

**Ubuntu/Debian:**
```bash
sudo apt install ngspice
```

**Windows:**
Baixe em: http://ngspice.sourceforge.net/download.html

### uv (gerenciador de pacotes Python)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### just (command runner)

```bash
# macOS
brew install just

# Ubuntu/Debian
sudo apt install just

# Cargo
cargo install just
```

### LaTeX (para esquematicos de alta qualidade)

O script `spice_to_schematic.py` usa **lcapy** + **circuitikz** para gerar esquematicos profissionais.
LaTeX e **obrigatorio** para gerar os esquematicos com simbolos corretos.

#### macOS

**Opcao 1: BasicTeX (recomendado, ~100MB)**
```bash
brew install --cask basictex

# Adicionar ao PATH (ou reinicie o terminal)
eval "$(/usr/libexec/path_helper)"

# Instalar pacotes necessarios
sudo tlmgr update --self
sudo tlmgr install circuitikz pgf standalone dvipng
```

**Opcao 2: MacTeX completo (~4GB)**
```bash
brew install --cask mactex

# Reinicie o terminal apos a instalacao
```

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install texlive-latex-base texlive-pictures texlive-latex-extra dvipng
```

#### Fedora/RHEL

```bash
sudo dnf install texlive-scheme-basic texlive-circuitikz texlive-standalone dvipng
```

#### Arch Linux

```bash
sudo pacman -S texlive-basic texlive-pictures texlive-latexextra
```

#### Windows

**Opcao 1: MiKTeX (recomendado)**
1. Baixe o instalador em: https://miktex.org/download
2. Execute o instalador e siga as instrucoes
3. Abra o MiKTeX Console e instale os pacotes: `circuitikz`, `pgf`, `standalone`

**Opcao 2: TeX Live**
1. Baixe em: https://tug.org/texlive/windows.html
2. Execute o instalador
3. Selecione os pacotes: `circuitikz`, `pgf`, `standalone`

#### Verificar instalacao

Apos instalar, verifique se o LaTeX esta funcionando:
```bash
just check
# Deve mostrar: ✓ LaTeX instalado

# Ou manualmente:
pdflatex --version
```

## Comandos (just)

### Setup

| Comando | Descricao |
|---------|-----------|
| `just setup` | Instala dependencias Python com uv |
| `just check` | Verifica se todas as dependencias estao instaladas |

### Simulacao

| Comando | Descricao |
|---------|-----------|
| `just sim <arquivo>` | Simula circuito (modo interativo) |
| `just sim-batch <arquivo>` | Simula circuito (modo batch) |
| `just sim-fundamentos` | Simula todos os circuitos de fundamentos |
| `just sim-filtros` | Simula todos os filtros |
| `just sim-osciladores` | Simula todos os osciladores |
| `just sim-all` | Simula TODOS os circuitos |

### Esquematicos

| Comando | Descricao |
|---------|-----------|
| `just schematic <arquivo>` | Gera esquematico PNG de um arquivo |
| `just schematic-verbose <arquivo>` | Gera com informacoes detalhadas |
| `just schematic-all` | Gera esquematicos de TODOS os circuitos |

### Graficos (CSV -> PNG)

| Comando | Descricao |
|---------|-----------|
| `just csv <arquivo>` | Converte CSV para PNG |
| `just csv-dir <diretorio>` | Converte todos CSVs de um diretorio |
| `just csv-all` | Converte TODOS os CSVs do projeto |

### Workflows Completos

| Comando | Descricao |
|---------|-----------|
| `just run <arquivo>` | Simula + converte CSVs |
| `just full <arquivo>` | Simula + CSVs + esquematico |
| `just full-all` | Workflow completo em TODOS os circuitos |

### Exemplos Rapidos

#### Fundamentos e Filtros
| Comando | Descricao |
|---------|-----------|
| `just exemplo-divisor` | Divisor de tensão |
| `just exemplo-filtro` | Filtro RC passa-baixa |

#### Osciladores
| Comando | Descricao |
|---------|-----------|
| `just exemplo-colpitts` | Oscilador Colpitts |
| `just exemplo-pierce` | Oscilador Pierce (JFET + cristal 10MHz) |
| `just exemplo-hartley` | Oscilador Hartley |
| `just exemplo-ring` | Oscilador Ring (3 e 5 estágios) |
| `just exemplo-vco` | VCO senoidal (varactor) |
| `just exemplo-multivibrador` | Multivibrador astável 10Hz |
| `just exemplo-osciladores-todos` | **Simula TODOS os osciladores** |

#### Amplificadores
| Comando | Descricao |
|---------|-----------|
| `just exemplo-classe-ab` | Amplificador Classe A/B Push-Pull |
| `just exemplo-jfet` | Amplificador JFET Self-Bias |

#### Amplificadores Operacionais
| Comando | Descricao |
|---------|-----------|
| `just exemplo-amp-op-inv` | Amp-Op Inversor |
| `just exemplo-integrador` | Amp-Op Integrador |

#### RF e Comunicações
| Comando | Descricao |
|---------|-----------|
| `just exemplo-mixer` | Mixer com Diodo |
| `just exemplo-am` | Modulador AM |
| `just exemplo-pll` | PLL (Phase-Locked Loop) |

#### Lógica Digital
| Comando | Descricao |
|---------|-----------|
| `just exemplo-cmos` | Portas Lógicas CMOS (7 portas) |

### Limpeza

| Comando | Descricao |
|---------|-----------|
| `just clean` | Remove todos os arquivos gerados |
| `just clean-csv` | Remove apenas CSVs |
| `just clean-png` | Remove apenas PNGs |

## Exemplos de Uso

### Simular um circuito especifico

```bash
# Modo interativo (com graficos)
just sim circuits/01_fundamentos/01_divisor_tensao.spice

# Modo batch (sem interface)
just sim-batch circuits/01_fundamentos/01_divisor_tensao.spice
```

### Gerar esquematico

```bash
just schematic circuits/01_fundamentos/01_divisor_tensao.spice
```

### Workflow completo

```bash
# Simula, gera graficos dos CSVs e esquematico
just full circuits/02_filtros/filtro_rc_passa_baixa.spice
```

### Processar todos os circuitos

```bash
just full-all
```

## Conteúdo dos Circuitos (24 circuitos)

### 00_esquematicos

Circuitos simples (sem subcircuitos) otimizados para geração de esquemáticos PNG.

| Arquivo | Descrição |
|---------|-----------|
| `divisor_tensao.spice` | Divisor de tensão básico (Vin-R1-R2-GND) |
| `divisor_corrente.spice` | Fonte de corrente com resistores em paralelo |
| `filtro_rc.spice` | Filtro RC passa-baixa simples |
| `amplificador_ec.spice` | Amplificador emissor comum com BC548 |

### 01_fundamentos

Circuitos didáticos com teoria explicada nos comentários e uso de subcircuitos.

| Arquivo | Descrição |
|---------|-----------|
| `01_divisor_tensao.spice` | Teoria completa e 3 exemplos de divisores de tensão |
| `02_divisor_corrente.spice` | Teoria completa e exemplos de divisores de corrente |

### 02_filtros

| Arquivo | Descrição |
|---------|-----------|
| `filtro_rc_passa_baixa.spice` | Filtro RC com análise Bode e sweep de parâmetros |

### 03_osciladores (6 circuitos)

| Arquivo | Descrição |
|---------|-----------|
| `colpitts_bc548.spice` | Oscilador Colpitts ~1MHz com transistor BC548 |
| `oscilador_ring.spice` | Oscilador Ring CMOS (3 e 5 estágios) |
| `oscilador_hartley.spice` | Oscilador Hartley com tanque LC indutivo |
| `oscilador_pierce_jfet.spice` | Oscilador Pierce com JFET e cristal 10MHz |
| `vco_senoidal.spice` | VCO (Voltage-Controlled Oscillator) com varactor |
| `multivibrador_astavel_10hz.spice` | Multivibrador astável clássico (onda quadrada) |

### 04_amplificadores (2 circuitos)

| Arquivo | Descrição |
|---------|-----------|
| `classe_ab_push_pull.spice` | Amplificador Classe A/B Push-Pull com análise THD |
| `amplificador_jfet_self_bias.spice` | Amplificador JFET (CS, SF, ganho controlado) |

### 05_amplificadores_operacionais (5 circuitos)

| Arquivo | Descrição |
|---------|-----------|
| `01_amp_op_inversor.spice` | Amplificador inversor (ganhos -10x, -1x, -0.1x) |
| `02_amp_op_nao_inversor.spice` | Não-inversor e buffer (ganhos +10x, +2x, +1x) |
| `03_amp_op_somador.spice` | Somador, mixer de áudio, DAC 3-bit |
| `04_amp_op_integrador.spice` | Integrador ideal, prático e com reset |
| `05_amp_op_comparador.spice` | Comparador, Schmitt trigger, janela, zero-crossing |

### 06_rf_comunicacoes (3 circuitos)

| Arquivo | Descrição |
|---------|-----------|
| `mixer_diodo.spice` | Mixer de frequência com diodo (simples e balanceado) |
| `modulador_am.spice` | Modulador AM (multiplicador, collector mod, DSB-SC) |
| `pll_completo.spice` | PLL (Phase-Locked Loop) completo com análise |

### 07_logica_digital_cmos (1 circuito)

| Arquivo | Descrição |
|---------|-----------|
| `portas_logicas_cmos.spice` | 7 portas lógicas CMOS (NOT, NAND, NOR, AND, OR, XOR, XNOR) |

## Scripts

### csv_to_png.py

Converte arquivos CSV gerados pelo ngspice em graficos PNG.

- Detecta automaticamente tipo de dados (tempo, frequencia, DC)
- Ajusta escalas (ms, us, ns; log para frequencia)
- Reconhece unidades pelos nomes das colunas

### spice_to_schematic.py

Gera esquematicos PNG a partir de arquivos SPICE usando **lcapy**.

Componentes suportados:
- **R** - Resistores
- **C** - Capacitores
- **L** - Indutores
- **D** - Diodos
- **Q** - BJT (NPN/PNP)
- **M** - MOSFET (NMOS/PMOS)
- **J** - JFET
- **V** - Fontes de tensao
- **I** - Fontes de corrente
- **X** - Subcircuitos / Op-Amps

## Documentacao

- [Tutorial SPICE](docs/tutorial_spice.md) - Tutorial completo da linguagem SPICE

## Referencias

- [Manual do ngspice](http://ngspice.sourceforge.net/docs.html)
- [lcapy Documentation](https://lcapy.readthedocs.io/)
- [Circuitikz Manual](https://ctan.org/pkg/circuitikz)

## Licenca

MIT - veja [LICENSE](LICENSE)
