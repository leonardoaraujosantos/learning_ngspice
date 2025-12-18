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
│   ├── 06_rf_comunicacoes/                 # RF (4 circuitos)
│   │   ├── mixer_diodo.spice               # Mixer de frequência
│   │   ├── modulador_am.spice              # AM (3 topologias)
│   │   ├── pll_completo.spice              # Phase-Locked Loop
│   │   └── gilbert_cell_mixer.spice        # Gilbert Cell (1MHz × 100Hz)
│   ├── 07_logica_digital_cmos/             # Lógica CMOS (1 circuito)
│   │   └── portas_logicas_cmos.spice       # 7 portas (NOT a XNOR)
│   ├── 08_logica_digital/                  # Lógica Digital Comportamental (2 circuitos)
│   │   ├── somador_4bits_digital.spice     # Somador 4 bits com portas ideais
│   │   └── contador_bcd_0_10.spice         # Contador BCD 0-10 com reset
│   ├── 09_fontes_alimentacao/              # Fontes e Reguladores (2 circuitos)
│   │   ├── 01_retificadores.spice          # Meia onda, onda completa, ponte
│   │   └── 02_reguladores_tensao.spice     # Zener, LM7805, LM317
│   ├── 10_timer_555/                       # Timer 555 (1 circuito)
│   │   └── 01_timer_555_astavel_monostavel_pwm.spice  # 3 modos
│   ├── 11_filtros_ativos/                  # Filtros Ativos (2 circuitos)
│   │   ├── 01_sallen_key_passa_baixa_passa_alta.spice  # 2ª ordem
│   │   └── 02_filtro_passa_banda_notch.spice          # Passa-banda e Notch 60Hz
│   ├── 12_amplificadores_diferenciais/     # Amplificadores Diferenciais (2 circuitos)
│   │   ├── 01_par_diferencial_bjt.spice    # Par diferencial BJT
│   │   └── 02_par_diferencial_jfet.spice   # Par diferencial JFET
│   ├── 13_espelhos_corrente/               # Espelhos de Corrente (1 circuito)
│   │   └── 01_espelhos_corrente_bjt_jfet_mosfet.spice  # BJT, JFET, MOSFET
│   ├── 14_conversores_dcdc/                # Conversores DC-DC (1 circuito)
│   │   └── 01_buck_boost_conversores.spice # Buck (12V→5V) e Boost (5V→12V)
│   ├── 15_pwm_modulacao/                   # Modulação PWM (1 circuito)
│   │   └── 01_pwm_modulador_demodulador.spice # Modulador e demodulador PWM
│   └── 16_conversao_ad_da/                 # Conversão A/D e D/A (1 circuito)
│       └── 01_dac_adc_sample_hold.spice    # DAC, ADC e Sample & Hold
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

O script `spice_to_schematic.py` usa **LaTeX + circuitikz** para gerar esquematicos profissionais.
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
| `just exemplo-gilbert` | **Gilbert Cell Mixer (1MHz×100Hz, FFT detalhado)** |

#### Lógica Digital
| Comando | Descricao |
|---------|-----------|
| `just exemplo-cmos` | Portas Lógicas CMOS (7 portas) |
| `just exemplo-somador` | Somador 4 Bits Digital (portas ideais) |
| `just exemplo-contador` | Contador BCD 0-10 Digital (portas ideais) |

#### Fontes de Alimentação
| Comando | Descricao |
|---------|-----------|
| `just exemplo-retificadores` | Retificadores (meia onda, onda completa, ponte) |
| `just exemplo-reguladores` | Reguladores de Tensão (Zener, LM7805, LM317) |

#### Timer 555
| Comando | Descricao |
|---------|-----------|
| `just exemplo-555` | Timer 555 (astável, monostável, PWM) |

#### Filtros Ativos
| Comando | Descricao |
|---------|-----------|
| `just exemplo-sallen-key` | Filtros Sallen-Key (passa-baixa, passa-alta) |

#### Amplificadores Diferenciais
| Comando | Descricao |
|---------|-----------|
| `just exemplo-diff-bjt` | Amplificador Diferencial BJT |
| `just exemplo-diff-jfet` | Amplificador Diferencial JFET |

#### Espelhos de Corrente
| Comando | Descricao |
|---------|-----------|
| `just exemplo-espelhos` | Espelhos de Corrente (BJT, JFET, MOSFET) |

#### Conversores DC-DC
| Comando | Descricao |
|---------|-----------|
| `just exemplo-buck-boost` | Conversores Buck (12V→5V) e Boost (5V→12V) |

#### Modulação PWM
| Comando | Descricao |
|---------|-----------|
| `just exemplo-pwm` | Modulador e Demodulador PWM (com AmpOp e JFET) |

#### Conversão A/D e D/A
| Comando | Descricao |
|---------|-----------|
| `just exemplo-ad-da` | DAC R-2R 4-bit, ADC Flash 3-bit e Sample & Hold |

#### Filtros Especiais
| Comando | Descricao |
|---------|-----------|
| `just exemplo-filtros-especiais` | Filtros Passa-Banda e Notch 60Hz |

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

