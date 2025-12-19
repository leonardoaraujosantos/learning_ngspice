# Lista de Exercícios Práticos — Eletrônica Analógica (ngspice)

Use estes projetos para praticar o que está no `eletronica_analogica.pdf` e no `tutorial_spice.md`. Todos devem ser simulados no ngspice (modo interativo ou batch) e documentados com capturas ou exportações (`wrdata`, `hardcopy`).

## 1) Pré-amplificador JFET (Self-bias)
- Monte um pré de pequenos sinais com JFET (2N5457) em source comum, auto-polarizado (resistor no source, gate em 0 V com resistor alto).
- Alvo: ganho de tensão |Av| ≈ 5–10, Zin ≥ 500 kΩ, banda de áudio (20 Hz–20 kHz) com variação < 1 dB.
- Plote Bode (magnitude/fase) e exporte os valores de ganho e Zin.
- Confirme ponto Q (Id e Vds) com `.op`.

## 2) Amplificador BJT Emissor Comum com Bypass Parcial
- BC548 em emissor comum, divisor de base, resistor de emissor com capacitor de bypass parcial.
- Alvo: ganho midband ≈ 40–60 (32–35 dB) com VCC = 12 V, RL = 10 kΩ.
- Plote ganho vs frequência e verifique o efeito do capacitor de bypass.
- Meça VCE, IC, Av midband e Zout aproximada.

## 3) Par Diferencial BJT com Cauda de Corrente (Espelho)
- Par diferencial NPN (BC548) com fonte de corrente feita por espelho BJT.
- Injete sinais diferenciais e comuns; meça Ad e CMRR a 1 kHz.
- Plote curva de transferência Vout vs (Vin+ – Vin−) e `db(v(out))` em AC.
- Avalie compliance do espelho (quando satura).

## 4) Amplificador Classe AB de Saída (Seguidor de Emissor)
- Push-pull NPN/PNP (BC548/BC558) com polarização por diodos ou VBE multiplier.
- Alvo: baixa distorção para 1 Vrms @ 1 kHz em carga 1 kΩ.
- Meça THD (via FFT) com e sem resistores de emissor de 22–47 Ω.
- Verifique dissipação em repouso (IBias).

## 5) Oscilador Colpitts com BJT
- Colpitts em emissor comum (BC548), LC ajustado para ~100 kHz.
- Provoque start-up com `uic` ou IC em capacitor.
- Plote amplitude estável, frequência e espectro (FFT) após regime.
- Verifique margem de ganho ajustando divisor capacitivo (C1/C2) ou resistência de feedback.

## 6) Oscilador Hartley com JFET
- Hartley com JFET (2N5457), self-bias no source, L1+L2 para ~100 kHz.
- Adicione resistor de dreno alto (ou choke) e capacitor de acoplamento de saída.
- Meça frequência, amplitude e impacto do valor de Rs (ganho/estabilidade).

## 7) Driver MOSFET de Carga Indutiva com Proteção
- NMOS de potência genérico (ex.: IRLZ44N) chaveando indutor/solenoide de 1–10 mH.
- Use Vpulse de 0–10 V, 1 kHz, duty 50%.
- Inclua diodo flyback rápido e snubber RC em paralelo com a carga.
- Plote Vds, Id, tensão na carga e corrente no diodo; mostre redução de overshoot com snubber.

## 8) Filtro Ativo Sallen-Key (2ª ordem) com Op-Amp
- Filtro passa-baixa de 2ª ordem, f0 = 10 kHz, Q ≈ 0.707 (Butterworth).
- Use op-amp ideal ou modelo de LM741/LM358; compare resposta ideal vs real.
- Plote Bode (ganho/fase), step response e ruído de saída (`.noise`).

## 9) Rede RC Passa-Fase para Oscilador (Phase Shift)
- Monte rede 3×RC igual e combine com amplificador inversor (BJT ou op-amp).
- Alvo: 200 Hz; ajuste ganho mínimo (≈29) para start-up.
- Mostre defasagem total ≈ 180° na frequência de oscilação e ganho de loop ≥ 1.

## 10) Projeto de PLL Simples (CD4046 ou Macro-Modelo)
- Use modelo comportamental do CD4046 ou blocos ideais: PFD, filtro RC de 1ª ordem, VCO (controlado por corrente/atraso).
- Alvo: travar de 10 kHz para 40 kHz com N=4 (divisor).
- Plote erro de fase vs tempo, frequência do VCO e tensão do filtro de loop.
- Estime largura de banda do loop e tempo de lock.

