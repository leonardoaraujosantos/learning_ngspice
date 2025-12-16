# Learning ngspice

Repositorio para aprendizado de simulacao de circuitos eletronicos usando **ngspice** e a linguagem **SPICE**.

## Estrutura do Projeto

```
learning_ngspice/
├── circuits/
│   ├── 01_fundamentos/           # Circuitos basicos
│   │   ├── 01_divisor_tensao.spice
│   │   └── 02_divisor_corrente.spice
│   ├── 02_filtros/               # Filtros passivos e ativos
│   │   └── filtro_rc_passa_baixa.spice
│   └── 03_osciladores/           # Circuitos osciladores
│       └── colpitts_bc548.spice
├── docs/
│   └── tutorial_spice.md         # Tutorial completo da linguagem SPICE
├── scripts/
│   ├── csv_to_png.py             # Converte CSV para graficos PNG
│   └── spice_to_schematic.py     # Gera esquematico PNG (usa lcapy)
├── justfile                      # Comandos de automacao
├── pyproject.toml                # Dependencias Python (uv)
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

**macOS:**
```bash
brew install --cask mactex
```

**Ubuntu/Debian:**
```bash
sudo apt install texlive-pictures texlive-latex-extra
```

**Windows:**
Instale MiKTeX: https://miktex.org/download

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

| Comando | Descricao |
|---------|-----------|
| `just exemplo-divisor` | Exemplo: divisor de tensao |
| `just exemplo-filtro` | Exemplo: filtro RC passa-baixa |
| `just exemplo-colpitts` | Exemplo: oscilador Colpitts |

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

## Conteudo dos Circuitos

### 01_fundamentos

| Arquivo | Descricao |
|---------|-----------|
| `01_divisor_tensao.spice` | Teoria e exemplos de divisores de tensao |
| `02_divisor_corrente.spice` | Teoria e exemplos de divisores de corrente |

### 02_filtros

| Arquivo | Descricao |
|---------|-----------|
| `filtro_rc_passa_baixa.spice` | Filtro RC com analise Bode e sweep |

### 03_osciladores

| Arquivo | Descricao |
|---------|-----------|
| `colpitts_bc548.spice` | Oscilador Colpitts ~1MHz com BC548 |

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
