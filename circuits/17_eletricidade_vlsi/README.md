# Verilog-A Examples with ngspice

Este diretório contém exemplos de modelos de dispositivos customizados escritos em **Verilog-A** para uso com **ngspice** através do suporte OSDI (Open Source Device Interface).

## O que é Verilog-A?

**Verilog-A** é uma linguagem de descrição de hardware (HDL) especializada para modelagem de sistemas analógicos e mixed-signal. Com ela você pode:

- Criar modelos personalizados de dispositivos semicondutores
- Implementar equações comportamentais complexas
- Simular dispositivos não-lineares, dependentes de temperatura, etc.
- Reutilizar modelos entre diferentes simuladores SPICE

## Pré-requisitos

### 1. OpenVAF (compilador Verilog-A)

OpenVAF é o compilador open-source que transforma código Verilog-A em módulos OSDI (.osdi) que o ngspice pode carregar.

**Instalação:**
```bash
# Linux/macOS
curl -L https://openva.akira.rip/install.sh | sh

# Verificar instalação
openvaf --version
```

**Documentação:** https://openvaf.semimod.de/

### 2. ngspice com suporte OSDI

O ngspice precisa ser compilado com suporte a OSDI habilitado.

**Ubuntu/Debian:**
```bash
# Instalar dependências
sudo apt install libffi-dev

# Compilar ngspice do source com OSDI
git clone https://git.code.sf.net/p/ngspice/ngspice
cd ngspice
./autogen.sh
./configure --enable-xspice --enable-cider --enable-openmp --enable-osdi
make -j$(nproc)
sudo make install
```

**Verificar suporte OSDI:**
```bash
ngspice -v | grep -i osdi
# Deve mostrar: OSDI=yes
```

## Estrutura do Diretório

```
17_eletricidade_vlsi/
├── verilog-a/                    # Módulos Verilog-A (.va)
│   ├── diodo_simples.va          # Modelo de diodo (equação de Shockley)
│   ├── resistor_naolinear.va     # Resistor não-linear R(V) = R0*(1+α*V²)
│   ├── varactor.va               # Capacitor variável C(V) para VCOs
│   ├── res_model.va              # Resistor simples (teste básico)
│   └── test_simple.va            # Resistor minimalista (debug)
├── analise_nodal*.cir            # Circuitos de análise nodal (não usam Verilog-A)
├── teste_diodo*.cir              # Testes do modelo diodo_simples
├── teste_resistor_naolinear.cir  # Teste do resistor não-linear
├── vco_varactor.cir              # VCO usando modelo varactor
├── retificador_meia_onda.cir     # Retificador (pode usar diodo Verilog-A)
├── rc_lowpass.cir                # Filtro RC (análise básica)
├── lc_switch.cir                 # Circuito LC com chaveamento
└── README.md                     # Este arquivo
```

## Módulos Verilog-A Disponíveis

### 1. diodo_simples.va

**Descrição:** Modelo de diodo baseado na equação de Shockley com capacitância de junção variável.

**Equação:** `I = Is * (exp(V/(n*Vt)) - 1)`

**Parâmetros:**
- `Is` - Corrente de saturação (padrão: 1e-14 A)
- `n` - Coeficiente de emissão (padrão: 1.0)
- `Rs` - Resistência série (padrão: 0 Ω)
- `Cj0` - Capacitância de junção em V=0 (padrão: 0 F)
- `Vj` - Potencial de junção (padrão: 0.7 V)
- `m` - Coeficiente de gradação (padrão: 0.5)

**Compilar:**
```bash
cd verilog-a
openvaf diodo_simples.va
# Gera: diodo_simples.osdi
```

**Uso em SPICE:**
```spice
.pre_osdi verilog-a/diodo_simples.osdi
D1 anode cathode diodo_simples Is=1e-14 n=1.0 Rs=10 Cj0=10p
```

**Exemplo:** `teste_diodo.cir`

---

### 2. resistor_naolinear.va

