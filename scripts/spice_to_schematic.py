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
    subckt_key = instance.subckt.upper()
    if subckt_key not in subckt_defs:
        return []

    sub = subckt_defs[subckt_key]
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


def _strip_inline_comment(line):
    """Remove comentarios inline usando ; ou $."""
    if not line:
        return line
    indices = []
    for marker in (';', '$'):
        idx = line.find(marker)
        if idx != -1:
            indices.append(idx)
    if indices:
        line = line[:min(indices)]
    return line.strip()


def _split_subckt_pins(tokens):
    """Separa lista de pinos ignorando parametros."""
    pins = []
    for tok in tokens:
        upper = tok.upper()
        if upper.startswith('PARAMS') or '=' in tok:
            break
        pins.append(tok)
    return pins


def _split_subckt_instance(tokens):
    """Separa nos e nome do subcircuito em uma instancia X."""
    params_start = len(tokens)
    for idx, tok in enumerate(tokens):
        upper = tok.upper()
        if upper.startswith('PARAMS') or '=' in tok:
            params_start = idx
            break
    if params_start == 0:
        return [], ""
    subckt_name = tokens[params_start - 1]
    node_list = tokens[:params_start - 1]
    return node_list, subckt_name


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
        if line.lstrip().startswith('+'):
            cont = _strip_inline_comment(line.lstrip()[1:]).strip()
            if not cont:
                continue
            if current_line:
                current_line += ' ' + cont
            else:
                current_line = cont
        else:
            if current_line:
                joined_lines.append(current_line)
            cleaned = _strip_inline_comment(line)
            if not cleaned or cleaned.lstrip().startswith('*'):
                current_line = ""
                continue
            current_line = cleaned
    if current_line:
        joined_lines.append(current_line)

    for line in joined_lines:
        line = line.strip()

        if not line or line.startswith('*'):
            continue

        if not line:
            continue

        line_upper = line.upper()

        if line_upper.startswith('.CONTROL'):
            in_control = True
            continue
        if line_upper.startswith('.ENDC'):
            in_control = False
            continue

        if in_control:
            continue

        if line_upper.startswith('.SUBCKT'):
            parts = line.split()
            if len(parts) >= 2:
                name = parts[1].upper()
                pins = _split_subckt_pins(parts[2:])
                subckt_defs[name] = SubcircuitDefinition(name, pins)
                current_subckt = name
            continue
        if line_upper.startswith('.ENDS'):
            current_subckt = None
            continue

        if line.startswith('.') or current_subckt is not None and line_upper.startswith('.ENDS'):
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
                node_list, subckt_name = _split_subckt_instance(parts[1:])
                if not subckt_name:
                    continue
                inst = SubcircuitInstance(name, subckt_name.upper(), node_list)
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


def _label_attr_for(comp, value_only=False):
    """Gera atributos de label para componentes circuitikz.

    Args:
        comp: Componente
        value_only: Se True, mostra apenas o valor (útil para evitar sobreposição)
    """
    name = comp.name or ""
    value = comp.value or comp.model or ""
    name_safe = str(name).replace('_', '\\_')
    value_safe = str(value).replace('_', '\\_')

    if value_only and value:
        return f",l=${value_safe}$"
    if name and value:
        return f",l=${name_safe}$,l_=${value_safe}$"
    if name:
        return f",l=${name_safe}$"
    return ""


def _collect_supply_nodes(components):
    supply_nodes = set()
    for comp in components:
        if comp.comp_type != 'V' or len(comp.nodes) < 2:
            continue
        n1 = normalize_node(comp.nodes[0])
        n2 = normalize_node(comp.nodes[1])
        if n1 == '0' and n2 != '0':
            supply_nodes.add(n2)
        elif n2 == '0' and n1 != '0':
            supply_nodes.add(n1)
    return supply_nodes


def _build_adj_for_types(components, group, types):
    adj = defaultdict(set)
    for comp in components:
        if comp.comp_type not in types or len(comp.nodes) < 2:
            continue
        n1 = normalize_node(comp.nodes[0])
        n2 = normalize_node(comp.nodes[1])
        if n1 == '0' or n2 == '0':
            continue
        if n1 in group and n2 in group:
            adj[n1].add(n2)
            adj[n2].add(n1)
    return adj


def _connected_components(adj):
    comps = []
    visited = set()
    for node in adj:
        if node in visited:
            continue
        stack = [node]
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
        comps.append(group)
    return comps


def _edge_count(adj, nodes):
    count = 0
    for n in nodes:
        for m in adj.get(n, []):
            if m in nodes:
                count += 1
    return count // 2


def _transistor_pins(comp):
    if comp.comp_type == 'Q' and len(comp.nodes) >= 3:
        return {
            'collector': normalize_node(comp.nodes[0]),
            'base': normalize_node(comp.nodes[1]),
            'emitter': normalize_node(comp.nodes[2]),
        }
    if comp.comp_type in ('M', 'J') and len(comp.nodes) >= 3:
        return {
            'drain': normalize_node(comp.nodes[0]),
            'gate': normalize_node(comp.nodes[1]),
            'source': normalize_node(comp.nodes[2]),
        }
    return {}


def _find_tank_nodes(group, components, main_pins, control_pin):
    reactive_adj = _build_adj_for_types(components, group, ('L', 'C'))
    if not reactive_adj:
        return set()
    comps = _connected_components(reactive_adj)
    best = set()
    best_score = (-1, -1, -1)
    for comp_nodes in comps:
        if not (comp_nodes & (main_pins | {control_pin})):
            continue
        edge_count = _edge_count(reactive_adj, comp_nodes)
        pin_priority = 2 if comp_nodes & main_pins else 1
        score = (edge_count, pin_priority, len(comp_nodes))
        if score > best_score:
            best_score = score
            best = comp_nodes
    return best


def _find_bias_nodes(group, components, control_pin, block_nodes):
    bias_adj = _build_adj_for_types(components, group, ('R', 'C'))
    if control_pin not in bias_adj:
        return set()
    visited = {control_pin}
    stack = [control_pin]
    while stack:
        cur = stack.pop()
        for nxt in bias_adj.get(cur, []):
            if nxt in visited or nxt in block_nodes:
                continue
            visited.add(nxt)
            stack.append(nxt)
    visited.discard(control_pin)
    return visited