## Conteúdo dos Circuitos (38 circuitos)

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

### 06_rf_comunicacoes (4 circuitos)

| Arquivo | Descrição |
|---------|-----------|
| `mixer_diodo.spice` | Mixer de frequência com diodo (simples e balanceado) |
| `modulador_am.spice` | Modulador AM (multiplicador, collector mod, DSB-SC) |
| `pll_completo.spice` | PLL (Phase-Locked Loop) completo com análise |
| `gilbert_cell_mixer.spice` | Gilbert Cell (mixer multiplicador BJT, 1MHz×100Hz, análise FFT completa) |

### 07_logica_digital_cmos (1 circuito)

| Arquivo | Descrição |
|---------|-----------|
| `portas_logicas_cmos.spice` | 7 portas lógicas CMOS (NOT, NAND, NOR, AND, OR, XOR, XNOR) |

### 08_logica_digital (2 circuitos)

Circuitos digitais puros usando portas lógicas comportamentais (B-sources).

| Arquivo | Descrição |
|---------|-----------|
| `somador_4bits_digital.spice` | Somador binário de 4 bits com full adders (portas XOR, AND, OR) |
| `contador_bcd_0_10.spice` | Contador BCD com reset automático em 10 (detector de estado + reset) |

### 09_fontes_alimentacao (2 circuitos)

Retificadores e reguladores de tensão para fontes de alimentação.

| Arquivo | Descrição |
|---------|-----------|
| `01_retificadores.spice` | Meia onda, onda completa e ponte retificadora (com/sem filtro capacitivo) |
| `02_reguladores_tensao.spice` | Reguladores Zener, LM7805 (5V fixo) e LM317 (ajustável 1.25-37V) |

### 10_timer_555 (1 circuito)

O icônico CI 555 em suas três configurações principais.

| Arquivo | Descrição |
|---------|-----------|
| `01_timer_555_astavel_monostavel_pwm.spice` | Astável (oscilador), monostável (one-shot) e PWM |

### 11_filtros_ativos (2 circuitos)

Filtros ativos de 2ª ordem usando amplificadores operacionais.

| Arquivo | Descrição |
|---------|-----------|
| `01_sallen_key_passa_baixa_passa_alta.spice` | Topologia Sallen-Key Butterworth (fc=1kHz) |
| `02_filtro_passa_banda_notch.spice` | Filtro passa-banda (250Hz-2kHz) e Notch 60Hz (Twin-T) |

### 12_amplificadores_diferenciais (2 circuitos)

Pares diferenciais - blocos fundamentais de amplificadores operacionais.

| Arquivo | Descrição |
|---------|-----------|
| `01_par_diferencial_bjt.spice` | Par diferencial com BJT (BC547), alta CMRR, configurações variadas |
| `02_par_diferencial_jfet.spice` | Par diferencial com JFET (2N5457), altíssima impedância de entrada |

### 13_espelhos_corrente (1 circuito)

Espelhos de corrente - replicação precisa de correntes.

| Arquivo | Descrição |
|---------|-----------|
| `01_espelhos_corrente_bjt_jfet_mosfet.spice` | Espelhos simples e Wilson (BJT), JFET e MOSFET com razões |

### 14_conversores_dcdc (1 circuito)

Conversores DC-DC fundamentais para regulação de tensão.

| Arquivo | Descrição |
|---------|-----------|
| `01_buck_boost_conversores.spice` | Buck (12V→5V step-down) e Boost (5V→12V step-up) com análise de eficiência |

### 15_pwm_modulacao (1 circuito)

Modulação e demodulação PWM (Pulse Width Modulation) para amplificadores classe D.

| Arquivo | Descrição |
|---------|-----------|
| `01_pwm_modulador_demodulador.spice` | Modulador PWM com comparador e carrier 20kHz, buffer JFET, demodulador com filtro ativo |

### 16_conversao_ad_da (1 circuito)

Conversão entre sinais analógicos e digitais - fundamentos de sistemas digitais.

| Arquivo | Descrição |
|---------|-----------|
| `01_dac_adc_sample_hold.spice` | DAC R-2R 4-bit, ADC Flash 3-bit (7 comparadores), Sample & Hold com JFET |

## Scripts

### csv_to_png.py

Converte arquivos CSV gerados pelo ngspice em graficos PNG.

- Detecta automaticamente tipo de dados (tempo, frequencia, DC)
- Ajusta escalas (ms, us, ns; log para frequencia)
- Reconhece unidades pelos nomes das colunas

### spice_to_schematic.py

Gera esquematicos PNG a partir de arquivos SPICE usando **LaTeX + circuitikz**.

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
- [Guia de Troubleshooting](docs/troubleshooting.md) - Solucoes para erros comuns no ngspice

## Referencias

- [Manual do ngspice](http://ngspice.sourceforge.net/docs.html)
- [Circuitikz Manual](https://ctan.org/pkg/circuitikz)

## Licenca

MIT - veja [LICENSE](LICENSE)
