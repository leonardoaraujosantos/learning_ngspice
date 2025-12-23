#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de filtro RC passa-baixa usando SLiCAP
"""

import SLiCAP as sl

# 1) Cria estrutura do projeto
prj = sl.initProject("RC_LowPass_SLiCAP")

# 2) Importa o circuito
cir = sl.makeCircuit("rc_lp.cir")

# 3) Análise MNA (matriz de equações)
MNA = sl.doMatrix(cir, source='V1', detector='V_out')

sl.htmlPage('Equações matriciais')
sl.text2html('A equação matricial MNA para a rede RC é:')
sl.matrices2html(MNA, label='MNA', labelText='Equação MNA da rede')

# 4) Calcula H(s) = V(out)/V(in) simbólico
gain = sl.doLaplace(cir, source='V1', detector='V_out')

print("\nH(s) = V_out/V_in:\n")
print(gain.laplace)

sl.htmlPage('Função de transferência')
sl.eqn2html('H(s)', gain.laplace, label='gainLaplace',
            labelText='Função de transferência Laplace')

# 5) Cálculo numérico com valores do circuito
numGain = sl.doLaplace(cir, source='V1', detector='V_out', pardefs='circuit')

# 6) Gerar gráficos de resposta em frequência
sl.htmlPage('Gráficos')
sl.head2html('Gráficos no domínio da frequência')

figMag = sl.plotSweep('RCmag', 'Característica de magnitude', numGain,
                      10, '100k', 100, yUnits='-', show=False)
sl.fig2html(figMag, 600, caption='Característica de magnitude da rede RC.',
            label='figMag')

figdBmag = sl.plotSweep('RCdBmag', 'Magnitude em dB', numGain,
                        10, '100k', 100, funcType='dBmag', show=False)
sl.fig2html(figdBmag, 600, caption='Magnitude em dB da rede RC.',
            label='figdBmag')

figPhase = sl.plotSweep('RCphase', 'Característica de fase', numGain,
                        10, '100k', 100, funcType='phase', show=False)
sl.fig2html(figPhase, 600, caption='Característica de fase da rede RC.',
            label='figPhase')

# 7) Análise de polos e zeros
pzResult = sl.doPZ(cir, source='V1', detector='V_out')
pzGain = sl.doPZ(cir, source='V1', detector='V_out', pardefs='circuit')

sl.htmlPage('Polos e zeros')
sl.pz2html(pzResult, label='PZlistSym',
           labelText='Valores simbólicos dos polos e zeros')
sl.pz2html(pzGain, label='PZlist',
           labelText='Polos e zeros da rede')

figPZ = sl.plotPZ('PZ', 'Polos e zeros da rede RC', pzGain)
sl.fig2html(figPZ, 600, caption='Polos e zeros da rede RC.', label='figPZ')

# 8) Resposta ao degrau
numStep = sl.doStep(cir, source='V1', detector='V_out', pardefs="circuit")
figStep = sl.plotSweep('step', 'Resposta ao degrau unitário', numStep,
                       0, 1, 50, sweepScale='m', show=False)

sl.htmlPage('Gráficos no domínio do tempo')
sl.fig2html(figStep, 600, caption='Resposta ao degrau unitário da rede RC.',
            label='figStep')

# 9) Gerar links de navegação
sl.links2html()
