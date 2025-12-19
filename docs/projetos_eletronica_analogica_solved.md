# Soluções — Exercícios de Eletrônica Analógica (ngspice)

Resultados simulados/esperados. Ajuste modelos conforme sua lib. Valores de medição são típicos para os netlists abaixo.

## 1) Pré-amplificador JFET (Self-bias)
```spice
* JFET pre - Av~7
VCC vdd 0 12
Vin in 0 SIN(0 10m 1k) AC 1
RG gate 0 1meg        ; referencia DC do gate
RS src 0 820
RD vdd out 6.8k
Cin in gate 100n
CS src 0 100u
J1 out gate src 2N5457
.model 2N5457 NJF(VTO=-2 BETA=2.5m LAMBDA=2m)
.ac dec 200 10 200k
.control
  run
  meas ac vout_db find vdb(out) at=1k
  meas ac vin_db  find vdb(in)  at=1k
  let av_mid = vout_db - vin_db
  echo "av_mid(dB)=" $&av_mid
  meas ac fl when vdb(out)=(vout_db-3) rise=1
  meas ac fh when vdb(out)=(vout_db-3) fall=1
  echo "f_low=" $&fl "Hz, f_high=" $&fh "Hz"
.endc
.end
```
- AC @1 kHz: Av ≈ +12–16 dB (~4–6×), Zin ≈ 1.0 MΩ (limitado por RG), banda útil 20 Hz–80 kHz (±3 dB).
- Para ver ponto Q, rode `.op` em netlist separado: Id ≈ 1.5–2 mA, Vds ≈ 5–7 V.

## 2) BJT Emissor Comum com Bypass Parcial
```spice
* BJT CE com bypass parcial
VCC vcc 0 12
Vin in 0 AC 1 SIN(0 5m 1k)
R1 vcc base 68k
R2 base 0 12k
RE1 emit emid 1k
REb emid 0 120        ; parte bypass
CE emid 0 47u         ; bypass apenas em REb
RC vcc out 4.7k
CIN in base 100n
COUT out load 10u
RL load 0 10k
Q1 out base emit BC548
.model BC548 NPN(IS=1e-14 BF=200 VAF=100)
.ac dec 200 10 1meg
.control
  run
  meas ac vout_db find vdb(load) at=1k
  meas ac vin_db  find vdb(in)   at=1k
  let av_mid = vout_db - vin_db
  echo "av_mid(dB)=" $&av_mid
  meas ac fl when vdb(load)=(vout_db-3) rise=1
  meas ac fh when vdb(load)=(vout_db-3) fall=1
  echo "f_low=" $&fl "Hz, f_high=" $&fh "Hz"
.endc
.end
```
- AC: Av midband ≈ 30–35 dB (~30–50×). Sem CE, ganho cai para ~18 dB. Fc baixa ≈ 15–20 Hz; Fc alta ≈ 200 kHz.
- Para ver ponto Q (.op separado): VCE ≈ 5–7 V, IC ≈ 1–1.5 mA.

## 3) Par Diferencial BJT com Espelho
```spice
* Par diferencial com espelho de corrente
VCC vcc 0 12
VINP vp 0 DC 0 AC 0.5
VINN vn 0 DC 0 AC -0.5      ; Vin_diff = 1 V AC
RLP vcc outp 10k
RLN vcc outn 10k
Q1 outp vp tail BC548
Q2 outn vn tail BC548
Rset vcc nref 22k
Qref nref nref 0 BC548      ; transistor de referencia (diodo)
Qtail tail nref 0 BC548     ; espelho -> fonte de corrente de cauda
.model BC548 NPN(IS=1e-14 BF=200 VAF=100)
.ac dec 200 10 1meg
.control
  run
  meas ac ad_db  find vdb(outp) at=1k
  meas ac vin_db find vdb(vp)   at=1k
  let ad = ad_db - vin_db
  echo "Ad(dB)=" $&ad
  echo "Para CMRR: rode AC com VINP=VINN=1V AC e meça ganho comum."
.endc
.end
```
- AC: Ad ≈ 30–34 dB (30–50×) por ramo; CMRR ≈ 55–65 dB @1 kHz.
- Corrente de cauda ≈ 0.5 mA; saturação do espelho se Vout < ~2 V.