**Descrição:** Resistor com resistência dependente da tensão aplicada e temperatura.

**Equação:** `R(V,T) = R0 * (1 + tc1*ΔT + tc2*ΔT²) * (1 + α*V²)`

**Parâmetros:**
- `R0` - Resistência nominal (padrão: 1kΩ)
- `alpha` - Coeficiente não-linear (padrão: 0.001 V⁻²)
- `tc1` - Coeficiente de temperatura linear (padrão: 0)
- `tc2` - Coeficiente de temperatura quadrático (padrão: 0)

**Compilar:**
```bash
cd verilog-a
openvaf resistor_naolinear.va
# Gera: resistor_naolinear.osdi
```

**Uso em SPICE:**
```spice
.pre_osdi verilog-a/resistor_naolinear.osdi
Rnl n1 n2 resistor_naolinear R0=1k alpha=0.001 tc1=0.003
```

**Exemplo:** `teste_resistor_naolinear.cir`

---

### 3. varactor.va

**Descrição:** Capacitor variável (varicap) para VCOs e circuitos sintonizáveis.

**Equação:**
- Polarização reversa (V<0): `C = C0 / (1 - V/Vj)^m`
- Polarização direta (V≥0): `C = C0 * (1 + m*V/Vj)`

**Parâmetros:**
- `C0` - Capacitância em V=0 (padrão: 10pF)
- `Vj` - Tensão de junção (padrão: 0.7 V)
- `m` - Coeficiente de gradação (padrão: 0.5)
- `Cmin` - Capacitância mínima (padrão: 1pF)
- `Cmax` - Capacitância máxima (padrão: 100pF)

**Compilar:**
```bash
cd verilog-a
openvaf varactor.va
# Gera: varactor.osdi
```

**Uso em SPICE:**
```spice
.pre_osdi verilog-a/varactor.osdi
Cvar n1 n2 varactor C0=50p Vj=0.7 m=0.5 Cmin=10p Cmax=200p
```

**Exemplo:** `vco_varactor.cir`

---

### 4. res_model.va & test_simple.va

**Descrição:** Modelos de resistor simples para teste básico de compilação e integração OSDI.

**Uso:** Testes de depuração da toolchain OpenVAF + ngspice.

## Workflow Completo

### 1. Compilar Modelo Verilog-A

```bash
cd verilog-a
openvaf diodo_simples.va
```

Isso gera `diodo_simples.osdi` no mesmo diretório.

### 2. Criar Circuito SPICE

```spice
* teste_meu_diodo.cir
.title Teste de Diodo Verilog-A

* Carregar modelo compilado
.pre_osdi verilog-a/diodo_simples.osdi

* Circuito
Vin in 0 DC 0
D1 in out diodo_simples Is=1e-14 n=1.0
Rload out 0 1k

* Análise DC sweep
.dc Vin -1 1 0.01

.control
  run
  plot i(Vin) vs v(in) title 'Curva I-V do Diodo'
.endc

.end
```

### 3. Simular

```bash
ngspice teste_meu_diodo.cir
```

## Exemplos Prontos

### Teste de Diodo (curva I-V e retificador)

```bash
cd circuits/17_eletricidade_vlsi
openvaf verilog-a/diodo_simples.va
ngspice teste_diodo.cir
```

**O que faz:**
- Análise DC: curva I-V característica (-1V a +1V)
- Análise transiente: retificador de meia onda com filtro capacitivo
- Medições automáticas: tensão de pico, ripple, correntes

### Teste de Resistor Não-Linear

```bash
cd circuits/17_eletricidade_vlsi
openvaf verilog-a/resistor_naolinear.va
ngspice teste_resistor_naolinear.cir
```

**O que faz:**
- Varre tensão de -10V a +10V
- Plota resistência instantânea vs tensão
- Demonstra comportamento não-linear R(V²)

### VCO com Varactor

```bash
cd circuits/17_eletricidade_vlsi
openvaf verilog-a/varactor.va
ngspice vco_varactor.cir
```

