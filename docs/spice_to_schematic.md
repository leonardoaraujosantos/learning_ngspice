# SPICE to Schematic (scripts/spice_to_schematic.py)

This document describes what `scripts/spice_to_schematic.py` does, the algorithms used,
external tools it depends on, and current layout heuristics. It is meant as a technical
reference for future improvements.

## Summary

The script parses SPICE netlists and generates schematic PNGs. It prefers a LaTeX
`circuitikz` backend (via `pdflatex` and `pdftocairo`) and falls back to a simple
matplotlib "box diagram" if LaTeX rendering fails. It supports basic components,
subcircuit expansion, and multiple layout heuristics to make the generated diagrams
readable.

## Inputs and Outputs

Inputs:
- A single SPICE file, a directory containing SPICE files, or a glob.
- Supported file extensions: `.spice`, `.sp`, `.cir`, `.net`.

Outputs:
- `*_schematic.png` next to each SPICE file, or `-o` output path for single input.

## External Tools and Libraries

Required for circuitikz rendering:
- `pdflatex` (TeX Live). The script writes a temporary LaTeX file and compiles it.
- `pdftocairo` for PDF -> PNG conversion.

Fallback (if LaTeX fails):
- Python matplotlib (only uses standard patches and text).

Runtime dependencies:
- Standard Python libraries only: `argparse`, `glob`, `os`, `re`, `subprocess`, `tempfile`,
  `pathlib`, `collections`.

## High-level Flow

1. Parse SPICE file(s):
   - Read file, merge continuation lines (`+`), skip comments and `.control` blocks.
   - Extract components and subcircuits.
2. Expand subcircuits:
   - Flatten `.SUBCKT` instances into standard components with prefixed names.
3. Choose schematic backend:
   - If a "simple voltage fan" (one V source + resistors + GND), use a fixed hand layout.
   - Else use generic circuitikz layout.
   - If circuitikz fails, use matplotlib fallback.
4. Render PNG:
   - Create a temporary LaTeX file in a `ckt_*` folder.
   - Run `pdflatex` then `pdftocairo`.

## Parsing and Normalization

### Component Support

Parsed component types:
- `R`, `C`, `L`, `D`
- `V` (voltage source)
- `I` (current source)
- `Q` (BJT, NPN/PNP)
- `M` (MOSFET)
- `J` (JFET)
- `X` (subcircuit instance)

Voltage/current sources detect `DC` values if present (e.g. `V1 n1 0 DC 5`).

### Node Normalization

`normalize_node()`:
- Lowercases.
- Maps `0` or `gnd` to `0`.
- Replaces non-alphanumeric characters with `_`.
- Prefixes numeric nodes with `n` (except `0`).

### Subcircuit Expansion

`.SUBCKT` definitions are parsed into `SubcircuitDefinition` (pins + components).
Instances `X...` are expanded by:
- Mapping instance pins to subckt pins.
- Prefixing internal nodes with the instance name.
- Recursively expanding nested subcircuits (depth limited to 8).

## Schematic Generation (Circuitikz)

### 1) Simple Voltage Fan Layout

Detected by `_is_simple_voltage_fan()`:
- Exactly one V source.
- All components are `V` or `R`.
- Ground node present.

Layout:
- A central hub node with a V source down to ground.
- Each resistor chain becomes a "branch" radiating right, up, left, down.
- Each branch is drawn as a series of resistors and ends at ground.

### 2) Generic Layout

#### Graph Construction

Builds an adjacency graph for non-ground nodes:
- Bipoles connect their two nodes.
- Transistors (`Q`, `M`, `J`) connect pin 0 to other pins as edges.

#### BFS Levels and Ordering

Per connected component group:
- Choose a reference node (prefers node tied to a V source to ground).
- BFS assigns node "levels" (x-axis).
- Order nodes within levels using a two-pass barycenter heuristic to reduce crossings.

#### Transistor-centric Layout (Single Transistor Groups)

If a group has exactly one transistor:
- Pin nodes are fixed to a small local frame:
  - BJT: base left, collector up, emitter down.
  - MOSFET/JFET: gate left, drain up, source down.
- The rest of the nodes are laid out around these fixed points.

#### Group Placement and Column Layout

Connected components are laid out as separate groups:
- Each group has padding and framing margins.
- For 3+ groups, groups are placed into 2-3 columns to avoid overly tall images.

#### Local Rails (Per Group)

Each group gets its own local rails:
- VCC bus at the top if a V source connects that group to ground.
- GND bus at the bottom if ground-connected components exist in that group.
- Nodes tied to V sources connect to the local VCC rail.

#### Shunt Bus for Parallel Ground Components

For nodes with multiple components to ground:
- A short horizontal bus is created under the node.
- Each shunt part connects to a dedicated bus tap.
- The bus drop is routed from the nearest bus edge to avoid crossing.

#### Labels

Component labels include both name and value:
- Example: name above, value below (`l` and `l_`).
- If no value exists, only the name is shown.

#### Routing and Wire Avoidance

Routing is orthogonal:
- Nodes snap to a small grid (`route_grid`).
- For non-aligned bipoles, choose the best bend by:
  - Counting node hits along each candidate path.
  - Counting crossings with bus lines.
  - Choosing the lower "hit" score (tie-breaker uses degree).
- If a bend lands on an existing node, offset it by one grid step.
- Transistor pins are connected with orthogonal paths using `|-` or `-|`.

## Matplotlib Fallback

If circuitikz rendering fails:
- A grid of rounded boxes is drawn with matplotlib.
- Each box shows component name and value/model.
- Connection labels show the two node names.

This is a last-resort visualization only.

## CLI and Flags

Usage:
```
python scripts/spice_to_schematic.py <input>
python scripts/spice_to_schematic.py <input> -o output.png
python scripts/spice_to_schematic.py <input> --netlist
```

Flags:
- `-o/--output`: output file for a single input.
- `-v/--verbose`: dump parsed components.
- `--netlist`: print an internal debug netlist representation.

## Temp Files

Each render creates a temporary folder: `ckt_<random>` in the workspace.
It contains:
- `circuit.tex`
- `circuit.pdf`
- `circuit.log`

These are left in place for debugging.

## Known Limitations

- The layout is heuristic. Complex analog designs can still have crossings.
- The simple fan layout only applies to a limited V+R topology.
- BJT/MOSFET/JFET symbols use basic anchoring; pin routing is naive.
- The script does not (yet) parse advanced SPICE constructs like `.include` or
  behavioral sources.

## Suggested Next Steps

Potential improvements:
- Explicit tank/bias grouping for oscillators (Colpitts, Hartley, Pierce).
- Smarter component clustering based on net roles (bias, load, coupling).
- Avoiding crossings via segment intersection checks (wire vs wire).
- Adaptive grid size based on group complexity.