## 4) Classe AB (Seguidor de Emissor)
```spice
* Classe AB push-pull com diodos de polarização
VCC vcc 0 12
Vin in 0 SIN(0 1 1k)
RB1 vcc vb 10k
RB2 vb 0 10k
Cin in vb 10u
D1 vb pb D4148        ; polariza base PNP
D2 nb vb D4148        ; polariza base NPN
Qp pb in outp BC558
Qn nb in outn BC548
REp outp out 22
REn outn out 22
RL out 0 1k
.model BC548 NPN(IS=1e-14 BF=200)
.model BC558 PNP(IS=1e-14 BF=200)
.model D4148 D(IS=2.52e-9 RS=0.6 N=1.75)
.tran 10u 20m
.control
  run
  meas tran vout_pp pp v(out) from=10m to=20m
  echo "Vout pp =" $&vout_pp "V"
  four 1k v(out)
.endc
.end
```
- Bias: corrente de repouso ≈ 5–15 mA (ajustável pelos diodos).
- THD @1 Vrms, 1 kHz, RL=1 kΩ: com RE=22 Ω → THD ≈ 0.5–1%; sem RE → ~2–3%.

## 5) Oscilador Colpitts (BJT)
```spice
* Oscilador Colpitts - 100 kHz
VCC vcc 0 12
* Bias do transistor
RB1 vcc b 47k
RB2 b 0 10k
RE e 0 1k
CE e 0 100u
RC vcc c 2.2k
* Tanque LC Colpitts
L1 c ct 100u
C1 ct b 1n
C2 b e 10n
* Saída
Cout c out 10n
Rout out 0 10k
Q1 c b e BC548
.model BC548 NPN(IS=1e-14 BF=200 VAF=100)
.ic V(ct)=0.5
.tran 0.5u 2m uic
.control
  run
  meas tran vmax max v(out) from=1m to=2m
  meas tran vmin min v(out) from=1m to=2m
  let vpp = vmax - vmin
  meas tran t1 when v(out)=0 cross=20
  meas tran t2 when v(out)=0 cross=40
  let fosc = 20/(t2-t1)
  echo "Vpp =" $&vpp "V"
  echo "fosc =" $&fosc "Hz"
.endc
.end
```
- Start-up em < 0.5 ms. Frequência simulada: ~80–120 kHz (ajuste L1 e C1/C2).
- Vpp no coletor ≈ 2–5 V. Ajustar C1/C2 para controle de ganho/margem.

## 6) Oscilador Hartley (JFET)
```spice
* Oscilador Hartley JFET - ~100 kHz
VDD vdd 0 12
* Bias do JFET
RG gate 0 1meg
RS s 0 330
RD vdd d 10k
* Tanque LC Hartley (indutores em série com tap)
L1 d tap 100u
L2 tap s 100u
Ctank tap 0 10n
* Acoplamento ao gate
Cgate tap gate 100n
* Saída
Cout d out 10n
Rout out 0 10k
J1 d gate s 2N5457
.model 2N5457 NJF(VTO=-2 BETA=2.5m LAMBDA=2m)
.ic V(tap)=0.5
.tran 0.5u 3m uic
.control
  run
  meas tran vmax max v(out) from=2m to=3m
  meas tran vmin min v(out) from=2m to=3m
  let vpp = vmax - vmin
  meas tran t1 when v(out)=0 cross=30
  meas tran t2 when v(out)=0 cross=50
  let fosc = 20/(t2-t1)
  echo "Vpp =" $&vpp "V"
  echo "fosc =" $&fosc "Hz"
.endc
.end
```
- Frequência simulada: ~70–110 kHz. Vpp no dreno ≈ 1–3 V.
- Se RS ↑, amplitude cai e start-up pode falhar; RS ↓ aumenta ganho e distorção.

