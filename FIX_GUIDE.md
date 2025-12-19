# Guia de Correcao dos Circuitos com Problemas

Este documento fornece instrucoes detalhadas para corrigir os circuitos SPICE que apresentaram problemas durante a verificacao.

---

## Prioridade Alta

### 1. Retificadores (01_retificadores.spice)

**Problema:** Singular matrix no no `ac_fw2`, timestep too small

**Diagnostico:**
- O retificador onda completa center-tap esta causando problemas de convergencia
- Node `ac_fw2` provavelmente sem caminho DC para terra

**Solucao:**

```spice
* Adicionar ao circuito:

* 1. Resistencias de carga minimas em todos os retificadores
Rload_hw out_hw 0 1k
Rload_fw out_fw 0 1k
Rload_br out_br 0 1k

* 2. Ajustar opcoes de convergencia
.options reltol=0.01 abstol=1e-9 vntol=1e-4
.options gmin=1e-10 method=gear

* 3. Adicionar resistor pequeno em serie com diodos problemáticos
* (previne corrente infinita no instante de chaveamento)
Rseries_fw2 ct out_fw2 0.1

* 4. Aumentar timestep inicial
.tran 1u 100m 0 10u uic
```

**Alteracoes especificas:**
- Arquivo: `/Users/leonardoaraujo/work/learning_ngspice/circuits/09_fontes_alimentacao/01_retificadores.spice`
- Adicionar as linhas acima antes da secao `.control`
- Se o problema persistir, considerar usar modelo de diodo mais simples

---

### 2. Timer 555 (01_timer_555_astavel_monostavel_pwm.spice)

**Problema:** Timestep too small nos nos de controle (ctrl_ast, ctrl_pwm, ctrl_mono)

**Diagnostico:**
- Modelo do 555 com comparadores muito sensiveis
- Nos de controle sem resistencias de estabilizacao

**Solucao Opcao 1 (Rapida):**

```spice
* Adicionar resistencias de pull-up nos nos de controle
Rpullup_ast ctrl_ast vcc_ast 1Meg
Rpullup_pwm ctrl_pwm vcc_pwm 1Meg
Rpullup_mono ctrl_mono vcc_mono 1Meg

* Adicionar capacitores de bypass
Cbypass_ast ctrl_ast 0 10p
Cbypass_pwm ctrl_pwm 0 10p
Cbypass_mono ctrl_mono 0 10p

* Ajustar opcoes
.options method=gear maxord=2
.options reltol=0.001 abstol=1e-10
```

**Solucao Opcao 2 (Robusta):**
Substituir o modelo atual do 555 por um modelo macro mais estavel:

```spice
* Usar modelo do 555 da biblioteca Texas Instruments
.include models/LM555.lib

* Ou criar subcircuito simplificado:
.subckt 555_simple VCC GND TRIG OUT CTRL THRESH DISCH RST
* Implementacao simplificada com comparadores menos sensiveis
* (ver exemplo em circuits/models/555_macro.spice)
.ends
```

**Alteracoes especificas:**
- Arquivo: `/Users/leonardoaraujo/work/learning_ngspice/circuits/10_timer_555/01_timer_555_astavel_monostavel_pwm.spice`
- Adicionar resistencias e capacitores conforme opcao 1
- Se nao funcionar, implementar opcao 2 com modelo alternativo

---

### 3. DAC/ADC Sample & Hold (01_dac_adc_sample_hold.spice)

**Problema:** Sintaxe incorreta em comandos `.measure`

**Diagnostico:**
- Comando `meas tran vsh_hold1 v(v_sh_out) at=1.1m` incorreto
- Comando `when v(adc_b2)=2.5 cross=1 rise` faltando operador `=`

**Solucao:**

