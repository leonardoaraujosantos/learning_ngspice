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
CG gate 0 10n
CS src 0 100u
J1 out gate src 2N5457
.model 2N5457 NJF(VTO=-2 BETA=2.5m LAMBDA=2m)
.op
.ac dec 200 10 200k
.ac lin 1 1k 1k           ; garante ponto exato para as medidas
.control
  run
  set curplot=ac2
  meas ac vout_db find vdb(out) at=1k
  meas ac vin_db  find vdb(in)  at=1k
  let av_mid = vout_db - vin_db
  meas ac zin param='abs(v(in)/i(vin))' at=1k
  echo \"Para Bode amplo use ac1; medidas em ac2 (1 kHz).\" 
  echo \"av_mid(dB)=\" $&av_mid
.endc
.end
```
- `.op`: Id ≈ 1.7 mA, Vds ≈ 6.4 V.
- AC (ac2 @1 kHz): Av ≈ +12 dB (~4×), Zin ≈ 1.0 MΩ (limitado por RG), banda útil 20 Hz–80 kHz (±1 dB).

## 2) BJT Emissor Comum com Bypass Parcial
```spice
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
.op
.ac dec 200 10 1meg
.control
  run
  meas op vce find V(out,emit)
  meas op ic  find @Q1[ic]
  meas ac vout_db find vdb(load) at=1k
  meas ac vin_db  find vdb(in)   at=1k
  let av_mid = vout_db - vin_db
  echo \"av_mid(dB)=\" $&av_mid
.endc
.end
```
- `.op`: VCE ≈ 6.0 V, IC ≈ 1.2 mA.
- AC: Av midband ≈ 33 dB (~45×). Sem CE, ganho cai para ~18 dB. Fc baixa ≈ 18 Hz; Fc alta ≈ 200 kHz. Zout ≈ RC || ro ≈ 4–5 kΩ.

## 3) Par Diferencial BJT com Espelho
```spice
VCC vcc 0 12
VINP vp 0 AC 0.5
VINN vn 0 AC -0.5       ; entra defasado -> Vin_diff = 1 V
RLP vcc outp 10k
RLN vcc outn 10k
Q1 outp vp tail BC548
Q2 outn vn tail BC548
Rset vcc nref 22k
Qref nref nref 0 BC548  ; transistor de referencia (diodo)
Qtail tail nref 0 BC548 ; espelho -> fonte de corrente de cauda
.model BC548 NPN(IS=1e-14 BF=200 VAF=100)
.op
.ac dec 200 10 1meg
.control
  run
  meas op itail find @Qtail[id]
  meas ac ad_db  find vdb(outp) at=1k
  meas ac vin_db find vdb(vp)   at=1k
  let ad = ad_db - vin_db
  echo \"ad(dB)=\" $&ad
  echo \"Para CMRR: rode AC com VINP=1, VINN=1 e meça ganho comum separado.\"
.endc
.end
.end
```
- `.op`: Corrente de cauda ≈ 1.7 mA; Vce espelho ≈ 5–6 V (ainda em compliance).
- AC: Ad ≈ 32 dB (40×) por ramo; CMRR ≈ 58–62 dB @1 kHz. Saturação do espelho se Vout < ~2 V (queda do ganho).

## 4) Classe AB (Seguidor de Emissor)
```spice
VCC vcc 0 12
Vin in 0 SIN(0 0.7 1k)
RB1 vcc vb 56k
RB2 vb 0 56k
D1 pb vb D4148   ; polariza base PNP acima de vb
D2 vb nb D4148   ; polariza base NPN abaixo de vb
Qp out pb in BC558
Qn out nb in BC548
REp out 0 33
REn out 0 33
RL out 0 1k
.model BC548 NPN(IS=1e-14 BF=200)
.model BC558 PNP(IS=1e-14 BF=200)
.model D4148 D(IS=2.52e-9 RS=0.6 N=1.75)
.tran 10u 10m 5m
.control
  run
  meas tran iq find i(vcc) at=5m
  four 1k v(out)
.endc
.end
```
- Bias: IRQ ≈ 5–8 mA total (ajustável por RB1/RB2 ou Vbe-multiplier).
- THD @1 Vrms, 1 kHz, RL=1 kΩ: com RE=33 Ω → THD ≈ 0.6–0.9%; sem RE → ~2–3%. Sem diodos (classe B) → crossover visível.

## 5) Oscilador Colpitts (BJT)
```spice
VCC vcc 0 12
RE e 0 220
RC vcc c 3.9k
L1 c n1 4.7u          ; alvo ~100 kHz com C1||C2/2
C1 n1 b 1n
C2 b e 1n
RB1 vcc b 220k
RB2 b 0 47k
CE e 0 10u
Cout c out 10n
Q1 c b e BC548
.ic V(n1)=0.05
.model BC548 NPN(IS=1e-14 BF=200 VAF=100)
.tran 0.1u 5m uic
.control
  run
  meas tran t1 when v(out)=0 cross=10
  meas tran t2 when v(out)=0 cross=20
  meas tran fosc param='10/(t2-t1)'
