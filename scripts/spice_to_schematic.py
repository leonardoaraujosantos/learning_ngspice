#!/usr/bin/env python3
"""
spice_to_schematic.py - Converte arquivos SPICE em esquematicos PNG usando circuitikz

Uso:
    python scripts/spice_to_schematic.py circuito.spice
    python scripts/spice_to_schematic.py circuito.spice -o saida.png
    python scripts/spice_to_schematic.py circuits/  # processa todos

Requer:
    LaTeX com circuitikz

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
import tempfile
import subprocess
from pathlib import Path
from collections import defaultdict


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


class SubcircuitDefinition:
    """Define um subcircuito com pinos e componentes."""

    def __init__(self, name, pins):
        self.name = name
        self.pins = [normalize_node(p) for p in pins]
        self.components = []
        self.instances = []


class SubcircuitInstance:
    """Instancia de subcircuito (.SUBCKT)."""

    def __init__(self, name, subckt, nodes):
        self.name = name
        self.subckt = subckt
        self.nodes = nodes


def expand_subcircuit(instance, subckt_defs, depth=0):
    """Expande uma instancia em componentes planos."""
    if depth > 8:
        return []
    if instance.subckt not in subckt_defs:
        return []

    sub = subckt_defs[instance.subckt]
    pin_map = {}
    for pin, node in zip(sub.pins, instance.nodes):
        pin_map[pin] = normalize_node(node)

    flattened = []
    prefix = instance.name

    def map_node(n):
        nn = normalize_node(n)
        if nn == '0':
            return '0'
        if nn in pin_map:
            return pin_map[nn]
        return f"{prefix}_{nn}"

    for comp in sub.components:
        mapped = [map_node(n) for n in comp.nodes]
        flattened.append(SpiceComponent(f"{prefix}_{comp.name}", comp.comp_type, mapped, comp.value, comp.model))

    for inst in sub.instances:
        mapped_nodes = [map_node(n) for n in inst.nodes]
        flat = expand_subcircuit(SubcircuitInstance(f"{prefix}_{inst.name}", inst.subckt, mapped_nodes), subckt_defs, depth + 1)
        flattened.extend(flat)

    return flattened


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
    current_subckt = None
    subckt_defs = {}
    instances = []
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
            parts = line.split()
            if len(parts) >= 2:
                name = parts[1]
                pins = parts[2:]
                subckt_defs[name] = SubcircuitDefinition(name, pins)
                current_subckt = name
            continue
        if line_upper.startswith('.ENDS'):
            current_subckt = None
            continue
        if line_upper.startswith('.CONTROL'):
            in_control = True
            continue
        if line_upper.startswith('.ENDC'):
            in_control = False
            continue

        if line.startswith('.') or current_subckt is not None and line_upper.startswith('.ENDS') or in_control:
            continue

        parts = line.split()
        if not parts:
            continue

        name = parts[0].upper()
        comp_type = name[0]

        target = components if current_subckt is None else subckt_defs[current_subckt].components

        try:
            if comp_type in ['R', 'C', 'L']:
                nodes = [parts[1], parts[2]]
                value = parse_value(parts[3]) if len(parts) > 3 else ""
                target.append(SpiceComponent(name, comp_type, nodes, value))

            elif comp_type == 'D':
                nodes = [parts[1], parts[2]]
                model = parts[3] if len(parts) > 3 else ""
                target.append(SpiceComponent(name, 'D', nodes, model=model))

            elif comp_type == 'Q':
                if len(parts) >= 5:
                    nodes = [parts[1], parts[2], parts[3]]  # C, B, E
                    model = parts[4]
                    target.append(SpiceComponent(name, 'Q', nodes, model=model))

            elif comp_type == 'M':
                if len(parts) >= 6:
                    nodes = [parts[1], parts[2], parts[3], parts[4]]  # D, G, S, B
                    model = parts[5]
                    target.append(SpiceComponent(name, 'M', nodes, model=model))

            elif comp_type == 'J':
                if len(parts) >= 5:
                    nodes = [parts[1], parts[2], parts[3]]  # D, G, S
                    model = parts[4]
                    target.append(SpiceComponent(name, 'J', nodes, model=model))

            elif comp_type == 'V':
                nodes = [parts[1], parts[2]]
                value = ""
                rest = ' '.join(parts[3:]).upper()
                dc_match = re.search(r'DC\s+([^\s]+)', rest)
                if dc_match:
                    value = parse_value(dc_match.group(1))
                elif len(parts) > 3 and parts[3].upper() not in ['AC', 'PULSE', 'SIN', 'PWL', 'EXP']:
                    value = parse_value(parts[3])
                target.append(SpiceComponent(name, 'V', nodes, value))

            elif comp_type == 'I':
                nodes = [parts[1], parts[2]]
                value = ""
                rest = ' '.join(parts[3:]).upper()
                dc_match = re.search(r'DC\s+([^\s]+)', rest)
                if dc_match:
                    value = parse_value(dc_match.group(1))
                elif len(parts) > 3 and parts[3].upper() not in ['AC', 'PULSE', 'SIN', 'PWL']:
                    value = parse_value(parts[3])
                target.append(SpiceComponent(name, 'I', nodes, value))

            elif comp_type == 'X' and len(parts) >= 3:
                subckt_name = parts[-1]
                node_list = parts[1:-1]
                inst = SubcircuitInstance(name, subckt_name, node_list)
                if current_subckt:
                    subckt_defs[current_subckt].instances.append(inst)
                else:
                    instances.append(inst)

        except (IndexError, ValueError):
            continue

    for inst in instances:
        components.extend(expand_subcircuit(inst, subckt_defs))

    return components, title


# =============================================================================
# CONVERSAO PARA NETLIST INTERNO
# =============================================================================

def normalize_node(node):
    """Normaliza nome de no para netlist interno."""
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


def _safe_id(text):
    """Gera um identificador seguro para TikZ."""
    return re.sub(r'[^a-zA-Z0-9]+', '_', str(text))


def _component_label(comp):
    if comp.value:
        return comp.value
    if comp.model:
        return comp.model
    return comp.name


def _label_attr(text):
    if not text:
        return ""
    safe = str(text).replace('_', '\\_')
    return f",l=${safe}$"


def create_netlist(components, title):
    """
    Cria netlist interno para debug.

    Nova estrategia:
    - Detectar componentes paralelos e usar wires para separa-los
    - Layout mais simples sem chain de ground nodes
    - Usar implicit ground connections
    """
    if not components:
        return ""

    # Caso especial: 1 fonte de tensao + resistores -> layout manual
    if _is_simple_voltage_fan(components):
        net = _create_netlist_simple_fan(components)
        if net:
            return net

    lines = []

    # Mapear nos para netlist interno
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

    # Gerar componentes
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
                kind = 'njfet' if is_njf else 'pjfet'

                lines.append(f"J{comp.name[1:]} {d} {g} {s}; {kind}")

    # Adicionar wires para conectar nos paralelos (stack vertical)
    for n1, n2 in wires_needed:
        lines.append(f"W {n1} {n2}; up")

    # Configuracoes de desenho
    lines.append("; draw_nodes=connections, label_nodes=none")

    return '\n'.join(lines)


def _is_simple_voltage_fan(components):
    """Detecta 1 fonte de tensao + resistores com ground presente."""
    vs = [c for c in components if c.comp_type == 'V']
    if len(vs) != 1:
        return False
    if any(c.comp_type not in ('V', 'R') for c in components):
        return False
    nodes = [normalize_node(n) for n in vs[0].nodes]
    return '0' in nodes


def _create_netlist_simple_fan(components):
    """Layout manual estilo tutorial para um fan de resistores."""
    v = next(c for c in components if c.comp_type == 'V')
    n1, n0 = normalize_node(v.nodes[0]), normalize_node(v.nodes[1])
    hub, gnd = (n1, n0) if n0 == '0' else (n0, n1)
    if gnd != '0':
        return None

    resistors = [c for c in components if c.comp_type == 'R']
    adj = defaultdict(list)
    for r in resistors:
        a, b = normalize_node(r.nodes[0]), normalize_node(r.nodes[1])
        adj[a].append((r, b))
        adj[b].append((r, a))

    used = set()
    branches = []

    def build_branch(res, other):
        chain = [res]
        used.add(res.name)
        prev = hub
        curr = other
        while True:
            next_r = None
            for r, nxt in adj[curr]:
                if r.name in used or nxt == prev:
                    continue
                next_r = (r, nxt)
                break
            if not next_r:
                break
            r, nxt = next_r
            chain.append(r)
            used.add(r.name)
            prev, curr = curr, nxt
        return chain, curr

    for r in resistors:
        if r.name in used:
            continue
        a, b = normalize_node(r.nodes[0]), normalize_node(r.nodes[1])
        if hub not in (a, b):
            continue
        other = b if a == hub else a
        chain, end_node = build_branch(r, other)
        branches.append((chain, end_node))

    lines = []
    lines.append(f"V{v.name[1:]} {hub} 0; down")
    dir_cycle = ['right', 'up', 'down', 'left']

    for idx, (chain, end_node) in enumerate(branches):
        branch_node = f"{hub}_b{idx}"
        direction = dir_cycle[idx % len(dir_cycle)]
        lines.append(f"W {hub} {branch_node}; {direction}")
        current = branch_node
        for j, r in enumerate(chain):
            is_last = (j == len(chain) - 1)
            end_norm = normalize_node(end_node)
            dest = '0' if is_last and end_norm == '0' else f"{branch_node}_n{j}"
            orient = 'down' if is_last and end_norm == '0' else 'right'
            val = r.value or ""
            lines.append(f"R{r.name[1:]} {current} {dest} {val}; {orient}")
            current = dest
        if normalize_node(end_node) == '0':
            lines.append(f"W {current} 0; down")

    lines.append("; draw_nodes=connections, label_nodes=none")
    return "\n".join(lines)


def _extract_fan_branches(components):
    """Extrai hub, resistores em ramos, e valor da fonte (sem linearizar ramos)."""
    v = next(c for c in components if c.comp_type == 'V')
    v_value = v.value or v.name
    n1, n0 = normalize_node(v.nodes[0]), normalize_node(v.nodes[1])
    hub, gnd = (n1, n0) if n0 == '0' else (n0, n1)
    resistors = [c for c in components if c.comp_type == 'R']

    adj = defaultdict(list)
    for r in resistors:
        a, b = normalize_node(r.nodes[0]), normalize_node(r.nodes[1])
        adj[a].append((r, b))
        adj[b].append((r, a))

    used = set()
    branches = []

    for r in resistors:
        if r.name in used:
            continue
        a, b = normalize_node(r.nodes[0]), normalize_node(r.nodes[1])
        if hub not in (a, b):
            continue
        other = b if a == hub else a
        chain = [r]
        used.add(r.name)

        prev = hub
        curr = other
        while True:
            if curr == '0':
                break
            next_r = None
            for rr, nxt in adj[curr]:
                if rr.name in used or nxt == prev:
                    continue
                next_r = (rr, nxt)
                break
            if not next_r:
                break
            rr, nxt = next_r
            chain.append(rr)
            used.add(rr.name)
            prev, curr = curr, nxt

        branches.append((chain, curr))

    return hub, gnd, v_value, branches


def _circuitikz_simple_fan(components, title):
    """Gera codigo circuitikz para um fan simples."""
    hub, gnd, vval, branches = _extract_fan_branches(components)

    lines = []
    lines.append("\\begin{circuitikz}[american voltages]")
    # Coordenadas
    lines.append("\\coordinate (hub) at (0,0);")
    lines.append("\\coordinate (gnd) at (0,-3);")
    lines.append(f"\\draw (hub) to[V,l=${vval}$, invert] (gnd);")

    # Posicoes fixas para ramos: direita, cima, esquerda, baixo
    dir_vectors = [(3, 0), (0, 3), (-3, 0), (0, -3)]

    for idx, (chain, end_node) in enumerate(branches):
        dx, dy = dir_vectors[idx % len(dir_vectors)]
        start = f"b{idx}_0"
        lines.append(f"\\draw (hub) to[short] ++({dx},{dy}) coordinate ({start});")
        current = start
        for j, r in enumerate(chain):
            is_last = (j == len(chain) - 1)
            end_norm = normalize_node(end_node)
            val = r.value or r.name

            if dx != 0:
                step_x, step_y = (2 if dx > 0 else -2), 0
            else:
                step_x, step_y = 0, (2 if dy > 0 else -2)

            if is_last and end_norm == '0':
                lines.append(f"\\draw ({current}) to[R,l=${val}$] ++({step_x},{step_y}) to[short] ++(0,-2) node[ground]{{}};")
            else:
                nxt = f"b{idx}_{j+1}"
                lines.append(f"\\draw ({current}) to[R,l=${val}$] ++({step_x},{step_y}) coordinate ({nxt});")
                current = nxt

    lines.append("\\end{circuitikz}")
    return "\n".join(lines)


def _circuitikz_generic(components, title):
    """Gera circuito circuitikz com layout simples em grade."""
    bipoles = {'R', 'C', 'L', 'V', 'I', 'D'}
    nodes = set()
    for comp in components:
        for node in comp.nodes[:4]:
            n = normalize_node(node)
            if n != '0':
                nodes.add(n)
    if not nodes:
        return None

    nodes = sorted(nodes)
    node_ids = {n: f"n{idx}" for idx, n in enumerate(nodes)}

    # Grafo para BFS (sem ground)
    adj = defaultdict(set)
    for comp in components:
        if comp.comp_type in bipoles and len(comp.nodes) >= 2:
            a = normalize_node(comp.nodes[0])
            b = normalize_node(comp.nodes[1])
            if a != '0' and b != '0':
                adj[a].add(b)
                adj[b].add(a)
        elif comp.comp_type in ('Q', 'M', 'J') and len(comp.nodes) >= 3:
            pins = [normalize_node(n) for n in comp.nodes[:4] if normalize_node(n) != '0']
            if len(pins) >= 2:
                hub = pins[0]
                for other in pins[1:]:
                    adj[hub].add(other)
                    adj[other].add(hub)

    # Componentes desconectados (ignora ground como ligacao)
    components_nodes = []
    visited = set()
    for n in nodes:
        if n in visited:
            continue
        stack = [n]
        group = set()
        while stack:
            cur = stack.pop()
            if cur in group:
                continue
            group.add(cur)
            for nxt in adj[cur]:
                if nxt not in group:
                    stack.append(nxt)
        visited |= group
        components_nodes.append(group)

    def choose_ref(group):
        for comp in components:
            if comp.comp_type not in ('V', 'I') or len(comp.nodes) < 2:
                continue
            n1 = normalize_node(comp.nodes[0])
            n2 = normalize_node(comp.nodes[1])
            if n1 in group and n2 == '0':
                return n1
            if n2 in group and n1 == '0':
                return n2
        degrees = {n: len(adj[n]) for n in group}
        return max(group, key=lambda n: (degrees.get(n, 0), n))

    def layout_group(group):
        ref = choose_ref(group)
        level = {ref: 0}
        queue = [ref]
        while queue:
            cur = queue.pop(0)
            for nxt in adj[cur]:
                if nxt in group and nxt not in level:
                    level[nxt] = level[cur] + 1
                    queue.append(nxt)

        max_level = max(level.values()) if level else 0
        for n in group:
            if n not in level:
                max_level += 1
                level[n] = max_level

        by_level = defaultdict(list)
        for n, lvl in level.items():
            by_level[lvl].append(n)

        order = {}
        for lvl, group_nodes in by_level.items():
            order[lvl] = sorted(group_nodes)

        max_lvl = max(order.keys()) if order else 0
        for _ in range(2):
            for lvl in range(1, max_lvl + 1):
                prev = order.get(lvl - 1, [])
                prev_idx = {n: i for i, n in enumerate(prev)}

                def key_prev(n):
                    indices = [prev_idx[p] for p in adj[n] if p in prev_idx]
                    return sum(indices) / len(indices) if indices else len(prev) / 2

                order[lvl].sort(key=key_prev)

            for lvl in range(max_lvl - 1, -1, -1):
                nxt = order.get(lvl + 1, [])
                nxt_idx = {n: i for i, n in enumerate(nxt)}

                def key_next(n):
                    indices = [nxt_idx[p] for p in adj[n] if p in nxt_idx]
                    return sum(indices) / len(indices) if indices else len(nxt) / 2

                order[lvl].sort(key=key_next)

        coords_local = {}
        dx, dy = 6, 4
        for lvl in sorted(order.keys()):
            group_nodes = order[lvl]
            total = len(group_nodes)
            for i, n in enumerate(group_nodes):
                y = (i - (total - 1) / 2) * dy
                x = lvl * dx
                coords_local[n] = (x, y)
        return coords_local

    # Posicionar grupos em grade
    coords = {}
    cursor_x = 0
    cursor_y = 0
    row_height = 0
    max_row_width = 36
    margin = 6

    for group in components_nodes:
        local = layout_group(group)
        xs = [v[0] for v in local.values()]
        ys = [v[1] for v in local.values()]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        width = maxx - minx if xs else 0
        height = maxy - miny if ys else 0

        if cursor_x + width > max_row_width and cursor_x > 0:
            cursor_x = 0
            cursor_y -= (row_height + margin)
            row_height = 0

        for n, (x, y) in local.items():
            coords[n] = (x - minx + cursor_x, y - miny + cursor_y)

        cursor_x += width + margin
        row_height = max(row_height, height)

    lines = []
    lines.append("\\begin{circuitikz}[american voltages]")
    for n, (x, y) in coords.items():
        lines.append(f"\\coordinate ({node_ids[n]}) at ({x},{y});")

    # Offsets para componentes em ground
    ground_groups = defaultdict(list)
    for comp in components:
        if comp.comp_type in bipoles and len(comp.nodes) >= 2:
            n1 = normalize_node(comp.nodes[0])
            n2 = normalize_node(comp.nodes[1])
            if (n1 == '0') ^ (n2 == '0'):
                other = n2 if n1 == '0' else n1
                if other in node_ids:
                    ground_groups[other].append(comp)

    ground_offsets = {}
    ground_spacing = 2.5
    for node, comps in ground_groups.items():
        total = len(comps)
        start = -(total - 1) / 2
        for idx, comp in enumerate(comps):
            ground_offsets[comp.name] = (start + idx) * ground_spacing

    def draw_ground_bipole(comp, node):
        comp_id = _safe_id(comp.name)
        offset = ground_offsets.get(comp.name, 0)
        base = node_ids[node]
        label = _component_label(comp)
        label_attr = _label_attr(label)
        kind = comp.comp_type
        if offset:
            anchor = f"{comp_id}_gnd"
            lines.append(f"\\draw ({base}) to[short] ++({offset},0) coordinate ({anchor});")
            start = anchor
        else:
            start = base
        lines.append(f"\\draw ({start}) to[{kind}{label_attr}] ++(0,-2.5) node[ground]{{}};")

    # Desenhar bipolos
    for comp in components:
        if comp.comp_type not in bipoles or len(comp.nodes) < 2:
            continue

        n1 = normalize_node(comp.nodes[0])
        n2 = normalize_node(comp.nodes[1])
        if (n1 == '0') ^ (n2 == '0'):
            other = n2 if n1 == '0' else n1
            if other in node_ids:
                draw_ground_bipole(comp, other)
            continue

        if n1 not in node_ids or n2 not in node_ids:
            continue

        id1 = node_ids[n1]
        id2 = node_ids[n2]
        label = _component_label(comp)
        label_attr = _label_attr(label)
        kind = comp.comp_type

        x1, y1 = coords.get(n1, (0, 0))
        x2, y2 = coords.get(n2, (0, 0))
        aligned = (x1 == x2) or (y1 == y2)
        if aligned:
            lines.append(f"\\draw ({id1}) to[{kind}{label_attr}] ({id2});")
            continue

        if abs(x2 - x1) >= abs(y2 - y1):
            bend = (x2, y1)
            lines.append(f"\\draw ({id1}) to[{kind}{label_attr}] ({bend[0]},{bend[1]}) to[short] ({id2});")
        else:
            bend = (x1, y2)
            lines.append(f"\\draw ({id1}) to[{kind}{label_attr}] ({bend[0]},{bend[1]}) to[short] ({id2});")

    # BJTs
    for comp in components:
        if comp.comp_type != 'Q' or len(comp.nodes) < 3:
            continue
        c = normalize_node(comp.nodes[0])
        b = normalize_node(comp.nodes[1])
        e = normalize_node(comp.nodes[2])
        kind = 'pnp' if 'PNP' in (comp.model or '').upper() else 'npn'
        comp_id = _safe_id(comp.name)

        pins = [n for n in (c, b, e) if n in coords]
        if not pins:
            continue
        cx = sum(coords[n][0] for n in pins) / len(pins)
        cy = sum(coords[n][1] for n in pins) / len(pins)

        lines.append(f"\\node[{kind}] ({comp_id}) at ({cx},{cy}) {{}};")
        if c in node_ids:
            lines.append(f"\\draw ({comp_id}.C) -- ({node_ids[c]});")
        if b in node_ids:
            lines.append(f"\\draw ({comp_id}.B) -- ({node_ids[b]});")
        if e in node_ids:
            lines.append(f"\\draw ({comp_id}.E) -- ({node_ids[e]});")
        elif e == '0':
            lines.append(f"\\draw ({comp_id}.E) -- ++(0,-2) node[ground]{{}};")

    # MOSFETs
    for comp in components:
        if comp.comp_type != 'M' or len(comp.nodes) < 3:
            continue
        d = normalize_node(comp.nodes[0])
        g = normalize_node(comp.nodes[1])
        s = normalize_node(comp.nodes[2])
        is_p = 'PMOS' in (comp.model or '').upper()
        kind = 'pfet' if is_p else 'nfet'
        comp_id = _safe_id(comp.name)

        pins = [n for n in (d, g, s) if n in coords]
        if not pins:
            continue
        cx = sum(coords[n][0] for n in pins) / len(pins)
        cy = sum(coords[n][1] for n in pins) / len(pins)

        lines.append(f"\\node[{kind}] ({comp_id}) at ({cx},{cy}) {{}};")
        if d in node_ids:
            lines.append(f"\\draw ({comp_id}.D) -- ({node_ids[d]});")
        if g in node_ids:
            lines.append(f"\\draw ({comp_id}.G) -- ({node_ids[g]});")
        if s in node_ids:
            lines.append(f"\\draw ({comp_id}.S) -- ({node_ids[s]});")
        elif s == '0':
            lines.append(f"\\draw ({comp_id}.S) -- ++(0,-2) node[ground]{{}};")

    # JFETs
    for comp in components:
        if comp.comp_type != 'J' or len(comp.nodes) < 3:
            continue
        d = normalize_node(comp.nodes[0])
        g = normalize_node(comp.nodes[1])
        s = normalize_node(comp.nodes[2])
        is_p = 'PJF' in (comp.model or '').upper()
        kind = 'pjfet' if is_p else 'njfet'
        comp_id = _safe_id(comp.name)

        pins = [n for n in (d, g, s) if n in coords]
        if not pins:
            continue
        cx = sum(coords[n][0] for n in pins) / len(pins)
        cy = sum(coords[n][1] for n in pins) / len(pins)

        lines.append(f"\\node[{kind}] ({comp_id}) at ({cx},{cy}) {{}};")
        if d in node_ids:
            lines.append(f"\\draw ({comp_id}.D) -- ({node_ids[d]});")
        if g in node_ids:
            lines.append(f"\\draw ({comp_id}.G) -- ({node_ids[g]});")
        if s in node_ids:
            lines.append(f"\\draw ({comp_id}.S) -- ({node_ids[s]});")
        elif s == '0':
            lines.append(f"\\draw ({comp_id}.S) -- ++(0,-2) node[ground]{{}};")

    lines.append("\\end{circuitikz}")
    return "\n".join(lines)


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

    ax.text(0.02, 0.02, f"Componentes: {len(components)}\n(Use LaTeX+circuitikz para esquematicos melhores)",
           transform=ax.transAxes, fontsize=8, va='bottom',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    return output_path


def create_schematic(components, title, output_path):
    """Cria esquematico usando circuitikz (LaTeX) ou fallback matplotlib."""
    result = create_schematic_circuitikz(components, title, output_path)
    if result:
        return result
    return create_schematic_matplotlib(components, title, output_path)


def run_cmd(cmd, cwd):
    proc = subprocess.run(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def create_schematic_circuitikz(components, title, output_path):
    """Gera circuito usando circuitikz + pdflatex."""
    if not components:
        return None

    if _is_simple_voltage_fan(components):
        tex_body = _circuitikz_simple_fan(components, title)
    else:
        tex_body = _circuitikz_generic(components, title)

    if not tex_body:
        return None

    output_path = Path(output_path)
    pdf_dir = Path(tempfile.mkdtemp(prefix="ckt_", dir=Path.cwd()))
    tex_path = pdf_dir / "circuit.tex"
    pdf_path = pdf_dir / "circuit.pdf"

    tex_content = r"""\documentclass[tikz,border=2pt]{standalone}
