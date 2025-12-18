#!/usr/bin/env python3
"""
Script para visualizar os resultados do Gilbert Cell Mixer (versão corrigida)
Gera gráficos detalhados no tempo e em frequência (FFT)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Diretórios
base_dir = Path(__file__).parent.parent
data_dir = base_dir / "circuits" / "06_rf_comunicacoes"

print("Carregando dados do Gilbert Cell Mixer (versão corrigida)...")

# Carregar dados (ngspice wrdata não gera cabeçalhos e repete coluna independente)
time_data = pd.read_csv(data_dir / "gilbert_fixed_time.csv", sep=r'\s+', header=None,
                        names=['time', 'time_dup1', 'time_dup2', 'v_rf_mon', 'time_dup3', 'v_lo_mon', 'time_dup4', 'v_out'])

fft_data = pd.read_csv(data_dir / "gilbert_fixed_fft.csv", sep=r'\s+', header=None,
                       names=['freq', 'freq_dup1', 'freq_dup2', 'db', 'freq_dup3', 'mag'])

# Remover colunas duplicadas
time_data = time_data[['time', 'v_rf_mon', 'v_lo_mon', 'v_out']]
fft_data = fft_data[['freq', 'db', 'mag']]

print(f"✓ Dados carregados:")
print(f"  Time range: {time_data['time'].min():.4f} to {time_data['time'].max():.4f} s ({len(time_data)} pontos)")
print(f"  Freq range: {fft_data['freq'].min():.0f} to {fft_data['freq'].max():.0f} Hz")

# ==============================================================================
# GRAFICO 1: Sinal no tempo - Primeiros 20ms (2 ciclos de 100Hz)
# ==============================================================================
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

# Filtrar primeiros 20ms
time_20ms = time_data[time_data['time'] <= 0.02]

# RF (1MHz)
axes[0].plot(time_20ms['time'] * 1000, time_20ms['v_rf_mon'] * 1000, 'b-', linewidth=1, label='RF: 1MHz, 100mVpp')
axes[0].set_ylabel('RF [mV]', fontsize=12)
axes[0].grid(True, alpha=0.3)
axes[0].legend(loc='upper right')
axes[0].set_title('Gilbert Cell Mixer - Sinais no Tempo (2 ciclos de 100Hz)', fontsize=14, fontweight='bold')

# LO (100Hz)
axes[1].plot(time_20ms['time'] * 1000, time_20ms['v_lo_mon'] * 1000, 'r-', linewidth=2, label='LO: 100Hz, 200mVpp')
axes[1].set_ylabel('LO [mV]', fontsize=12)
axes[1].grid(True, alpha=0.3)
axes[1].legend(loc='upper right')

# Saída (produto)
axes[2].plot(time_20ms['time'] * 1000, time_20ms['v_out'] * 1000, 'g-', linewidth=1, label='Output: RF × LO (gain=10)')
axes[2].set_xlabel('Tempo [ms]', fontsize=12)
axes[2].set_ylabel('Saída [mV]', fontsize=12)
axes[2].grid(True, alpha=0.3)
axes[2].legend(loc='upper right')

plt.tight_layout()
plt.savefig(data_dir / "gilbert_fixed_time_detail.png", dpi=150, bbox_inches='tight')
print(f"✓ Salvo: gilbert_fixed_time_detail.png")
plt.close()

# ==============================================================================
# GRAFICO 2: FFT Completo (visão geral)
# ==============================================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 6))

# Plotar FFT em escala logarítmica
ax.semilogx(fft_data['freq'], fft_data['db'], 'b-', linewidth=1, label='Espectro de Saída')
ax.set_xlabel('Frequência [Hz]', fontsize=12)
ax.set_ylabel('Magnitude [dB]', fontsize=12)
ax.set_title('Gilbert Cell Mixer - Espectro FFT Completo (DC a 5MHz)', fontsize=14, fontweight='bold')
ax.grid(True, which='both', alpha=0.3)
ax.legend(loc='upper right')
ax.set_xlim(1, 5e6)

# Destacar frequências de interesse
freq_interest = [100, 999900, 1e6, 1000100]
labels = ['100Hz\n(LO)', '999.9kHz\n(f_RF - f_LO)', '1MHz\n(RF)', '1.0001MHz\n(f_RF + f_LO)']
for f, lbl in zip(freq_interest, labels):
    ax.axvline(f, color='r', linestyle='--', alpha=0.5, linewidth=1)

plt.tight_layout()
plt.savefig(data_dir / "gilbert_fixed_fft_overview.png", dpi=150, bbox_inches='tight')
print(f"✓ Salvo: gilbert_fixed_fft_overview.png")
plt.close()

# ==============================================================================
# GRAFICO 3: FFT Zoom em 100Hz (vazamento de LO)
# ==============================================================================
fig, ax = plt.subplots(1, 1, figsize=(10, 6))

# Filtrar 0-1kHz
fft_lowfreq = fft_data[(fft_data['freq'] >= 0) & (fft_data['freq'] <= 1000)]

ax.plot(fft_lowfreq['freq'], fft_lowfreq['db'], 'b-', linewidth=2, label='Espectro (0-1kHz)')
ax.set_xlabel('Frequência [Hz]', fontsize=12)
ax.set_ylabel('Magnitude [dB]', fontsize=12)
ax.set_title('Gilbert Cell Mixer - Zoom em Baixa Frequência (0-1kHz)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(loc='upper right')

# Destacar componentes
ax.axvline(100, color='r', linestyle='--', alpha=0.7, linewidth=2, label='100Hz (LO leakage)')
ax.axvline(200, color='orange', linestyle='--', alpha=0.5, linewidth=1, label='200Hz (2×LO)')

ax.legend(loc='upper right')

plt.tight_layout()
plt.savefig(data_dir / "gilbert_fixed_fft_lowfreq.png", dpi=150, bbox_inches='tight')
print(f"✓ Salvo: gilbert_fixed_fft_lowfreq.png")
plt.close()

# ==============================================================================
# GRAFICO 4: FFT Zoom em 1MHz (produtos de mistura) - PRINCIPAL!
# ==============================================================================
fig, ax = plt.subplots(1, 1, figsize=(12, 6))

# Filtrar 999kHz - 1.001MHz
fft_1mhz = fft_data[(fft_data['freq'] >= 999000) & (fft_data['freq'] <= 1001000)]

ax.plot(fft_1mhz['freq'] / 1e3, fft_1mhz['db'], 'b-', linewidth=2, label='Espectro (999-1001kHz)')
ax.set_xlabel('Frequência [kHz]', fontsize=12)
ax.set_ylabel('Magnitude [dB]', fontsize=12)
ax.set_title('Gilbert Cell Mixer - Produtos de Mistura em 1MHz', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

# Destacar produtos
ax.axvline(999.9, color='g', linestyle='--', alpha=0.7, linewidth=2, label='999.9kHz (f_RF - f_LO) ← DOWNCONVERSION')
ax.axvline(1000, color='orange', linestyle='--', alpha=0.5, linewidth=1.5, label='1000kHz (RF carrier leak)')
ax.axvline(1000.1, color='purple', linestyle='--', alpha=0.7, linewidth=2, label='1000.1kHz (f_RF + f_LO) ← UPCONVERSION')

ax.legend(loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig(data_dir / "gilbert_fixed_fft_1mhz.png", dpi=150, bbox_inches='tight')
print(f"✓ Salvo: gilbert_fixed_fft_1mhz.png")
plt.close()

# ==============================================================================
# GRAFICO 5: Visão completa temporal - 10 ciclos de 100Hz
# ==============================================================================
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

# Plotar todos os 10 ciclos
axes[0].plot(time_data['time'] * 1000, time_data['v_lo_mon'] * 1000, 'r-', linewidth=1.5, alpha=0.7, label='LO (100Hz)')
axes[0].set_ylabel('LO [mV]', fontsize=12)
axes[0].grid(True, alpha=0.3)
axes[0].legend(loc='upper right')
axes[0].set_title('Gilbert Cell Mixer - 10 Ciclos Completos (0.1 segundo)', fontsize=14, fontweight='bold')

# Envelope da saída (modulação)
# Downsample para visualização (muito denso com 1 milhão de pontos)
time_down = time_data[::100]  # Pegar 1 a cada 100 pontos
axes[1].plot(time_down['time'] * 1000, time_down['v_out'] * 1000, 'g-', linewidth=0.5, alpha=0.6, label='Output (RF × LO)')
axes[1].set_xlabel('Tempo [ms]', fontsize=12)
axes[1].set_ylabel('Saída [mV]', fontsize=12)
axes[1].grid(True, alpha=0.3)
axes[1].legend(loc='upper right')

plt.tight_layout()
plt.savefig(data_dir / "gilbert_fixed_time_full.png", dpi=150, bbox_inches='tight')
print(f"✓ Salvo: gilbert_fixed_time_full.png")
plt.close()

# ==============================================================================
# RESUMO
# ==============================================================================
print("\n" + "="*80)
print("RESUMO DA ANALISE DO GILBERT CELL MIXER (VERSÃO CORRIGIDA)")
print("="*80)

# Encontrar picos no FFT
# DC component
dc_idx = np.argmin(np.abs(fft_data['freq'] - 10))
dc_level = fft_data.iloc[dc_idx]['db']

# 100Hz (LO leakage)
lo_idx = np.argmin(np.abs(fft_data['freq'] - 100))
lo_level = fft_data.iloc[lo_idx]['db']

# 999.9kHz (diferença)
diff_idx = np.argmin(np.abs(fft_data['freq'] - 999900))
diff_level = fft_data.iloc[diff_idx]['db']
diff_freq = fft_data.iloc[diff_idx]['freq']

# 1MHz (RF carrier)
rf_idx = np.argmin(np.abs(fft_data['freq'] - 1e6))
rf_level = fft_data.iloc[rf_idx]['db']

# 1.0001MHz (soma)
sum_idx = np.argmin(np.abs(fft_data['freq'] - 1000100))
sum_level = fft_data.iloc[sum_idx]['db']
sum_freq = fft_data.iloc[sum_idx]['freq']

print(f"\nCOMPONENTES ESPECTRAIS:")
print(f"  DC (~0Hz):                  {dc_level:8.2f} dB")
print(f"  LO leakage (100Hz):         {lo_level:8.2f} dB")
print(f"  Diferença ({diff_freq/1e3:.1f}kHz):  {diff_level:8.2f} dB  ← DOWNCONVERSION (f_RF - f_LO)")
print(f"  RF carrier (1MHz):          {rf_level:8.2f} dB  (vazamento)")
print(f"  Soma ({sum_freq/1e3:.1f}kHz):       {sum_level:8.2f} dB  ← UPCONVERSION (f_RF + f_LO)")

# Conversão de dB para linear
diff_linear = 10**(diff_level/20)
sum_linear = 10**(sum_level/20)

print(f"\nNÍVEIS LINEARES:")
print(f"  Produto de diferença:  {diff_linear*1000:.2f} mV")
print(f"  Produto de soma:       {sum_linear*1000:.2f} mV")

print(f"\nREJEIÇÃO E ISOLAMENTO:")
print(f"  Supressão de RF: {diff_level - rf_level:.1f} dB")
print(f"  Isolamento LO-output: {diff_level - lo_level:.1f} dB")

print(f"\nRESULTADO:")
if diff_level > -30 and sum_level > -30:
    print(f"  ✅ MIXER FUNCIONANDO CORRETAMENTE!")
    print(f"     Produtos de mistura claramente visíveis em:")
    print(f"     - {diff_freq/1e3:.1f} kHz (downconversion)")
    print(f"     - {sum_freq/1e3:.1f} kHz (upconversion)")
else:
    print(f"  ⚠ Produtos de mistura fracos")

print(f"\nAPLICAÇÕES:")
print(f"  • Receptor super-heteródino: converte RF → IF (usa diferença)")
print(f"  • Transmissor: converte baseband → RF (usa soma)")
print(f"  • Demodulador: recupera sinal modulado")
print(f"  • PLL: detector de fase")

print("\n" + "="*80)
print("Gráficos gerados:")
print("  1. gilbert_fixed_time_detail.png - Sinais no tempo (2 ciclos)")
print("  2. gilbert_fixed_fft_overview.png - FFT completo (DC a 5MHz)")
print("  3. gilbert_fixed_fft_lowfreq.png - FFT zoom em 0-1kHz")
print("  4. gilbert_fixed_fft_1mhz.png - Produtos de mistura em 1MHz ⭐")
print("  5. gilbert_fixed_time_full.png - 10 ciclos completos")
print("="*80)
