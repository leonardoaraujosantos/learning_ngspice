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
    X  - Subcircuito / Op-Amp
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

    def __init__(self, name, comp_type, nodes, value=None, model=None, params=None):
        self.name = name
        self.comp_type = comp_type
        self.nodes = nodes
        self.value = value
        self.model = model
        self.params = params or {}

    def __repr__(self):
        return f"{self.comp_type}:{self.name}({self.nodes}) = {self.value}"


def parse_value(value_str):
    """Converte string de valor SPICE para formato legivel."""
    if not value_str:
        return ""

    value_str = value_str.strip()

    # Remover chaves de expressao
    if value_str.startswith('{') and value_str.endswith('}'):
        return value_str[1:-1]

    # Manter sufixos SPICE como estao (1k, 100n, etc.)
    return value_str


def parse_spice_file(filepath):
    """
    Parseia arquivo SPICE e retorna lista de componentes.
    Ignora componentes dentro de .subckt (apenas pega o circuito principal).
    """
    components = []
    title = ""
    in_subckt = False
    in_control = False

    with open(filepath, 'r') as f:
        lines = f.readlines()

    if not lines:
        return components, title

    # Primeira linha e o titulo
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

    # Parsear cada linha
    for line in joined_lines:
        line = line.strip()

        # Ignorar comentarios e linhas vazias
        if not line or line.startswith('*'):
            continue

        # Remover comentario inline
        if ';' in line:
            line = line[:line.index(';')].strip()
        if not line:
            continue

        # Verificar diretivas
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

        # Ignorar outras diretivas e conteudo de subckt/control
        if line.startswith('.') or in_subckt or in_control:
            continue

        parts = line.split()
        if not parts:
            continue

        name = parts[0].upper()
        comp_type = name[0]

        try:
            if comp_type == 'R':
                nodes = [parts[1].lower(), parts[2].lower()]
                value = parse_value(parts[3]) if len(parts) > 3 else ""
                components.append(SpiceComponent(name, 'R', nodes, value))

            elif comp_type == 'C':
                nodes = [parts[1].lower(), parts[2].lower()]
                value = parse_value(parts[3]) if len(parts) > 3 else ""
                components.append(SpiceComponent(name, 'C', nodes, value))

            elif comp_type == 'L':
                nodes = [parts[1].lower(), parts[2].lower()]
                value = parse_value(parts[3]) if len(parts) > 3 else ""
                components.append(SpiceComponent(name, 'L', nodes, value))

            elif comp_type == 'D':
                nodes = [parts[1].lower(), parts[2].lower()]
                model = parts[3] if len(parts) > 3 else ""
                components.append(SpiceComponent(name, 'D', nodes, model=model))

            elif comp_type == 'Q':
                # Qnome coletor base emissor modelo
                if len(parts) >= 5:
                    nodes = [parts[1].lower(), parts[2].lower(), parts[3].lower()]
                    model = parts[4]
                    components.append(SpiceComponent(name, 'Q', nodes, model=model))

            elif comp_type == 'M':
                # Mnome drain gate source bulk modelo
                if len(parts) >= 6:
                    nodes = [parts[1].lower(), parts[2].lower(), parts[3].lower(), parts[4].lower()]
                    model = parts[5]
                    components.append(SpiceComponent(name, 'M', nodes, model=model))

            elif comp_type == 'J':
                # Jnome drain gate source modelo
                if len(parts) >= 5:
                    nodes = [parts[1].lower(), parts[2].lower(), parts[3].lower()]
                    model = parts[4]
                    components.append(SpiceComponent(name, 'J', nodes, model=model))

            elif comp_type == 'V':
                nodes = [parts[1].lower(), parts[2].lower()]
                # Extrair valor DC
                value = ""
                rest = ' '.join(parts[3:]).upper()
                dc_match = re.search(r'DC\s+([^\s]+)', rest)
                if dc_match:
                    value = parse_value(dc_match.group(1))
                elif len(parts) > 3 and parts[3].upper() not in ['AC', 'PULSE', 'SIN', 'PWL', 'EXP']:
                    value = parse_value(parts[3])
                components.append(SpiceComponent(name, 'V', nodes, value))

            elif comp_type == 'I':
                nodes = [parts[1].lower(), parts[2].lower()]
                value = ""
                rest = ' '.join(parts[3:]).upper()
                dc_match = re.search(r'DC\s+([^\s]+)', rest)
                if dc_match:
                    value = parse_value(dc_match.group(1))
                elif len(parts) > 3 and parts[3].upper() not in ['AC', 'PULSE', 'SIN', 'PWL']:
                    value = parse_value(parts[3])
                components.append(SpiceComponent(name, 'I', nodes, value))

            elif comp_type == 'X':
                # Xnome no1 no2 ... subckt_name
                # Ultimo item (antes de params) e o nome do subcircuito
                nodes = []
                subckt_name = None
                for i, p in enumerate(parts[1:], 1):
                    if '=' in p or p.upper() == 'PARAMS:':
                        break
                    nodes.append(p.lower())
                if nodes:
                    subckt_name = nodes.pop()  # Ultimo e o nome do subcircuito
                if subckt_name:
                    components.append(SpiceComponent(name, 'X', nodes, model=subckt_name))

        except (IndexError, ValueError):
            continue

    return components, title


