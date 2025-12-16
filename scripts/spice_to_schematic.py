#!/usr/bin/env python3
"""
spice_to_schematic.py - Converte arquivos SPICE em esquematicos PNG usando lcapy

Uso:
    python scripts/spice_to_schematic.py circuito.spice
    python scripts/spice_to_schematic.py circuito.spice -o saida.png
    python scripts/spice_to_schematic.py circuits/  # processa todos

Requer:
    pip install lcapy

Componentes suportados:
    R  - Resistor
    C  - Capacitor
    L  - Indutor
    D  - Diodo
    Q  - Transistor BJT (NPN/PNP)
    M  - MOSFET (NMOS/PMOS)
    J  - JFET (NJF/PJF)
    V  - Fonte de tensao
    I  - Fonte de corrente
"""

import sys
import os
import re
import glob
import argparse
from collections import defaultdict

try:
    from lcapy import Circuit
    LCAPY_AVAILABLE = True
except ImportError:
    LCAPY_AVAILABLE = False
    print("Aviso: lcapy nao encontrado. Instale com: pip install lcapy")
    print("       Tambem precisa de LaTeX com circuitikz instalado.")


# =============================================================================
# PARSER DE NETLIST SPICE
# =============================================================================

class SpiceComponent:
    """Representa um componente do circuito SPICE."""

    def __init__(self, name, comp_type, nodes, value=None, model=None):
        self.name = name
        self.comp_type = comp_type
        self.nodes = nodes
        self.value = value
        self.model = model

    def __repr__(self):
        return f"{self.comp_type}:{self.name}({self.nodes}) = {self.value or self.model}"


def parse_value(value_str):
    """Converte string de valor SPICE para formato legivel."""
    if not value_str:
        return ""
    value_str = value_str.strip()
    if value_str.startswith('{') and value_str.endswith('}'):
        return value_str[1:-1]
    return value_str


def parse_spice_file(filepath):
    """Parseia arquivo SPICE e retorna lista de componentes."""
    components = []
    title = ""
    in_subckt = False
    in_control = False

    with open(filepath, 'r') as f:
        lines = f.readlines()

    if not lines:
        return components, title

    title = lines[0].strip()
    if title.startswith('*'):
        title = title[1:].strip()

    # Juntar linhas continuadas (+)
    joined_lines = []
    current_line = ""

    for line in lines[1:]:
        line = line.rstrip()
        if line.startswith('+'):
            current_line += ' ' + line[1:].strip()
        else:
            if current_line:
                joined_lines.append(current_line)
            current_line = line
    if current_line:
        joined_lines.append(current_line)

    for line in joined_lines:
        line = line.strip()

        if not line or line.startswith('*'):
            continue

        if ';' in line:
            line = line[:line.index(';')].strip()
        if not line:
            continue

        line_upper = line.upper()

        if line_upper.startswith('.SUBCKT'):
            in_subckt = True
            continue
        if line_upper.startswith('.ENDS'):
            in_subckt = False
            continue
        if line_upper.startswith('.CONTROL'):
            in_control = True
            continue
        if line_upper.startswith('.ENDC'):
            in_control = False
            continue

        if line.startswith('.') or in_subckt or in_control:
            continue

        parts = line.split()
        if not parts:
            continue

        name = parts[0].upper()
        comp_type = name[0]

        try:
            if comp_type in ['R', 'C', 'L']:
                nodes = [parts[1], parts[2]]
                value = parse_value(parts[3]) if len(parts) > 3 else ""
                components.append(SpiceComponent(name, comp_type, nodes, value))

            elif comp_type == 'D':
                nodes = [parts[1], parts[2]]
                model = parts[3] if len(parts) > 3 else ""
                components.append(SpiceComponent(name, 'D', nodes, model=model))

            elif comp_type == 'Q':
                if len(parts) >= 5:
                    nodes = [parts[1], parts[2], parts[3]]  # C, B, E
                    model = parts[4]
                    components.append(SpiceComponent(name, 'Q', nodes, model=model))

            elif comp_type == 'M':
                if len(parts) >= 6:
                    nodes = [parts[1], parts[2], parts[3], parts[4]]  # D, G, S, B
                    model = parts[5]
                    components.append(SpiceComponent(name, 'M', nodes, model=model))

            elif comp_type == 'J':
                if len(parts) >= 5:
                    nodes = [parts[1], parts[2], parts[3]]  # D, G, S
                    model = parts[4]
                    components.append(SpiceComponent(name, 'J', nodes, model=model))

            elif comp_type == 'V':
                nodes = [parts[1], parts[2]]
                value = ""
                rest = ' '.join(parts[3:]).upper()
                dc_match = re.search(r'DC\s+([^\s]+)', rest)
                if dc_match:
                    value = parse_value(dc_match.group(1))
                elif len(parts) > 3 and parts[3].upper() not in ['AC', 'PULSE', 'SIN', 'PWL', 'EXP']:
                    value = parse_value(parts[3])
                components.append(SpiceComponent(name, 'V', nodes, value))

            elif comp_type == 'I':
                nodes = [parts[1], parts[2]]
                value = ""
                rest = ' '.join(parts[3:]).upper()
                dc_match = re.search(r'DC\s+([^\s]+)', rest)
                if dc_match:
                    value = parse_value(dc_match.group(1))
                elif len(parts) > 3 and parts[3].upper() not in ['AC', 'PULSE', 'SIN', 'PWL']:
                    value = parse_value(parts[3])
                components.append(SpiceComponent(name, 'I', nodes, value))

        except (IndexError, ValueError):
            continue

    return components, title