def _layout_cluster_nodes(nodes, adj, ref_node, origin, x_step, y_step, x_dir=1):
    if not nodes:
        return {}
    ref = ref_node if ref_node in nodes else next(iter(nodes))
    level = {ref: 0}
    queue = [ref]
    while queue:
        cur = queue.pop(0)
        for nxt in adj.get(cur, []):
            if nxt in nodes and nxt not in level:
                level[nxt] = level[cur] + 1
                queue.append(nxt)
    max_level = max(level.values()) if level else 0
    for n in nodes:
        if n not in level:
            max_level += 1
            level[n] = max_level
    by_level = defaultdict(list)
    for n, lvl in level.items():
        if n in nodes:
            by_level[lvl].append(n)
    coords = {}
    for lvl in sorted(by_level.keys()):
        group_nodes = sorted(by_level[lvl])
        total = len(group_nodes)
        for i, n in enumerate(group_nodes):
            x = origin[0] + x_dir * lvl * x_step
            y = origin[1] + (i - (total - 1) / 2) * y_step
            coords[n] = (x, y)
    return coords


def _group_layout_params(group, group_components):
    node_count = len(group)
    reactive_count = sum(1 for comp in group_components if comp.comp_type in ('L', 'C'))
    bjt_count = sum(1 for comp in group_components if comp.comp_type == 'Q')
    mos_count = sum(1 for comp in group_components if comp.comp_type == 'M')
    jfet_count = sum(1 for comp in group_components if comp.comp_type == 'J')
    transistor_count = bjt_count + mos_count + jfet_count
    has_inductor = any(comp.comp_type == 'L' for comp in group_components)
    cap_shunt_only = True
    for comp in group_components:
        if comp.comp_type != 'C' or len(comp.nodes) < 2:
            continue
        n1 = normalize_node(comp.nodes[0])
        n2 = normalize_node(comp.nodes[1])
        if n1 != '0' and n2 != '0':
            cap_shunt_only = False
            break

    scale = 1.0
    if node_count >= 10:
        scale += 0.2
    if reactive_count >= 6:
        scale += 0.2
    if transistor_count >= 2:
        scale += 0.25
    scale = min(scale, 1.6)

    level_max_nodes = None
    logic_like = mos_count >= 6 and not has_inductor and cap_shunt_only
    if logic_like:
        level_max_nodes = 4
        scale = max(scale, 1.15)
    return scale, level_max_nodes


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


def _is_simple_current_divider(components):
    """Detecta múltiplas fontes de corrente + resistores em paralelo."""
    current_sources = [c for c in components if c.comp_type == 'I']
    if len(current_sources) == 0:
        return False
    # Verificar se há pelo menos resistores
    resistors = [c for c in components if c.comp_type == 'R']
    if len(resistors) == 0:
        return False
    # Aceitar I, R, V (para VCC opcional), D (para LEDs opcionais)
    allowed = {'I', 'R', 'V', 'D'}
    if any(c.comp_type not in allowed for c in components):
        return False
    # Verificar que há pelo menos uma fonte de corrente conectada entre 0 e outro nó
    has_valid_i = False
    for i_src in current_sources:
        n1, n2 = normalize_node(i_src.nodes[0]), normalize_node(i_src.nodes[1])
        if '0' in (n1, n2):
            has_valid_i = True
            break
    return has_valid_i


def _extract_current_divider_groups(components):
    """Extrai grupos de fontes de corrente com seus resistores em paralelo.

    Retorna lista de grupos, cada grupo é:
    (current_source, hub_node, parallel_components)
    onde parallel_components são componentes (R ou D+R) conectados de hub para ground.
    """
    current_sources = [c for c in components if c.comp_type == 'I']
    groups = []

    for i_src in current_sources:
        n1, n2 = normalize_node(i_src.nodes[0]), normalize_node(i_src.nodes[1])
        if n1 == '0':
            hub = n2
        elif n2 == '0':
            hub = n1
        else:
            continue  # Fonte não conectada a ground

        # Encontrar componentes paralelos: R ou D entre hub e ground
        parallel = []
        for comp in components:
            if comp.name == i_src.name:
                continue
            if comp.comp_type in ('R', 'D'):
                cn1, cn2 = normalize_node(comp.nodes[0]), normalize_node(comp.nodes[1])
                # Resistor direto hub-ground
                if comp.comp_type == 'R' and set([cn1, cn2]) == set([hub, '0']):
                    parallel.append([comp])
                # Diodo que conecta hub a um nó intermediário
                elif comp.comp_type == 'D' and hub in (cn1, cn2):
                    other = cn2 if cn1 == hub else cn1
                    # Procurar resistor desse nó intermediário para ground
                    for r in components:
                        if r.comp_type == 'R':
                            rn1, rn2 = normalize_node(r.nodes[0]), normalize_node(r.nodes[1])
                            if set([rn1, rn2]) == set([other, '0']):
                                parallel.append([comp, r])
                                break

        if parallel:
            groups.append((i_src, hub, parallel))

    return groups

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
    """Gera codigo circuitikz para divisores de tensao em serie."""
    hub, gnd, vval, branches = _extract_fan_branches(components)
    v = next(c for c in components if c.comp_type == 'V')

    lines = []
    lines.append("\\begin{circuitikz}[american voltages]")

    # MELHORADO: Layout compacto para múltiplos divisores
    # Se há múltiplos ramos (divisores), colocá-los lado a lado
    n_branches = len(branches)

    if n_branches <= 2:
        # Layout tradicional em fan para 1-2 ramos
        lines.append("\\coordinate (hub) at (0,0);")
        lines.append("\\coordinate (gnd) at (0,-3);")
        v_label = _label_attr_for(v)
        lines.append(f"\\draw (hub) to[V{v_label}, invert] (gnd);")

        dir_vectors = [(3, 0), (-3, 0)]  # Apenas direita e esquerda
        for idx, (chain, end_node) in enumerate(branches):
            dx, dy = dir_vectors[idx % len(dir_vectors)]
            start = f"b{idx}_0"
            lines.append(f"\\draw (hub) to[short] ++({dx},{dy}) coordinate ({start});")
            current = start
            for j, r in enumerate(chain):
                is_last = (j == len(chain) - 1)
                end_norm = normalize_node(end_node)
                label_attr = _label_attr_for(r)
                step_x, step_y = (2 if dx > 0 else -2), 0

                if is_last and end_norm == '0':
                    lines.append(f"\\draw ({current}) to[R{label_attr}] ++({step_x},{step_y}) to[short] ++(0,-2) node[ground]{{}};")
                else:
                    nxt = f"b{idx}_{j+1}"
                    lines.append(f"\\draw ({current}) to[R{label_attr}] ++({step_x},{step_y}) coordinate ({nxt});")
                    current = nxt
    else:
        # Layout em colunas para 3+ divisores (mais compacto)
        spacing = 5
        start_x = -(n_branches - 1) * spacing / 2

        # Fonte centralizada
        lines.append(f"\\coordinate (vcc) at (0,0);")
        lines.append(f"\\coordinate (gnd) at (0,-8);")
        v_label = _label_attr_for(v)
        lines.append(f"\\draw (vcc) to[V{v_label}, invert] (gnd);")

        # Barra de VCC
        left_x = start_x - 1
        right_x = start_x + (n_branches - 1) * spacing + 1
        lines.append(f"\\draw ({left_x},0) -- ({right_x},0);")

        # Cada divisor em uma coluna
        for idx, (chain, end_node) in enumerate(branches):
            x_pos = start_x + idx * spacing
            lines.append(f"\\coordinate (div{idx}_top) at ({x_pos},0);")

            current = f"div{idx}_top"
            y_offset = 0
            for j, r in enumerate(chain):
                is_last = (j == len(chain) - 1)
                end_norm = normalize_node(end_node)
                label_attr = _label_attr_for(r)

                if is_last and end_norm == '0':
                    lines.append(f"\\draw ({current}) to[R{label_attr}] ++(0,-2.5) node[ground]{{}};")
                else:
                    nxt = f"div{idx}_{j+1}"
                    lines.append(f"\\draw ({current}) to[R{label_attr}] ++(0,-2.5) coordinate ({nxt});")
                    current = nxt

    lines.append("\\end{circuitikz}")
    return "\n".join(lines)


