# SLiCAP Examples

This directory contains examples demonstrating how to use SLiCAP (Symbolic Linear Circuit Analysis Program) for circuit analysis.

## Examples Included

1. **Voltage Divider** - DC analysis of a resistive voltage divider
2. **RC Low Pass Filter** - Frequency response analysis of a first-order filter

---

# Example 1: Voltage Divider

This example demonstrates DC analysis of a simple voltage divider circuit.

## Circuit Description

The voltage divider consists of:
- **V1**: 10V DC voltage source
- **R1**: 1kΩ resistor (top resistor)
- **R2**: 2kΩ resistor (bottom resistor)
- **Output**: Voltage measured at node 'out' (between R1 and R2)

## Circuit Schematic

```
      V_in (10V)
         |
        R1 (1kΩ)
         |
    out o--------> V_out
         |
        R2 (2kΩ)
         |
        GND
```

## Expected Output

Using the voltage divider formula:

```
V_out = V_in × R2/(R1 + R2)
V_out = 10V × 2000Ω/(1000Ω + 2000Ω)
V_out = 10V × 0.6667
V_out = 6.667V
```

## Files

- `cir/voltage_divider.cir` - SPICE netlist for the voltage divider circuit
- `voltage_divider.py` - Python script that performs SLiCAP analysis

## How to Run

1. Make sure SLiCAP is installed:
   ```bash
   pip install SLiCAP
   ```

2. Run the analysis script:
   ```bash
   python3 voltage_divider.py
   ```

## What the Script Does

The script performs the following steps:

1. **Initialize Project**: Creates a SLiCAP project named "Voltage Divider Example"

2. **Load Circuit**: Reads the netlist from `cir/voltage_divider.cir`

3. **Define Parameters**: Sets the values for R1, R2, and V_in

4. **Symbolic Analysis**:
   - Computes the symbolic transfer function H(s) = V_out/V_in
   - Shows the result as R2/(R1 + R2)

5. **Numeric Analysis**:
   - Substitutes numerical values into the symbolic expression
   - Calculates the actual output voltage

6. **Verification**:
   - Compares the result with the voltage divider formula
   - Shows step-by-step calculation

## Expected Output

When you run the script, you should see:

```
============================================================
VOLTAGE DIVIDER CIRCUIT ANALYSIS
============================================================

Circuit title: Voltage Divider Circuit
Circuit nodes: ['0', 'in', 'out']
Circuit elements: ['V1', 'R1', 'R2']

------------------------------------------------------------
CIRCUIT PARAMETERS
------------------------------------------------------------
R1 = 1000 Ω
R2 = 2000 Ω
V_in = 10 V

------------------------------------------------------------
SYMBOLIC ANALYSIS
------------------------------------------------------------

Symbolic transfer function H(s) = V_out/V_in:
R2/(R1 + R2)

DC gain (at s=0):
R2/(R1 + R2)

------------------------------------------------------------
NUMERIC ANALYSIS
------------------------------------------------------------

Numeric transfer function:
R2/(R1 + R2)

*** Output voltage V_out = 10 V × 0.6667 = 6.6667 V ***

------------------------------------------------------------
VERIFICATION USING VOLTAGE DIVIDER FORMULA
------------------------------------------------------------
V_out = V_in × R2/(R1+R2)
V_out = 10 × 2000/(1000+2000)
V_out = 6.6667 V

------------------------------------------------------------
STEP-BY-STEP CALCULATION
------------------------------------------------------------
1. Total resistance: R_total = R1 + R2 = 1000 + 2000 = 3000 Ω
2. Transfer ratio: H = R2 / R_total = 2000 / 3000 = 0.6667
3. Output voltage: V_out = V_in × H = 10 × 0.6667 = 6.6667 V

============================================================
ANALYSIS COMPLETE
============================================================
```

## Key SLiCAP Functions Used

- `initProject(name)` - Initialize a SLiCAP project
- `makeCircuit(filename)` - Create a circuit object from a netlist
- `circuit.defPar(param, value)` - Define a circuit parameter value
- `doLaplace(circuit, source, detector)` - Perform Laplace domain analysis
- Result attributes:
  - `result.laplace` - The transfer function H(s)
  - `result.numer` - Numerator of the transfer function
  - `result.denom` - Denominator of the transfer function

## Learning Points

1. **SLiCAP Directory Structure**: Circuit files must be in a `cir/` subdirectory
2. **Node Naming**: Detector names are automatically created as 'V_' + node_name
3. **Source Naming**: Voltage sources are referenced by their element name (e.g., 'V1')
4. **Symbolic vs Numeric**: SLiCAP can work with both symbolic expressions and numerical values
5. **Parameter Substitution**: Use `.subs()` to substitute values into symbolic expressions

---

# Example 2: RC Low Pass Filter

This example demonstrates frequency response analysis of a first-order RC low pass filter.

## Circuit Description

The RC low pass filter consists of:
- **V1**: 1V AC voltage source
- **R**: 1kΩ resistor (series)
- **C**: 100nF capacitor (to ground)
- **Output**: Voltage measured across the capacitor at node 'out'

## Circuit Schematic

```
           V_in (1V AC)
              |
             R (1kΩ)
              |
         out o--------> V_out
              |
             C (100nF)
              |
             GND
```

## Transfer Function

The transfer function of a first-order RC low pass filter is:

```
H(s) = 1/(1 + sRC)
     = 1/(1 + s/ωc)
     = ωc/(s + ωc)
```