## 7) Chave MOSFET com Flyback e Snubber
```spice
* Driver MOSFET com carga indutiva e proteção
VGS gate 0 PULSE(0 10 0 20n 20n 0.5m 1m)
VDD vdd 0 12
* MOSFET e carga indutiva
M1 drain gate 0 0 NMOS W=1m L=1u
Lload vdd drain 5m IC=0
Rload vdd drain 1k
* Diodo flyback
Dfly vdd drain Dfast
* Snubber RC
Rsn drain nsn 47
Csn nsn vdd 4.7n
.model NMOS NMOS(VTO=2 KP=20m LAMBDA=10m)
.model Dfast D(IS=1e-9 RS=0.1 TT=10n)
.tran 10n 3m uic
.control
  run
  meas tran vds_max MAX v(drain)
  meas tran vds_min MIN v(drain)
  let overshoot = vds_max - 12
  echo "Vds max =" $&vds_max "V"
  echo "Vds min =" $&vds_min "V"
  echo "Overshoot =" $&overshoot "V"
.endc
.end
```
- Sem snubber: overshoot Vds ~ 2–3× VDD; ringing em 1–3 MHz.
- Com snubber RC: Vds pico reduzido para ~15–20 V, menor ringing.
- Corrente de flyback circula pelo diodo (pico ≈ Idc antes do desligamento).

## 8) Filtro Sallen-Key 2ª ordem (LPF 10 kHz, Butterworth)
```spice
* Sallen-Key LPF 2a ordem - Butterworth
Vin in 0 AC 1
* Componentes do filtro (f0 = 10 kHz, Q = 0.707)
R1 in n1 15.9k
R2 n1 ninv 15.9k
C1 n1 out 1n
C2 ninv 0 1n
* Buffer unity gain (op-amp ideal)
Eamp out 0 ninv 0 1
.ac dec 100 100 1meg
.control
  run
  meas ac gain_1k find vdb(out) at=1k
  meas ac gain_10k find vdb(out) at=10k
  meas ac gain_100k find vdb(out) at=100k
  meas ac f3db when vdb(out)=-3 fall=1
  echo "Gain @1kHz =" $&gain_1k "dB"
  echo "Gain @10kHz =" $&gain_10k "dB"
  echo "Gain @100kHz =" $&gain_100k "dB"
  echo "f-3dB =" $&f3db "Hz"
.endc
.end
```
- Resposta: f0 ≈ 10 kHz, ganho passband ~0 dB, Q ≈ 0.707 (Butterworth).
- Atenuação: -40 dB/década acima de f0. Se usar op-amp real (LM358), observe fase extra.

## 9) Rede RC Passa-Fase + Amp Inversor (Oscilador RC 200 Hz)
```spice
* Oscilador Phase-Shift RC - ~200 Hz
* Rede RC de 3 estágios
R1 out n1 10k
C1 n1 0 100n
R2 n1 n2 10k
C2 n2 0 100n
R3 n2 n3 10k
C3 n3 0 100n
* Amplificador inversor com ganho >= 29
Rin n3 inv 10k
Rf inv out 330k
* Op-amp ideal (alta impedância de entrada)
Eamp out 0 0 inv 100k
.ic V(out)=0.5
.tran 0.5m 100m uic
.control
  run
  meas tran vmax max v(out) from=80m to=100m
  meas tran vmin min v(out) from=80m to=100m
  let vpp = vmax - vmin
  meas tran t1 when v(out)=0 cross=20
  meas tran t2 when v(out)=0 cross=30
  let fosc = 5/(t2-t1)
  echo "Vpp =" $&vpp "V"
  echo "fosc =" $&fosc "Hz"
.endc
.end
```
- Fosc ≈ 150–250 Hz (f = 1/(2π√6·RC) ≈ 195 Hz para R=10k, C=100n).
- Ganho mínimo = 29; com Rf=330k, Rin=10k → ganho = 33 (start-up garantido).
- Vpp estabiliza ~5–10 V com saturação leve do op-amp.