# =============================================================================
# CONVERSAO PARA LCAPY
# =============================================================================

def normalize_node(node):
    """Normaliza nome de no para lcapy (sem caracteres especiais)."""
    node = str(node).lower()
    # lcapy usa numeros para nos, mas aceita nomes
    # Substituir caracteres problematicos
    node = re.sub(r'[^a-z0-9_]', '_', node)
    return node


def build_node_graph(components):
    """Constroi grafo de conexoes entre nos."""
    graph = defaultdict(set)
    for comp in components:
        nodes = [normalize_node(n) for n in comp.nodes]
        for i, n1 in enumerate(nodes):
            for n2 in nodes[i+1:]:
                graph[n1].add(n2)
                graph[n2].add(n1)
    return graph


def assign_positions(components):
    """
    Atribui posicoes e orientacoes aos componentes.
    Retorna dict {comp_name: (x, y, direction)}
    """
    positions = {}
    node_pos = {'0': (0, 0)}  # GND no centro-baixo

    # Primeira passada: posicionar nos conectados ao GND
    gnd_connected = []
    other_comps = []

    for comp in components:
        nodes = [normalize_node(n) for n in comp.nodes]
        if '0' in nodes:
            gnd_connected.append(comp)
        else:
            other_comps.append(comp)

    # Posicionar componentes conectados ao GND em linha horizontal
    x_offset = 0
    for comp in gnd_connected:
        nodes = [normalize_node(n) for n in comp.nodes]
        other_node = [n for n in nodes if n != '0'][0] if len(nodes) > 1 else nodes[0]

        if other_node not in node_pos:
            node_pos[other_node] = (x_offset, 2)

        positions[comp.name] = {
            'from': other_node,
            'to': '0',
            'dir': 'down'
        }
        x_offset += 3

    # Posicionar outros componentes
    for comp in other_comps:
        nodes = [normalize_node(n) for n in comp.nodes]

        # Encontrar no ja posicionado
        known = [n for n in nodes if n in node_pos]
        unknown = [n for n in nodes if n not in node_pos]

        if known and unknown:
            base = known[0]
            base_x, base_y = node_pos[base]

            for i, n in enumerate(unknown):
                node_pos[n] = (base_x + 3 * (i + 1), base_y)

            positions[comp.name] = {
                'from': nodes[0],
                'to': nodes[1] if len(nodes) > 1 else nodes[0],
                'dir': 'right'
            }
        elif len(known) >= 2:
            # Ambos nos conhecidos
            n1, n2 = nodes[0], nodes[1]
            x1, y1 = node_pos.get(n1, (0, 0))
            x2, y2 = node_pos.get(n2, (1, 0))

            if abs(x2 - x1) > abs(y2 - y1):
                direction = 'right' if x2 > x1 else 'left'
            else:
                direction = 'up' if y2 > y1 else 'down'

            positions[comp.name] = {
                'from': n1,
                'to': n2,
                'dir': direction
            }
        else:
            # Nenhum no conhecido - criar novos
            for n in nodes:
                if n not in node_pos:
                    node_pos[n] = (x_offset, 2)
                    x_offset += 3

            if len(nodes) >= 2:
                positions[comp.name] = {
                    'from': nodes[0],
                    'to': nodes[1],
                    'dir': 'right'
                }

    return positions, node_pos


