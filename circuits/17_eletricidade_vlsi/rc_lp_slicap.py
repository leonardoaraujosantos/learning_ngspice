import slicap as sl

# 1) Cria estrutura do projeto
sl.initProject("RC_LowPass_SLiCAP")

# 2) Importa o circuito
cir = sl.makeCircuit("rc_lp.cir")

# 3) Define instrução de análise (transferência Laplace)
instr = sl.instruction()
instr.setCircuit(cir)

# Fonte de excitação (nome do elemento de fonte)
instr.setSource("V1")

# Detector: tensão de saída no nó "out"
instr.setDetector("V(out)")

# 4) Calcula H(s) = V(out)/V(in) simbólico
res = sl.doLaplace(instr)

print("\nH(s) = V(out)/V(in):\n")
print(res.laplace)

# 5) (Opcional) gerar relatório
sl.htmlPage("RC_LowPass_Report")