where:
- ωc = 1/(RC) is the cutoff angular frequency
- fc = ωc/(2π) = 1/(2πRC) is the cutoff frequency in Hz

## Expected Results

For R = 1kΩ and C = 100nF:

```
fc = 1/(2π × 1000 × 100×10⁻⁹)
fc = 1591.55 Hz
ωc = 10000 rad/s
```

**Filter Characteristics:**
- DC gain: 0 dB (magnitude = 1.0)
- Cutoff frequency: fc = 1591.55 Hz
- Attenuation at fc: -3 dB (magnitude = 0.707)
- Phase shift at fc: -45°
- Roll-off rate: -20 dB/decade
- Pole: p = -1/(RC) = -10000 rad/s
- Time constant: τ = RC = 100 μs

## Files

- `cir/rc_lowpass.cir` - SPICE netlist for the RC filter circuit
- `rc_lowpass.py` - Comprehensive analysis script with frequency response
- `rc_lowpass_plot.py` - Script to generate Bode plots

## How to Run

1. **Basic analysis** (frequency response calculations):
   ```bash
   python3 rc_lowpass.py
   ```

2. **Generate Bode plots**:
   ```bash
   python3 rc_lowpass_plot.py
   ```

## What the Scripts Do

### rc_lowpass.py

1. **Initialize Project** and load the circuit

2. **Define Parameters**:
   - R = 1kΩ
   - C = 100nF
   - Calculate fc = 1591.55 Hz

3. **Symbolic Analysis**:
   - Derives transfer function: H(s) = 1/(C*R*s + 1)
   - Shows numerator and denominator

4. **Frequency Response Analysis**:
   - Evaluates |H(jω)| and ∠H(jω) at key frequencies
   - Verifies -3dB and -45° at cutoff frequency

5. **Pole-Zero Analysis**:
   - Finds pole at p = -1/(RC) = -10000 rad/s
   - Confirms no finite zeros

6. **Filter Characterization**:
   - DC gain, time constant, roll-off rate

### rc_lowpass_plot.py

Generates Bode plots (magnitude and phase vs frequency) for visualization.

## Expected Output

```
======================================================================
RC LOW PASS FILTER ANALYSIS
======================================================================

Circuit title: RC Low Pass Filter
Circuit nodes: ['0', 'in', 'out']
Circuit elements: ['V1', 'R1', 'C1']

----------------------------------------------------------------------
CIRCUIT PARAMETERS
----------------------------------------------------------------------
R = 1000 Ω = 1.0 kΩ
C = 1e-07 F = 100.0 nF
V_in = 1 V

Calculated cutoff frequency fc = 1/(2πRC)
fc = 1/(2π × 1000 × 1e-07)
fc = 1591.55 Hz
ωc = 2πfc = 10000.00 rad/s

----------------------------------------------------------------------
SYMBOLIC ANALYSIS
----------------------------------------------------------------------

Symbolic transfer function H(s) = V_out/V_in:
1/(C*R*s + 1)

----------------------------------------------------------------------
FREQUENCY RESPONSE ANALYSIS
----------------------------------------------------------------------

Magnitude and phase at key frequencies:
Frequency [Hz]  |H(jω)|      |H(jω)| [dB]    ∠H(jω) [°]
----------------------------------------------------------------------
10.00           1.0000       -0.00           -0.36
100.00          0.9980       -0.02           -3.60
1591.55 (fc)    0.7071       -3.01           -45.00
1000.00         0.8467       -1.45           -32.14
10000.00        0.1572       -16.07          -80.96

At cutoff frequency fc = 1591.55 Hz:
  Expected |H(jωc)| = 1/√2 ≈ 0.707 (-3 dB)
  Expected ∠H(jωc) = -45°

----------------------------------------------------------------------
POLE-ZERO ANALYSIS
----------------------------------------------------------------------

Poles:
  p1 = -1/(C*R) = -10000.00 rad/s

Zeros:
  None (no zeros in finite s-plane)

----------------------------------------------------------------------
FILTER CHARACTERISTICS SUMMARY
----------------------------------------------------------------------
Filter type:        First-order RC low pass filter
Cutoff frequency:   fc = 1591.55 Hz
Time constant:      τ = RC = 0.000100 s = 0.100 ms
Attenuation at fc:  -3 dB
Phase shift at fc:  -45°
Roll-off:           -20 dB/decade
DC gain:            0 dB (1.0)
```

## Key SLiCAP Functions Used

- `doLaplace(circuit, source, detector)` - Frequency domain transfer function
- `doPZ(circuit, source, detector)` - Pole-zero analysis
- `plotSweep(name, result, plot_type)` - Generate Bode plots
- Frequency configuration via `ini.frequency`, `ini.freqStart`, `ini.freqStop`

## Learning Points

1. **Frequency Domain Analysis**: How to analyze AC behavior of circuits
2. **Complex Frequency Variable**: Using s = jω for frequency response
3. **Bode Plots**: Visualizing magnitude and phase vs frequency
4. **Pole-Zero Analysis**: Understanding system stability and frequency response
5. **Filter Design**: Calculating cutoff frequency from component values
6. **3dB Point**: At cutoff frequency, output is 70.7% of input (1/√2)

---

## General Information

## References

- [SLiCAP Official Documentation](https://www.slicap.org/)
- [SLiCAP User Guide](https://www.slicap.org/userguide/SLiCAPuserguide)
- [RC Filter Wikipedia](https://en.wikipedia.org/wiki/RC_circuit)
