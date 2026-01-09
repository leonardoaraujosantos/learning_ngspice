"""
Test Lead/Lag Compensator for Inverted Pendulum
Versão melhorada com Lead duplo e otimização robusta
"""
import numpy as np
import matplotlib.pyplot as plt
import control as ct
from scipy.optimize import differential_evolution

print("="*70)
print("COMPENSADOR LEAD/LAG PARA PÊNDULO INVERTIDO")
print("="*70)

# =============================================================================
# 1. PLANTA - Pêndulo Invertido com Atrito
# =============================================================================
num_G = [1.0, 0.0]  # s
den_G = [0.15, 0.03, -6.867, -0.981]
G = ct.tf(num_G, den_G)

print("\n" + "="*70)
print("1. ANÁLISE DA PLANTA")
print("="*70)
print(G)

polos_G = G.poles()
print("\nPolos da Planta:")
for i, p in enumerate(polos_G):
    status = "INSTÁVEL" if p.real > 0 else "estável"
    print(f"  p{i+1} = {p.real:+.4f}  [{status}]")

print("""
ANÁLISE:
- O pêndulo tem um POLO INSTÁVEL em s = +6.74
- Um compensador Lead simples pode não ser suficiente
- Vamos testar: Lead-Lead (duplo), Lead com Integrador
""")

# =============================================================================
# 2. COMPENSADOR LEAD COM INTEGRADOR (equivalente a PID)
# =============================================================================
print("\n" + "="*70)
print("2. LEAD COM INTEGRADOR (Similar ao PID)")
print("="*70)

print("""
Estrutura:
                  (s + z₁)(s + z₂)
    C(s) = K · ─────────────────────
                        s

Isto é equivalente a um controlador PID!
- O 's' no denominador dá ação integral
- Os zeros (s + z₁)(s + z₂) dão ação proporcional-derivativa

Parâmetros: K, z₁, z₂ (3 parâmetros)
""")

def lead_integrator(K, z1, z2):
    """Lead com integrador: C(s) = K * (s+z1)*(s+z2) / s"""
    num = [K, K*(z1+z2), K*z1*z2]  # K*(s² + (z1+z2)*s + z1*z2)
    den = [1, 0]  # s
    return ct.tf(num, den)

def cost_lead_int(params):
    """Custo para Lead com Integrador."""
    K, z1, z2 = params

    if K <= 0 or z1 <= 0 or z2 <= 0:
        return 1e6

    try:
        C = lead_integrator(K, z1, z2)
        T = ct.feedback(C * G, 1)
        T = ct.minreal(T, verbose=False)

        poles = T.poles()
        max_real = max(p.real for p in poles)
        if max_real >= -0.01:
            return 1e6 + max_real * 100

        t = np.linspace(0, 15, 500)
        t, y = ct.step_response(T, t)

        overshoot = max(0, np.max(y) - 1)
        iae = np.trapz(np.abs(1 - y), t)
        ess = abs(1 - y[-1])

        return 5*overshoot**2 + 0.5*iae + 10*ess

    except:
        return 1e6

print("Otimizando Lead com Integrador...")
bounds_li = [(10, 500), (0.1, 20), (0.1, 20)]
result_li = differential_evolution(cost_lead_int, bounds_li, seed=42,
                                    maxiter=500, tol=1e-6, disp=False)

K_li, z1_li, z2_li = result_li.x
print(f"\nResultado:")
print(f"  K = {K_li:.4f}")
print(f"  z₁ = {z1_li:.4f}")
print(f"  z₂ = {z2_li:.4f}")
print(f"  Custo = {result_li.fun:.4f}")

C_li = lead_integrator(K_li, z1_li, z2_li)
T_li = ct.minreal(ct.feedback(C_li * G, 1), verbose=False)
poles_li = T_li.poles()

print(f"\nCompensador C(s):")
print(C_li)

print(f"\nPolos da Malha Fechada:")
stable_li = True
for i, p in enumerate(poles_li):
    status = "INSTÁVEL" if p.real > 0 else "estável"
    if p.real > 0: stable_li = False
    print(f"  p{i+1} = {p.real:+.4f} + {p.imag:+.4f}j  [{status}]")
print(f"\nSistema é {'ESTÁVEL' if stable_li else 'INSTÁVEL'}")

# =============================================================================
# 3. COMPENSADOR LEAD DUPLO (Lead-Lead)
# =============================================================================
print("\n" + "="*70)
print("3. LEAD DUPLO (Lead-Lead)")
print("="*70)

