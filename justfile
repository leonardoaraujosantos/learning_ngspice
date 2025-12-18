# Justfile para learning_ngspice
# Uso: just <comando>

# Variaveis
python := "uv run python"
ngspice := "ngspice"

# Comando padrao - mostra ajuda
default:
    @just --list

# =============================================================================
# SETUP
# =============================================================================

# Instala dependencias com uv
setup:
    uv sync
    @echo "Dependencias instaladas!"
    @echo "Certifique-se de ter ngspice e LaTeX instalados:"
    @echo "  macOS: brew install ngspice && brew install --cask mactex"
    @echo "  Ubuntu: sudo apt install ngspice texlive-pictures texlive-latex-extra"

# Verifica se todas as dependencias estao instaladas
check:
    @echo "Verificando dependencias..."
    @which ngspice > /dev/null && echo "✓ ngspice instalado" || echo "✗ ngspice NAO encontrado"
    @which pdflatex > /dev/null && echo "✓ LaTeX instalado" || echo "✗ LaTeX NAO encontrado (necessario para esquematicos)"
    @{{python}} -c "import matplotlib; print('✓ matplotlib', matplotlib.__version__)" 2>/dev/null || echo "✗ matplotlib NAO encontrado"
    @{{python}} -c "import numpy; print('✓ numpy', numpy.__version__)" 2>/dev/null || echo "✗ numpy NAO encontrado"

# =============================================================================
# SIMULACAO
# =============================================================================

# Simula um circuito especifico (modo interativo)
sim file:
    {{ngspice}} {{file}}

# Simula um circuito em modo batch (sem interface)
sim-batch file:
    {{ngspice}} -b {{file}}

# Simula todos os circuitos de fundamentos
sim-fundamentos:
    @echo "Simulando circuitos de fundamentos..."
    {{ngspice}} -b circuits/01_fundamentos/01_divisor_tensao.spice
    {{ngspice}} -b circuits/01_fundamentos/02_divisor_corrente.spice
    @echo "Concluido!"

# Simula todos os circuitos de filtros
sim-filtros:
    @echo "Simulando circuitos de filtros..."
    {{ngspice}} -b circuits/02_filtros/filtro_rc_passa_baixa.spice
    @echo "Concluido!"

# Simula todos os circuitos de osciladores
sim-osciladores:
    @echo "Simulando circuitos de osciladores..."
    {{ngspice}} -b circuits/03_osciladores/colpitts_bc548.spice
    @echo "Concluido!"