def _circuitikz_current_divider(components, title):
    """Gera código circuitikz para divisores de corrente com layout compacto."""
    groups = _extract_current_divider_groups(components)
    if not groups:
        return None

    lines = []
    lines.append("\\begin{circuitikz}[american voltages]")

    # Layout compacto: colocar grupos lado a lado
    n_groups = len(groups)
    spacing = 8  # Aumentado de 6 para evitar sobreposição
    start_x = -(n_groups - 1) * spacing / 2

    # Barra de ground (comum a todos os grupos) - com margens maiores
    left_x = start_x - 3.5  # Aumentado de 2 para 3.5
    right_x = start_x + (n_groups - 1) * spacing + 3.5  # Aumentado de 2 para 3.5
    lines.append(f"\\draw ({left_x},-6) -- ({right_x},-6);")

    # Desenhar cada grupo (fonte de corrente + resistores paralelos)
    for group_idx, (i_src, hub, parallel_comps) in enumerate(groups):
        x_pos = start_x + group_idx * spacing

        # Resistores/diodos em paralelo de hub para ground
        n_parallel = len(parallel_comps)
        if n_parallel == 1:
            # Apenas um resistor: colocar ao lado da fonte
            branch = parallel_comps[0]
            # Fonte à esquerda, resistor à direita com mais espaçamento
            i_label = _label_attr_for(i_src, value_only=True)
            lines.append(f"\\coordinate (grp{group_idx}_gnd) at ({x_pos - 1.8},-6);")
            lines.append(f"\\coordinate (grp{group_idx}_hub) at ({x_pos - 1.8},0);")
            lines.append(f"\\draw (grp{group_idx}_gnd) to[I{i_label}] (grp{group_idx}_hub);")

            if len(branch) == 1:
                # Resistor com mais distância
                r_label = _label_attr_for(branch[0])
                lines.append(f"\\coordinate (r{group_idx}) at ({x_pos + 1.8},0);")
                lines.append(f"\\draw (grp{group_idx}_hub) to[short] (r{group_idx});")
                lines.append(f"\\draw (r{group_idx}) to[R{r_label}] ++(0,-6) -- ({x_pos + 1.8},-6);")
            else:
                # Diodo + resistor
                d_label = _label_attr_for(branch[0])
                r_label = _label_attr_for(branch[1])
                lines.append(f"\\coordinate (r{group_idx}) at ({x_pos + 1.8},0);")
                lines.append(f"\\draw (grp{group_idx}_hub) to[short] (r{group_idx});")
                lines.append(f"\\draw (r{group_idx}) to[D{d_label}] ++(0,-2) coordinate (tmp);")
                lines.append(f"\\draw (tmp) to[R{r_label}] ++(0,-4) -- ({x_pos + 1.8},-6);")
        else:
            # Múltiplos resistores: todos à DIREITA da fonte (não no centro)
            # Fonte à esquerda
            lines.append(f"\\coordinate (grp{group_idx}_gnd) at ({x_pos - 2.5},-6);")
            lines.append(f"\\coordinate (grp{group_idx}_hub) at ({x_pos - 2.5},0);")
            i_label = _label_attr_for(i_src, value_only=True)
            lines.append(f"\\draw (grp{group_idx}_gnd) to[I{i_label}] (grp{group_idx}_hub);")

            # Distribuir resistores à direita da fonte
            par_spacing = 2.5
            par_start_x = x_pos - (n_parallel - 1) * par_spacing / 2

            # Barra horizontal conectando fonte aos resistores
            bar_left = x_pos - 2.5  # posição da fonte
            bar_right = par_start_x + (n_parallel - 1) * par_spacing + 0.5
            lines.append(f"\\draw ({bar_left},0) -- ({bar_right},0);")

            for par_idx, branch in enumerate(parallel_comps):
                par_x = par_start_x + par_idx * par_spacing
                lines.append(f"\\coordinate (par{group_idx}_{par_idx}) at ({par_x},0);")

                if len(branch) == 1:
                    # Apenas resistor
                    r_label = _label_attr_for(branch[0])
                    lines.append(f"\\draw (par{group_idx}_{par_idx}) to[R{r_label}] ++(0,-6) -- ({par_x},-6);")
                else:
                    # Diodo + resistor
                    d_label = _label_attr_for(branch[0])
                    r_label = _label_attr_for(branch[1])
                    lines.append(f"\\draw (par{group_idx}_{par_idx}) to[D{d_label}] ++(0,-2) coordinate (tmp{group_idx}_{par_idx});")
                    lines.append(f"\\draw (tmp{group_idx}_{par_idx}) to[R{r_label}] ++(0,-4) -- ({par_x},-6);")

    # Adicionar símbolos de ground na barra
    for group_idx in range(n_groups):
        x_pos = start_x + group_idx * spacing
        lines.append(f"\\draw ({x_pos},-6) node[ground]{{}};")

    lines.append("\\end{circuitikz}")
    return "\n".join(lines)


