# Learning ngspice

Repositorio dedicado ao aprendizado de simulacao de circuitos eletronicos usando **ngspice** e a linguagem **SPICE**.

## O que e ngspice?

O [ngspice](http://ngspice.sourceforge.net/) e um simulador de circuitos de codigo aberto baseado no SPICE (Simulation Program with Integrated Circuit Emphasis), originalmente desenvolvido na UC Berkeley. E amplamente utilizado para:

- Simulacao de circuitos analogicos e digitais
- Analise DC, AC e transiente
- Projeto e verificacao de circuitos antes da montagem fisica

## Estrutura do Projeto

```
learning_ngspice/
├── circuits/
│   ├── 01_fundamentos/        # Circuitos basicos
│   │   ├── 01_divisor_tensao.spice
│   │   └── 02_divisor_corrente.spice
│   ├── 02_filtros/            # Filtros passivos e ativos
│   │   └── filtro_rc_passa_baixa.spice
│   └── 03_osciladores/        # Circuitos osciladores
│       └── colpitts_bc548.spice
├── docs/                      # Documentacao e tutoriais
│   └── tutorial_spice.md
├── scripts/                   # Scripts utilitarios
│   └── csv_to_png.py          # Converte CSV para graficos PNG
├── LICENSE
└── README.md
```

## Pre-requisitos

### Instalacao do ngspice

**macOS (Homebrew):**
```bash
brew install ngspice
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ngspice
```

**Fedora:**
```bash
sudo dnf install ngspice
```

**Windows:**
Baixe o instalador em: http://ngspice.sourceforge.net/download.html

### Python (para scripts)

```bash
pip install matplotlib numpy
```

## Como Executar

### Modo interativo
```bash
ngspice circuits/01_fundamentos/01_divisor_tensao.spice
```

### Modo batch (sem interface)
```bash
ngspice -b circuits/01_fundamentos/01_divisor_tensao.spice
```

### Executar e sair automaticamente
```bash
ngspice -b -r output.raw circuits/01_fundamentos/01_divisor_tensao.spice
```

## Conteudo dos Exemplos

### 01_fundamentos

| Arquivo | Descricao |
|---------|-----------|
| `01_divisor_tensao.spice` | Teoria e exemplos praticos de divisores de tensao |
| `02_divisor_corrente.spice` | Teoria e exemplos de divisores de corrente |

### 02_filtros

| Arquivo | Descricao |
|---------|-----------|
| `filtro_rc_passa_baixa.spice` | Filtro RC com analise Bode, sweep de parametros e exportacao CSV |

### 03_osciladores

| Arquivo | Descricao |
|---------|-----------|
| `colpitts_bc548.spice` | Oscilador Colpitts ~1MHz com transistor BC548 |

## Documentacao

Consulte o tutorial completo da linguagem SPICE em:
- [Tutorial SPICE](docs/tutorial_spice.md)

## Scripts Utilitarios

### csv_to_png.py

Converte arquivos CSV gerados pelo ngspice em graficos PNG de alta qualidade.

```bash
# Processar todos os CSVs em circuits/
python scripts/csv_to_png.py

# Processar arquivo especifico
python scripts/csv_to_png.py circuits/01_fundamentos/divisor_tensao.csv

# Processar CSVs em um diretorio
python scripts/csv_to_png.py circuits/01_fundamentos/

# Modo verbose
python scripts/csv_to_png.py -v
```

O script detecta automaticamente:
- Tipo de dados (tempo, frequencia, DC sweep)
- Escala apropriada (ms, us, ns para tempo; log para frequencia)
- Unidades (V, mA, dB, graus)

## Comandos Uteis do ngspice

```spice
* Dentro do ngspice (modo interativo):
help              ; lista de comandos
source file.spice ; carrega um arquivo
run               ; executa a simulacao
plot v(out)       ; plota tensao no no 'out'
print all         ; imprime todos os valores
quit              ; sai do ngspice
```

## Referencias

- [Manual do ngspice](http://ngspice.sourceforge.net/docs.html)
- [SPICE Quick Reference](http://bwrcs.eecs.berkeley.edu/Classes/IcsBook/SPICE/)
- [ngspice User Manual (PDF)](http://ngspice.sourceforge.net/docs/ngspice-manual.pdf)

## Licenca

Este projeto esta licenciado sob a licenca MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