print("""
Estrutura:
                  s + z₁     s + z₂
    C(s) = K · ────────── · ──────────
                  s + p₁     s + p₂

Restrições:
- LEAD 1: z₁ < p₁
- LEAD 2: z₂ < p₂

Cada estágio Lead adiciona até +90° de fase!
Dois estágios podem adicionar até +180° → mais chance de estabilizar
""")

def lead_lead(K, z1, p1, z2, p2):
    """Lead duplo."""
    return K * ct.tf([1, z1], [1, p1]) * ct.tf([1, z2], [1, p2])

def cost_lead_lead(params):
    K, z1, p1, z2, p2 = params

    # Restrições Lead
    if z1 >= p1 or z2 >= p2:
        return 1e6
    if K <= 0:
        return 1e6

    try:
        C = lead_lead(K, z1, p1, z2, p2)
        T = ct.feedback(C * G, 1)
        T = ct.minreal(T, verbose=False)

        poles = T.poles()
        max_real = max(p.real for p in poles)
        if max_real >= -0.01:
            return 1e6 + max_real * 100

        t = np.linspace(0, 15, 500)
        t, y = ct.step_response(T, t)

        overshoot = max(0, np.max(y) - 1)
        iae = np.trapz(np.abs(1 - y), t)
        ess = abs(1 - y[-1])

        return 5*overshoot**2 + 0.5*iae + 10*ess

    except:
        return 1e6

print("Otimizando Lead-Lead...")
bounds_ll = [(10, 1000), (0.1, 50), (1, 100), (0.1, 50), (1, 100)]
result_ll = differential_evolution(cost_lead_lead, bounds_ll, seed=42,
                                    maxiter=500, tol=1e-6, disp=False)

K_ll, z1_ll, p1_ll, z2_ll, p2_ll = result_ll.x
print(f"\nResultado:")
print(f"  K = {K_ll:.4f}")
print(f"  LEAD 1: z₁={z1_ll:.4f}, p₁={p1_ll:.4f} (razão={p1_ll/z1_ll:.2f})")
print(f"  LEAD 2: z₂={z2_ll:.4f}, p₂={p2_ll:.4f} (razão={p2_ll/z2_ll:.2f})")
print(f"  Custo = {result_ll.fun:.4f}")

C_ll = lead_lead(K_ll, z1_ll, p1_ll, z2_ll, p2_ll)
T_ll = ct.minreal(ct.feedback(C_ll * G, 1), verbose=False)
poles_ll = T_ll.poles()

print(f"\nPolos da Malha Fechada:")
stable_ll = True
for i, p in enumerate(poles_ll):
    status = "INSTÁVEL" if p.real > 0 else "estável"
    if p.real > 0: stable_ll = False
    print(f"  p{i+1} = {p.real:+.4f} + {p.imag:+.4f}j  [{status}]")
print(f"\nSistema é {'ESTÁVEL' if stable_ll else 'INSTÁVEL'}")

# =============================================================================
# 4. COMPARAÇÃO E ESCOLHA DO MELHOR
# =============================================================================
print("\n" + "="*70)
print("4. COMPARAÇÃO")
print("="*70)

t = np.linspace(0, 15, 500)
best_name = None
best_T = None
best_C = None

if stable_li:
    t_li, y_li = ct.step_response(T_li, t)
    os_li = (np.max(y_li) - 1) * 100
    ess_li = abs(1 - y_li[-1]) * 100
    print(f"\nLEAD + INTEGRADOR:")
    print(f"  Overshoot: {os_li:.1f}%")
    print(f"  Erro regime: {ess_li:.2f}%")
    print(f"  Custo: {result_li.fun:.4f}")
    if best_name is None or result_li.fun < result_ll.fun:
        best_name = "Lead + Integrador"
        best_T = T_li
        best_C = C_li

if stable_ll:
    t_ll, y_ll = ct.step_response(T_ll, t)
    os_ll = (np.max(y_ll) - 1) * 100
    ess_ll = abs(1 - y_ll[-1]) * 100
    print(f"\nLEAD DUPLO:")
    print(f"  Overshoot: {os_ll:.1f}%")
    print(f"  Erro regime: {ess_ll:.2f}%")
    print(f"  Custo: {result_ll.fun:.4f}")
    if best_name is None or (stable_li and result_ll.fun < result_li.fun):
        best_name = "Lead Duplo"
        best_T = T_ll
        best_C = C_ll

if best_name:
    print(f"\n→ MELHOR COMPENSADOR: {best_name}")
else:
    print("\n→ Nenhum compensador estabilizou o sistema!")