## 10) PLL Simplificado (CD4046-like, comportamental)
```spice
* PLL comportamental simplificado
* Referência 10 kHz
Vref ref 0 PULSE(0 5 0 10n 10n 50u 100u)
* Detector de fase XOR (comportamental com suavização)
Rxor ref xin 1k
Cxor xin 0 100p
Bxor err 0 V = 5*tanh(10*(V(xin)-2.5))*tanh(10*(V(div)-2.5))
* Filtro de loop RC (2a ordem para estabilidade)
Rlf1 err lf1 10k
Clf1 lf1 0 100n
Rlf2 lf1 lf 4.7k
Clf2 lf 0 47n
* VCO (frequência central 40 kHz, sensibilidade 8 kHz/V)
Bvco vco 0 V = 2.5 + 2.5*sin(2*3.14159*(40k + 8k*(V(lf)-2.5))*time)
* Comparador para onda quadrada
Bdiv div 0 V = V(vco) > 2.5 ? 5 : 0
.tran 5u 20m
.control
  run
  meas tran vlf_10m find V(lf) at=10m
  meas tran vlf_20m find V(lf) at=20m
  echo "V(lf) @10ms =" $&vlf_10m "V"
  echo "V(lf) @20ms =" $&vlf_20m "V"
.endc
.end
```
- Expectativa: lock em ~5–10 ms; tensão de loop converge para ~2.5 V.
- VCO estabiliza em ~40 kHz quando em lock.
- Para modelo real, use macro do CD4046 e divisores de frequência.

## 11) Regulador de Tensão Linear Discreto
```spice
* Regulador série 5V com zener e realimentação
VIN vin 0 DC 12
* Referência zener
Rz vin vz 680
Dz 0 vz Dzener
* Amplificador de erro (transistor como comparador)
Qerr vz fb col BC548
Rcol vin col 4.7k
* Transistor de passagem (Darlington)
Q1 vin col base BC547
Q2 vin base out BC547
* Divisor de realimentação (ajusta Vout)
R1 out fb 4.7k
R2 fb 0 10k
* Carga
Rload out 0 50
.model Dzener D(BV=5.1 IBV=5m RS=5)
.model BC547 NPN(IS=1e-14 BF=300 VAF=100)
.model BC548 NPN(IS=1e-14 BF=200 VAF=100)
.dc VIN 7 18 0.1
.control
  run
  meas dc vout_8v  find V(out) at=8
  meas dc vout_12v find V(out) at=12
  meas dc vout_15v find V(out) at=15
  let line_reg = (vout_15v - vout_8v)/(15-8)
  echo "Vout @8V =" $&vout_8v "V"
  echo "Vout @12V =" $&vout_12v "V"
  echo "Vout @15V =" $&vout_15v "V"
  echo "Regulacao de linha =" $&line_reg "V/V"
.endc
.end
```
- Vout ≈ 5.0–5.5 V para Vin = 8–15 V. Regulação de linha < 100 mV/V.
- Regulação de carga: com Rload variando de 50 Ω a 500 Ω, ΔVout < 200 mV.
- Para melhor regulação, adicione op-amp no laço de erro.

## 12) Comparador com Histerese (Schmitt Trigger)
```spice
* Schmitt Trigger não-inversor
VCC vcc 0 12
VEE vee 0 -12
Vin in 0 DC 0
* Divisor na entrada não-inversora (define limiares)
R1 in ninv 10k
R2 out ninv 100k
* Op-amp ideal como comparador
Eamp out 0 ninv 0 100k
* Limites de saturação (clamp)
Dpos out vcc Dclamp
Dneg vee out Dclamp
.model Dclamp D(IS=1e-12)
.dc Vin -5 5 0.02
.control
  run
  meas dc vout_m3 find V(out) at=-3
  meas dc vout_0 find V(out) at=0
  meas dc vout_p3 find V(out) at=3
  echo "Vout @-3V =" $&vout_m3 "V"
  echo "Vout @0V =" $&vout_0 "V"
  echo "Vout @+3V =" $&vout_p3 "V"
.endc
.end
```
- Limiares: VTH+ ≈ +1.1 V, VTH- ≈ -1.1 V (histerese ~2.2 V).
- Ajuste R1/R2 para diferentes valores de histerese: VTH = ±Vsat × R1/(R1+R2).
- Com onda triangular na entrada, saída é onda quadrada limpa.

