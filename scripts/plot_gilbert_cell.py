#!/usr/bin/env python3
"""
Script para visualizar os resultados do Gilbert Cell Mixer
Gera gráficos detalhados no tempo e em frequência (FFT)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Diretórios
base_dir = Path(__file__).parent.parent
data_dir = base_dir / "circuits" / "06_rf_comunicacoes"

# Carregar dados (ngspice wrdata não gera cabeçalhos)
time_full = pd.read_csv(data_dir / "gilbert_time_full.csv", sep=r'\s+', header=None,
                        names=['time', 'time_dup1', 'time_dup2', 'v_rf_ref', 'time_dup3', 'v_lo_ref', 'time_dup4', 'v_out'])

fft_data = pd.read_csv(data_dir / "gilbert_fft.csv", sep=r'\s+', header=None,
                       names=['freq', 'freq_dup1', 'freq_dup2', 'db', 'freq_dup3', 'mag'])

# Remover colunas duplicadas (ngspice wrdata repete a coluna independente)
time_full = time_full[['time', 'v_rf_ref', 'v_lo_ref', 'v_out']]
fft_data = fft_data[['freq', 'db', 'mag']]

print("Colunas time_full:", time_full.columns.tolist())
print("Colunas fft_data:", fft_data.columns.tolist())
print(f"Time range: {time_full['time'].min():.3f} to {time_full['time'].max():.3f} s")
print(f"Freq range: {fft_data['freq'].min():.0f} to {fft_data['freq'].max():.0f} Hz")

# ==============================================================================
# GRAFICO 1: Sinal no tempo - Primeiros 50ms (5 ciclos de 100Hz)
# ==============================================================================
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

# Filtrar primeiros 50ms
time_50ms = time_full[time_full['time'] <= 0.05]

# RF (1MHz)
axes[0].plot(time_50ms['time'] * 1000, time_50ms['v_rf_ref'], 'b-', linewidth=1.5, label='RF (1MHz, 200mVpp)')
axes[0].set_ylabel('RF [V]', fontsize=12)
axes[0].grid(True, alpha=0.3)
axes[0].legend(loc='upper right')
axes[0].set_title('Gilbert Cell Mixer - Sinais no Tempo (5 ciclos de 100Hz)', fontsize=14, fontweight='bold')

# LO (100Hz)
axes[1].plot(time_50ms['time'] * 1000, time_50ms['v_lo_ref'], 'r-', linewidth=2, label='LO (100Hz, 400mVpp)')
axes[1].set_ylabel('LO [V]', fontsize=12)
axes[1].grid(True, alpha=0.3)
axes[1].legend(loc='upper right')

# Saída (produto)
axes[2].plot(time_50ms['time'] * 1000, time_50ms['v_out'], 'g-', linewidth=1.5, label='Output (RF × LO)')
axes[2].set_xlabel('Tempo [ms]', fontsize=12)
axes[2].set_ylabel('Saída [V]', fontsize=12)
axes[2].grid(True, alpha=0.3)
axes[2].legend(loc='upper right')

plt.tight_layout()
plt.savefig(data_dir / "gilbert_time_detail.png", dpi=150, bbox_inches='tight')
print(f"✓ Salvo: gilbert_time_detail.png")
plt.close()

# ==============================================================================
# GRAFICO 2: FFT Completo (visão geral)
# ==============================================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 6))

# Plotar FFT em escala logarítmica
ax.semilogx(fft_data['freq'], fft_data['db'], 'b-', linewidth=1, label='Espectro de Saída')
ax.set_xlabel('Frequência [Hz]', fontsize=12)
ax.set_ylabel('Magnitude [dB]', fontsize=12)
ax.set_title('Gilbert Cell Mixer - Espectro FFT Completo', fontsize=14, fontweight='bold')
ax.grid(True, which='both', alpha=0.3)
ax.legend(loc='upper right')

# Destacar frequências de interesse
freq_interest = [100, 1e6-100, 1e6, 1e6+100]
for f in freq_interest:
    ax.axvline(f, color='r', linestyle='--', alpha=0.5, linewidth=1)

# Anotações
ax.text(100, -20, '100Hz\n(LO)', ha='center', fontsize=9, color='r')
ax.text(1e6-100, -20, '999.9kHz\n(f_RF - f_LO)', ha='center', fontsize=9, color='r')
ax.text(1e6, -20, '1MHz\n(RF)', ha='center', fontsize=9, color='r')
ax.text(1e6+100, -20, '1.0001MHz\n(f_RF + f_LO)', ha='center', fontsize=9, color='r')

plt.tight_layout()
plt.savefig(data_dir / "gilbert_fft_overview.png", dpi=150, bbox_inches='tight')
print(f"✓ Salvo: gilbert_fft_overview.png")
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

# Destacar 100Hz
ax.axvline(100, color='r', linestyle='--', alpha=0.7, linewidth=2, label='100Hz (LO leakage)')
ax.axvline(200, color='orange', linestyle='--', alpha=0.5, linewidth=1, label='200Hz (2×LO)')
ax.axvline(0, color='purple', linestyle='--', alpha=0.5, linewidth=1, label='DC')

ax.legend(loc='upper right')

plt.tight_layout()
plt.savefig(data_dir / "gilbert_fft_lowfreq.png", dpi=150, bbox_inches='tight')
print(f"✓ Salvo: gilbert_fft_lowfreq.png")
plt.close()

# ==============================================================================
# GRAFICO 4: FFT Zoom em 1MHz (produtos de mistura)
# ==============================================================================
fig, ax = plt.subplots(1, 1, figsize=(12, 6))

# Filtrar 999kHz - 1.001MHz
fft_1mhz = fft_data[(fft_data['freq'] >= 999000) & (fft_data['freq'] <= 1001000)]

ax.plot(fft_1mhz['freq'] / 1e3, fft_1mhz['db'], 'b-', linewidth=2, label='Espectro (999kHz - 1.001MHz)')
ax.set_xlabel('Frequência [kHz]', fontsize=12)
ax.set_ylabel('Magnitude [dB]', fontsize=12)
ax.set_title('Gilbert Cell Mixer - Zoom em 1MHz (Produtos de Mistura)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

# Destacar produtos
ax.axvline((1e6-100)/1e3, color='r', linestyle='--', alpha=0.7, linewidth=2, label='999.9kHz (f_RF - f_LO)')
ax.axvline(1e6/1e3, color='orange', linestyle='--', alpha=0.5, linewidth=1, label='1MHz (RF carrier)')
ax.axvline((1e6+100)/1e3, color='g', linestyle='--', alpha=0.7, linewidth=2, label='1000.1kHz (f_RF + f_LO)')

ax.legend(loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig(data_dir / "gilbert_fft_1mhz.png", dpi=150, bbox_inches='tight')
print(f"✓ Salvo: gilbert_fft_1mhz.png")
plt.close()

# ==============================================================================
# GRAFICO 5: Comparação temporal - 100 ciclos completos
# ==============================================================================
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

# Plotar todos os 100 ciclos
axes[0].plot(time_full['time'], time_full['v_lo_ref'], 'r-', linewidth=1.5, alpha=0.7, label='LO (100Hz)')
axes[0].set_ylabel('LO [V]', fontsize=12)
axes[0].grid(True, alpha=0.3)
axes[0].legend(loc='upper right')
axes[0].set_title('Gilbert Cell Mixer - 100 Ciclos Completos (1 segundo)', fontsize=14, fontweight='bold')

# Envelope da saída (modulação)
axes[1].plot(time_full['time'], time_full['v_out'], 'g-', linewidth=0.5, alpha=0.6, label='Output (RF × LO)')
axes[1].set_xlabel('Tempo [s]', fontsize=12)
axes[1].set_ylabel('Saída [V]', fontsize=12)
axes[1].grid(True, alpha=0.3)
axes[1].legend(loc='upper right')

plt.tight_layout()
plt.savefig(data_dir / "gilbert_time_100cycles.png", dpi=150, bbox_inches='tight')
print(f"✓ Salvo: gilbert_time_100cycles.png")
plt.close()

# ==============================================================================
# RESUMO
# ==============================================================================
print("\n" + "="*80)
print("RESUMO DA ANALISE DO GILBERT CELL MIXER")
print("="*80)

# Encontrar picos no FFT
# DC component
dc_idx = np.argmin(np.abs(fft_data['freq']))
dc_level = fft_data.iloc[dc_idx]['db']

# 100Hz (LO leakage)
lo_idx = np.argmin(np.abs(fft_data['freq'] - 100))
lo_level = fft_data.iloc[lo_idx]['db']

# 999.9kHz (diferença)
diff_idx = np.argmin(np.abs(fft_data['freq'] - 999900))
diff_level = fft_data.iloc[diff_idx]['db']

# 1MHz (RF carrier)
rf_idx = np.argmin(np.abs(fft_data['freq'] - 1e6))
rf_level = fft_data.iloc[rf_idx]['db']

# 1.0001MHz (soma)
sum_idx = np.argmin(np.abs(fft_data['freq'] - 1000100))
sum_level = fft_data.iloc[sum_idx]['db']

print(f"\nCOMPONENTES ESPECTRAIS:")
print(f"  DC (0Hz):              {dc_level:8.2f} dB")
print(f"  LO leakage (100Hz):    {lo_level:8.2f} dB")
print(f"  Diferença (999.9kHz):  {diff_level:8.2f} dB  <- Downconversion")
print(f"  RF carrier (1MHz):     {rf_level:8.2f} dB")
print(f"  Soma (1.0001MHz):      {sum_level:8.2f} dB  <- Upconversion")

print(f"\nREJEICAO DE PORTADORA:")
print(f"  RF suppression: {rf_level - diff_level:.2f} dB (ideal: >40dB)")

print(f"\nPRODUTOS UTEIS:")
print(f"  - Downconversion (999.9kHz): Usado em receptores super-heteródinos")
print(f"  - Upconversion (1.0001MHz): Usado em transmissores")

print("\n" + "="*80)
print("Gráficos gerados:")
print("  1. gilbert_time_detail.png   - Sinais no tempo (5 ciclos)")
print("  2. gilbert_fft_overview.png  - FFT completo (visão geral)")
print("  3. gilbert_fft_lowfreq.png   - FFT zoom em 0-1kHz")
print("  4. gilbert_fft_1mhz.png      - FFT zoom em 1MHz (produtos)")
print("  5. gilbert_time_100cycles.png - 100 ciclos completos")
print("="*80)