# =============================================================================
# 5. GRÁFICOS
# =============================================================================
print("\n" + "="*70)
print("5. GERANDO GRÁFICOS")
print("="*70)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Resposta ao degrau
ax1 = axes[0, 0]
if stable_li:
    ax1.plot(t_li, y_li, 'b-', lw=2, label=f'Lead+Int (OS={os_li:.1f}%)')
if stable_ll:
    ax1.plot(t_ll, y_ll, 'g-', lw=2, label=f'Lead-Lead (OS={os_ll:.1f}%)')
ax1.axhline(1, color='r', linestyle='--', label='Referência')
ax1.fill_between(t, 0.95, 1.05, alpha=0.2, color='green')
ax1.set_xlabel('Tempo (s)')
ax1.set_ylabel('Ângulo θ')
ax1.set_title('Resposta ao Degrau', fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 15])

# Bode Magnitude
ax2 = axes[0, 1]
omega = np.logspace(-2, 3, 500)
mag_G, _, _ = ct.frequency_response(G, omega)
ax2.semilogx(omega, 20*np.log10(np.abs(mag_G)), 'k--', lw=1.5, label='Planta G(s)')
if stable_li:
    L_li = C_li * G
    mag_li, _, _ = ct.frequency_response(L_li, omega)
    ax2.semilogx(omega, 20*np.log10(np.abs(mag_li)), 'b-', lw=2, label='Lead+Int · G')
if stable_ll:
    L_ll = C_ll * G
    mag_ll, _, _ = ct.frequency_response(L_ll, omega)
    ax2.semilogx(omega, 20*np.log10(np.abs(mag_ll)), 'g-', lw=2, label='Lead-Lead · G')
ax2.axhline(0, color='r', linestyle=':', lw=1)
ax2.set_xlabel('Frequência (rad/s)')
ax2.set_ylabel('Magnitude (dB)')
ax2.set_title('Diagrama de Bode - Magnitude', fontweight='bold')
ax2.legend()
ax2.grid(True, which='both', alpha=0.3)

# Bode Fase
ax3 = axes[1, 0]
phase_G = np.rad2deg(np.unwrap(np.angle(mag_G)))
ax3.semilogx(omega, phase_G, 'k--', lw=1.5, label='Planta G(s)')
if stable_li:
    phase_li = np.rad2deg(np.unwrap(np.angle(mag_li)))
    ax3.semilogx(omega, phase_li, 'b-', lw=2, label='Lead+Int · G')
if stable_ll:
    phase_ll = np.rad2deg(np.unwrap(np.angle(mag_ll)))
    ax3.semilogx(omega, phase_ll, 'g-', lw=2, label='Lead-Lead · G')
ax3.axhline(-180, color='r', linestyle=':', lw=1)
ax3.set_xlabel('Frequência (rad/s)')
ax3.set_ylabel('Fase (graus)')
ax3.set_title('Diagrama de Bode - Fase', fontweight='bold')
ax3.legend()
ax3.grid(True, which='both', alpha=0.3)

# Mapa de Polos
ax4 = axes[1, 1]
for p in polos_G:
    color = 'red' if p.real > 0 else 'black'
    ax4.plot(p.real, p.imag, 'x', ms=15, mew=3, color=color)
ax4.plot([], [], 'kx', ms=12, mew=2, label='Planta (MA)')
if stable_li:
    for p in poles_li:
        ax4.plot(p.real, p.imag, 'bs', ms=10, mfc='none', mew=2)
    ax4.plot([], [], 'bs', ms=10, mfc='none', mew=2, label='Lead+Int (MF)')
if stable_ll:
    for p in poles_ll:
        ax4.plot(p.real, p.imag, 'go', ms=8, mfc='none', mew=2)
    ax4.plot([], [], 'go', ms=8, mfc='none', mew=2, label='Lead-Lead (MF)')

ax4.axvspan(-50, 0, alpha=0.1, color='green')
ax4.axvspan(0, 10, alpha=0.1, color='red')
ax4.axvline(0, color='k', lw=0.5)
ax4.axhline(0, color='k', lw=0.5)
ax4.set_xlabel('Re(s)')
ax4.set_ylabel('Im(s)')
ax4.set_title('Mapa de Polos', fontweight='bold')
ax4.legend(loc='upper left')
ax4.grid(True, alpha=0.3)
ax4.set_xlim([-50, 10])
ax4.set_ylim([-20, 20])

plt.tight_layout()
plt.savefig('/Users/leonardoaraujo/work/learning_ngspice/control/lead_lag_test.png', dpi=150)
print("Gráfico salvo: lead_lag_test.png")

print("\n" + "="*70)
print("TESTE CONCLUÍDO!")
print("="*70)