def _circuitikz_generic(components, title):
    """Gera circuito circuitikz com layout hierarquico."""
    bipoles = {'R', 'C', 'L', 'V', 'I', 'D'}
    # Espaçamento reduzido para circuitos mais compactos
    dx, dy = 7, 4.5  # Reduzido de 10,6 para tornar schematics menores
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

    def layout_group(group, fixed=None, scale=1.0, level_max_nodes=None):
        fixed = fixed or {}
        local_dx = dx * scale
        local_dy = dy * scale

        # MELHORADO: Atribuição hierárquica de camadas (VCC -> componentes -> GND)
        level = {}

        # Identificar nós de supply (conectados a VCC via fonte)
        supply_in_group = set(supply_nodes) & group

        # Estratégia hierárquica: começar de nós fixed ou supply nodes
        if fixed:
            # Se há nós fixos, usá-los como raiz
            for n in fixed:
                if n in group:
                    level[n] = 0
        elif supply_in_group:
            # Começar dos nós de alimentação (topo da hierarquia)
            for n in supply_in_group:
                level[n] = 0
        else:
            # Fallback: escolher nó de referência
            ref = choose_ref(group)
            level[ref] = 0

        # BFS para atribuir camadas
        queue = list(level.keys())
        while queue:
            cur = queue.pop(0)
            for nxt in adj[cur]:
                if nxt in group and nxt not in level:
                    level[nxt] = level[cur] + 1
                    queue.append(nxt)

        # Nós não alcançados
        max_level = max(level.values()) if level else 0
        for n in group:
            if n not in level:
                max_level += 1
                level[n] = max_level

        # Agrupar nós por camada
        by_level = defaultdict(list)
        for n, lvl in level.items():
            by_level[lvl].append(n)

        order = {}
        for lvl, group_nodes in by_level.items():
            order[lvl] = sorted(group_nodes)

        # MELHORADO: Crossing reduction com mais iterações (barycenter heuristic)
        max_lvl = max(order.keys()) if order else 0
        for iteration in range(5):  # Aumentado de 2 para 5 iterações
            # Forward pass: ordenar baseado em camada anterior
            for lvl in range(1, max_lvl + 1):
                prev = order.get(lvl - 1, [])
                prev_idx = {n: i for i, n in enumerate(prev)}

                def key_prev(n):
                    indices = [prev_idx[p] for p in adj[n] if p in prev_idx]
                    if not indices:
                        return len(prev) / 2
                    # Barycenter: média das posições dos vizinhos
                    return sum(indices) / len(indices)

                order[lvl].sort(key=key_prev)

            # Backward pass: ordenar baseado em camada seguinte
            for lvl in range(max_lvl - 1, -1, -1):
                nxt = order.get(lvl + 1, [])
                nxt_idx = {n: i for i, n in enumerate(nxt)}

                def key_next(n):
                    indices = [nxt_idx[p] for p in adj[n] if p in nxt_idx]
                    if not indices:
                        return len(nxt) / 2
                    return sum(indices) / len(indices)

                order[lvl].sort(key=key_next)

        if level_max_nodes:
            new_order = {}
            new_lvl = 0
            for lvl in sorted(order.keys()):
                nodes_in_level = order[lvl]
                for start in range(0, len(nodes_in_level), level_max_nodes):
                    new_order[new_lvl] = nodes_in_level[start:start + level_max_nodes]
                    new_lvl += 1
            order = new_order

        coords_local = {}
        for lvl in sorted(order.keys()):
            group_nodes = order[lvl]
            total = len(group_nodes)
            for i, n in enumerate(group_nodes):
                y = (i - (total - 1) / 2) * local_dy
                x = lvl * local_dx
                coords_local[n] = (x, y)

        if fixed:
            ref_node = next(iter(fixed.keys()), None)
            if ref_node in coords_local:
                dx_shift = fixed[ref_node][0] - coords_local[ref_node][0]
                dy_shift = fixed[ref_node][1] - coords_local[ref_node][1]
                for n in coords_local:
                    x, y = coords_local[n]
                    coords_local[n] = (x + dx_shift, y + dy_shift)
            for n, (fx, fy) in fixed.items():
                if n in coords_local:
                    coords_local[n] = (fx, fy)
        return coords_local

    # Posicionar grupos em grade
    coords = {}
    cursor_x = 0
    cursor_y = 0
    row_height = 0
    max_row_width = 60
    margin = 6
    group_padding_x = 8
    group_padding_y = 4
    group_frame_x = 6
    group_frame_y = 4

    supply_nodes = _collect_supply_nodes(components)

    def fixed_for_group(group, group_components, scale):
        transistors = []
        for comp in group_components:
            if comp.comp_type not in ('Q', 'M', 'J'):
                continue
            nodes_list = [normalize_node(n) for n in comp.nodes[:3]]
            if any(n in group for n in nodes_list):
                transistors.append(comp)
        if len(transistors) != 1:
            return {}

        t = transistors[0]
        pins = _transistor_pins(t)
        if not pins:
            return {}

        pin_dx = 8 * scale
        pin_dy = 6 * scale
        fixed = {}
        if t.comp_type == 'Q':
            control = pins['base']
            main_pins = {pins['collector'], pins['emitter']}
            fixed[control] = (-pin_dx, 0)
            fixed[pins['collector']] = (0, pin_dy)
            fixed[pins['emitter']] = (0, -pin_dy)
        else:
            control = pins['gate']
            main_pins = {pins['drain'], pins['source']}
            fixed[control] = (-pin_dx, 0)
            fixed[pins['drain']] = (0, pin_dy)
            fixed[pins['source']] = (0, -pin_dy)

        tank_nodes = _find_tank_nodes(group, group_components, main_pins, control)
        if tank_nodes:
            tank_adj = _build_adj_for_types(group_components, group, ('L', 'C'))
            tank_nodes = {n for n in tank_nodes if n not in fixed}
            origin = (pin_dx + 6 * scale, 0)
            tank_positions = _layout_cluster_nodes(
                tank_nodes,
                tank_adj,
                next(iter(main_pins)),
                origin,
                x_step=6 * scale,
                y_step=4 * scale,
                x_dir=1,
            )
            fixed.update(tank_positions)

        block_nodes = set(main_pins) | set(supply_nodes) | tank_nodes
        bias_nodes = _find_bias_nodes(group, group_components, control, block_nodes)
        if bias_nodes:
            bias_adj = _build_adj_for_types(group_components, group, ('R', 'C'))
            origin = (-pin_dx - 6 * scale, 0)
            bias_positions = _layout_cluster_nodes(
                bias_nodes,
                bias_adj,
                control,
                origin,
                x_step=5 * scale,
                y_step=3.5 * scale,
                x_dir=-1,
            )
            fixed.update(bias_positions)

        supply_in_group = sorted(n for n in supply_nodes if n in group and n not in fixed)
        for idx, node in enumerate(supply_in_group):
            fixed[node] = (idx * 4 * scale, pin_dy + 8 * scale)

        return fixed

    group_infos = []
    for group in components_nodes:
        group_components = [
            comp for comp in components
            if any(normalize_node(n) in group for n in comp.nodes[:4])
        ]
        scale, level_max_nodes = _group_layout_params(group, group_components)
        fixed = fixed_for_group(group, group_components, scale)
        local = layout_group(group, fixed, scale=scale, level_max_nodes=level_max_nodes)
        xs = [v[0] for v in local.values()]
        ys = [v[1] for v in local.values()]
        if not xs or not ys:
            continue
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        width = (maxx - minx) + 2 * (group_padding_x + group_frame_x)
        height = (maxy - miny) + 2 * (group_padding_y + group_frame_y)
        group_infos.append((group, local, minx, miny, width, height))

    n_groups = len(group_infos)
    use_columns = n_groups >= 3
    if use_columns:
        columns = 2 if n_groups <= 4 else 3
        columns = min(columns, n_groups)
        col_heights = [0] * columns
        col_groups = [[] for _ in range(columns)]

        for info in sorted(group_infos, key=lambda g: g[5], reverse=True):
            idx = min(range(columns), key=lambda i: col_heights[i])
            col_groups[idx].append(info)
            col_heights[idx] += info[5] + margin

        col_widths = [max((g[4] for g in col), default=0) for col in col_groups]
        col_x = []
        current_x = 0
        for w in col_widths:
            col_x.append(current_x)
            current_x += w + margin

        for idx, col in enumerate(col_groups):
            y_cursor = 0
            for group, local, minx, miny, width, height in col:
                for n, (x, y) in local.items():
                    coords[n] = (x - minx + col_x[idx] + group_padding_x + group_frame_x,
                                 y - miny + y_cursor + group_padding_y + group_frame_y)
                y_cursor -= (height + margin)
    else:
        for group, local, minx, miny, width, height in group_infos:
            if cursor_x + width > max_row_width and cursor_x > 0:
                cursor_x = 0
                cursor_y -= (row_height + margin)
                row_height = 0

            for n, (x, y) in local.items():
                coords[n] = (x - minx + cursor_x + group_padding_x + group_frame_x,
                             y - miny + cursor_y + group_padding_y + group_frame_y)

            cursor_x += width + margin
            row_height = max(row_height, height)

    # Garantir coordenadas positivas para evitar cortes
    if coords:
        min_x = min(x for x, _ in coords.values())
        min_y = min(y for _, y in coords.values())
        shift_x = -min_x + 2 if min_x < 0 else 0
        shift_y = -min_y + 2 if min_y < 0 else 0
        if shift_x or shift_y:
            for n in coords:
                x, y = coords[n]
                coords[n] = (x + shift_x, y + shift_y)

    # Snapping em grade para roteamento
    route_grid = 2.0
    def snap(value):
        return round(value / route_grid) * route_grid

    for n in coords:
        x, y = coords[n]
        coords[n] = (snap(x), snap(y))

    # Mapear grupos para rails locais
    group_of = {}
    for idx, group in enumerate(components_nodes):
        for n in group:
            group_of[n] = idx

    group_bounds = {}
    for idx, group in enumerate(components_nodes):
        xs = [coords[n][0] for n in group if n in coords]
        ys = [coords[n][1] for n in group if n in coords]
        if xs and ys:
            group_bounds[idx] = (min(xs), max(xs), min(ys), max(ys))

    supply_nodes_by_group = defaultdict(list)
    for comp in components:
        if comp.comp_type != 'V' or len(comp.nodes) < 2:
            continue
        n1 = normalize_node(comp.nodes[0])
        n2 = normalize_node(comp.nodes[1])
        if n1 == '0' and n2 in coords:
            supply_nodes_by_group[group_of[n2]].append(n2)
        elif n2 == '0' and n1 in coords:
            supply_nodes_by_group[group_of[n1]].append(n1)

    # MELHORADO: Detectar TODOS os componentes conectados a ground
    has_ground_by_group = defaultdict(bool)
    for comp in components:
        # Bipolos (R, C, L, V, I, D) com pelo menos 1 nó em ground
        if comp.comp_type in bipoles and len(comp.nodes) >= 2:
            n1 = normalize_node(comp.nodes[0])
            n2 = normalize_node(comp.nodes[1])
            if (n1 == '0') ^ (n2 == '0'):
                other = n2 if n1 == '0' else n1
                if other in coords:
                    has_ground_by_group[group_of[other]] = True
        # Transistores com emitter/source em ground
        elif comp.comp_type in ('Q', 'M', 'J') and len(comp.nodes) >= 3:
            if normalize_node(comp.nodes[2]) == '0':
                for n in comp.nodes[:3]:
                    nn = normalize_node(n)
                    if nn in coords:
                        has_ground_by_group[group_of[nn]] = True
                        break

    lines = []
    lines.append("\\begin{circuitikz}[american voltages]")
    for n, (x, y) in coords.items():
        lines.append(f"\\coordinate ({node_ids[n]}) at ({x},{y});")

    # Barramentos locais de VCC e GND
    gnd_bus_name = {}
    gnd_y_by_group = {}
    for idx, bounds in group_bounds.items():
        min_x, max_x, min_y, max_y = bounds
        if supply_nodes_by_group.get(idx):
            top_y = max_y + 6
            rail_left = min_x - 4
            rail_right = max_x + 4
            lines.append(f"\\coordinate (vccbusL_g{idx}) at ({rail_left},{top_y});")
            lines.append(f"\\coordinate (vccbusR_g{idx}) at ({rail_right},{top_y});")
            lines.append(f"\\draw (vccbusL_g{idx}) -- (vccbusR_g{idx});")
            for node in sorted(set(supply_nodes_by_group[idx])):
                nid = node_ids.get(node)
                if nid:
                    lines.append(f"\\draw ({nid}) -- ({nid} |- vccbusL_g{idx});")

        if has_ground_by_group.get(idx):
            ground_y = min_y - 6
            gnd_left = min_x - 4
            gnd_right = max_x + 4
            lines.append(f"\\coordinate (gndbusL_g{idx}) at ({gnd_left},{ground_y});")
            lines.append(f"\\coordinate (gndbusR_g{idx}) at ({gnd_right},{ground_y});")
            lines.append(f"\\draw (gndbusL_g{idx}) -- (gndbusR_g{idx});")
            lines.append(f"\\node[ground] at (gndbusL_g{idx}) {{}};")
            gnd_bus_name[idx] = f"gndbusL_g{idx}"
            gnd_y_by_group[idx] = ground_y

    degrees = {n: len(adj[n]) for n in nodes}

    # Offsets para componentes paralelos entre dois nos
    edge_groups = defaultdict(list)
    for comp in components:
        if comp.comp_type not in bipoles or len(comp.nodes) < 2:
            continue
        n1 = normalize_node(comp.nodes[0])
        n2 = normalize_node(comp.nodes[1])
        if n1 == '0' or n2 == '0':
            continue
        key = tuple(sorted([n1, n2]))
        edge_groups[key].append(comp)

    edge_offsets = {}
    parallel_spacing = 2.0
    for key, comps in edge_groups.items():
        total = len(comps)
        if total <= 1:
            continue
        start = -(total - 1) / 2
        for idx, comp in enumerate(comps):
            edge_offsets[comp.name] = (start + idx) * parallel_spacing

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

    # Barramento para muitos shunts no mesmo no
    bus_nodes = {node: comps for node, comps in ground_groups.items() if len(comps) >= 2}
    bus_positions = {}
    bus_gap = 3
    bus_spacing = 4
    bus_lines = []

    for node, comps in bus_nodes.items():
        node_x, node_y = coords[node]
        group_id = group_of.get(node)
        group_ground = gnd_y_by_group.get(group_id, node_y - 6)
        bus_y = max(node_y - bus_gap, group_ground + 2)
        bus_y = snap(bus_y)
        total = len(comps)
        start = -(total - 1) / 2
        xs = []
        for idx, comp in enumerate(sorted(comps, key=lambda c: c.name)):
            x = snap(node_x + (start + idx) * bus_spacing)
            xs.append(x)
            bus_positions[comp.name] = (x, bus_y)
        if xs:
            x_min, x_max = min(xs), max(xs)
            bus_lines.append((x_min, bus_y, x_max, bus_y))
            mid = (x_min + x_max) / 2
            drop_x = x_min if node_x <= mid else x_max
            if drop_x != node_x:
                bus_lines.append((node_x, node_y, drop_x, node_y))
            bus_lines.append((drop_x, node_y, drop_x, bus_y))

    ground_offsets = {}
    ground_spacing = 2.5
    for node, comps in ground_groups.items():
        if node in bus_nodes:
            continue
        total = len(comps)
        start = -(total - 1) / 2
        for idx, comp in enumerate(comps):
            ground_offsets[comp.name] = (start + idx) * ground_spacing

    # Desenhar barramentos de shunt
    for x1, y1, x2, y2 in bus_lines:
        lines.append(f"\\draw ({x1},{y1}) -- ({x2},{y2});")

    node_positions = {n: coords[n] for n in coords}
    bus_segments = list(bus_lines)
    bend_offset = route_grid

    # Mapear componentes bipolares para detectar cruzamentos
    component_segments = []
    for comp in components:
        if comp.comp_type not in bipoles or len(comp.nodes) < 2:
            continue
        n1 = normalize_node(comp.nodes[0])
        n2 = normalize_node(comp.nodes[1])
        # Ignorar componentes conectados a ground (sao verticais)
        if n1 == '0' or n2 == '0':
            continue
        if n1 in coords and n2 in coords:
            x1, y1 = coords[n1]
            x2, y2 = coords[n2]
            component_segments.append((x1, y1, x2, y2, comp.name))

    # DEBUG: Imprimir componentes mapeados
    if False:  # Ativar para debug
        print(f"DEBUG: {len(component_segments)} componentes mapeados para deteccao")
        for x1, y1, x2, y2, name in component_segments[:5]:
            print(f"  {name}: ({x1},{y1}) -> ({x2},{y2})")

    def segment_hits_nodes(x1, y1, x2, y2, ignore):
        hits = 0
        if x1 == x2:
            ymin, ymax = sorted([y1, y2])
            for node, (nx, ny) in node_positions.items():
                if node in ignore:
                    continue
                if abs(nx - x1) < 0.01 and ymin < ny < ymax:
                    hits += 1
        elif y1 == y2:
            xmin, xmax = sorted([x1, x2])
            for node, (nx, ny) in node_positions.items():
                if node in ignore:
                    continue
                if abs(ny - y1) < 0.01 and xmin < nx < xmax:
                    hits += 1
        return hits

    def segment_hits_components(x1, y1, x2, y2, ignore_comps=set()):
        """Detecta se um segmento cruza sobre componentes bipolares."""
        hits = 0

        if abs(x1 - x2) < 0.01 and abs(y1 - y2) < 0.01:
            return hits

        for cx1, cy1, cx2, cy2, cname in component_segments:
            if cname in ignore_comps:
                continue

            # Normalizar coordenadas dos segmentos
            sx1, sy1, sx2, sy2 = x1, y1, x2, y2

            # Segmento de teste é vertical (x constante)
            if abs(sx1 - sx2) < 0.1:
                x_seg = sx1
                y_seg_min, y_seg_max = sorted([sy1, sy2])

                # Componente é horizontal (y constante)
                if abs(cy1 - cy2) < 0.1:
                    x_comp_min, x_comp_max = sorted([cx1, cx2])
                    y_comp = cy1

                    # Verificar cruzamento: segmento vertical passa por y_comp
                    # e componente horizontal passa por x_seg
                    if (x_comp_min - route_grid) < x_seg < (x_comp_max + route_grid):
                        if (y_seg_min - route_grid) < y_comp < (y_seg_max + route_grid):
                            hits += 10  # Penalidade MUITO alta para cruzamento direto

            # Segmento de teste é horizontal (y constante)
            elif abs(sy1 - sy2) < 0.1:
                y_seg = sy1
                x_seg_min, x_seg_max = sorted([sx1, sx2])

                # Componente é vertical (x constante)
                if abs(cx1 - cx2) < 0.1:
                    y_comp_min, y_comp_max = sorted([cy1, cy2])
                    x_comp = cx1

                    # Verificar cruzamento: segmento horizontal passa por x_comp
                    # e componente vertical passa por y_seg
                    if (y_comp_min - route_grid) < y_seg < (y_comp_max + route_grid):
                        if (x_seg_min - route_grid) < x_comp < (x_seg_max + route_grid):
                            hits += 10  # Penalidade MUITO alta para cruzamento direto

        return hits

    def segment_hits_bus(x1, y1, x2, y2):
        hits = 0
        if x1 == x2 and y1 == y2:
            return hits
        for bx1, by1, bx2, by2 in bus_segments:
            if bx1 == bx2 and by1 == by2:
                continue
            # vertical segment vs horizontal bus
            if x1 == x2 and by1 == by2:
                if min(bx1, bx2) < x1 < max(bx1, bx2) and min(y1, y2) < by1 < max(y1, y2):
                    hits += 1
            # horizontal segment vs vertical bus
            if y1 == y2 and bx1 == bx2:
                if min(x1, x2) < bx1 < max(x1, x2) and min(by1, by2) < y1 < max(by1, by2):
                    hits += 1
        return hits

    def bend_score(bx, by, x1, y1, x2, y2, ignore):
        hits = segment_hits_nodes(x1, y1, bx, by, ignore)
        hits += segment_hits_nodes(bx, by, x2, y2, ignore)
        hits += segment_hits_bus(x1, y1, bx, by)
        hits += segment_hits_bus(bx, by, x2, y2)
        # NOVO: Penalizar cruzamentos com componentes
        hits += segment_hits_components(x1, y1, bx, by)
        hits += segment_hits_components(bx, by, x2, y2)
        length = abs(x1 - bx) + abs(y1 - by) + abs(x2 - bx) + abs(y2 - by)
        return hits, length

    def bend_hits_node(bx, by, ignore):
        for node, (nx, ny) in node_positions.items():
            if node in ignore:
                continue
            if abs(nx - bx) < 0.01 and abs(ny - by) < 0.01:
                return True
        return False

    def ortho_path(start_pos, end_pos, ignore_nodes):
        x1, y1 = start_pos
        x2, y2 = end_pos
        if abs(x1 - x2) < 0.01 or abs(y1 - y2) < 0.01:
            return "--"
        cand1 = (x1, y2)
        cand2 = (x2, y1)
        score1 = bend_score(cand1[0], cand1[1], x1, y1, x2, y2, ignore_nodes)
        score2 = bend_score(cand2[0], cand2[1], x1, y1, x2, y2, ignore_nodes)
        return "|-" if score1 <= score2 else "-|"

    def draw_ground_bipole(comp, node, group_id):
        comp_id = _safe_id(comp.name)
        offset = ground_offsets.get(comp.name, 0)
        base = node_ids[node]
        label_attr = _label_attr_for(comp)
        kind = comp.comp_type
        if comp.name in bus_positions:
            bx, by = bus_positions[comp.name]
            node_x, node_y = coords[node]
            start = node_ids[node]
            if bx != node_x:
                anchor = f"{comp_id}_top"
                lines.append(f"\\draw ({start}) to[short] ++({bx - node_x},0) coordinate ({anchor});")
                start = anchor
            lines.append(f"\\draw ({start}) to[{kind}{label_attr}] ({bx},{by});")
            return
        elif offset:
            anchor = f"{comp_id}_gnd"
            lines.append(f"\\draw ({base}) to[short] ++({offset},0) coordinate ({anchor});")
            start = anchor
        else:
            start = base

        gnd_anchor = gnd_bus_name.get(group_id)
        if gnd_anchor:
            lines.append(f"\\draw ({start}) to[{kind}{label_attr}] ({start} |- {gnd_anchor});")
        else:
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
                group_id = group_of.get(other)
                draw_ground_bipole(comp, other, group_id)
            continue

        if n1 not in node_ids or n2 not in node_ids:
            continue

        id1 = node_ids[n1]
        id2 = node_ids[n2]
        label_attr = _label_attr_for(comp)
        kind = comp.comp_type

        x1, y1 = coords.get(n1, (0, 0))
        x2, y2 = coords.get(n2, (0, 0))
        aligned = (x1 == x2) or (y1 == y2)
        offset = edge_offsets.get(comp.name, 0)
        if aligned:
            if offset == 0:
                lines.append(f"\\draw ({id1}) to[{kind}{label_attr}] ({id2});")
            else:
                if x1 == x2:
                    p1 = f"{id1}_{_safe_id(comp.name)}_p1"
                    p2 = f"{id2}_{_safe_id(comp.name)}_p2"
                    lines.append(f"\\draw ({id1}) to[short] ++({offset},0) coordinate ({p1});")
                    lines.append(f"\\draw ({id2}) to[short] ++({offset},0) coordinate ({p2});")
                    lines.append(f"\\draw ({p1}) to[{kind}{label_attr}] ({p2});")
                else:
                    p1 = f"{id1}_{_safe_id(comp.name)}_p1"
                    p2 = f"{id2}_{_safe_id(comp.name)}_p2"
                    lines.append(f"\\draw ({id1}) to[short] ++(0,{offset}) coordinate ({p1});")
                    lines.append(f"\\draw ({id2}) to[short] ++(0,{offset}) coordinate ({p2});")
                    lines.append(f"\\draw ({p1}) to[{kind}{label_attr}] ({p2});")
            continue

        deg1 = degrees.get(n1, 0)
        deg2 = degrees.get(n2, 0)
        cand1 = (x1, y2)
        cand2 = (x2, y1)
        ignore_nodes = {n1, n2}
        score1 = bend_score(cand1[0], cand1[1], x1, y1, x2, y2, ignore_nodes)
        score2 = bend_score(cand2[0], cand2[1], x1, y1, x2, y2, ignore_nodes)
        if score1 == score2:
            bend = cand1 if deg1 >= deg2 else cand2
        else:
            bend = cand1 if score1 < score2 else cand2
        bx, by = bend
        if bend_hits_node(bx, by, ignore_nodes):
            if bx == x1:
                cand_offsets = [by + bend_offset, by - bend_offset]
                best = None
                for off in cand_offsets:
                    score = bend_score(bx, off, x1, y1, x2, y2, ignore_nodes)
                    if best is None or score < best[0]:
                        best = (score, off)
                by = best[1]
                lines.append(f"\\draw ({id1}) to[{kind}{label_attr}] ({bx},{by}) to[short] ({x2},{by}) to[short] ({id2});")
            else:
                cand_offsets = [bx + bend_offset, bx - bend_offset]
                best = None
                for off in cand_offsets:
                    score = bend_score(off, by, x1, y1, x2, y2, ignore_nodes)
                    if best is None or score < best[0]:
                        best = (score, off)
                bx = best[1]
                lines.append(f"\\draw ({id1}) to[{kind}{label_attr}] ({bx},{by}) to[short] ({bx},{y2}) to[short] ({id2});")
        else:
            lines.append(f"\\draw ({id1}) to[{kind}{label_attr}] ({bx},{by}) to[short] ({id2});")

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
        group_id = group_of.get(pins[0])
        cx = sum(coords[n][0] for n in pins) / len(pins)
        cy = sum(coords[n][1] for n in pins) / len(pins)
        pin_offset = route_grid

        lines.append(f"\\node[{kind}] ({comp_id}) at ({cx},{cy}) {{}};")
        if c in node_ids:
            start = (cx, cy + pin_offset)
            end = coords[c]
            path = ortho_path(start, end, {c})
            lines.append(f"\\draw ({comp_id}.C) {path} ({node_ids[c]});")
        if b in node_ids:
            start = (cx - pin_offset, cy)
            end = coords[b]
            path = ortho_path(start, end, {b})
            lines.append(f"\\draw ({comp_id}.B) {path} ({node_ids[b]});")
        if e in node_ids:
            start = (cx, cy - pin_offset)
            end = coords[e]
            path = ortho_path(start, end, {e})
            lines.append(f"\\draw ({comp_id}.E) {path} ({node_ids[e]});")
        elif e == '0':
            gnd_anchor = gnd_bus_name.get(group_id)
            if gnd_anchor:
                lines.append(f"\\draw ({comp_id}.E) -- ({comp_id}.E |- {gnd_anchor});")
            else:
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
        group_id = group_of.get(pins[0])
        cx = sum(coords[n][0] for n in pins) / len(pins)
        cy = sum(coords[n][1] for n in pins) / len(pins)
        pin_offset = route_grid

        lines.append(f"\\node[{kind}] ({comp_id}) at ({cx},{cy}) {{}};")
        if d in node_ids:
            start = (cx, cy + pin_offset)
            end = coords[d]
            path = ortho_path(start, end, {d})
            lines.append(f"\\draw ({comp_id}.D) {path} ({node_ids[d]});")
        if g in node_ids:
            start = (cx - pin_offset, cy)
            end = coords[g]
            path = ortho_path(start, end, {g})
            lines.append(f"\\draw ({comp_id}.G) {path} ({node_ids[g]});")
        if s in node_ids:
            start = (cx, cy - pin_offset)
            end = coords[s]
            path = ortho_path(start, end, {s})
            lines.append(f"\\draw ({comp_id}.S) {path} ({node_ids[s]});")
        elif s == '0':
            gnd_anchor = gnd_bus_name.get(group_id)
            if gnd_anchor:
                lines.append(f"\\draw ({comp_id}.S) -- ({comp_id}.S |- {gnd_anchor});")
            else:
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
        group_id = group_of.get(pins[0])
        cx = sum(coords[n][0] for n in pins) / len(pins)
        cy = sum(coords[n][1] for n in pins) / len(pins)
        pin_offset = route_grid

        lines.append(f"\\node[{kind}] ({comp_id}) at ({cx},{cy}) {{}};")
        if d in node_ids:
            start = (cx, cy + pin_offset)
            end = coords[d]
            path = ortho_path(start, end, {d})
            lines.append(f"\\draw ({comp_id}.D) {path} ({node_ids[d]});")
        if g in node_ids:
            start = (cx - pin_offset, cy)
            end = coords[g]
            path = ortho_path(start, end, {g})
            lines.append(f"\\draw ({comp_id}.G) {path} ({node_ids[g]});")
        if s in node_ids:
            start = (cx, cy - pin_offset)
            end = coords[s]
            path = ortho_path(start, end, {s})
            lines.append(f"\\draw ({comp_id}.S) {path} ({node_ids[s]});")
        elif s == '0':
            gnd_anchor = gnd_bus_name.get(group_id)
            if gnd_anchor:
                lines.append(f"\\draw ({comp_id}.S) -- ({comp_id}.S |- {gnd_anchor});")
            else:
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
    env = os.environ.copy()
    # Adicionar LaTeX ao PATH (macOS)
    if '/Library/TeX/texbin' not in env.get('PATH', ''):
        env['PATH'] = f"/Library/TeX/texbin:{env.get('PATH', '')}"
    proc = subprocess.run(cmd, shell=True, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def create_schematic_circuitikz(components, title, output_path):
    """Gera circuito usando circuitikz + pdflatex."""
    if not components:
        return None

    if _is_simple_voltage_fan(components):
        tex_body = _circuitikz_simple_fan(components, title)
    elif _is_simple_current_divider(components):
        tex_body = _circuitikz_current_divider(components, title)
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
\usepackage[active,tightpage]{preview}
\PreviewEnvironment{circuitikz}
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