# =============================================================================
# CONVERSAO PARA LCAPY
# =============================================================================

def normalize_node(node):
    """Normaliza nome de no para lcapy."""
    node = str(node).lower().strip()
    # Substituir 0 por 0 (terra)
    if node == '0' or node == 'gnd':
        return '0'
    # Remover caracteres invalidos
    node = re.sub(r'[^a-z0-9_]', '_', node)
    # Garantir que nao comeca com numero (exceto 0)
    if node and node[0].isdigit() and node != '0':
        node = 'n' + node
    return node


def create_lcapy_netlist(components, title):
    """
    Cria netlist no formato lcapy com layout correto.

    Nova estrategia:
    - Detectar componentes paralelos e usar wires para separa-los
    - Layout mais simples sem chain de ground nodes
    - Usar implicit ground connections
    """
    if not components:
        return ""

    lines = []

    # Mapear nos para formato lcapy
    node_map = {'0': '0', 'gnd': '0'}
    node_counter = 1

    # Primeiro passar: identificar todos os nos unicos
    all_nodes = set()
    for comp in components:
        for node in comp.nodes[:4]:  # Max 4 nodes (MOSFET)
            n = normalize_node(node)
            all_nodes.add(n)

    # Remover ground
    all_nodes.discard('0')

    # Mapear nos em ordem alfabetica para consistencia
    for node in sorted(all_nodes):
        node_map[node] = str(node_counter)
        node_counter += 1

    # Detectar componentes paralelos (mesmos nos)
    connection_map = defaultdict(list)
    for comp in components:
        if len(comp.nodes) >= 2:
            n1 = node_map.get(normalize_node(comp.nodes[0]), '0')
            n2 = node_map.get(normalize_node(comp.nodes[1]), '0')
            key = tuple(sorted([n1, n2]))
            connection_map[key].append(comp)

    # Criar nos auxiliares para componentes paralelos
    parallel_node_map = {}
    aux_counter = 100

    for key, comps in connection_map.items():
        if len(comps) > 1:  # Componentes em paralelo
            # Primeiro componente usa os nos originais
            # Demais usam nos auxiliares
            for i, comp in enumerate(comps[1:], 1):
                n1, n2 = key
                # Criar no auxiliar apenas para o no nao-ground
                if n1 != '0' and n2 == '0':
                    aux_node = f"{aux_counter}"
                    parallel_node_map[comp.name] = (n1, aux_node, n2)
                    aux_counter += 1
                elif n2 != '0' and n1 == '0':
                    aux_node = f"{aux_counter}"
                    parallel_node_map[comp.name] = (n2, aux_node, n1)
                    aux_counter += 1

    # Gerar componentes lcapy
    wires_needed = []

    for comp in components:
        if len(comp.nodes) < 2:
            continue

        # Verificar se este componente precisa de no auxiliar
        if comp.name in parallel_node_map:
            orig_node, aux_node, gnd_node = parallel_node_map[comp.name]
            wires_needed.append((orig_node, aux_node))
            n1, n2 = aux_node, gnd_node
        else:
            n1 = node_map.get(normalize_node(comp.nodes[0]), '0')
            n2 = node_map.get(normalize_node(comp.nodes[1]), '0')

        # Determinar orientacao
        is_to_ground = (n2 == '0' or n1 == '0')

        # Sempre colocar ground como segundo no
        if n1 == '0' and n2 != '0':
            n1, n2 = n2, n1

        if comp.comp_type == 'V':
            label = comp.name
            if comp.value:
                label = f"{comp.value}V"
            lines.append(f"V{comp.name[1:]} {n1} {n2}; down, v={{{label}}}")

        elif comp.comp_type == 'I':
            label = comp.name
            if comp.value:
                label = f"{comp.value}A"
            lines.append(f"I{comp.name[1:]} {n1} {n2}; down, i={{{label}}}")

        elif comp.comp_type == 'R':
            label = comp.name
            if comp.value:
                label = f"{comp.value}"
            if is_to_ground:
                lines.append(f"R{comp.name[1:]} {n1} {n2}; down")
            else:
                lines.append(f"R{comp.name[1:]} {n1} {n2}; right")

        elif comp.comp_type == 'C':
            label = comp.name
            if comp.value:
                label = f"{comp.value}"
            if is_to_ground:
                lines.append(f"C{comp.name[1:]} {n1} {n2}; down")
            else:
                lines.append(f"C{comp.name[1:]} {n1} {n2}; right")

        elif comp.comp_type == 'L':
            label = comp.name
            if comp.value:
                label = f"{comp.value}"
            if is_to_ground:
                lines.append(f"L{comp.name[1:]} {n1} {n2}; down")
            else:
                lines.append(f"L{comp.name[1:]} {n1} {n2}; right")

        elif comp.comp_type == 'D':
            label = comp.name
            if is_to_ground:
                lines.append(f"D{comp.name[1:]} {n1} {n2}; down")
            else:
                lines.append(f"D{comp.name[1:]} {n1} {n2}; right")

        elif comp.comp_type == 'Q':
            # BJT: precisa de 3 terminais (C, B, E)
            if len(comp.nodes) >= 3:
                c = node_map.get(normalize_node(comp.nodes[0]), '1')
                b = node_map.get(normalize_node(comp.nodes[1]), '2')
                e = node_map.get(normalize_node(comp.nodes[2]), '0')

                is_npn = 'PNP' not in (comp.model or '').upper()
                kind = 'npn' if is_npn else 'pnp'

                lines.append(f"Q{comp.name[1:]} {c} {b} {e}; {kind}")

        elif comp.comp_type == 'M':
            # MOSFET: D, G, S, B
            if len(comp.nodes) >= 3:
                d = node_map.get(normalize_node(comp.nodes[0]), '1')
                g = node_map.get(normalize_node(comp.nodes[1]), '2')
                s = node_map.get(normalize_node(comp.nodes[2]), '0')

                is_nmos = 'PMOS' not in (comp.model or '').upper()
                kind = 'nfet' if is_nmos else 'pfet'

                lines.append(f"M{comp.name[1:]} {d} {g} {s}; {kind}")

        elif comp.comp_type == 'J':
            # JFET: D, G, S
            if len(comp.nodes) >= 3:
                d = node_map.get(normalize_node(comp.nodes[0]), '1')
                g = node_map.get(normalize_node(comp.nodes[1]), '2')
                s = node_map.get(normalize_node(comp.nodes[2]), '0')

                is_njf = 'PJF' not in (comp.model or '').upper()
                kind = 'njf' if is_njf else 'pjf'

                lines.append(f"J{comp.name[1:]} {d} {g} {s}; {kind}")

    # Adicionar wires para conectar nos paralelos (stack vertical)
    for n1, n2 in wires_needed:
        lines.append(f"W {n1} {n2}; up")

    # Configuracoes de desenho
    lines.append("; draw_nodes=connections, label_nodes=none")

    return '\n'.join(lines)