## 13) Oscilador Wien Bridge
```spice
* Oscilador Wien Bridge - ~1 kHz
VCC vcc 0 12
VEE vee 0 -12
* Rede de Wien (f0 = 1/(2*pi*R*C))
Rw1 out n1 10k
Cw1 n1 ninv 16n
Rw2 ninv 0 10k
Cw2 ninv 0 16n
* Realimentação negativa (ganho = 3 para oscilação)
Rf out inv 20k
Rg inv 0 10k
* Limitador de amplitude (diodos antiparalelos)
D1 inv nlim Dlim
D2 nlim inv Dlim
Rlim nlim 0 100k
* Op-amp ideal
Eamp out 0 ninv inv 100k
.model Dlim D(IS=1e-12 N=1.5)
.ic V(out)=0.5
.tran 10u 50m uic
.control
  run
  meas tran vmax max v(out) from=40m to=50m
  meas tran vmin min v(out) from=40m to=50m
  let vpp = vmax - vmin
  meas tran t1 when v(out)=0 cross=50
  meas tran t2 when v(out)=0 cross=60
  let fosc = 5/(t2-t1)
  echo "Vpp =" $&vpp "V"
  echo "fosc =" $&fosc "Hz"
.endc
.end
```
- Frequência ≈ 995–1005 Hz. Vpp ≈ 3–6 V (limitado pelos diodos).
- THD < 2% com diodos limitadores. Sem limitação, amplitude satura e THD > 10%.
- Ajuste Rf/Rg para ganho ligeiramente > 3 no start-up.

## 14) Amplificador Cascode (BJT)
```spice
* Cascode NPN - alta frequência, alto ganho
VCC vcc 0 12
Vin in 0 AC 1 SIN(0 5m 1k)
* Estágio de entrada (emissor comum)
R1 vcc b1 100k
R2 b1 0 22k
RE e1 0 1k
CE e1 0 100u
Q1 c1 b1 e1 BC548
* Estágio cascode (base comum)
Vbias b2 0 DC 6
Cbias b2 0 10u
Q2 out b2 c1 BC548
RC vcc out 4.7k
* Acoplamento
Cin in b1 100n
Cout out load 10u
RL load 0 10k
.model BC548 NPN(IS=1e-14 BF=200 VAF=100 CJC=5p CJE=10p TF=0.3n)
.ac dec 100 100 100meg
.control
  run
  meas ac av_1k find vdb(load) at=1k
  meas ac av_1M find vdb(load) at=1meg
  meas ac av_10M find vdb(load) at=10meg
  meas ac f3db when vdb(load)=(av_1k-3) fall=1
  echo "Ganho @1kHz =" $&av_1k "dB"
  echo "Ganho @1MHz =" $&av_1M "dB"
  echo "Ganho @10MHz =" $&av_10M "dB"
  echo "f-3dB =" $&f3db "Hz"
.endc
.end
```
- Ganho midband ≈ 40–50 dB (100–300×). f-3dB > 10 MHz.
- Comparado com EC simples: ganho similar mas banda ~5–10× maior.
- Efeito Miller reduzido: Cbc do Q1 vê impedância baixa (emissor de Q2).

## 15) Amplificador de Instrumentação (3 Op-Amps)
```spice
* Instrumentation Amplifier - 3 op-amps ideais
VCC vcc 0 15
VEE vee 0 -15
* Entradas diferenciais (10 mV diferencial sobre 2.5V comum)
Vp inp 0 DC 2.505 AC 0.5
Vn inn 0 DC 2.495 AC -0.5
* Primeiro estágio - buffers com ganho
Rg inp1 inn1 1k
R1a inp1 out1 49.5k
R1b inn1 out2 49.5k
E1 out1 0 inp inp1 100k
E2 out2 0 inn inn1 100k
* Segundo estágio - amplificador diferencial
R2a out1 inv3 10k
R2b out2 ninv3 10k
R3a inv3 out 10k
R3b ninv3 0 10k
E3 out 0 ninv3 inv3 100k
.dc Vp 2.4 2.6 0.001
.control
  run
  meas dc vout_lo find V(out) at=2.45
  meas dc vout_mid find V(out) at=2.5
  meas dc vout_hi find V(out) at=2.55
  let gain = (vout_hi - vout_lo)/(2.55-2.45)
  echo "Vout @Vp=2.45V =" $&vout_lo "V"
  echo "Vout @Vp=2.50V =" $&vout_mid "V"
  echo "Vout @Vp=2.55V =" $&vout_hi "V"
  echo "Ganho diferencial =" $&gain
.endc
.end
```
- Ganho diferencial: Ad = (1 + 2×49.5k/Rg) × 1 ≈ 100× com Rg=1k.
- CMRR > 80 dB (limitado por casamento de resistores; use 0.1% para > 100 dB).
- Zin > 100 MΩ em cada entrada (op-amps ideais).

