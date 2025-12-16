#!/usr/bin/env python3
"""
csv_to_png.py - Converte arquivos CSV gerados pelo ngspice em graficos PNG

Uso:
    python scripts/csv_to_png.py                    # processa todos os CSVs em circuits/
    python scripts/csv_to_png.py arquivo.csv        # processa um arquivo especifico
    python scripts/csv_to_png.py circuits/01_*/     # processa CSVs em um diretorio

O script detecta automaticamente o tipo de dados (tempo, frequencia, tensao DC)
e ajusta os eixos e escalas apropriadamente.
"""

import sys
import os
import glob
import argparse
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except ImportError:
    print("Erro: matplotlib nao encontrado.")
    print("Instale com: pip install matplotlib")
    sys.exit(1)


def parse_ngspice_csv(filepath):
    """
    Le arquivo CSV gerado pelo ngspice (wrdata).

    O formato do ngspice e peculiar:
    - Primeira linha: nomes das colunas (se wr_vecnames estiver ativo)
    - Dados separados por espacos ou tabs
    - Numeros podem estar em notacao cientifica

    Retorna: (nomes_colunas, dados_numpy)
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    if not lines:
        raise ValueError(f"Arquivo vazio: {filepath}")

    # Detectar se primeira linha e cabecalho
    first_line = lines[0].strip()
    has_header = False
    header = []

    # Tentar parsear primeira linha como numeros
    try:
        [float(x) for x in first_line.split()]
    except ValueError:
        # Nao e numero, entao e cabecalho
        has_header = True
        header = first_line.split()

    # Parsear dados
    data_lines = lines[1:] if has_header else lines
    data = []

    for line in data_lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('*'):
            continue
        try:
            values = [float(x) for x in line.split()]
            if values:
                data.append(values)
        except ValueError:
            continue

    if not data:
        raise ValueError(f"Nenhum dado numerico encontrado em: {filepath}")

    data = np.array(data)

    # Gerar nomes de colunas se nao houver cabecalho
    if not header:
        header = [f'col_{i}' for i in range(data.shape[1])]

    return header, data


def detect_data_type(header, data):
    """
    Detecta o tipo de dados baseado nos nomes das colunas e valores.

    Retorna: 'time', 'frequency', 'dc_sweep', ou 'unknown'
    """
    header_lower = [h.lower() for h in header]

    # Verificar pelo nome da coluna
    if any('time' in h or 'tempo' in h for h in header_lower):
        return 'time'
    if any('freq' in h for h in header_lower):
        return 'frequency'

    # Verificar pelo range de valores da primeira coluna (eixo X)
    x_data = data[:, 0]
    x_range = x_data.max() - x_data.min()

    # Se valores sao muito pequenos (< 1) e positivos, provavelmente e tempo
    if x_data.min() >= 0 and x_range < 10 and x_range > 0:
        return 'time'

    # Se valores vao de 0 a dezenas/centenas, provavelmente e DC sweep
    if x_data.min() >= 0 and x_range >= 1:
        return 'dc_sweep'

    return 'unknown'


def format_engineering(value, unit=''):
    """Formata valor em notacao de engenharia."""
    if value == 0:
        return f"0 {unit}"

    prefixes = {
        -15: 'f', -12: 'p', -9: 'n', -6: 'u', -3: 'm',
        0: '', 3: 'k', 6: 'M', 9: 'G', 12: 'T'
    }

    exp = int(np.floor(np.log10(abs(value)) / 3) * 3)
    exp = max(-15, min(12, exp))

    scaled = value / (10 ** exp)
    prefix = prefixes.get(exp, f'e{exp}')

    return f"{scaled:.3g} {prefix}{unit}"


def create_plot(header, data, data_type, title, output_path):
    """
    Cria grafico PNG a partir dos dados.
    """
    # Configurar estilo
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'ggplot')

    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

    x_data = data[:, 0]
    x_label = header[0] if header else 'X'

    # Cores para multiplas curvas
    colors = plt.cm.tab10(np.linspace(0, 1, max(data.shape[1] - 1, 1)))

    # Plotar cada coluna Y
    for i in range(1, data.shape[1]):
        y_data = data[:, i]
        y_label = header[i] if i < len(header) else f'Y{i}'

        ax.plot(x_data, y_data, label=y_label, color=colors[i-1], linewidth=1.5)

    # Configurar eixos baseado no tipo de dados
    if data_type == 'time':
        ax.set_xlabel('Tempo (s)')
        # Usar escala apropriada para tempo
        x_max = x_data.max()
        if x_max < 1e-6:
            ax.set_xlabel('Tempo (ns)')
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x*1e9:.1f}'))
        elif x_max < 1e-3:
            ax.set_xlabel('Tempo (us)')
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x*1e6:.1f}'))
        elif x_max < 1:
            ax.set_xlabel('Tempo (ms)')
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x*1e3:.1f}'))

    elif data_type == 'frequency':
        ax.set_xlabel('Frequencia (Hz)')
        ax.set_xscale('log')
        # Verificar se Y parece ser dB (valores negativos tipicos)
        y_all = data[:, 1:].flatten()
        if y_all.min() < -100 or (y_all.min() < 0 and y_all.max() < 20):
            ax.set_ylabel('Magnitude (dB)')

    elif data_type == 'dc_sweep':
        ax.set_xlabel(x_label if x_label != 'col_0' else 'Tensao (V)')

    else:
        ax.set_xlabel(x_label)

    # Detectar unidade Y
    y_labels = [h for h in header[1:] if h]
    if any('v(' in h.lower() for h in y_labels):
        ax.set_ylabel('Tensao (V)')
    elif any('i(' in h.lower() for h in y_labels):
        ax.set_ylabel('Corrente (A)')
        # Formatar eixo Y para correntes pequenas
        y_max = abs(data[:, 1:]).max()
        if y_max < 1e-3:
            ax.set_ylabel('Corrente (mA)')
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, p: f'{y*1e3:.2f}'))
    elif any('db(' in h.lower() for h in y_labels):
        ax.set_ylabel('Magnitude (dB)')
    elif any('phase(' in h.lower() for h in y_labels):
        ax.set_ylabel('Fase (graus)')

    # Titulo e legenda
    ax.set_title(title, fontsize=12, fontweight='bold')

    if data.shape[1] > 2:  # Multiplas curvas
        ax.legend(loc='best', fontsize=9)

    # Grid
    ax.grid(True, alpha=0.3)
    ax.minorticks_on()
    ax.grid(which='minor', alpha=0.1)

    # Salvar
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)

    return output_path


def process_csv(csv_path, output_dir=None):
    """
    Processa um arquivo CSV e gera PNG.

    Retorna: caminho do arquivo PNG gerado
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Arquivo nao encontrado: {csv_path}")

    # Definir diretorio de saida
    if output_dir is None:
        output_dir = os.path.dirname(csv_path)

    # Nome do arquivo de saida
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}.png")

    # Ler dados
    header, data = parse_ngspice_csv(csv_path)

    # Detectar tipo
    data_type = detect_data_type(header, data)

    # Titulo baseado no nome do arquivo
    title = base_name.replace('_', ' ').title()

    # Criar grafico
    create_plot(header, data, data_type, title, output_path)

    return output_path