## 11) Regulador de Tensão Linear Discreto
- Monte regulador série com transistor de passagem (NPN ou Darlington), zener de referência e divisor de realimentação.
- Alvo: Vout = 5 V estável para Vin = 9–15 V, carga 0–100 mA.
- Meça regulação de linha (ΔVout/ΔVin) e regulação de carga (ΔVout/ΔIout).
- Plote Vout vs Vin (varredura DC) e resposta transitória a degrau de carga.

## 12) Comparador com Histerese (Schmitt Trigger)
- Schmitt Trigger com op-amp (LM741 ou ideal) e realimentação positiva resistiva.
- Alvo: VTH+ = 3.3 V, VTH- = 1.7 V (histerese ~1.6 V) com VCC = ±12 V.
- Plote curva de transferência Vout vs Vin (varredura DC lenta) mostrando histerese.
- Aplique onda triangular e verifique forma de onda quadrada na saída.

## 13) Oscilador Wien Bridge
- Oscilador senoidal com op-amp, rede RC de Wien (R-C série + R-C paralelo), e controle de amplitude com JFET ou lâmpada incandescente (modelo resistivo).
- Alvo: frequência ~1 kHz, THD < 1% em regime.
- Plote start-up, estabilização de amplitude e espectro FFT.
- Compare THD com e sem controle automático de ganho (AGC).

## 14) Amplificador Cascode (BJT)
- Cascode NPN (BC548 × 2) em configuração emissor comum + base comum.
- Alvo: ganho > 50 dB, banda > 1 MHz, baixa capacitância Miller.
- Plote Bode (ganho e fase) e compare com emissor comum simples.
- Meça Zout e verifique melhoria na impedância de saída.

## 15) Amplificador de Instrumentação (3 Op-Amps)
- Topologia clássica com 3 op-amps (2 buffers de entrada + diferencial de saída).
- Alvo: ganho diferencial ajustável (1–100×) via Rgain, CMRR > 80 dB.
- Injete sinal comum e diferencial; meça Ad, Ac e calcule CMRR.
- Verifique linearidade com varredura DC de entrada diferencial.

## 16) Amplificador de Transimpedância (TIA)
- Op-amp com realimentação resistiva para converter corrente (fotodiodo modelado) em tensão.
- Alvo: ganho 100 kΩ (Vout = 1 V para Iin = 10 µA), banda > 100 kHz.
- Inclua capacitor de compensação para estabilidade.
- Plote resposta em frequência e ruído de saída (`.noise`).

## 17) Retificador de Precisão (Meia-Onda)
- Retificador de meia-onda com op-amp e diodos no laço de realimentação.
- Alvo: retificação precisa de sinais < 100 mV sem perda de 0.6 V do diodo.
- Plote entrada senoidal (100 mVpp, 1 kHz) e saída retificada.
- Compare com retificador passivo simples.

## 18) Fonte de Corrente de Precisão (Wilson Mirror)
- Espelho de corrente Wilson (3 BJTs NPN) para alta impedância de saída.
- Alvo: Iout = 1 mA com compliance > 8 V (VCC = 12 V).
- Compare Zout e precisão com espelho simples de 2 transistores.
- Plote Iout vs Vout para verificar região de compliance.

## 19) Mixer Analógico (Célula de Gilbert Simplificada)
- Par diferencial com modulação da corrente de cauda por segundo sinal.
- Injete RF = 1 MHz e LO = 1.1 MHz; observe produto IF = 100 kHz.
- Plote espectro de saída (FFT) mostrando componentes de mistura.
- Meça ganho de conversão e isolação LO-RF.

## 20) Retificador de Onda Completa com Filtro Capacitivo
- Ponte de diodos (1N4148 ou 1N4007) com filtro RC/LC.
- Alvo: Vout DC ≈ 5 V com ripple < 5% para carga de 100 mA.
- Plote tensão de saída, ripple e corrente nos diodos.
- Calcule e compare ripple teórico vs simulado.

---

> Sugestão: para cada exercício, produza: (1) netlist SPICE, (2) plots exportados, (3) tabelas de medidas `.meas` no log, (4) breve interpretação dos resultados e verificações (ganho, fase, start-up, compliance, THD, ruído).