# Simula TODOS os circuitos do projeto
sim-all:
    @echo "Simulando TODOS os circuitos..."
    #!/usr/bin/env bash
    for file in circuits/*/*.spice; do \
        echo "Simulando $file..."; \
        {{ngspice}} -b "$file" || true; \
    done
    @echo "Todas as simulacoes concluidas!"

# =============================================================================
# ESQUEMATICOS
# =============================================================================

# Gera esquematico PNG de um arquivo SPICE
schematic file:
    {{python}} scripts/spice_to_schematic.py {{file}}

# Gera esquematico com modo verbose
schematic-verbose file:
    {{python}} scripts/spice_to_schematic.py -v {{file}}

# Gera esquematicos de todos os circuitos de fundamentos
schematic-fundamentos:
    @echo "Gerando esquematicos de fundamentos..."
    {{python}} scripts/spice_to_schematic.py circuits/01_fundamentos/

# Gera esquematicos de todos os circuitos de filtros
schematic-filtros:
    @echo "Gerando esquematicos de filtros..."
    {{python}} scripts/spice_to_schematic.py circuits/02_filtros/

# Gera esquematicos de todos os circuitos de osciladores
schematic-osciladores:
    @echo "Gerando esquematicos de osciladores..."
    {{python}} scripts/spice_to_schematic.py circuits/03_osciladores/

# Gera TODOS os esquematicos do projeto
schematic-all:
    @echo "Gerando TODOS os esquematicos..."
    {{python}} scripts/spice_to_schematic.py circuits/
    @echo "Todos os esquematicos gerados!"

# =============================================================================
# GRAFICOS CSV -> PNG
# =============================================================================

# Converte CSV para PNG
csv file:
    {{python}} scripts/csv_to_png.py {{file}}

# Converte todos os CSVs de um diretorio
csv-dir dir:
    {{python}} scripts/csv_to_png.py {{dir}}

# Converte todos os CSVs do projeto
csv-all:
    @echo "Convertendo todos os CSVs para PNG..."
    {{python}} scripts/csv_to_png.py circuits/
    @echo "Conversao concluida!"

# =============================================================================
# WORKFLOWS COMPLETOS
# =============================================================================

# Simula um circuito e gera graficos dos CSVs
run file:
    @echo "=== Simulando {{file}} ==="
    {{ngspice}} -b {{file}}
    @echo "=== Convertendo CSVs para PNG ==="
    {{python}} scripts/csv_to_png.py $(dirname {{file}})/
    @echo "=== Concluido! ==="

# Workflow completo: simula, gera CSVs->PNG e esquematico
full file:
    @echo "=== Workflow completo para {{file}} ==="
    @echo "1. Simulando..."
    {{ngspice}} -b {{file}}
    @echo "2. Gerando graficos dos CSVs..."
    {{python}} scripts/csv_to_png.py $(dirname {{file}})/ || true
    @echo "3. Gerando esquematico..."
    {{python}} scripts/spice_to_schematic.py {{file}}
    @echo "=== Workflow concluido! ==="

# Executa workflow completo em TODOS os circuitos
full-all:
    @echo "=== Workflow completo para todos os circuitos ==="
    just sim-all
    just csv-all
    just schematic-all
    @echo "=== Todos os workflows concluidos! ==="

# =============================================================================
# LIMPEZA
# =============================================================================

# Remove arquivos gerados (CSVs, PNGs, RAWs)
clean:
    @echo "Removendo arquivos gerados..."
    find circuits/ -name "*.csv" -delete 2>/dev/null || true
    find circuits/ -name "*.png" -delete 2>/dev/null || true
    find circuits/ -name "*.raw" -delete 2>/dev/null || true
    @echo "Limpeza concluida!"

# Remove apenas CSVs
clean-csv:
    find circuits/ -name "*.csv" -delete 2>/dev/null || true
    @echo "CSVs removidos!"

# Remove apenas PNGs
clean-png:
    find circuits/ -name "*.png" -delete 2>/dev/null || true
    @echo "PNGs removidos!"

# =============================================================================
# DESENVOLVIMENTO
# =============================================================================

# Formata codigo Python
fmt:
    uv run black scripts/

# Lint do codigo Python
lint:
    uv run ruff check scripts/

# Executa testes
test:
    uv run pytest

# =============================================================================
# EXEMPLOS RAPIDOS
# =============================================================================

# Exemplo: divisor de tensao
exemplo-divisor:
    @echo "=== Exemplo: Divisor de Tensao ==="
    just full circuits/01_fundamentos/01_divisor_tensao.spice

# Exemplo: filtro RC
exemplo-filtro:
    @echo "=== Exemplo: Filtro RC Passa-Baixa ==="
    just full circuits/02_filtros/filtro_rc_passa_baixa.spice

# Exemplo: oscilador Colpitts
exemplo-colpitts:
    @echo "=== Exemplo: Oscilador Colpitts ==="
    just full circuits/03_osciladores/colpitts_bc548.spice

# Exemplo: oscilador Pierce com JFET e cristal
exemplo-pierce:
    @echo "=== Exemplo: Oscilador Pierce (JFET + Cristal 10MHz) ==="
    just run circuits/03_osciladores/oscilador_pierce_jfet.spice

# Exemplo: oscilador Hartley
exemplo-hartley:
    @echo "=== Exemplo: Oscilador Hartley ==="
    just run circuits/03_osciladores/oscilador_hartley.spice

# Exemplo: oscilador Ring
exemplo-ring:
    @echo "=== Exemplo: Oscilador Ring (3 e 5 estagios) ==="
    just run circuits/03_osciladores/oscilador_ring.spice

# Exemplo: VCO senoidal
exemplo-vco:
    @echo "=== Exemplo: VCO Senoidal (controle por tensao) ==="
    just run circuits/03_osciladores/vco_senoidal.spice

# Exemplo: multivibrador astavel 10Hz
exemplo-multivibrador:
    @echo "=== Exemplo: Multivibrador Astavel 10Hz ==="
    just run circuits/03_osciladores/multivibrador_astavel_10hz.spice

# Exemplo: amplificador classe A/B
exemplo-classe-ab:
    @echo "=== Exemplo: Amplificador Classe A/B Push-Pull ==="
    just run circuits/04_amplificadores/classe_ab_push_pull.spice

# Exemplo: amplificador JFET
exemplo-jfet:
    @echo "=== Exemplo: Amplificador JFET Self-Bias ==="
    just run circuits/04_amplificadores/amplificador_jfet_self_bias.spice

# Exemplo: amp-op inversor
exemplo-amp-op-inv:
    @echo "=== Exemplo: Amplificador Operacional Inversor ==="
    just run circuits/05_amplificadores_operacionais/01_amp_op_inversor.spice

# Exemplo: amp-op integrador
exemplo-integrador:
    @echo "=== Exemplo: Amplificador Operacional Integrador ==="
    just run circuits/05_amplificadores_operacionais/04_amp_op_integrador.spice

# Exemplo: mixer com diodo
exemplo-mixer:
    @echo "=== Exemplo: Mixer de Frequencia (Diodo) ==="
    just run circuits/06_rf_comunicacoes/mixer_diodo.spice

# Exemplo: modulador AM
exemplo-am:
    @echo "=== Exemplo: Modulador AM ==="
    just run circuits/06_rf_comunicacoes/modulador_am.spice

# Exemplo: PLL completo
exemplo-pll:
    @echo "=== Exemplo: PLL (Phase-Locked Loop) ==="
    just run circuits/06_rf_comunicacoes/pll_completo.spice

# Exemplo: portas logicas CMOS
exemplo-cmos:
    @echo "=== Exemplo: Portas Logicas CMOS (7 portas) ==="
    just run circuits/07_logica_digital_cmos/portas_logicas_cmos.spice

# Exemplo: somador 4 bits digital
exemplo-somador:
    @echo "=== Exemplo: Somador 4 Bits Digital (Portas Ideais) ==="
    just run circuits/08_logica_digital/somador_4bits_digital.spice

# Exemplo: contador BCD 0-10 digital
exemplo-contador:
    @echo "=== Exemplo: Contador BCD 0-10 Digital (Portas Ideais) ==="
    just run circuits/08_logica_digital/contador_bcd_0_10.spice

# Exemplo: retificadores (meia onda, onda completa, ponte)
exemplo-retificadores:
    @echo "=== Exemplo: Retificadores (Meia Onda, Onda Completa, Ponte) ==="
    just run circuits/09_fontes_alimentacao/01_retificadores.spice

# Exemplo: reguladores de tensão (Zener, LM7805, LM317)
exemplo-reguladores:
    @echo "=== Exemplo: Reguladores de Tensao (Zener, LM7805, LM317) ==="
    just run circuits/09_fontes_alimentacao/02_reguladores_tensao.spice

# Exemplo: Timer 555 (astável, monostável, PWM)
exemplo-555:
    @echo "=== Exemplo: Timer 555 (Astavel, Monostavel, PWM) ==="
    just run circuits/10_timer_555/01_timer_555_astavel_monostavel_pwm.spice

# Exemplo: filtros ativos Sallen-Key
exemplo-sallen-key:
    @echo "=== Exemplo: Filtros Ativos Sallen-Key (Passa-Baixa, Passa-Alta) ==="
    just run circuits/11_filtros_ativos/01_sallen_key_passa_baixa_passa_alta.spice

# Exemplo: amplificador diferencial BJT
exemplo-diff-bjt:
    @echo "=== Exemplo: Amplificador Diferencial BJT ==="
    just run circuits/12_amplificadores_diferenciais/01_par_diferencial_bjt.spice

# Exemplo: amplificador diferencial JFET
exemplo-diff-jfet:
    @echo "=== Exemplo: Amplificador Diferencial JFET ==="
    just run circuits/12_amplificadores_diferenciais/02_par_diferencial_jfet.spice

# Exemplo: espelhos de corrente (BJT, JFET, MOSFET)
exemplo-espelhos:
    @echo "=== Exemplo: Espelhos de Corrente (BJT, JFET, MOSFET) ==="
    just run circuits/13_espelhos_corrente/01_espelhos_corrente_bjt_jfet_mosfet.spice

# Exemplo: conversores DC-DC Buck e Boost
exemplo-buck-boost:
    @echo "=== Exemplo: Conversores DC-DC (Buck 12V→5V e Boost 5V→12V) ==="
    just run circuits/14_conversores_dcdc/01_buck_boost_conversores.spice

# Exemplo: modulação e demodulação PWM
exemplo-pwm:
    @echo "=== Exemplo: Modulação e Demodulação PWM (AmpOp e JFET) ==="
    just run circuits/15_pwm_modulacao/01_pwm_modulador_demodulador.spice

# Simula todos os novos osciladores
exemplo-osciladores-todos:
    @echo "=== Simulando TODOS os osciladores ==="
    just exemplo-colpitts
    just exemplo-pierce
    just exemplo-hartley
    just exemplo-ring
    just exemplo-vco
    just exemplo-multivibrador
    @echo "=== Todos osciladores simulados! ==="
