import sympy as sp
from sympy import Function, symbols, Eq, solve, sqrt

# Parâmetros e tempo
t, s = symbols('t s', positive=True)
M, m, l, g = symbols('M m l g', positive=True)

# Funções do tempo
x = Function('x')(t)
θ = Function('theta')(t)
F = Function('F')(t)

# Equações de movimento (domínio do tempo, sem atrito b=0)
eq_carro   = Eq((M+m)*x.diff(t,2) + m*l*θ.diff(t,2), F)
eq_pendulo = Eq(m*l*x.diff(t,2) + m*l**2*θ.diff(t,2) - m*g*l*θ, 0)

print("=== Domínio do Tempo (b=0) ===")
sp.pprint(eq_carro)
sp.pprint(eq_pendulo)

# Transformada de Laplace (condições iniciais = 0)
X, Θ, Fs = symbols('X Theta F_s')
subs = {x.diff(t,2): s**2*X, x.diff(t): s*X, x: X,
        θ.diff(t,2): s**2*Θ, θ.diff(t): s*Θ, θ: Θ, F: Fs}

eq1_s = Eq(eq_carro.lhs.subs(subs), eq_carro.rhs.subs(subs))
eq2_s = Eq(eq_pendulo.lhs.subs(subs), eq_pendulo.rhs.subs(subs))

print("\n=== Domínio de Laplace ===")
sp.pprint(eq1_s)
sp.pprint(eq2_s)

# Resolver sistema e obter G(s) = Θ(s)/F(s)
sol = solve([eq1_s, eq2_s], (X, Θ), dict=True)[0]
G = sp.together(sp.simplify(sol[Θ] / Fs))

print("\n=== Função de Transferência G(s) = Θ(s)/F(s) ===")
sp.pprint(G)

# Numerador e Denominador
num, den = sp.fraction(G)
print("\nNumerador:", sp.expand(num))
print("Denominador:", sp.expand(den))
print("Coeficientes:", sp.Poly(den, s).all_coeffs())

# Polos simbólicos (resolver sem assumir s positivo)
s_geral = symbols('s')
den_geral = den.subs(s, s_geral)
polos = solve(den_geral, s_geral)

print("\n=== Polos (raízes do denominador) ===")
for i, p in enumerate(polos):
    print(f"p{i+1} =", sp.simplify(p))