def component_to_lcapy(comp, positions):
    """Converte um componente SPICE para sintaxe lcapy."""
    pos = positions.get(comp.name, {})
    direction = pos.get('dir', 'right')
    node_from = pos.get('from', normalize_node(comp.nodes[0]) if comp.nodes else '1')
    node_to = pos.get('to', normalize_node(comp.nodes[1]) if len(comp.nodes) > 1 else '0')

    # Garantir que nos sao validos
    node_from = normalize_node(node_from)
    node_to = normalize_node(node_to)

    # Label do componente
    label = comp.name
    if comp.value:
        label = f"{comp.name}={comp.value}"

    if comp.comp_type == 'R':
        return f"R{comp.name[1:]} {node_from} {node_to}; {direction}, l={{{label}}}"

    elif comp.comp_type == 'C':
        return f"C{comp.name[1:]} {node_from} {node_to}; {direction}, l={{{label}}}"

    elif comp.comp_type == 'L':
        return f"L{comp.name[1:]} {node_from} {node_to}; {direction}, l={{{label}}}"

    elif comp.comp_type == 'D':
        model_str = comp.model or ""
        return f"D{comp.name[1:]} {node_from} {node_to}; {direction}, l={{{comp.name} {model_str}}}"

    elif comp.comp_type == 'V':
        # Fonte de tensao
        val = comp.value or ""
        return f"V{comp.name[1:]} {node_from} {node_to}; {direction}, l={{{comp.name} {val}}}"

    elif comp.comp_type == 'I':
        val = comp.value or ""
        return f"I{comp.name[1:]} {node_from} {node_to}; {direction}, l={{{comp.name} {val}}}"

    elif comp.comp_type == 'Q':
        # BJT: Q nome c b e
        nodes = [normalize_node(n) for n in comp.nodes]
        if len(nodes) >= 3:
            c, b, e = nodes[0], nodes[1], nodes[2]
            kind = 'npn' if 'NPN' in (comp.model or '').upper() else 'pnp'
            if 'NPN' not in (comp.model or '').upper() and 'PNP' not in (comp.model or '').upper():
                kind = 'npn'  # Default
            return f"Q{comp.name[1:]} {c} {b} {e}; {direction}, l={{{comp.name}}}, kind={kind}"
        return ""

    elif comp.comp_type == 'M':
        # MOSFET: M nome d g s b
        nodes = [normalize_node(n) for n in comp.nodes]
        if len(nodes) >= 3:
            d, g, s = nodes[0], nodes[1], nodes[2]
            kind = 'nfet' if 'NMOS' in (comp.model or '').upper() else 'pfet'
            if 'NMOS' not in (comp.model or '').upper() and 'PMOS' not in (comp.model or '').upper():
                kind = 'nfet'
            return f"M{comp.name[1:]} {d} {g} {s}; {direction}, l={{{comp.name}}}, kind={kind}"
        return ""

    elif comp.comp_type == 'J':
        # JFET: J nome d g s
        nodes = [normalize_node(n) for n in comp.nodes]
        if len(nodes) >= 3:
            d, g, s = nodes[0], nodes[1], nodes[2]
            kind = 'njf' if 'NJF' in (comp.model or '').upper() else 'pjf'
            if 'NJF' not in (comp.model or '').upper() and 'PJF' not in (comp.model or '').upper():
                kind = 'njf'
            return f"J{comp.name[1:]} {d} {g} {s}; {direction}, l={{{comp.name}}}, kind={kind}"
        return ""

    elif comp.comp_type == 'X':
        # Subcircuito - desenhar como caixa
        nodes = [normalize_node(n) for n in comp.nodes]
        if len(nodes) >= 2:
            return f"W {nodes[0]} {nodes[1]}; {direction}, l={{{comp.name}: {comp.model or ''}}}"
        return ""

    return ""


