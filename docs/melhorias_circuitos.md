# Melhorias nos Circuitos de Eletrônica Analógica

Este documento contém as versões melhoradas dos circuitos que apresentavam problemas na simulação.

## Resumo das Melhorias

| Ex  | Circuito      | Original     | Melhorado    | Status |
|-----|---------------|--------------|--------------|--------|
| 4   | Classe AB     | Não funciona | Ganho ~1     | Parcial |
| 5   | Colpitts      | Vpp = 70µV   | Vpp = 1.24V  | OK |
| 6   | Hartley       | Vpp = 0      | Difícil      | Precisa trabalho |
| 9   | Phase Shift   | Vpp = 0      | Vpp = 0.87V  | OK (decai) |
| 13  | Wien Bridge   | Vpp = 0      | Vpp = 1.06V  | OK |

---

## 5) Oscilador Colpitts MELHORADO

**Problema original:** Vpp = 70µV (praticamente não oscila)

**Solução:** Ajustar bias para maior corrente (maior gm) e valores do tanque LC.

```spice
* Oscilador Colpitts MELHORADO - ~200 kHz
VCC vcc 0 12

* Bias - Ic ~ 3mA para bom gm
RB1 vcc b 22k
RB2 b 0 10k
RE e 0 560
CE e 0 100u
RC vcc c 1k

* Tanque LC otimizado
* Ceq = 2.2n*22n/(2.2n+22n) = 2nF
* f = 1/(2*pi*sqrt(330u*2n)) ~ 196kHz
L1 c ct 330u IC=0.5
C1 ct b 2.2n
C2 b 0 22n

* Saída
Cout c out 100n
Rout out 0 10k

Q1 c b e BC548
.model BC548 NPN(IS=1e-14 BF=300 VAF=100)

.ic V(ct)=6 V(c)=7 V(b)=3.7 V(e)=3
.tran 0.1u 1m uic
.end
```

**Resultado:** Vpp = 1.24V no coletor

---

## 9) Oscilador Phase Shift MELHORADO

**Problema original:** Não oscila com op-amp ideal

**Solução:** Usar BJT com alto ganho (CE) ao invés de op-amp.

```spice
* Oscilador Phase-Shift com BJT
VCC vcc 0 12

* Transistor com alto ganho
RB1 vcc b 100k
RB2 b 0 22k
RC vcc c 3.3k
RE e 0 1k
CE e 0 100u

* Rede RC de 3 estágios
R1 c n1 10k
C1 n1 0 100n
R2 n1 n2 10k
C2 n2 0 100n
R3 n2 n3 10k
C3 n3 b 100n

* Saída
Cout c out 1u
Rout out 0 10k

Q1 c b e BC548
.model BC548 NPN(IS=1e-14 BF=300 VAF=100)

.ic V(c)=6 V(n1)=3 V(n2)=1 V(n3)=0.3
.tran 0.2m 200m uic
.end
```

**Resultado:** Vpp = 0.87V inicialmente (decai lentamente - ganho de loop marginalmente < 1)

**Nota:** Para oscilação sustentada, aumentar RC ou ajustar valores da rede RC.

---

## 13) Oscilador Wien Bridge MELHORADO

**Problema original:** Não oscila

**Solução:** Ajustar ganho para ligeiramente > 3 e usar op-amp com ganho finito.

```spice
* Oscilador Wien Bridge MELHORADO
* Rede de Wien (f ~ 1.6 kHz)
Rw1 out n1 10k
Cw1 n1 ninv 10n
Rw2 ninv 0 10k
Cw2 ninv 0 10n

* Realimentação negativa (ganho = 3.05)
Rf out inv 20.5k
Rg inv 0 10k

* Op-amp com ganho moderado
Eamp out 0 ninv inv 1k

.ic V(out)=0.1 V(ninv)=0.03
.tran 5u 5m uic
.end
```

**Resultado:** Vpp = 1.06V

**Nota:** Sem limitação de amplitude, a oscilação crescerá. Para amplitude estável, adicionar diodos limitadores ou controle AGC.

---

## 6) Oscilador Hartley - NOTAS

**Problema:** Muito difícil de simular em ngspice. Várias topologias testadas sem sucesso.

**Observações:**
1. A configuração com JFET (original) não oscila
2. Configurações com BJT também apresentam problemas de convergência
3. O problema parece ser a interação entre o tanque LC e o transistor

**Recomendação:** Usar LTspice ou simulador comercial para este circuito, ou testar em bancada.

---

## 4) Classe AB - NOTAS

**Problema:** Topologia original incorreta. Dificuldade em estabelecer bias correto em ngspice.

**Solução parcial:** Usar op-amp como driver com realimentação.

```spice
* Classe AB com driver op-amp
VCC vcc 0 12
VEE vee 0 -12
Vin in 0 SIN(0 5 1k)

* Driver op-amp
Edrv drv 0 in 0 1
Rdrv opout drv 100

* Diodos de bias
Rp drv bp 10
Rn drv bn 10
D1 bp drv D4148
D2 drv bn D4148

* Transistores de saída
Qp vcc bp out BC558
Qn vee bn out BC548

* Carga
RL out 0 100

.model BC548 NPN(IS=1e-14 BF=200)
.model BC558 PNP(IS=1e-14 BF=200)
.model D4148 D(IS=2.52e-9 RS=0.6 N=1.75)
.tran 10u 10m
.end
```

**Resultado:** Ganho ~1 (funciona como buffer, mas bias não ideal para classe AB)

---

## Dicas Gerais para Simulação de Osciladores

1. **Condições iniciais:** Sempre usar `.ic` com `uic` para quebrar a simetria
2. **Ganho de loop:** Deve ser ligeiramente > 1 para startup
3. **Tempo de simulação:** Osciladores podem precisar de vários ciclos para estabilizar
4. **Limitação de amplitude:** Sem limitação, osciladores com ganho > 1 explodirão
5. **Convergência:** ngspice pode ter problemas com diodos em configurações de limitação