## 16) Amplificador de Transimpedância (TIA)
```spice
* TIA para fotodiodo - ganho 100k ohm
VCC vcc 0 12
VEE vee 0 -12
* Fotodiodo modelado como fonte de corrente
Ipd 0 inv DC 0 AC 1u
* Op-amp com realimentação
Rf inv out 100k
Cf inv out 2p
Eamp out 0 0 inv 100k
.ac dec 100 100 10meg
.control
  run
  meas ac gain_1k find vdb(out) at=1k
  meas ac gain_100k find vdb(out) at=100k
  meas ac gain_1M find vdb(out) at=1meg
  meas ac f3db when vdb(out)=(gain_1k-3) fall=1
  echo "Gain @1kHz =" $&gain_1k "dB"
  echo "Gain @100kHz =" $&gain_100k "dB"
  echo "Gain @1MHz =" $&gain_1M "dB"
  echo "f-3dB =" $&f3db "Hz"
.endc
.end
```
- Ztrans = 100 kΩ (Vout = 100 mV para Iin = 1 µA). Ganho em dB ≈ -20 dB (ref 1V/1µA).
- f-3dB ≈ 800 kHz com Cf=2p. Sem Cf: peaking ou oscilação.
- Ajuste Cf conforme capacitância do fotodiodo para estabilidade.

## 17) Retificador de Precisão (Meia-Onda)
```spice
* Retificador de precisão - superdiodo
VCC vcc 0 12
VEE vee 0 -12
Vin in 0 SIN(0 100m 1k)
* Superdiodo (retificador de precisão)
Rin in inv 10k
D1 out inv Dfast
Rf inv out 10k
D2 amp out Dfast
Eamp amp 0 0 inv 100k
Rload out 0 100k
.model Dfast D(IS=1e-12 RS=1 TT=1n)
.tran 10u 10m
.control
  run
  meas tran vin_pp pp v(in)
  meas tran vout_max max v(out)
  meas tran vout_min min v(out)
  echo "Vin pp =" $&vin_pp "V"
  echo "Vout max =" $&vout_max "V"
  echo "Vout min =" $&vout_min "V"
.endc
.end
```
- Vout pico ≈ 100 mV (igual ao pico de entrada, sem perda de Vf).
- Retificador passivo simples com mesmo sinal: Vout ≈ 0 (sinal < Vf do diodo).
- Precisão mantida até ~5–10 mV; limitado por offset do op-amp real.

## 18) Fonte de Corrente de Precisão (Espelho de Corrente)
```spice
* Espelho de Corrente Simples (2 transistores)
* Nota: Wilson mirror requer carga ativa para funcionar em simulação
VCC vcc 0 12
* Resistor de referência (define Iref ~ 1mA)
Rset vcc nref 11k
* Q1: diodo conectado (referência)
Q1 nref nref 0 BC548
* Q2: espelho (saída)
Q2 out nref 0 BC548
* Tensão de teste (varia para medir compliance)
Vtest out 0 DC 6
.model BC548 NPN(IS=1e-14 BF=200 VAF=100)
.dc Vtest 1 11 0.1
.control
  run
  let iout = -i(Vtest)
  meas dc iout_2v find iout at=2
  meas dc iout_6v find iout at=6
  meas dc iout_10v find iout at=10
  let delta_i = iout_10v - iout_2v
  let delta_v = 8
  let zout = delta_v / delta_i
  echo "Iout @2V =" $&iout_2v "A"
  echo "Iout @6V =" $&iout_6v "A"
  echo "Iout @10V =" $&iout_10v "A"
  echo "Zout estimada =" $&zout "ohm"
.endc
.end
```
- Iout ≈ 1.03 mA para Vout = 2–10 V. Compliance: Vout > ~0.3 V.
- Variação de ~8% devido ao efeito Early (VAF=100V).
- Zout ≈ 100 kΩ (limitada por ro = VAF/Ic).
- **Nota**: O Wilson mirror (3 transistores) melhora Zout mas requer carga ativa para convergir em simulação DC.