**O que faz:**
- Oscilador Colpitts com varactor Verilog-A
- Varre tensão de controle (0V a 5V)
- Mede frequência de oscilação para cada tensão
- Análise FFT do espectro

## Troubleshooting

### Erro: "unknown device type osdi"

**Causa:** ngspice não foi compilado com suporte OSDI.

**Solução:**
```bash
ngspice -v | grep -i osdi
# Se não mostrar OSDI=yes, recompilar ngspice:
./configure --enable-osdi --enable-openmp
make && sudo make install
```

### Erro: "Cannot open shared library"

**Causa:** O arquivo .osdi não está no caminho correto.

**Solução:**
- Usar caminho absoluto ou relativo correto no `.pre_osdi`
- Verificar se o arquivo .osdi existe:
  ```bash
  ls -l verilog-a/*.osdi
  ```

### Erro de Convergência

**Causas comuns:**
- Parâmetros irrealistas (Ex: `Is=1e-50`)
- Falta de condições iniciais `.ic`
- Timestep muito grande

**Soluções:**
```spice
* Adicionar condições iniciais
.ic v(node)=valor

* Ajustar timestep
.tran 0.1u 100u uic

* Usar parâmetros mais conservadores
.options reltol=1e-4 abstol=1e-10 vntol=1e-4
```

### OpenVAF não encontra `constants.vams` ou `disciplines.vams`

**Causa:** Arquivos de include do Verilog-A não estão no path.

**Solução:**
```bash
# OpenVAF geralmente inclui esses arquivos automaticamente
# Se necessário, copiar de:
# https://github.com/Qucs/ADMS/tree/master/admsXml

# Ou comentar os includes se não forem usados:
# //`include "constants.vams"
# //`include "disciplines.vams"
```

## Recursos e Referências

### Documentação Verilog-A
- [Verilog-A Language Reference Manual](https://www.eda.org/verilog-ams/)
- [OpenVAF Documentation](https://openvaf.semimod.de/docs/)
- [Verilog-A Tutorial (UC Berkeley)](https://bwrcs.eecs.berkeley.edu/Classes/icdesign/ee242_02/verilog-a-tutorial.pdf)

### ngspice + OSDI
- [ngspice Manual - Chapter OSDI](http://ngspice.sourceforge.net/docs/ngspice-manual.pdf)
- [OSDI Specification](https://github.com/dwarning/OpenVAF/wiki/OSDI)

### Exemplos Verilog-A
- [Repositório OpenVAF Examples](https://github.com/pascalkuthe/OpenVAF/tree/master/integration_tests/BSIM)
- [Verilog-A Model Library](https://www.designers-guide.org/verilog-ams/)

## Outros Circuitos no Diretório

Este diretório também contém circuitos que **não** usam Verilog-A, mas demonstram conceitos de análise nodal e circuitos para ensino de Eletricidade VLSI:

| Arquivo | Descrição |
|---------|-----------|
| `analise_nodal.cir` | Demonstração de análise nodal básica |
| `analise_nodal_modificada.cir` | Análise nodal modificada (com fontes de tensão) |
| `analise_nodal_modificada_BJT.cir` | Análise nodal com transistor BJT |
| `rc_lowpass.cir` | Filtro RC passa-baixa (análise AC) |
| `rlc_lowpass.cir` | Filtro RLC passa-baixa |
| `lc_switch.cir` | Circuito LC com chaveamento |
| `retificador_meia_onda.cir` | Retificador usando modelo de diodo padrão ngspice |

## Contribuindo

Para adicionar novos modelos Verilog-A:

1. Criar arquivo `.va` em `verilog-a/`
2. Adicionar comentários explicativos (equações, parâmetros)
3. Compilar com OpenVAF
4. Criar circuito de teste `.cir`
5. Documentar neste README

## Licença

MIT - veja [LICENSE](../../LICENSE) na raiz do repositório.
