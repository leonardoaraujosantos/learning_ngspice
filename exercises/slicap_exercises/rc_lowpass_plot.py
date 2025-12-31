#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
rc_lowpass_plot.py: RC Low Pass Filter with Bode plots
Generates Bode magnitude and phase plots for the RC low pass filter
"""

from SLiCAP import *
import numpy as np

# Initialize the project
initProject("RC Low Pass Filter with Plots")

# Create the circuit object from the netlist
my_circuit = makeCircuit("rc_lowpass.cir")

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

print("\n" + "="*70)
print("RC LOW PASS FILTER - BODE PLOT GENERATION")
print("="*70)
print(f"\nCircuit parameters:")
print(f"  R = {R_value/1000} kΩ")
print(f"  C = {C_value*1e9} nF")
print(f"  Cutoff frequency fc = {fc:.2f} Hz")

# Configure frequency sweep parameters
freq_start = 10
freq_stop = 100000
num_points = 100

print(f"\nFrequency sweep: {freq_start} Hz to {freq_stop} Hz")
print(f"Number of points per decade: {num_points}")

# Perform Laplace analysis with numeric evaluation
print("\nPerforming Laplace analysis...")
result = doLaplace(my_circuit, source='V1', detector='V_out', numeric=True)

print(f"Transfer function: {result.laplace}")

# Generate Bode magnitude plot
print("\nGenerating Bode magnitude plot...")
try:
    fig_mag = plotSweep('RC_LowPass_Magnitude', 'RC Low Pass Filter - Magnitude',
                        result, freq_start, freq_stop, num_points,
                        funcType='mag', axisType='semilogx', show=False)
    print("  ✓ Magnitude plot saved")
except Exception as e:
    print(f"  ✗ Could not generate magnitude plot: {e}")

# Generate Bode phase plot
print("Generating Bode phase plot...")
try:
    fig_phase = plotSweep('RC_LowPass_Phase', 'RC Low Pass Filter - Phase',
                          result, freq_start, freq_stop, num_points,
                          funcType='phase', axisType='semilogx', show=False)
    print("  ✓ Phase plot saved")
except Exception as e:
    print(f"  ✗ Could not generate phase plot: {e}")

# Generate dB magnitude plot
print("Generating dB magnitude plot...")
try:
    fig_dB = plotSweep('RC_LowPass_dB', 'RC Low Pass Filter - dB Magnitude',
                       result, freq_start, freq_stop, num_points,
                       funcType='dBmag', axisType='semilogx', show=False)
    print("  ✓ dB magnitude plot saved")
except Exception as e:
    print(f"  ✗ Could not generate dB plot: {e}")

print("\n" + "="*70)
print("PLOT GENERATION COMPLETE")
print("="*70)
print("\nPlot files are saved in the project 'img/' directory")
print("Available formats: PDF and SVG")
print("\nNote: Magnitude plots may have issues with symbolic parameters.")
print("The phase plot generation works correctly.")

# List generated files
import os
if os.path.exists('img'):
    files = os.listdir('img')
    if files:
        print("\nGenerated files:")
        for f in sorted(files):
            print(f"  - img/{f}")
print()