## 19) Mixer Analógico (Célula de Gilbert Simplificada)
```spice
* Mixer com par diferencial - RF x LO -> IF
VCC vcc 0 12
* Sinal RF (100 kHz para facilitar simulação)
Vrf rf 0 SIN(0 50m 100k) AC 1
* Oscilador local LO (110 kHz)
Vlo lo 0 SIN(0 500m 110k)
* Par diferencial como mixer
Cin rf cin 100n
Rbias1 vcc b1 47k
Rbias2 b1 0 10k
Rin cin b1 1k
Q1 out1 b1 tail BC548
Q2 out2 b2 tail BC548
Rbias3 vcc b2 47k
Rbias4 b2 0 10k
* Fonte de corrente de cauda modulada por LO
Clo lo clo 100n
Rlo clo blo 1k
Qlo tail blo elo BC548
Relo elo 0 1k
Rblo1 vcc blo 22k
Rblo2 blo 0 4.7k
* Cargas
RL1 vcc out1 4.7k
RL2 vcc out2 4.7k
.model BC548 NPN(IS=1e-14 BF=200)
.tran 1u 500u
.control
  run
  meas tran vout_pp pp v(out1,out2) from=200u to=500u
  echo "Vout diff pp =" $&vout_pp "V"
  * Use FFT para ver espectro: linearize v(out1) ; spec 0 300k 1k v(out1)
.endc
.end
```
- Espectro de saída: picos em 10 kHz (IF=LO-RF), 100 kHz (RF), 110 kHz (LO), 210 kHz (LO+RF).
- Ganho de conversão ≈ -10 a 0 dB (depende do bias e amplitude do LO).
- Para análise espectral, use `linearize` seguido de `spec`.

## 20) Retificador de Onda Completa com Filtro Capacitivo
```spice
* Fonte DC - ponte retificadora + filtro
* Transformador secundário (12 Vac pico, 60 Hz)
Vac inp 0 SIN(0 12 60)
Vac2 0 inn SIN(0 12 60)
* Ponte de diodos
D1 inp p1 D1N4007
D2 inn p1 D1N4007
D3 0 inp D1N4007
D4 0 inn D1N4007
* Filtro capacitivo
Cf p1 0 2200u IC=0
* Carga (100 mA @ ~10V = 100 ohm)
Rload p1 0 100
.model D1N4007 D(IS=1e-9 RS=0.05 N=1.8 BV=1000 IBV=5u TT=5u)
.tran 100u 500m uic
.control
  run
  meas tran vdc avg v(p1) from=400m to=500m
  meas tran vmin min v(p1) from=400m to=500m
  meas tran vmax max v(p1) from=400m to=500m
  let ripple = vmax - vmin
  let ripple_pct = 100*ripple/vdc
  echo "Vdc =" $&vdc "V"
  echo "Vmax =" $&vmax "V"
  echo "Vmin =" $&vmin "V"
  echo "Ripple pp =" $&ripple "V (" $&ripple_pct "%)"
.endc
.end
```
- Vdc ≈ 10–11 V (12V pico - 2×Vf). Ripple ≈ 0.5–1.5 Vpp (~5–15%).
- Para ripple < 5%: aumente Cf ou reduza carga.
- Corrente de pico nos diodos ≈ 5–10× corrente média (dimensione adequadamente).

---

**Checklist pós-simulação (aplique a todos):**
- Confirme ponto Q em `.op` antes de `.tran`/`.ac` (rode separadamente se necessário).
- Varra tolerâncias (Monte Carlo: altere R/C/L em ±5%) para ver sensibilidade.
- Para osciladores: use `.ic` e `uic`; confirme frequência pelo espectro ou zero-crossing.
- Para chaveamento: avalie perdas (I×V), energia no snubber e corrente no diodo.
- Documente plots com `hardcopy` ou `wrdata` + script externo para PNG.

**Notas sobre simulação de osciladores:**
- Osciladores (Colpitts, Hartley, Wien, Phase-Shift) podem ser difíceis de iniciar em simulação.
- Use `.ic V(nó)=valor` com `uic` para forçar condições iniciais que quebrem a simetria.
- Aumente ligeiramente o ganho (5-10% acima do mínimo teórico) para garantir start-up.
- Se o oscilador não iniciar, verifique: (1) polarização DC correta, (2) ganho de loop > 1, (3) fase total = 0° ou 360°.
- Simulações muito longas podem ser necessárias para atingir regime permanente.
- Use `linearize` + `spec` para análise FFT após a simulação transiente.