def create_schematic_lcapy(components, title, output_path):
    """Cria esquematico usando lcapy."""
    if not LCAPY_AVAILABLE:
        print("  Erro: lcapy nao disponivel")
        return None

    netlist = create_lcapy_netlist(components, title)

    if not netlist:
        print("  Erro: netlist vazio")
        return None

    try:
        cct = Circuit(netlist)
        cct.draw(output_path, draw_nodes='connections', label_ids=False, label_nodes='none')
        return output_path
    except Exception as e:
        error_msg = str(e)
        # Se for erro de pdflatex, avisar especificamente
        if "pdflatex" in error_msg.lower():
            print(f"  Aviso: pdflatex nao instalado ou nao disponivel")
            print(f"  Instale LaTeX: sudo apt install texlive-latex-base texlive-pictures")
            print(f"  Usando fallback matplotlib...")
            return None
        # Se for erro de loop no grafico (circuito muito complexo), usar fallback
        if "loop" in error_msg.lower() or "graph" in error_msg.lower() or "size violation" in error_msg.lower():
            print(f"  Aviso lcapy: Circuito muito complexo para layout automatico")
            print(f"  Usando fallback matplotlib...")
            return None
        # Outros erros
        print(f"  Erro lcapy: {e}")
        print(f"  Netlist gerado:\n{netlist}")
        return None