```spice
* ANTES (incorreto):
*meas tran vsh_hold1 v(v_sh_out) at=1.1m
*meas tran vadc_b2_trans when v(adc_b2)=2.5 cross=1 rise

* DEPOIS (correto):
meas tran vsh_hold1 find v(v_sh_out) at=1.1m
meas tran vsh_hold2 find v(v_sh_out) at=1.9m
meas tran sh_droop_rate param='abs(vsh_hold2 - vsh_hold1) / 0.8m'

meas tran vadc_b2_trans when v(adc_b2)=2.5 cross=1 rise=1
meas tran vadc_b1_trans when v(adc_b1)=2.5 cross=1 rise=1
meas tran vadc_b0_trans when v(adc_b0)=2.5 cross=1 rise=1
```

**Alteracoes especificas:**
- Arquivo: `/Users/leonardoaraujo/work/learning_ngspice/circuits/16_conversao_ad_da/01_dac_adc_sample_hold.spice`
- Substituir os comandos `.measure` incorretos pelos corretos acima
- Verificar se os nomes dos nos estao corretos (pode ser `v_sh_out` ou `sh_out`)

---

## Prioridade Media

### 4. Gilbert Cell Mixers

**Problema:** Erro ao salvar CSV em path relativo

**Solucao:**

```spice
* ANTES:
*wrdata circuits/06_rf_comunicacoes/gilbert_fixed_time.csv v(v_rf) v(v_lo) v(v_out)

* DEPOIS (opcao 1 - path absoluto):
wrdata /Users/leonardoaraujo/work/learning_ngspice/circuits/06_rf_comunicacoes/gilbert_fixed_time.csv v(v_rf) v(v_lo) v(v_out)

* DEPOIS (opcao 2 - remover salvamento):
* Comentar as linhas wrdata se nao precisar dos CSVs
*wrdata circuits/06_rf_comunicacoes/gilbert_fixed_time.csv v(v_rf) v(v_lo) v(v_out)
```

**Alteracoes especificas:**
- Arquivo: `circuits/06_rf_comunicacoes/gilbert_cell_mixer_fixed.spice`
- Arquivo: `circuits/06_rf_comunicacoes/gilbert_cell_mixer.spice`
- Substituir todos os `wrdata` com paths relativos

---

### 5. Amplificadores Diferenciais

**Problema:** Argument out of range for db

**Diagnostico:**
- Tentativa de calcular `vdb(vo1,vo2)` quando a diferenca e zero ou muito pequena
- Falta de excitacao diferencial na analise AC

**Solucao:**

```spice
* Garantir excitacao diferencial na analise AC:

* ANTES:
*vin1 vin1 0 ac 1
*vin2 vin2 0 ac 0

* DEPOIS:
vin1 vin1 0 ac 0.5
vin2 vin2 0 ac -0.5

* Ou usar fonte diferencial:
vin_diff vin1 vin2 ac 1

* Corrigir comando measure:
* ANTES:
*meas ac Ad_mag find vdb(vo1,vo2) at=1k

* DEPOIS (opcao 1 - verificar se ha sinal):
meas ac Ad_mag find vdb(vo1,vo2) at=1k when mag(v(vo1,vo2))>0.001

* DEPOIS (opcao 2 - calcular em escala linear primeiro):
meas ac vo_diff find v(vo1,vo2) at=1k
meas ac Ad_mag param='db(vo_diff)'
```

**Alteracoes especificas:**
- Arquivo: `circuits/12_amplificadores_diferenciais/01_par_diferencial_bjt.spice`
- Arquivo: `circuits/12_amplificadores_diferenciais/02_par_diferencial_jfet.spice`
- Corrigir excitacao AC e comandos measure

---

### 6. Filtro Passa-Banda/Notch

**Problema:** Measure fora do intervalo

**Solucao:**

```spice
* Verificar range da analise AC:
.ac dec 50 1 100k

* Ajustar comando measure para incluir range:
* ANTES:
*meas ac freq_bpn_peak when mag(v(out_bpn))=max

* DEPOIS:
meas ac freq_bpn_peak when mag(v(out_bpn))=max from=100 to=10k
```

**Alteracoes especificas:**
- Arquivo: `circuits/11_filtros_ativos/02_filtro_passa_banda_notch.spice`
- Ajustar range do comando measure ou range da analise AC

---

### 7. Adicionar Modelos Faltantes

**Para Reguladores de Tensao:**