\usepackage[siunitx]{circuitikz}
\begin{document}
%s
\end{document}
""" % tex_body

    tex_path.write_text(tex_content)

    code, out, err = run_cmd("pdflatex -interaction=nonstopmode -halt-on-error circuit.tex", cwd=pdf_dir)
    if code != 0 or not pdf_path.exists():
        return None

    # Converter para PNG
    code, out, err = run_cmd(f"pdftocairo -png -singlefile circuit.pdf {pdf_path.with_suffix('').as_posix()}", cwd=pdf_dir)
    if code != 0:
        return None

    png_generated = pdf_path.with_suffix('.png')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    png_generated.replace(output_path)
    return str(output_path)


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

Requer LaTeX com circuitikz:
  macOS: brew install --cask mactex
  Ubuntu: sudo apt install texlive-pictures texlive-latex-extra
        """
    )

    parser.add_argument('input', help='Arquivo SPICE ou diretorio')
    parser.add_argument('-o', '--output', help='Arquivo de saida PNG')
    parser.add_argument('-v', '--verbose', action='store_true', help='Modo verbose')
    parser.add_argument('--netlist', action='store_true', help='Mostrar netlist interno gerado')

    args = parser.parse_args()

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
                netlist = create_netlist(components, title)
                print(f"\nNetlist interno:\n{netlist}\n")

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