def create_schematic_matplotlib(components, title, output_path):
    """Fallback usando matplotlib."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=14, fontweight='bold')

    n_cols = min(4, len(components))
    n_rows = (len(components) + n_cols - 1) // n_cols

    for i, comp in enumerate(components):
        row = i // n_cols
        col = i % n_cols

        x = col * 3 + 1.5
        y = (n_rows - row - 1) * 2 + 1

        rect = FancyBboxPatch((x - 0.8, y - 0.4), 1.6, 0.8,
                             boxstyle="round,pad=0.05",
                             facecolor='lightyellow',
                             edgecolor='black', linewidth=1.5)
        ax.add_patch(rect)

        label = f"{comp.name}"
        if comp.value:
            label += f"\n{comp.value}"
        elif comp.model:
            label += f"\n{comp.model}"

        ax.text(x, y, label, ha='center', va='center', fontsize=8)
        nodes_str = ' - '.join(comp.nodes[:2]) if comp.nodes else ""
        ax.text(x, y - 0.6, nodes_str, ha='center', va='top', fontsize=6, color='blue')

    ax.set_xlim(0, n_cols * 3)
    ax.set_ylim(0, n_rows * 2 + 1)

    ax.text(0.02, 0.02, f"Componentes: {len(components)}\n(Instale lcapy para esquematicos melhores)",
           transform=ax.transAxes, fontsize=8, va='bottom',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    return output_path


def create_schematic(components, title, output_path):
    """Cria esquematico usando lcapy ou fallback."""
    if LCAPY_AVAILABLE:
        result = create_schematic_lcapy(components, title, output_path)
        if result:
            return result
    return create_schematic_matplotlib(components, title, output_path)


# =============================================================================
# MAIN
# =============================================================================

def find_spice_files(search_path):
    """Encontra arquivos SPICE."""
    if os.path.isfile(search_path):
        return [search_path]

    if os.path.isdir(search_path):
        patterns = ['*.spice', '*.sp', '*.cir', '*.net']
        files = []
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(search_path, '**', pattern), recursive=True))
        return files

    return glob.glob(search_path, recursive=True)


def main():
    parser = argparse.ArgumentParser(
        description='Converte arquivos SPICE em esquematicos PNG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python spice_to_schematic.py circuito.spice
  python spice_to_schematic.py circuito.spice -o esquematico.png
  python spice_to_schematic.py circuits/

Requer lcapy para esquematicos de alta qualidade:
  pip install lcapy

Tambem precisa de LaTeX com circuitikz:
  macOS: brew install --cask mactex
  Ubuntu: sudo apt install texlive-pictures texlive-latex-extra
        """
    )

    parser.add_argument('input', help='Arquivo SPICE ou diretorio')
    parser.add_argument('-o', '--output', help='Arquivo de saida PNG')
    parser.add_argument('-v', '--verbose', action='store_true', help='Modo verbose')
    parser.add_argument('--netlist', action='store_true', help='Mostrar netlist lcapy gerado')

    args = parser.parse_args()

    if not LCAPY_AVAILABLE:
        print("=" * 50)
        print("AVISO: lcapy nao encontrado!")
        print("Para esquematicos de alta qualidade, instale:")
        print("  pip install lcapy")
        print("  + LaTeX com circuitikz")
        print("Usando fallback matplotlib (qualidade reduzida)")
        print("=" * 50)

    spice_files = find_spice_files(args.input)

    if not spice_files:
        print(f"Nenhum arquivo SPICE encontrado em: {args.input}")
        return 1

    print(f"Encontrados {len(spice_files)} arquivo(s) SPICE")
    print("-" * 50)

    success = 0
    errors = 0

    for spice_path in spice_files:
        try:
            if args.verbose:
                print(f"Processando: {spice_path}")

            components, title = parse_spice_file(spice_path)

            if args.verbose:
                print(f"  Componentes encontrados: {len(components)}")
                for comp in components:
                    print(f"    {comp}")

            if not components:
                print(f"  Aviso: Nenhum componente encontrado em {spice_path}")
                continue

            if args.netlist:
                netlist = create_lcapy_netlist(components, title)
                print(f"\nNetlist lcapy:\n{netlist}\n")

            if args.output and len(spice_files) == 1:
                output_path = args.output
            else:
                base = os.path.splitext(spice_path)[0]
                output_path = base + '_schematic.png'

            result = create_schematic(components, title or os.path.basename(spice_path), output_path)

            if result:
                print(f"  {spice_path} -> {output_path}")
                success += 1
            else:
                errors += 1

        except Exception as e:
            print(f"  ERRO em {spice_path}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            errors += 1

    print("-" * 50)
    print(f"Concluido: {success} sucesso, {errors} erro(s)")

    return 0 if errors == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