```bash
# Criar arquivo de modelos
mkdir -p circuits/models

# Opcao 1: Usar modelos prontos
wget -O circuits/models/LM7805.lib "https://www.ti.com/lit/zip/slpm010"

# Opcao 2: Criar modelo simplificado
cat > circuits/models/regulators.lib << 'EOF'
* Modelo simplificado LM7805
.subckt LM7805 IN GND OUT
* Implementacao simplificada
R1 IN OUT 1k
D1 OUT 0 DMOD
V_ref OUT_internal 0 5.0
E1 OUT 0 OUT_internal 0 1
.model DMOD D
.ends
EOF
```

**Para Conversores DC-DC:**

```bash
# Adicionar modelos de MOSFETs de potencia
cat > circuits/models/power_mosfets.lib << 'EOF'
* IRF540 N-Channel Power MOSFET
.model IRF540 NMOS (Level=3 Vto=4 Kp=20u)

* IRF9540 P-Channel Power MOSFET
.model IRF9540 PMOS (Level=3 Vto=-4 Kp=10u)
EOF
```

**Para Logica Digital:**

```bash
# Adicionar modelos de flip-flops
cat > circuits/models/digital_logic.lib << 'EOF'
* Modelo de D Flip-Flop
.subckt DFF D CLK Q QB VDD GND
* Implementacao usando portas NAND
* (ver exemplo completo)
.ends

* Modelo de porta XOR
.subckt XOR A B OUT VDD GND
* Implementacao CMOS
.ends
EOF
```

**Incluir nos circuitos:**

```spice
.include circuits/models/regulators.lib
.include circuits/models/power_mosfets.lib
.include circuits/models/digital_logic.lib
```

---

## Prioridade Baixa

### 8. Esquematicos (00_esquematicos/)

**Problema:** Netlist incompleto para modo batch

**Opcao 1:** Deixar como estao (arquivos de referencia)

**Opcao 2:** Adicionar secao .control para simulacao batch

```spice
* Adicionar ao final de cada arquivo:

.control
* Para divisor de tensao:
op
print v(out)

* Para amplificador:
op
ac dec 50 10 100k
plot vdb(out)

* Para filtro:
ac dec 50 1 100k
plot vdb(out)
.endc

.end
```

---

## Comandos de Teste

Apos aplicar as correcoes, execute:

```bash
# Testar circuito especifico
cd circuits/09_fontes_alimentacao
ngspice -b 01_retificadores.spice

# Testar todos os circuitos novamente
python3 /tmp/check_all_circuits.py

# Verificar apenas circuitos corrigidos
for circuit in circuits/09_fontes_alimentacao/*.spice circuits/10_timer_555/*.spice circuits/16_conversao_ad_da/*.spice; do
    echo "Testing $circuit..."
    ngspice -b "$circuit" 2>&1 | grep -i "error\|done"
done
```

---

## Checklist de Correcao

- [ ] 01_retificadores.spice - Adicionar resistencias de carga
- [ ] 01_timer_555_astavel_monostavel_pwm.spice - Adicionar resistencias de controle
- [ ] 01_dac_adc_sample_hold.spice - Corrigir sintaxe .measure
- [ ] Gilbert Cell mixers - Corrigir paths CSV
- [ ] Amplificadores diferenciais - Corrigir excitacao AC
- [ ] Filtro passa-banda/notch - Ajustar range measure
- [ ] Adicionar modelos de reguladores
- [ ] Adicionar modelos de MOSFETs de potencia
- [ ] Adicionar modelos de logica digital
- [ ] Re-executar verificacao completa
- [ ] Atualizar documentacao

---

## Referencias

- [Ngspice Manual](https://ngspice.sourceforge.io/docs/ngspice-manual.pdf)
- [Convergence Problems in SPICE](https://www.seas.upenn.edu/~jan/spice/spice.overview.html)
- [555 Timer Models](https://www.ti.com/product/LM555)
- [Power MOSFET Models](https://www.infineon.com/cms/en/product/power/mosfet/)

---

**Ultima atualizacao:** 2025-12-18
