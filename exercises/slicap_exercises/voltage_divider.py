#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
voltage_divider_v2.py: Voltage divider analysis with SLiCAP
Calculates the output voltage of a voltage divider with 2 resistors and a 10V DC battery
"""

from SLiCAP import *

# Initialize the project
initProject("Voltage Divider Example")

# Create the circuit object from the netlist
my_circuit = makeCircuit("voltage_divider.cir")

# Display circuit information
print("\n" + "="*60)
print("VOLTAGE DIVIDER CIRCUIT ANALYSIS")
print("="*60)
print("\nCircuit title:", my_circuit.title)
print("Circuit nodes:", my_circuit.nodes)
print("Circuit elements:", list(my_circuit.elements.keys()))

# Define parameter values
R1_value = 1000    # 1kΩ
R2_value = 2000    # 2kΩ
V_in_value = 10    # 10V DC

# Set the circuit parameters
my_circuit.defPar("R1", R1_value)
my_circuit.defPar("R2", R2_value)
my_circuit.defPar("V_in", V_in_value)

print("\n" + "-"*60)
print("CIRCUIT PARAMETERS")
print("-"*60)
print(f"R1 = {R1_value} Ω")
print(f"R2 = {R2_value} Ω")
print(f"V_in = {V_in_value} V")

print("\n" + "-"*60)
print("SYMBOLIC ANALYSIS")
print("-"*60)

# Perform Laplace analysis
# Specify source=V1 and detector=V_out explicitly
result = doLaplace(my_circuit, source='V1', detector='V_out')

print("\nSymbolic transfer function H(s) = V_out/V_in:")
if isinstance(result.laplace, list):
    if len(result.laplace) > 0:
        print(result.laplace[0])
        transfer = result.laplace[0]
    else:
        print("Empty result")
        transfer = None
else:
    print(result.laplace)
    transfer = result.laplace

if transfer is not None:
    # Evaluate at s=0 for DC gain
    print("\nDC gain (at s=0):")
    dc_gain_symbolic = transfer.subs('s', 0) if hasattr(transfer, 'subs') else transfer
    print(dc_gain_symbolic)

    print("\n" + "-"*60)
    print("NUMERIC ANALYSIS")
    print("-"*60)

    # Perform numeric analysis with parameter values substituted
    result_numeric = doLaplace(my_circuit, source='V1', detector='V_out', numeric=True)

    print("\nNumeric transfer function:")
    if isinstance(result_numeric.laplace, list) and len(result_numeric.laplace) > 0:
        print(result_numeric.laplace[0])
        transfer_numeric = result_numeric.laplace[0]
    else:
        print(result_numeric.laplace)
        transfer_numeric = result_numeric.laplace

    # Calculate output voltage
    # Substitute s=0 and parameter values
    dc_gain_expr = transfer_numeric.subs('s', 0) if hasattr(transfer_numeric, 'subs') else transfer_numeric
    # Substitute R1 and R2 values
    dc_gain_with_params = dc_gain_expr.subs([('R1', R1_value), ('R2', R2_value)])
    # Evaluate to get numeric value
    dc_gain = float(dc_gain_with_params)
    v_out_calc = V_in_value * dc_gain

    print(f"\n*** Output voltage V_out = {V_in_value} V × {dc_gain:.4f} = {v_out_calc:.4f} V ***")

print("\n" + "-"*60)
print("VERIFICATION USING VOLTAGE DIVIDER FORMULA")
print("-"*60)

# Direct calculation using voltage divider formula
v_out_formula = V_in_value * R2_value / (R1_value + R2_value)
print(f"V_out = V_in × R2/(R1+R2)")
print(f"V_out = {V_in_value} × {R2_value}/({R1_value}+{R2_value})")
print(f"V_out = {v_out_formula:.4f} V")

# Show the calculation step by step
print("\n" + "-"*60)
print("STEP-BY-STEP CALCULATION")
print("-"*60)
print(f"1. Total resistance: R_total = R1 + R2 = {R1_value} + {R2_value} = {R1_value + R2_value} Ω")
print(f"2. Transfer ratio: H = R2 / R_total = {R2_value} / {R1_value + R2_value} = {R2_value/(R1_value + R2_value):.4f}")
print(f"3. Output voltage: V_out = V_in × H = {V_in_value} × {R2_value/(R1_value + R2_value):.4f} = {v_out_formula:.4f} V")

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60 + "\n")
