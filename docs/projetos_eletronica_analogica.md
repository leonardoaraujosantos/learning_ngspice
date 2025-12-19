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

> Sugestão: para cada exercício, produza: (1) netlist SPICE, (2) plots exportados, (3) tabelas de medidas `.meas` no log, (4) breve interpretação dos resultados e verificações (ganho, fase, start-up, compliance, THD, ruído).