def find_csv_files(search_path):
    """
    Encontra todos os arquivos CSV em um diretorio (recursivamente).
    """
    if os.path.isfile(search_path):
        return [search_path] if search_path.endswith('.csv') else []

    if os.path.isdir(search_path):
        return glob.glob(os.path.join(search_path, '**', '*.csv'), recursive=True)

    # Pode ser um glob pattern
    return glob.glob(search_path, recursive=True)


def main():
    parser = argparse.ArgumentParser(
        description='Converte arquivos CSV do ngspice em graficos PNG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python csv_to_png.py                           # Processa todos CSVs em circuits/
  python csv_to_png.py dados.csv                 # Processa arquivo especifico
  python csv_to_png.py circuits/01_fundamentos/  # Processa CSVs em um diretorio
  python csv_to_png.py "circuits/**/*.csv"       # Usa glob pattern
        """
    )

    parser.add_argument(
        'input',
        nargs='?',
        default='circuits',
        help='Arquivo CSV, diretorio ou glob pattern (padrao: circuits/)'
    )

    parser.add_argument(
        '-o', '--output-dir',
        help='Diretorio de saida para os PNGs (padrao: mesmo diretorio do CSV)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mostra informacoes detalhadas'
    )

    args = parser.parse_args()

    # Encontrar arquivos CSV
    csv_files = find_csv_files(args.input)

    if not csv_files:
        print(f"Nenhum arquivo CSV encontrado em: {args.input}")
        print("Execute uma simulacao ngspice primeiro para gerar os arquivos CSV.")
        return 1

    print(f"Encontrados {len(csv_files)} arquivo(s) CSV")
    print("-" * 50)

    success_count = 0
    error_count = 0

    for csv_path in csv_files:
        try:
            if args.verbose:
                print(f"Processando: {csv_path}")

            output_path = process_csv(csv_path, args.output_dir)
            print(f"  {csv_path} -> {output_path}")
            success_count += 1

        except Exception as e:
            print(f"  ERRO em {csv_path}: {e}")
            error_count += 1

    print("-" * 50)
    print(f"Concluido: {success_count} sucesso, {error_count} erro(s)")

    return 0 if error_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