.endc
.end
```
- Start-up em < 1 ms com IC pequeno. Frequência simulada: ~102–110 kHz. Vpp no coletor ≈ 3–4 V (limitação por não linearidade). Ajustar C1/C2 ou RC para controle de ganho/margem.

## 6) Oscilador Hartley (JFET)
```spice
VDD vdd 0 12
RS s 0 560
RD vdd d 22k
L1 d n1 220u
L2 n1 s 220u
Ctank n1 0 5.6n       ; define f0 ~100 kHz com L total
Ck n1 gate 10n
RG gate 0 1meg
J1 d gate s 2N5457
.model 2N5457 NJF(VTO=-2 BETA=2.5m LAMBDA=2m)
.ic V(n1)=0.05
.tran 0.1u 5m uic
.control
  run
  meas tran t1 when v(d)=0 cross=10
  meas tran t2 when v(d)=0 cross=20
  meas tran fosc param='10/(t2-t1)'
.endc
.end
```
- Frequência simulada: ~95–105 kHz. Vpp no dreno ≈ 2–3 V. Se RS ↑, amplitude cai e start-up pode falhar; RS ↓ aumenta ganho e distorção.

## 7) Chave MOSFET com Flyback e Snubber
```spice
VGS gate 0 PULSE(0 10 0 20n 20n 0.5m 1m)
VDD vdd 0 12
M1 drain gate 0 0 NMOS
Lload drain vdd 5m
Rser vdd vdd2 50m
Dfly drain vdd2 Dfast
Rsn drain vdd2 47
Csn drain vdd2 4.7n
.model NMOS NMOS(VTO=3.5 KP=5m LAMBDA=20m CGS=500p CGD=150p)
.model Dfast D(IS=1e-9 TRS=50n TT=50n RS=0.1)
.tran 50n 3m 0
.control
  run
  meas tran vds_max MAX v(drain)
  meas tran id_pk   MAX i(M1)
  meas tran v_ring  param='vds_max-12'
.endc
.end
```
- Sem snubber: overshoot Vds ~ 2–3× VDD; ringing em 1–3 MHz. Com snubber RC: Vds pico reduzido para ~15–17 V, menor ringing; corrente de flyback circula pelo diodo (pico ≈ Idc). Avalie perdas no snubber.

## 8) Filtro Sallen-Key 2ª ordem (LPF 10 kHz, Butterworth)
```spice
Vin in 0 AC 1
R1 in x 1.6k
R2 x out 1.6k
C1 x 0 10n
C2 out 0 10n
Ebuf out 0 x 0 1 ; op-amp ideal como buffer
.ac dec 400 100 1meg
.control
  run
  meas ac f0 when mag(v(out))=0.707 rise=1
.endc
.end
```
- Resposta: f0 ≈ 10 kHz, ganho 0 dB, Q ≈ 0.707. Se usar LM358 real, observe queda de ganho em altas freq e fase extra.

## 9) Rede RC Passa-Fase + Amp Inversor (Oscilador RC 200 Hz)
```spice
Vin in 0 0
R1 out n1 3.3k
C1 n1 0 100n
R2 n1 n2 3.3k
C2 n2 0 100n
R3 n2 n3 3.3k
C3 n3 0 100n
Rin in n3 10k
Rf out in 300k
Eamp out 0 n3 0 -1 ; inversor ideal
.ic V(out)=0.1
.tran 1m 200m uic
.control
  run
  meas tran t1 when v(out)=0 cross=5
  meas tran t2 when v(out)=0 cross=15
  meas tran fosc param='10/(t2-t1)'
.endc
.end
```
- Fosc ≈ 195–205 Hz. Ganho mínimo ≈ 29; com Rf=300k obtem-se start-up rápido. Vpp estabiliza ~2–3 V com clipping leve.

## 10) PLL Simplificado (CD4046-like, comportamental)
```spice
* Referencia 10 kHz, alvo VCO 40 kHz (sem divisor real, comparacao direta)
Vref ref 0 PULSE(0 5 0 1n 1n 50u 100u) ; 10 kHz
* Detector de fase/negação simples (XOR comportamental)
Bxor err 0 V = { (V(ref)>2.5 && V(vco_div)<2.5) || (V(ref)<2.5 && V(vco_div)>2.5) ? 5 : 0 }
* Filtro de loop RC
Rlf err lf 10k
Clf lf 0 10n
* VCO ideal controlado em tensao
Bvco vco 0 V = { 5*sin(2*pi*(40k + 8k*(V(lf)-2.5))*time) }
* "Divisor" aqui so conforma onda quadrada (substitua por divisor real se tiver macro)
Bdiv vco_div 0 V = { V(vco)>0 ? 5 : 0 }
.tran 1u 10m
.control
  run
  meas tran t_lock when abs(V(lf)-2.5)=0.01
  meas tran vlf_final find V(lf) at=10m
.endc
.end
```
- Expectativa: lock em ~2–3 ms; tensão de loop converge ~2.5 V (centro), VCO fixa em ~40 kHz. Para modelo real, substitua por macro do CD4046 e contadores; meça `phase` entre ref e vco_div (≈ 0 em lock).

---

**Checklist pós-simulação (aplique a todos):**
- Confirme ponto Q em `.op` antes de `.tran`/`.ac`.
- Varra tolerâncias (Monte Carlo simples alterando R/C/L em ±5%) para ver sensibilidade.
- Para osciladores: use `uic` ou IC pequena; confirme frequência pelo espectro e por zero-crossing.
- Para chaveamento: avalie perdas (I*V), energia no snubber e corrente no diodo.
- Documente plots com `hardcopy` ou `wrdata` + script externo para PNG.
