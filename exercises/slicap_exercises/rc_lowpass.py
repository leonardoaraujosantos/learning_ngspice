#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
rc_lowpass.py: RC Low Pass Filter analysis with SLiCAP
Analyzes a first-order RC low pass filter
"""

from SLiCAP import *
import numpy as np

# Initialize the project
initProject("RC Low Pass Filter")

# Create the circuit object from the netlist
my_circuit = makeCircuit("rc_lowpass.cir")

# Display circuit information
print("\n" + "="*70)
print("RC LOW PASS FILTER ANALYSIS")
print("="*70)
print("\nCircuit title:", my_circuit.title)
print("Circuit nodes:", my_circuit.nodes)
print("Circuit elements:", list(my_circuit.elements.keys()))

# Define parameter values
R_value = 1000      # 1kΩ
C_value = 100e-9    # 100nF
V_in_value = 1      # 1V AC source

# Calculate cutoff frequency
fc = 1 / (2 * np.pi * R_value * C_value)

# Set the circuit parameters
my_circuit.defPar("R", R_value)
my_circuit.defPar("C", C_value)
my_circuit.defPar("V_in", V_in_value)

print("\n" + "-"*70)
print("CIRCUIT PARAMETERS")
print("-"*70)
print(f"R = {R_value} Ω = {R_value/1000} kΩ")
print(f"C = {C_value} F = {C_value*1e9} nF")
print(f"V_in = {V_in_value} V")
print(f"\nCalculated cutoff frequency fc = 1/(2πRC)")
print(f"fc = 1/(2π × {R_value} × {C_value})")
print(f"fc = {fc:.2f} Hz")
print(f"ωc = 2πfc = {2*np.pi*fc:.2f} rad/s")

print("\n" + "-"*70)
print("SYMBOLIC ANALYSIS")
print("-"*70)

# Perform Laplace analysis
result = doLaplace(my_circuit, source='V1', detector='V_out')

print("\nSymbolic transfer function H(s) = V_out/V_in:")
transfer = result.laplace
print(transfer)

# Simplify and factor the transfer function
from sympy import simplify, factor, expand
transfer_simplified = simplify(transfer)
print("\nSimplified transfer function:")
print(transfer_simplified)

# Display numerator and denominator separately
print("\nNumerator:")
print(result.numer)
print("\nDenominator:")
print(result.denom)

# Expected form: H(s) = 1/(1 + sRC)
print("\n" + "-"*70)
print("TRANSFER FUNCTION ANALYSIS")
print("-"*70)
print("Expected form for RC low pass filter:")
print("H(s) = 1/(1 + sRC)")
print("     = 1/(1 + s/ωc)")
print("     = ωc/(s + ωc)")
print(f"\nwhere ωc = 1/(RC) = {1/(R_value*C_value):.2f} rad/s")

print("\n" + "-"*70)
print("FREQUENCY RESPONSE ANALYSIS")
print("-"*70)

# Define frequency points for analysis (logarithmic spacing)
# From 10 Hz to 100 kHz
freq_start = 10
freq_stop = 100000
num_points = 100

# Create numeric result for frequency response
result_numeric = doLaplace(my_circuit, source='V1', detector='V_out', numeric=True)

print(f"\nAnalyzing frequency response from {freq_start} Hz to {freq_stop} Hz")

# Evaluate transfer function at specific frequencies
test_frequencies = [10, 100, fc, 1000, 10000]
print(f"\nMagnitude and phase at key frequencies:")
print(f"{'Frequency [Hz]':<15} {'|H(jω)|':<12} {'|H(jω)| [dB]':<15} {'∠H(jω) [°]':<15}")
print("-"*70)

for freq in test_frequencies:
    omega = 2 * np.pi * freq
    # Substitute s = jω
    H_at_freq = transfer_simplified.subs([('R', R_value), ('C', C_value), ('s', 1j*omega)])
    magnitude = abs(complex(H_at_freq))
    magnitude_dB = 20 * np.log10(magnitude) if magnitude > 0 else -np.inf
    phase_deg = np.angle(complex(H_at_freq)) * 180 / np.pi

    freq_str = f"{freq:.2f}" if freq != fc else f"{freq:.2f} (fc)"
    print(f"{freq_str:<15} {magnitude:<12.4f} {magnitude_dB:<15.2f} {phase_deg:<15.2f}")

# Theoretical values at cutoff frequency
print(f"\nAt cutoff frequency fc = {fc:.2f} Hz:")
print(f"  Expected |H(jωc)| = 1/√2 ≈ 0.707 (-3 dB)")
print(f"  Expected ∠H(jωc) = -45°")

print("\n" + "-"*70)
print("DC AND HIGH FREQUENCY BEHAVIOR")
print("-"*70)

# DC gain (s=0)
dc_gain = transfer_simplified.subs('s', 0)
print(f"DC Gain (f=0, s=0): H(0) = {dc_gain}")
print(f"  Magnitude: {abs(float(dc_gain.subs([('R', R_value), ('C', C_value)])))}")

# High frequency behavior (s→∞)
print(f"\nHigh frequency behavior (f→∞):")
print(f"  H(s) → 0 (signals are attenuated)")

# Roll-off rate
print(f"\nRoll-off rate: -20 dB/decade (first-order filter)")
print(f"             or -6 dB/octave")

print("\n" + "-"*70)
print("POLE-ZERO ANALYSIS")
print("-"*70)

# Find poles and zeros
result_pz = doPZ(my_circuit, source='V1', detector='V_out')

print("\nPoles (values of s where denominator = 0):")
if hasattr(result_pz, 'poles') and result_pz.poles:
    poles = result_pz.poles
    print(f"  {poles}")
    # Substitute numeric values
    if not isinstance(poles, list):
        poles = [poles]
    for i, pole in enumerate(poles):
        pole_numeric = pole.subs([('R', R_value), ('C', C_value)])
        print(f"  p{i+1} = {pole} = {complex(pole_numeric)}")
        print(f"       = {float(pole_numeric.evalf()):.2f} rad/s")
else:
    # Calculate manually
    pole = -1/(R_value*C_value)
    print(f"  p = -1/(RC) = {pole:.2f} rad/s")
    print(f"  fp = |p|/(2π) = {abs(pole)/(2*np.pi):.2f} Hz")

print("\nZeros (values of s where numerator = 0):")
if hasattr(result_pz, 'zeros') and result_pz.zeros:
    print(f"  {result_pz.zeros}")
else:
    print("  None (no zeros in finite s-plane)")

print("\n" + "-"*70)
print("FILTER CHARACTERISTICS SUMMARY")
print("-"*70)
print(f"Filter type:        First-order RC low pass filter")
print(f"Cutoff frequency:   fc = {fc:.2f} Hz")
print(f"Time constant:      τ = RC = {R_value*C_value:.6f} s = {R_value*C_value*1000:.3f} ms")
print(f"Attenuation at fc:  -3 dB")
print(f"Phase shift at fc:  -45°")
print(f"Roll-off:           -20 dB/decade")
print(f"DC gain:            0 dB (1.0)")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)

# Optional: Generate Bode plots if possible
print("\n" + "-"*70)
print("GENERATING PLOTS")
print("-"*70)

try:
    # Set frequency range for plotting
    ini.frequency = 'decade'
    ini.freqStart = freq_start
    ini.freqStop = freq_stop
    ini.freqSteps = num_points

    print(f"Frequency sweep: {freq_start} Hz to {freq_stop} Hz ({num_points} points/decade)")
    print("Plot files will be saved in the project directory")
    print("\nTo generate Bode plots, you can use:")
    print("  result_plot = doLaplace(my_circuit, source='V1', detector='V_out')")
    print("  fig_mag = plotSweep('RC_Filter_Magnitude', result_plot, 'magnitude', show=True)")
    print("  fig_phase = plotSweep('RC_Filter_Phase', result_plot, 'phase', show=True)")

except Exception as e:
    print(f"Note: Plot generation skipped ({e})")

print()