def create_lcapy_netlist(components, title):
    """Cria netlist no formato lcapy."""
    positions, node_pos = assign_positions(components)

    lines = []
    lines.append(f"# {title}")

    for comp in components:
        lcapy_line = component_to_lcapy(comp, positions)
        if lcapy_line:
            lines.append(lcapy_line)

    # Adicionar configuracoes de desenho
    lines.append("; draw_nodes=connections, label_nodes=primary, label_ids=false")

    return '\n'.join(lines)


def create_schematic_lcapy(components, title, output_path):
    """Cria esquematico usando lcapy."""
    if not LCAPY_AVAILABLE:
        print("  Erro: lcapy nao disponivel")
        return None

    netlist = create_lcapy_netlist(components, title)

    try:
        cct = Circuit(netlist)
        cct.draw(output_path, draw_nodes='connections', label_nodes='primary')
        return output_path
    except Exception as e:
        print(f"  Erro lcapy: {e}")
        print(f"  Netlist gerado:\n{netlist}")
        return None


# =============================================================================
# FALLBACK: MATPLOTLIB (versao simplificada)
# =============================================================================

def create_schematic_matplotlib(components, title, output_path):
    """Fallback usando matplotlib quando lcapy nao esta disponivel."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=14, fontweight='bold')

    # Layout simples em grid
    n_cols = min(4, len(components))
    n_rows = (len(components) + n_cols - 1) // n_cols

    for i, comp in enumerate(components):
        row = i // n_cols
        col = i % n_cols

        x = col * 3 + 1.5
        y = (n_rows - row - 1) * 2 + 1

        # Desenhar caixa do componente
        rect = FancyBboxPatch((x - 0.8, y - 0.4), 1.6, 0.8,
                             boxstyle="round,pad=0.05",
                             facecolor='lightyellow',
                             edgecolor='black', linewidth=1.5)
        ax.add_patch(rect)

        # Texto do componente
        label = f"{comp.name}"
        if comp.value:
            label += f"\n{comp.value}"
        elif comp.model:
            label += f"\n{comp.model}"

        ax.text(x, y, label, ha='center', va='center', fontsize=8)

        # Nos
        nodes_str = ' - '.join(comp.nodes[:2]) if comp.nodes else ""
        ax.text(x, y - 0.6, nodes_str, ha='center', va='top', fontsize=6, color='blue')

    ax.set_xlim(0, n_cols * 3)
    ax.set_ylim(0, n_rows * 2 + 1)

    # Legenda
    ax.text(0.02, 0.02, f"Componentes: {len(components)}\n(Instale lcapy para esquematicos melhores)",
           transform=ax.transAxes, fontsize=8, va='bottom',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    return output_path


def create_schematic(components, title, output_path):
    """Cria esquematico usando lcapy ou fallback para matplotlib."""
    if LCAPY_AVAILABLE:
        result = create_schematic_lcapy(components, title, output_path)
        if result:
            return result

    # Fallback para matplotlib
    return create_schematic_matplotlib(components, title, output_path)


# =============================================================================
# MAIN
# =============================================================================

def find_spice_files(search_path):
    """Encontra arquivos SPICE em um diretorio."""
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

    # Verificar lcapy
    if not LCAPY_AVAILABLE:
        print("=" * 50)
        print("AVISO: lcapy nao encontrado!")
        print("Para esquematicos de alta qualidade, instale:")
        print("  pip install lcapy")
        print("  + LaTeX com circuitikz")
        print("Usando fallback matplotlib (qualidade reduzida)")
        print("=" * 50)

    # Encontrar arquivos
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

            # Parsear arquivo
            components, title = parse_spice_file(spice_path)

            if args.verbose:
                print(f"  Componentes encontrados: {len(components)}")
                for comp in components:
                    print(f"    {comp}")

            if not components:
                print(f"  Aviso: Nenhum componente encontrado em {spice_path}")
                continue

            # Mostrar netlist se solicitado
            if args.netlist:
                netlist = create_lcapy_netlist(components, title)
                print(f"\nNetlist lcapy:\n{netlist}\n")

            # Definir saida
            if args.output and len(spice_files) == 1:
                output_path = args.output
            else:
                base = os.path.splitext(spice_path)[0]
                output_path = base + '_schematic.png'

            # Criar esquematico
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
