# Complete Tutorial: Verilog-A with ngspice

## Table of Contents
1. [Introduction](#introduction)
2. [What is Verilog-A?](#what-is-verilog-a)
3. [Prerequisites](#prerequisites)
4. [Basic Verilog-A Syntax](#basic-verilog-a-syntax)
5. [Creating Your First Model](#creating-your-first-model)
6. [Compiling with OpenVAF](#compiling-with-openvaf)
7. [Using OSDI Models in ngspice](#using-osdi-models-in-ngspice)
8. [Complete Examples](#complete-examples)
9. [Advanced Topics](#advanced-topics)
10. [Common Pitfalls](#common-pitfalls)
11. [Troubleshooting](#troubleshooting)

---

## Introduction

This tutorial teaches you how to create custom analog circuit models using Verilog-A and simulate them in ngspice using the OSDI (Open Source Device Interface) framework.

**What you'll learn:**
- Write Verilog-A models for custom components
- Compile models using OpenVAF
- Integrate compiled models into ngspice circuits
- Debug and optimize your models

---

## What is Verilog-A?

**Verilog-A** is a hardware description language (HDL) for analog circuits. It allows you to:
- Model custom semiconductor devices
- Create behavioral models of complex components
- Implement mathematical equations as circuit elements
- Prototype new device physics

**Key advantages:**
- Industry-standard language
- Portable across simulators (with OSDI)
- More flexible than SPICE subcircuits
- Can include noise, temperature effects, etc.

---

## Prerequisites

### Required Software

1. **ngspice** (version 42+) compiled with OSDI support
2. **OpenVAF** (latest version recommended)
3. **Text editor** (vim, nano, VS Code, etc.)

### Required Knowledge

- Basic circuit theory (Ohm's law, KVL, KCL)
- Basic programming concepts
- Familiarity with SPICE netlists (helpful but not required)

---

## Basic Verilog-A Syntax

### Module Structure

Every Verilog-A model is defined in a **module**:

```verilog
`include "disciplines.vams"

module module_name(terminal1, terminal2, ...);
    // Port declarations
    inout terminal1, terminal2;
    electrical terminal1, terminal2;

    // Parameters
    parameter real param_name = default_value;

    // Variables (if needed)
    real variable_name;

    // Analog behavior
    analog begin
        // Equations go here
    end
endmodule
```

### Key Concepts

1. **Disciplines**: Define what type of signal (electrical, thermal, etc.)
   ```verilog
   `include "disciplines.vams"  // Standard disciplines
   electrical node1, node2;     // Declares electrical nodes
   ```

2. **Parameters**: User-configurable values
   ```verilog
   parameter real resistance = 1k from (0:inf);
   parameter integer num_turns = 10 from [1:inf);
   ```

3. **Analog Block**: Where the physics/math happens
   ```verilog
   analog begin
       I(p,n) <+ V(p,n) / resistance;  // Ohm's law
   end
   ```

4. **Contribution Operator** `<+`: Adds to node equations
   - `V(p,n)` - voltage across nodes p and n
   - `I(p,n)` - current through branch from p to n

---

## Creating Your First Model

### Example 1: Simple Resistor

Let's create a basic resistor model:

```verilog
`include "disciplines.vams"

module simple_resistor(p, n);
    // Declare terminals as electrical
    inout p, n;
    electrical p, n;

    // Parameter: resistance in Ohms
    parameter real r = 1k from (0:inf);

    // Analog behavior: Ohm's law
    analog begin
        I(p, n) <+ V(p, n) / r;
    end
endmodule
```

**Save this as:** `simple_resistor.va`

**What it does:**
- Defines a two-terminal component (p and n)
- Has one parameter: resistance `r` (default 1kΩ)
- Implements Ohm's law: I = V/R
- The `from (0:inf)` ensures resistance is positive

### Example 2: Voltage-Controlled Voltage Source (VCVS)

```verilog
`include "disciplines.vams"

module vcvs(inp, inn, outp, outn);
    // Input and output terminals
    inout inp, inn, outp, outn;
    electrical inp, inn, outp, outn;

    // Voltage gain parameter
    parameter real gain = 1.0;

    analog begin
        // Output voltage = gain × input voltage
        V(outp, outn) <+ gain * V(inp, inn);
    end
endmodule
```

**Save this as:** `vcvs.va`

### Example 3: Simple Diode (Shockley Equation)

```verilog
`include "disciplines.vams"

module simple_diode(anode, cathode);
    inout anode, cathode;
    electrical anode, cathode;

    // Parameters
    parameter real is = 1e-14 from (0:inf);      // Saturation current (A)
    parameter real n = 1.0 from (0:inf);         // Ideality factor
    parameter real temp = 300 from (0:inf);      // Temperature (K)

    // Physical constants
    real vt;        // Thermal voltage
    real q, k;      // Charge, Boltzmann constant

    analog begin
        // Constants
        q = 1.602176634e-19;    // Elementary charge (C)
        k = 1.380649e-23;        // Boltzmann constant (J/K)

        // Thermal voltage: Vt = kT/q
        vt = k * temp / q;

        // Shockley diode equation: I = Is * (exp(V/(n*Vt)) - 1)
        I(anode, cathode) <+ is * (exp(V(anode, cathode) / (n * vt)) - 1);
    end
endmodule
```

**Save this as:** `simple_diode.va`

---

## Compiling with OpenVAF

### Installation

Install OpenVAF (if not already installed):

```bash
# Download latest release from:
# https://github.com/pascalkuthe/OpenVAF/releases

# Make it executable
chmod +x openvaf

# Move to system path
sudo mv openvaf /usr/local/bin/
```

### Compilation

Compile a Verilog-A file to OSDI format:

```bash
openvaf model_name.va
```

**Example:**
```bash
openvaf simple_resistor.va
```

**Output:**
- Creates `simple_resistor.osdi` (binary shared library)
- This is the file ngspice will load

### Compilation Options

```bash
# Basic compilation
openvaf model.va

# Specify output name
openvaf model.va -o custom_name.osdi

# Enable optimizations
openvaf model.va -O3

# Verbose output for debugging
openvaf model.va -v
```

### Verifying Compilation

```bash
# Check if .osdi file was created
ls -lh *.osdi

# Check file type
file simple_resistor.osdi
# Should show: ELF 64-bit LSB shared object
```

---

## Using OSDI Models in ngspice

### Circuit Syntax

The correct pattern for using OSDI models:

```spice
* Title line

* Voltage/current sources
V1 node1 node2 dc value

* Define model OUTSIDE .control block
* Syntax: .model <instance_name> <module_name> [parameters]
.model inst_name module_name param1=value1 param2=value2

* Use device with 'N' prefix (OSDI device)
Nxx node1 node2 inst_name

.control
    * Load OSDI library INSIDE .control block
    pre_osdi model_name.osdi

    * Run simulation
    op
    dc ...
    ac ...
    tran ...

    * Output
    print V(node1)
    plot I(source)
.endc

.end
```

### Critical Rules

1. **Module name** in `.model` must match Verilog-A module name
2. **`.model`** statement goes BEFORE `.control` block
3. **`pre_osdi`** command goes INSIDE `.control` block
4. **OSDI devices** use **`N`** prefix (not R, C, D, etc.)
5. **Path to .osdi** can be relative or absolute

---

## Complete Examples

### Example 1: Testing the Simple Resistor

**File:** `test_resistor.cir`

```spice
* Test simple resistor OSDI model

* Voltage source: 10V
V1 in 0 dc 10

* Define resistor model (r=500 ohms)
.model myres simple_resistor r=500

* Use the resistor
N1 in out myres

* Load to ground (built-in resistor)
R1 out 0 500

.control
    * Load OSDI model
    pre_osdi simple_resistor.osdi

    * Operating point analysis
    op

    * Print results
    echo "Test: Two 500-ohm resistors in series with 10V source"
    print V(in) V(out) I(V1)
    echo "Expected: V(in)=10V, V(out)=5V, I(V1)=-10mA"
.endc

.end
```

**Run it:**
```bash
ngspice -b test_resistor.cir
```

**Expected output:**
- V(in) = 10V
- V(out) = 5V (voltage divider)
- I(V1) = -10mA (10V / 1000Ω total)

### Example 2: Testing the Diode

**File:** `test_diode.cir`

```spice
* Test simple diode OSDI model

* Voltage source for DC sweep
V1 anode 0 dc 0

* Define diode model with custom parameters
.model d1 simple_diode is=1e-14 n=1.0 temp=300

* Diode from anode to ground
N1 anode 0 d1

.control
    * Load OSDI model
    pre_osdi simple_diode.osdi

    * DC sweep from -1V to +1V
    dc V1 -1 1 0.01

    * Save I-V data
    wrdata diode_iv.dat V(anode) I(V1)

    echo "I-V data saved to diode_iv.dat"
    echo "To plot: gnuplot> plot 'diode_iv.dat' using 1:2"
.endc

.end
```

**Run it:**
```bash
ngspice -b test_diode.cir
```

**Plot with gnuplot:**
```bash
gnuplot
gnuplot> plot 'diode_iv.dat' using 1:2 with lines title 'Diode I-V'
```

### Example 3: RC Low-Pass Filter with Custom Components

**Verilog-A files:** Use `simple_resistor.va` and create `simple_capacitor.va`:

```verilog
`include "disciplines.vams"

module simple_capacitor(p, n);
    inout p, n;
    electrical p, n;

    parameter real c = 1e-9 from (0:inf);  // Capacitance in Farads

    analog begin
        I(p, n) <+ c * ddt(V(p, n));  // I = C × dV/dt
    end
endmodule
```

**Compile both:**
```bash
openvaf simple_resistor.va
openvaf simple_capacitor.va
```

**Circuit:** `test_rc_filter.cir`

```spice
* RC Low-Pass Filter with OSDI components

* AC voltage source: 1V amplitude
V1 in 0 dc 0 ac 1

* Define models
.model myres simple_resistor r=1k
.model mycap simple_capacitor c=1e-6

* RC circuit
N1 in out myres    * Resistor: in -> out
N2 out 0 mycap     * Capacitor: out -> ground

.control
    * Load both OSDI models
    pre_osdi simple_resistor.osdi
    pre_osdi simple_capacitor.osdi

    * AC analysis: 1Hz to 100kHz
    ac dec 50 1 100k

    * Save frequency response
    wrdata rc_filter.dat frequency vdb(out) vp(out)

    echo "Frequency response saved to rc_filter.dat"
    echo "Cutoff frequency = 1/(2*pi*R*C) = 159 Hz"
.endc

.end
```

### Example 4: Voltage-Controlled Resistor

**Create:** `vcr.va`

```verilog
`include "disciplines.vams"

module vcr(p, n, ctrl);
    // Resistor terminals and control voltage input
    inout p, n, ctrl;
    electrical p, n, ctrl;

    // Parameters
    parameter real r0 = 1k from (0:inf);      // Base resistance
    parameter real alpha = 0.1 from (0:1);    // Control sensitivity

    real resistance;

    analog begin
        // Resistance varies with control voltage
        // R = R0 * (1 + alpha * Vctrl)
        resistance = r0 * (1 + alpha * V(ctrl));

        // Ensure resistance stays positive
        if (resistance < 1.0)
            resistance = 1.0;

        // Apply Ohm's law
        I(p, n) <+ V(p, n) / resistance;
    end
endmodule
```

**Test circuit:** `test_vcr.cir`

```spice
* Voltage-Controlled Resistor Test

* Main circuit voltage
V1 in 0 dc 5

* Control voltage (sweep this)
Vctrl ctrl 0 dc 0

* VCR model
.model myvrc vcr r0=1k alpha=0.1

* VCR: in->out, controlled by ctrl
N1 in out ctrl myvrc

* Current measurement
Vmeas out 0 dc 0

.control
    pre_osdi vcr.osdi

    * Sweep control voltage from 0 to 10V
    dc Vctrl 0 10 0.1

    * Calculate effective resistance
    let reff = V(in) / (-I(Vmeas))

    * Plot resistance vs control voltage
    wrdata vcr_test.dat V(ctrl) reff

    echo "Effective resistance vs control voltage saved"
.endc

.end
```

---

## Advanced Topics

### 1. Temperature-Dependent Models

```verilog
`include "disciplines.vams"

module temp_resistor(p, n);
    inout p, n;
    electrical p, n;

    parameter real r = 1k from (0:inf);
    parameter real tc1 = 0.0;     // Linear temp coefficient (1/°C)
    parameter real tc2 = 0.0;     // Quadratic temp coefficient (1/°C²)
    parameter real tnom = 27.0;   // Nominal temperature (°C)

    real temp_celsius, delta_t, r_temp;

    analog begin
        // Get simulation temperature
        temp_celsius = $temperature - 273.15;
        delta_t = temp_celsius - tnom;

        // Temperature-dependent resistance
        r_temp = r * (1.0 + tc1*delta_t + tc2*delta_t*delta_t);

        I(p, n) <+ V(p, n) / r_temp;
    end
endmodule
```

### 2. Noise Modeling

```verilog
`include "disciplines.vams"

module noisy_resistor(p, n);
    inout p, n;
    electrical p, n;

    parameter real r = 1k from (0:inf);
    parameter integer has_noise = 1;  // Enable/disable noise

    analog begin
        // DC current (Ohm's law)
        I(p, n) <+ V(p, n) / r;

        // Thermal noise (Johnson-Nyquist)
        if (has_noise) begin
            // PSD = 4*k*T/R
            I(p, n) <+ white_noise(4 * 1.38064852e-23 * $temperature / r, "thermal");
        end
    end
endmodule
```

### 3. Using `ddt()` for Dynamic Elements

```verilog
// Inductor: V = L × dI/dt
analog begin
    V(p, n) <+ inductance * ddt(I(p, n));
end

// Capacitor: I = C × dV/dt
analog begin
    I(p, n) <+ capacitance * ddt(V(p, n));
end
```

### 4. Conditional Behavior

```verilog
analog begin
    if (V(p, n) > 0) begin
        // Forward bias behavior
        I(p, n) <+ is * (exp(V(p, n) / vt) - 1);
    end else begin
        // Reverse bias behavior
        I(p, n) <+ -is;
    end
end
```

### 5. Using System Functions

```verilog
$temperature    // Simulation temperature (Kelvin)
$vt             // Thermal voltage kT/q
$abstime        // Absolute simulation time
$random         // Random number generator
```

### 6. Limiting Functions (for convergence)

```verilog
// Limit exponential growth
I(p,n) <+ is * limexp(V(p,n) / vt);

// Smooth transitions
V(out) <+ transition(target_value, delay, rise_time, fall_time);
```

---

## Common Pitfalls

### 1. Variable Name Conflicts

**❌ WRONG:**
```verilog
real V;  // Variable named 'V'
analog begin
    V = V(p, n);  // ERROR: 'V' conflicts with V() function
end
```

**✓ CORRECT:**
```verilog
real voltage;
analog begin
    voltage = V(p, n);  // Use different name
end
```

### 2. Forgetting Disciplines

**❌ WRONG:**
```verilog
module bad_resistor(p, n);
    inout p, n;
    // Missing: electrical p, n;
```

**✓ CORRECT:**
```verilog
module good_resistor(p, n);
    inout p, n;
    electrical p, n;  // Declare discipline
```

### 3. Wrong Contribution Operator

**❌ WRONG:**
```verilog
I(p, n) = V(p, n) / r;  // Assignment operator
```

**✓ CORRECT:**
```verilog
I(p, n) <+ V(p, n) / r;  // Contribution operator
```

### 4. Missing `from` Ranges

**⚠ WARNING (may cause issues):**
```verilog
parameter real r = 1k;  // No range checking
```

**✓ BETTER:**
```verilog
parameter real r = 1k from (0:inf);  // Prevents negative values
```

### 5. Division by Zero

**❌ RISKY:**
```verilog
I(p, n) <+ V(p, n) / resistance;  // What if resistance = 0?
```

**✓ SAFER:**
```verilog
if (resistance < 1e-12)
    resistance = 1e-12;
I(p, n) <+ V(p, n) / resistance;
```

---

## Troubleshooting

### OpenVAF Compilation Errors

**Error: "Segmentation fault"**
- Update OpenVAF to latest version
- Check Verilog-A syntax
- Simplify model to isolate issue

**Error: "undefined reference to V"**
- Missing `disciplines.vams` include
- Check that `V()` function is used correctly

### ngspice Runtime Errors

**Error: "model name is not found"**

**Solution:**
1. Check `.model` name matches module name in `.va` file
2. Ensure `pre_osdi` is INSIDE `.control` block
3. Verify `.osdi` file exists in correct path

**Error: "Unable to find definition of model"**

**Solution:**
- Move `.model` statement BEFORE `.control` block
- Load `.osdi` file with `pre_osdi` before running simulation

**Error: "Device N1: no such model"**

**Solution:**
- Ensure device uses `N` prefix (OSDI devices)
- Check model name in device line matches `.model` statement

### Convergence Issues

**Symptoms:**
- "Timestep too small"
- "singular matrix"
- Simulation hangs

**Solutions:**

1. **Add limiting functions:**
   ```verilog
   I(p,n) <+ is * limexp(V(p,n) / vt);  // Instead of exp()
   ```

2. **Use better initial conditions:**
   ```spice
   .ic V(node)=value
   ```

3. **Adjust solver options:**
   ```spice
   .options reltol=1e-4 abstol=1e-10
   ```

4. **Add small conductance:**
   ```verilog
   I(p,n) <+ 1e-12 * V(p,n);  // Tiny conductance for stability
   ```

---

## Best Practices

1. **Always include parameter ranges:**
   ```verilog
   parameter real r = 1k from (0:inf);
   ```

2. **Use descriptive names:**
   ```verilog
   module mosfet_nch(drain, gate, source, bulk);  // Clear
   module m1(d, g, s, b);                          // Unclear
   ```

3. **Comment your code:**
   ```verilog
   // Shockley diode equation: I = Is(exp(V/Vt) - 1)
   I(a, c) <+ is * (limexp(V(a,c) / vt) - 1);
   ```

4. **Test incrementally:**
   - Start with DC behavior
   - Add AC behavior
   - Add noise last
   - Test each feature separately

5. **Validate against known models:**
   - Compare with built-in SPICE models
   - Check extreme cases (very large/small values)
   - Verify temperature dependence

---

## Resources

### Documentation
- [Verilog-A Language Reference Manual](https://www.verilog-ams.com/)
- [OpenVAF Documentation](https://openvaf.semimod.de/)
- [ngspice Manual](http://ngspice.sourceforge.net/docs/ngspice-manual.pdf)

### Example Models
- ngspice OSDI examples: `ngspice-source/examples/osdi/`
- OpenVAF test models: OpenVAF repository
- Industry models: Check semiconductor manufacturer websites

### Community
- ngspice mailing list
- EDA Stack Exchange
- GitHub: OpenVAF issues

---

## Quick Reference Card

### Verilog-A Basics
```verilog
`include "disciplines.vams"
module name(p, n);
    inout p, n;
    electrical p, n;
    parameter real param = value from (min:max);
    analog begin
        I(p,n) <+ expression;
        V(p,n) <+ expression;
    end
endmodule
```

### Compilation
```bash
openvaf model.va          # Creates model.osdi
```

### ngspice Circuit
```spice
.model inst module param=value
Nxx n1 n2 inst
.control
    pre_osdi model.osdi
    op / dc / ac / tran
.endc
.end
```

### Common Equations
```verilog
I(p,n) <+ V(p,n) / r;                    // Resistor
I(p,n) <+ c * ddt(V(p,n));              // Capacitor
V(p,n) <+ l * ddt(I(p,n));              // Inductor
I(p,n) <+ is * (limexp(V(p,n)/vt) - 1); // Diode
```

---

## Conclusion

You now have a complete foundation for creating and using Verilog-A models in ngspice! Start with simple resistive models, then gradually add complexity as you become comfortable with the syntax and workflow.

**Next steps:**
1. Create a simple resistor model and test it
2. Implement a diode and verify the I-V curve
3. Try a dynamic element (capacitor or inductor)
4. Explore temperature and noise modeling

Happy modeling!
