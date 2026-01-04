# Tutorial Completo de cocotb

## Sumário

1. [Introdução](#1-introdução)
2. [Instalação](#2-instalação)
3. [Estrutura de um Projeto](#3-estrutura-de-um-projeto)
4. [Conceitos Fundamentais](#4-conceitos-fundamentais)
5. [Escrevendo Testes](#5-escrevendo-testes)
6. [Triggers e Temporização](#6-triggers-e-temporização)
7. [Acessando Sinais do DUT](#7-acessando-sinais-do-dut)
8. [Trabalhando com Clock](#8-trabalhando-com-clock)
9. [Exemplos Práticos (SystemVerilog)](#9-exemplos-práticos-systemverilog)
10. [Exemplos em VHDL](#10-exemplos-em-vhdl)
11. [Makefile e Simuladores](#11-makefile-e-simuladores)
12. [Execução sem Makefile (Python/Jupyter)](#12-execução-sem-makefile-pythonjupyter)
13. [Técnicas Avançadas](#13-técnicas-avançadas)
14. [Boas Práticas](#14-boas-práticas)
15. [Debugging](#15-debugging)
16. [Referência Rápida](#16-referência-rápida)

---

## 1. Introdução

**cocotb** (Coroutine Co-simulation Test Bench) é um framework de verificação baseado em Python para testar designs HDL (Verilog, SystemVerilog, VHDL). Ele permite escrever testbenches em Python usando corrotinas assíncronas (`async/await`).

### Vantagens do cocotb

- **Python**: Linguagem de alto nível com vasto ecossistema de bibliotecas
- **Sem necessidade de HDL para testbench**: Toda lógica de teste em Python
- **Corrotinas**: Código assíncrono limpo e legível
- **Compatibilidade**: Funciona com Verilator, Icarus Verilog, ModelSim, VCS, etc.
- **Randomização**: Fácil integração com bibliotecas de teste como `random`, `hypothesis`

---

## 2. Instalação

### Requisitos

- Python 3.8+
- Simulador HDL (Verilator, Icarus Verilog, etc.)

### Instalação via pip

```bash
pip install cocotb
```

### Instalação do Verilator (macOS)

```bash
brew install verilator
```

### Instalação do Verilator (Ubuntu/Debian)

```bash
sudo apt-get install verilator
```

### Verificar instalação

```bash
cocotb-config --version
cocotb-config --makefiles
```

---

## 3. Estrutura de um Projeto

### Estrutura mínima

```
projeto/
├── modulo.sv          # Design HDL (SystemVerilog/Verilog)
├── test_modulo.py     # Testbench em Python
└── Makefile           # Configuração de build
```

### Makefile básico

```makefile
SIM ?= verilator
TOPLEVEL_LANG ?= verilog

TOPLEVEL ?= nome_do_modulo
COCOTB_TEST_MODULES ?= test_modulo

VERILOG_SOURCES += $(PWD)/modulo.sv

EXTRA_ARGS += --sv --timescale 1ns/1ps -Wall

include $(shell cocotb-config --makefiles)/Makefile.sim
```

### Variáveis importantes do Makefile

| Variável | Descrição |
|----------|-----------|
| `SIM` | Simulador (verilator, icarus, modelsim, etc.) |
| `TOPLEVEL_LANG` | Linguagem (verilog, vhdl) |
| `TOPLEVEL` | Nome do módulo top-level |
| `COCOTB_TEST_MODULES` | Módulo Python com os testes |
| `VERILOG_SOURCES` | Arquivos fonte HDL |
| `EXTRA_ARGS` | Argumentos extras para o simulador |

---

## 4. Conceitos Fundamentais

### DUT (Device Under Test)

O `dut` é o objeto que representa seu módulo HDL no Python:

```python
@cocotb.test()
async def meu_teste(dut):
    # dut é o módulo HDL instanciado
    # Acesse sinais: dut.nome_do_sinal
    pass
```

### Corrotinas (async/await)

cocotb usa corrotinas Python para simular paralelismo:

```python
async def minha_funcao(dut):
    await Timer(10, unit="ns")  # Espera 10ns
    dut.sinal.value = 1
```

### Decorador @cocotb.test()

Marca uma função como um teste:

```python
@cocotb.test()
async def test_exemplo(dut):
    """Descrição do teste"""
    # Código do teste
    pass
```

---

## 5. Escrevendo Testes

### Teste básico

```python
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_basico(dut):
    """Teste básico de exemplo"""

    # Aplica valores nas entradas
    dut.entrada_a.value = 5
    dut.entrada_b.value = 3

    # Espera propagação
    await Timer(10, unit="ns")

    # Verifica saída
    assert dut.saida.value == 8, f"Esperado 8, obtido {dut.saida.value}"
```

### Múltiplos testes no mesmo arquivo

```python
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_caso_1(dut):
    """Primeiro caso de teste"""
    dut.a.value = 0
    await Timer(10, unit="ns")
    assert dut.y.value == 0

@cocotb.test()
async def test_caso_2(dut):
    """Segundo caso de teste"""
    dut.a.value = 1
    await Timer(10, unit="ns")
    assert dut.y.value == 1

@cocotb.test()
async def test_caso_3(dut):
    """Terceiro caso de teste"""
    # Os testes são executados em sequência
    pass
```

### Usando expect_error para testes que devem falhar

```python
@cocotb.test(expect_error=AssertionError)
async def test_deve_falhar(dut):
    """Este teste espera uma falha"""
    assert False, "Este assert deve falhar"
```

### Pulando testes condicionalmente

```python
@cocotb.test(skip=True)
async def test_pulado(dut):
    """Este teste será pulado"""
    pass
```

---

## 6. Triggers e Temporização

Triggers são eventos que pausam a corrotina até uma condição ser satisfeita.

### Timer - Espera por tempo

```python
from cocotb.triggers import Timer

await Timer(10, unit="ns")    # Espera 10 nanosegundos
await Timer(1, unit="us")     # Espera 1 microsegundo
await Timer(100, unit="ps")   # Espera 100 picosegundos
```

### RisingEdge / FallingEdge - Bordas de clock

```python
from cocotb.triggers import RisingEdge, FallingEdge

await RisingEdge(dut.clk)     # Espera borda de subida
await FallingEdge(dut.clk)    # Espera borda de descida
```

### Edge - Qualquer transição

```python
from cocotb.triggers import Edge

await Edge(dut.sinal)         # Espera qualquer mudança no sinal
```

### ClockCycles - Múltiplos ciclos de clock

```python
from cocotb.triggers import ClockCycles

await ClockCycles(dut.clk, 5)           # Espera 5 ciclos de clock
await ClockCycles(dut.clk, 10, rising=False)  # 10 falling edges
```

### Combine - Espera múltiplos triggers (AND)

```python
from cocotb.triggers import Combine, RisingEdge

await Combine(RisingEdge(dut.clk), RisingEdge(dut.ready))
```

### First - Espera o primeiro trigger (OR)

```python
from cocotb.triggers import First, Timer, RisingEdge

trigger = await First(Timer(100, unit="ns"), RisingEdge(dut.done))
```

### with_timeout - Timeout para operações

```python
from cocotb.triggers import with_timeout, RisingEdge

try:
    await with_timeout(RisingEdge(dut.done), 1000, unit="ns")
except cocotb.result.SimTimeoutError:
    print("Timeout!")
```

---

## 7. Acessando Sinais do DUT

### Leitura de sinais

```python
# Ler valor como inteiro
valor = int(dut.sinal.value)

# Ler valor binário
valor_bin = dut.sinal.value.binstr

# Verificar se é X ou Z
is_resolvable = dut.sinal.value.is_resolvable
```

### Escrita de sinais

```python
# Atribuir valor inteiro
dut.sinal.value = 42

# Atribuir valor binário
dut.sinal.value = 0b1010

# Atribuir valor hexadecimal
dut.sinal.value = 0xFF

# Atribuir string binária
dut.sinal.value = "1010"
```

### Sinais de múltiplos bits

```python
# Ler barramento de 8 bits
byte_val = int(dut.data_bus.value)

# Escrever em barramento
dut.data_bus.value = 0xAB

# Acessar bits individuais (se suportado pelo simulador)
bit0 = dut.data_bus[0].value
```

### Hierarquia de sinais

```python
# Acessar sinais em submódulos
dut.submodulo.sinal_interno.value

# Usando getattr para nomes dinâmicos
sinal = getattr(dut, "nome_sinal")
```

---

## 8. Trabalhando com Clock

### Criando um clock

```python
from cocotb.clock import Clock

# Clock de 10ns de período (100MHz)
cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

# Clock de 20ns de período (50MHz)
cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
```

### Clock com duty cycle personalizado

```python
# Clock com 25% duty cycle
async def custom_clock(signal, period, duty_cycle=0.25):
    high_time = period * duty_cycle
    low_time = period * (1 - duty_cycle)
    while True:
        signal.value = 1
        await Timer(high_time, unit="ns")
        signal.value = 0
        await Timer(low_time, unit="ns")

cocotb.start_soon(custom_clock(dut.clk, 10, 0.25))
```

### Padrão para testes síncronos

```python
@cocotb.test()
async def test_sincrono(dut):
    # Inicia clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Reset
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.rst.value = 0

    # Teste principal
    for i in range(10):
        await RisingEdge(dut.clk)
        # Verifica na falling edge (sinais estáveis)
        await FallingEdge(dut.clk)
        assert dut.count.value == i
```

---

## 9. Exemplos Práticos (SystemVerilog)

### Exemplo 1: Testando um MUX 2:1

**mux2.sv:**
```systemverilog
module mux2 (
    input  logic       sel,
    input  logic [7:0] a,
    input  logic [7:0] b,
    output logic [7:0] y
);
    assign y = sel ? b : a;
endmodule
```

**test_mux2.py:**
```python
import cocotb
from cocotb.triggers import Timer
import random

@cocotb.test()
async def test_mux_sel0(dut):
    """Testa MUX com sel=0 (seleciona A)"""
    dut.sel.value = 0
    dut.a.value = 0xAA
    dut.b.value = 0x55

    await Timer(10, unit="ns")

    assert int(dut.y.value) == 0xAA, "Com sel=0, y deveria ser igual a A"

@cocotb.test()
async def test_mux_sel1(dut):
    """Testa MUX com sel=1 (seleciona B)"""
    dut.sel.value = 1
    dut.a.value = 0xAA
    dut.b.value = 0x55

    await Timer(10, unit="ns")

    assert int(dut.y.value) == 0x55, "Com sel=1, y deveria ser igual a B"

@cocotb.test()
async def test_mux_random(dut):
    """Testa MUX com valores aleatórios"""
    for _ in range(100):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        sel = random.randint(0, 1)

        dut.a.value = a
        dut.b.value = b
        dut.sel.value = sel

        await Timer(10, unit="ns")

        expected = b if sel else a
        assert int(dut.y.value) == expected
```

### Exemplo 2: Testando um Contador

**counter.sv:**
```systemverilog
module counter #(
    parameter WIDTH = 8
)(
    input  logic             clk,
    input  logic             rst,
    input  logic             en,
    output logic [WIDTH-1:0] count
);
    always_ff @(posedge clk) begin
        if (rst)
            count <= '0;
        else if (en)
            count <= count + 1'b1;
    end
endmodule
```

**test_counter.py:**
```python
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

async def reset_dut(dut):
    """Função auxiliar para reset"""
    dut.rst.value = 1
    dut.en.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0

@cocotb.test()
async def test_reset(dut):
    """Verifica que reset zera o contador"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)
    await FallingEdge(dut.clk)

    assert int(dut.count.value) == 0, "Contador deveria ser 0 após reset"

@cocotb.test()
async def test_count_enable(dut):
    """Verifica contagem com enable"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)
    dut.en.value = 1

    for expected in range(1, 20):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)
        assert int(dut.count.value) == expected, \
            f"Esperado {expected}, obtido {int(dut.count.value)}"

@cocotb.test()
async def test_count_disable(dut):
    """Verifica que contador para quando en=0"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)
    dut.en.value = 1

    # Conta até 5
    await ClockCycles(dut.clk, 5)
    await FallingEdge(dut.clk)
    valor_antes = int(dut.count.value)

    # Desabilita
    dut.en.value = 0
    await ClockCycles(dut.clk, 5)
    await FallingEdge(dut.clk)
    valor_depois = int(dut.count.value)

    assert valor_antes == valor_depois, "Contador deveria parar com en=0"

@cocotb.test()
async def test_overflow(dut):
    """Verifica overflow do contador"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)
    dut.en.value = 1

    # Conta até overflow (256 para 8 bits)
    await ClockCycles(dut.clk, 256)
    await FallingEdge(dut.clk)

    assert int(dut.count.value) == 0, "Contador deveria voltar a 0 após overflow"
```

### Exemplo 3: Testando uma FSM

**fsm.sv:**
```systemverilog
module fsm (
    input  logic clk,
    input  logic rst,
    input  logic start,
    input  logic done,
    output logic busy,
    output logic complete
);
    typedef enum logic [1:0] {
        IDLE    = 2'b00,
        RUNNING = 2'b01,
        DONE    = 2'b10
    } state_t;

    state_t state, next_state;

    always_ff @(posedge clk) begin
        if (rst)
            state <= IDLE;
        else
            state <= next_state;
    end

    always_comb begin
        next_state = state;
        busy = 1'b0;
        complete = 1'b0;

        case (state)
            IDLE: begin
                if (start)
                    next_state = RUNNING;
            end

            RUNNING: begin
                busy = 1'b1;
                if (done)
                    next_state = DONE;
            end

            DONE: begin
                complete = 1'b1;
                next_state = IDLE;
            end
        endcase
    end
endmodule
```

**test_fsm.py:**
```python
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

@cocotb.test()
async def test_fsm_idle(dut):
    """Testa estado IDLE"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    dut.start.value = 0
    dut.done.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0
    await FallingEdge(dut.clk)

    assert int(dut.busy.value) == 0, "busy deveria ser 0 em IDLE"
    assert int(dut.complete.value) == 0, "complete deveria ser 0 em IDLE"

@cocotb.test()
async def test_fsm_full_cycle(dut):
    """Testa ciclo completo da FSM"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Reset
    dut.rst.value = 1
    dut.start.value = 0
    dut.done.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0

    # IDLE -> RUNNING
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    await FallingEdge(dut.clk)

    assert int(dut.busy.value) == 1, "busy deveria ser 1 em RUNNING"

    # RUNNING -> DONE
    dut.done.value = 1
    await RisingEdge(dut.clk)
    dut.done.value = 0
    await FallingEdge(dut.clk)

    assert int(dut.complete.value) == 1, "complete deveria ser 1 em DONE"

    # DONE -> IDLE
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)

    assert int(dut.busy.value) == 0
    assert int(dut.complete.value) == 0
```

### Exemplo 4: Testando Memória

**memory.sv:**
```systemverilog
module memory #(
    parameter DEPTH = 256,
    parameter WIDTH = 8
)(
    input  logic                    clk,
    input  logic                    we,
    input  logic [$clog2(DEPTH)-1:0] addr,
    input  logic [WIDTH-1:0]        din,
    output logic [WIDTH-1:0]        dout
);
    logic [WIDTH-1:0] mem [DEPTH];

    always_ff @(posedge clk) begin
        if (we)
            mem[addr] <= din;
        dout <= mem[addr];
    end
endmodule
```

**test_memory.py:**
```python
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
import random

async def write_mem(dut, addr, data):
    """Escreve na memória"""
    dut.we.value = 1
    dut.addr.value = addr
    dut.din.value = data
    await RisingEdge(dut.clk)
    dut.we.value = 0

async def read_mem(dut, addr):
    """Lê da memória"""
    dut.we.value = 0
    dut.addr.value = addr
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    return int(dut.dout.value)

@cocotb.test()
async def test_write_read(dut):
    """Testa escrita e leitura básica"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Escreve 0xAB no endereço 0x10
    await write_mem(dut, 0x10, 0xAB)

    # Lê de volta
    data = await read_mem(dut, 0x10)

    assert data == 0xAB, f"Esperado 0xAB, obtido {data:#x}"

@cocotb.test()
async def test_random_access(dut):
    """Testa acesso aleatório"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Gera dados aleatórios
    test_data = {addr: random.randint(0, 255) for addr in range(50)}

    # Escreve todos
    for addr, data in test_data.items():
        await write_mem(dut, addr, data)

    # Lê todos e verifica
    for addr, expected in test_data.items():
        data = await read_mem(dut, addr)
        assert data == expected, f"Addr {addr}: esperado {expected}, obtido {data}"
```

---

## 10. Exemplos em VHDL

cocotb funciona perfeitamente com VHDL. Abaixo estão os mesmos exemplos da seção anterior, mas em VHDL.

### Exemplo 1: MUX 2:1 em VHDL

**mux2.vhd:**
```vhdl
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity mux2 is
    port (
        sel : in  std_logic;
        a   : in  std_logic_vector(7 downto 0);
        b   : in  std_logic_vector(7 downto 0);
        y   : out std_logic_vector(7 downto 0)
    );
end mux2;

architecture behavioral of mux2 is
begin
    y <= b when sel = '1' else a;
end behavioral;
```

**Makefile para VHDL (GHDL):**
```makefile
SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl

TOPLEVEL ?= mux2
COCOTB_TEST_MODULES ?= test_mux2

VHDL_SOURCES += $(PWD)/mux2.vhd

# GHDL flags
SIM_ARGS += --std=08

include $(shell cocotb-config --makefiles)/Makefile.sim
```

**test_mux2.py (mesmo teste funciona!):**
```python
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_mux_sel0(dut):
    """Testa MUX com sel=0"""
    dut.sel.value = 0
    dut.a.value = 0xAA
    dut.b.value = 0x55

    await Timer(10, unit="ns")

    assert int(dut.y.value) == 0xAA

@cocotb.test()
async def test_mux_sel1(dut):
    """Testa MUX com sel=1"""
    dut.sel.value = 1
    dut.a.value = 0xAA
    dut.b.value = 0x55

    await Timer(10, unit="ns")

    assert int(dut.y.value) == 0x55
```

### Exemplo 2: Contador em VHDL

**counter.vhd:**
```vhdl
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity counter is
    generic (
        WIDTH : integer := 8
    );
    port (
        clk   : in  std_logic;
        rst   : in  std_logic;
        en    : in  std_logic;
        count : out std_logic_vector(WIDTH-1 downto 0)
    );
end counter;

architecture behavioral of counter is
    signal count_reg : unsigned(WIDTH-1 downto 0) := (others => '0');
begin
    process(clk)
    begin
        if rising_edge(clk) then
            if rst = '1' then
                count_reg <= (others => '0');
            elsif en = '1' then
                count_reg <= count_reg + 1;
            end if;
        end if;
    end process;

    count <= std_logic_vector(count_reg);
end behavioral;
```

**test_counter.py:**
```python
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

@cocotb.test()
async def test_reset(dut):
    """Verifica reset"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    dut.en.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0
    await FallingEdge(dut.clk)

    assert int(dut.count.value) == 0

@cocotb.test()
async def test_count(dut):
    """Verifica contagem"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    dut.en.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0
    dut.en.value = 1

    for expected in range(1, 10):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)
        assert int(dut.count.value) == expected
```

### Exemplo 3: ALU em VHDL

**alu.vhd:**
```vhdl
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity alu is
    port (
        a      : in  std_logic_vector(7 downto 0);
        b      : in  std_logic_vector(7 downto 0);
        op     : in  std_logic_vector(2 downto 0);
        result : out std_logic_vector(15 downto 0);
        zero   : out std_logic
    );
end alu;

architecture behavioral of alu is
    constant OP_ADD : std_logic_vector(2 downto 0) := "000";
    constant OP_SUB : std_logic_vector(2 downto 0) := "001";
    constant OP_AND : std_logic_vector(2 downto 0) := "010";
    constant OP_OR  : std_logic_vector(2 downto 0) := "011";
    constant OP_XOR : std_logic_vector(2 downto 0) := "100";
    constant OP_NOT : std_logic_vector(2 downto 0) := "101";
    constant OP_SHL : std_logic_vector(2 downto 0) := "110";
    constant OP_SHR : std_logic_vector(2 downto 0) := "111";

    signal result_int : std_logic_vector(15 downto 0);
begin
    process(a, b, op)
        variable a_uns : unsigned(7 downto 0);
        variable b_uns : unsigned(7 downto 0);
        variable shift_amt : integer;
    begin
        a_uns := unsigned(a);
        b_uns := unsigned(b);
        shift_amt := to_integer(unsigned(b(2 downto 0)));
        result_int <= (others => '0');

        case op is
            when OP_ADD =>
                result_int <= std_logic_vector(resize(a_uns + b_uns, 16));
            when OP_SUB =>
                result_int <= std_logic_vector(resize(a_uns - b_uns, 16));
            when OP_AND =>
                result_int(7 downto 0) <= a and b;
            when OP_OR =>
                result_int(7 downto 0) <= a or b;
            when OP_XOR =>
                result_int(7 downto 0) <= a xor b;
            when OP_NOT =>
                result_int(7 downto 0) <= not a;
            when OP_SHL =>
                result_int <= std_logic_vector(shift_left(resize(a_uns, 16), shift_amt));
            when OP_SHR =>
                result_int(7 downto 0) <= std_logic_vector(shift_right(a_uns, shift_amt));
            when others =>
                result_int <= (others => '0');
        end case;
    end process;

    result <= result_int;
    zero <= '1' when result_int = x"0000" else '0';
end behavioral;
```

**test_alu.py:**
```python
import cocotb
from cocotb.triggers import Timer

OP_ADD = 0b000
OP_SUB = 0b001
OP_AND = 0b010
OP_OR  = 0b011
OP_XOR = 0b100
OP_NOT = 0b101
OP_SHL = 0b110
OP_SHR = 0b111

@cocotb.test()
async def test_add(dut):
    """Testa adição"""
    dut.a.value = 10
    dut.b.value = 20
    dut.op.value = OP_ADD
    await Timer(10, unit="ns")

    assert int(dut.result.value) == 30

@cocotb.test()
async def test_sub(dut):
    """Testa subtração"""
    dut.a.value = 50
    dut.b.value = 20
    dut.op.value = OP_SUB
    await Timer(10, unit="ns")

    assert int(dut.result.value) == 30

@cocotb.test()
async def test_and(dut):
    """Testa AND"""
    dut.a.value = 0xF0
    dut.b.value = 0x0F
    dut.op.value = OP_AND
    await Timer(10, unit="ns")

    assert int(dut.result.value) == 0x00

@cocotb.test()
async def test_or(dut):
    """Testa OR"""
    dut.a.value = 0xF0
    dut.b.value = 0x0F
    dut.op.value = OP_OR
    await Timer(10, unit="ns")

    assert int(dut.result.value) == 0xFF

@cocotb.test()
async def test_zero_flag(dut):
    """Testa flag zero"""
    dut.a.value = 0xAA
    dut.b.value = 0xAA
    dut.op.value = OP_XOR
    await Timer(10, unit="ns")

    assert int(dut.zero.value) == 1
```

### Exemplo 4: Flip-Flop D em VHDL

**dff.vhd:**
```vhdl
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity dff is
    port (
        clk : in  std_logic;
        rst : in  std_logic;
        d   : in  std_logic;
        q   : out std_logic
    );
end dff;

architecture behavioral of dff is
begin
    process(clk)
    begin
        if rising_edge(clk) then
            if rst = '1' then
                q <= '0';
            else
                q <= d;
            end if;
        end if;
    end process;
end behavioral;
```

**test_dff.py:**
```python
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge

@cocotb.test()
async def test_dff_basic(dut):
    """Testa flip-flop D básico"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Reset
    dut.rst.value = 1
    dut.d.value = 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert int(dut.q.value) == 0

    # Libera reset
    dut.rst.value = 0

    # Testa D=1
    dut.d.value = 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert int(dut.q.value) == 1

    # Testa D=0
    dut.d.value = 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert int(dut.q.value) == 0
```

### Makefile genérico para VHDL (GHDL)

```makefile
SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl

TOPLEVEL ?= nome_entidade
COCOTB_TEST_MODULES ?= test_nome

SIM_BUILD ?= sim_build
VHDL_SOURCES += $(PWD)/arquivo.vhd

# GHDL com VHDL-2008
SIM_ARGS += --std=08

# Habilita waves
ifeq ($(WAVES),1)
  SIM_ARGS += --wave=dump.ghw
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: run waves cleanall

run: sim

waves:
	rm -rf $(SIM_BUILD)
	$(MAKE) WAVES=1 sim

cleanall:: clean
	rm -rf $(SIM_BUILD) __pycache__ *.vcd *.ghw *.xml
```

### Diferenças importantes entre Verilog e VHDL no cocotb

| Aspecto | Verilog/SystemVerilog | VHDL |
|---------|----------------------|------|
| Variável `SIM` | `verilator`, `icarus` | `ghdl`, `nvc`, `modelsim` |
| Variável `TOPLEVEL_LANG` | `verilog` | `vhdl` |
| Fontes | `VERILOG_SOURCES` | `VHDL_SOURCES` |
| Waveforms | `.vcd`, `.fst` | `.ghw`, `.vcd` |
| Acesso a sinais | Igual | Igual |
| Tipos de dados | Convertidos automaticamente | Convertidos automaticamente |

---

## 11. Makefile e Simuladores

### Makefile completo com waves

```makefile
SIM ?= verilator
TOPLEVEL_LANG ?= verilog

TOPLEVEL ?= meu_modulo
COCOTB_TEST_MODULES ?= test_meu_modulo

SIM_BUILD ?= sim_build
VERILOG_SOURCES += $(PWD)/meu_modulo.sv

# Flags do Verilator
EXTRA_ARGS += --sv --timescale 1ns/1ps -Wall

# Habilita waves quando WAVES=1
ifeq ($(WAVES),1)
  EXTRA_ARGS += --trace --trace-fst --trace-structs
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: run waves clean_all

run: sim

waves:
	rm -rf $(SIM_BUILD)
	$(MAKE) WAVES=1 sim
	@echo "Waveform gerado: dump.fst"

clean_all:: clean
	rm -rf $(SIM_BUILD) __pycache__ *.vcd *.fst *.xml
```

### Usando Icarus Verilog

```makefile
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

TOPLEVEL ?= meu_modulo
COCOTB_TEST_MODULES ?= test_meu_modulo

VERILOG_SOURCES += $(PWD)/meu_modulo.v

include $(shell cocotb-config --makefiles)/Makefile.sim
```

### Executando testes específicos

```bash
# Executar todos os testes
make run

# Executar teste específico
make COCOTB_TESTCASE=test_meu_caso run

# Executar testes que correspondem a um padrão
make COCOTB_TEST_FILTER="test_add*" run

# Com waves
make WAVES=1 run
```

---

## 12. Execução sem Makefile (Python/Jupyter)

A partir do cocotb 1.6+, é possível executar testes sem Makefile usando o **cocotb.runner** ou a API programática. Isso é especialmente útil para **Jupyter Notebooks** e integração com pytest.

### Instalação do cocotb-runner

```bash
pip install cocotb pytest
```

### Método 1: Usando cocotb.runner (Recomendado)

O `cocotb.runner` permite executar simulações diretamente do Python.

**run_test.py:**
```python
from cocotb.runner import get_runner
import os

def test_adder():
    """Executa o teste do adder usando cocotb.runner"""

    # Obtém o diretório atual
    proj_path = os.path.dirname(os.path.abspath(__file__))

    # Configuração do runner
    runner = get_runner("verilator")  # ou "icarus", "ghdl", etc.

    # Build do design
    runner.build(
        verilog_sources=[os.path.join(proj_path, "adder_4bit.sv")],
        hdl_toplevel="adder_4bit",
        build_args=["--sv", "-Wall"],
    )

    # Executa os testes
    runner.test(
        hdl_toplevel="adder_4bit",
        test_module="test_adder",  # Nome do arquivo Python sem .py
    )

if __name__ == "__main__":
    test_adder()
```

**Executando:**
```bash
python run_test.py
```

### Método 2: Exemplo completo em Jupyter Notebook

```python
# Célula 1: Imports
import os
from cocotb.runner import get_runner

# Célula 2: Criar arquivo HDL
hdl_code = """
module adder_4bit (
    input  logic [3:0] a,
    input  logic [3:0] b,
    input  logic       cin,
    output logic [3:0] sum,
    output logic       cout
);
    logic [4:0] result;
    assign result = {1'b0, a} + {1'b0, b} + {4'b0, cin};
    assign sum    = result[3:0];
    assign cout   = result[4];
endmodule
"""

with open("adder_4bit.sv", "w") as f:
    f.write(hdl_code)

# Célula 3: Criar arquivo de teste
test_code = '''
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_basic(dut):
    """Teste básico"""
    dut.a.value = 5
    dut.b.value = 3
    dut.cin.value = 0
    await Timer(10, unit="ns")
    assert int(dut.sum.value) == 8
    print(f"5 + 3 = {int(dut.sum.value)} ✓")

@cocotb.test()
async def test_overflow(dut):
    """Teste de overflow"""
    dut.a.value = 15
    dut.b.value = 1
    dut.cin.value = 0
    await Timer(10, unit="ns")
    assert int(dut.sum.value) == 0
    assert int(dut.cout.value) == 1
    print(f"15 + 1 = {int(dut.sum.value)}, cout={int(dut.cout.value)} ✓")
'''

with open("test_adder.py", "w") as f:
    f.write(test_code)

# Célula 4: Executar simulação
runner = get_runner("verilator")

runner.build(
    verilog_sources=["adder_4bit.sv"],
    hdl_toplevel="adder_4bit",
    build_args=["--sv", "-Wall"],
)

runner.test(
    hdl_toplevel="adder_4bit",
    test_module="test_adder",
)

print("Testes concluídos!")
```

### Método 3: Classe auxiliar para Jupyter

```python
"""
Módulo para executar cocotb em Jupyter Notebooks
"""
import os
import shutil
from cocotb.runner import get_runner

class JupyterCocotb:
    """Helper para rodar cocotb no Jupyter"""

    def __init__(self, simulator="verilator"):
        self.simulator = simulator
        self.runner = None

    def clean(self):
        """Limpa diretório de build"""
        shutil.rmtree("sim_build", ignore_errors=True)

    def run(self, hdl_sources, toplevel, test_module,
            lang="verilog", build_args=None, waves=False):
        """
        Executa um teste cocotb.

        Args:
            hdl_sources: Lista de arquivos HDL
            toplevel: Nome do módulo top-level
            test_module: Nome do módulo Python de teste (sem .py)
            lang: "verilog" ou "vhdl"
            build_args: Lista de argumentos extras
            waves: Gerar waveforms

        Returns:
            True se passou, False se falhou
        """
        self.clean()
        self.runner = get_runner(self.simulator)

        # Argumentos padrão
        args = build_args or []
        if self.simulator == "verilator":
            args.extend(["--sv", "-Wall"])
            if waves:
                args.extend(["--trace", "--trace-fst"])

        # Build
        if lang == "verilog":
            self.runner.build(
                verilog_sources=hdl_sources,
                hdl_toplevel=toplevel,
                build_args=args,
            )
        else:
            self.runner.build(
                vhdl_sources=hdl_sources,
                hdl_toplevel=toplevel,
                build_args=args,
            )

        # Test
        try:
            self.runner.test(
                hdl_toplevel=toplevel,
                test_module=test_module,
            )
            return True
        except Exception as e:
            print(f"Erro: {e}")
            return False

# Uso:
# cocotb = JupyterCocotb()
# cocotb.run(["adder.sv"], "adder", "test_adder")
```

### Método 4: Usando pytest

Integração com pytest para executar testes cocotb.

**test_with_pytest.py:**
```python
import pytest
from cocotb.runner import get_runner
import os

@pytest.fixture
def build_adder():
    """Fixture que compila o adder"""
    runner = get_runner("verilator")
    runner.build(
        verilog_sources=["adder_4bit.sv"],
        hdl_toplevel="adder_4bit",
        build_args=["--sv"],
    )
    return runner

def test_adder_basic(build_adder):
    """Executa teste básico do adder"""
    build_adder.test(
        hdl_toplevel="adder_4bit",
        test_module="test_adder",
    )

@pytest.mark.parametrize("test_name", [
    "test_basic_addition",
    "test_overflow",
])
def test_adder_individual(build_adder, test_name):
    """Executa testes individuais"""
    os.environ["COCOTB_TESTCASE"] = test_name
    build_adder.test(
        hdl_toplevel="adder_4bit",
        test_module="test_adder",
    )
```

**Executando com pytest:**
```bash
pytest test_with_pytest.py -v
```

### Método 5: Runner para VHDL (GHDL)

```python
from cocotb.runner import get_runner

runner = get_runner("ghdl")

runner.build(
    vhdl_sources=["counter.vhd"],
    hdl_toplevel="counter",
    build_args=["--std=08"],
)

runner.test(
    hdl_toplevel="counter",
    test_module="test_counter",
)
```

### Comparação dos métodos

| Método | Vantagens | Desvantagens |
|--------|-----------|--------------|
| **cocotb.runner** | Oficial, simples, Python puro | Requer cocotb 1.6+ |
| **JupyterCocotb** | Integração fácil com notebooks | Wrapper adicional |
| **pytest** | Integração com CI/CD, parametrização | Setup mais complexo |
| **Makefile** | Documentado, padrão da comunidade | Menos flexível |

### Dicas para Jupyter Notebook

1. **Limpe o estado entre execuções:**
   ```python
   import shutil
   shutil.rmtree("sim_build", ignore_errors=True)
   ```

2. **Capture output verboso:**
   ```python
   %%capture output
   runner.test(...)
   # Depois: print(output) se necessário
   ```

3. **Verifique simulador instalado:**
   ```python
   import shutil
   print("Verilator:", shutil.which("verilator"))
   print("GHDL:", shutil.which("ghdl"))
   print("Icarus:", shutil.which("iverilog"))
   ```

4. **Use magic para criar arquivos:**
   ```python
   %%writefile adder.sv
   module adder(...);
   ...
   endmodule
   ```

---

## 13. Técnicas Avançadas

### Fork e Join - Execução paralela

```python
@cocotb.test()
async def test_paralelo(dut):
    """Executa múltiplas tarefas em paralelo"""

    async def tarefa_a():
        for i in range(10):
            await RisingEdge(dut.clk)
            dut.a.value = i

    async def tarefa_b():
        for i in range(10):
            await RisingEdge(dut.clk)
            dut.b.value = i * 2

    # Inicia tarefas em paralelo
    task_a = cocotb.start_soon(tarefa_a())
    task_b = cocotb.start_soon(tarefa_b())

    # Espera ambas terminarem
    await task_a
    await task_b
```

### Scoreboard - Verificação automática

```python
class Scoreboard:
    def __init__(self):
        self.expected = []
        self.received = []
        self.errors = 0

    def add_expected(self, value):
        self.expected.append(value)

    def add_received(self, value):
        self.received.append(value)
        if self.expected:
            expected = self.expected.pop(0)
            if value != expected:
                self.errors += 1
                print(f"ERRO: esperado {expected}, recebido {value}")

    def check(self):
        assert self.errors == 0, f"Scoreboard encontrou {self.errors} erros"
        assert len(self.expected) == 0, f"Faltaram {len(self.expected)} respostas"

@cocotb.test()
async def test_com_scoreboard(dut):
    sb = Scoreboard()
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Adiciona valores esperados
    for i in range(10):
        sb.add_expected(i * 2)

    # Envia estímulos e coleta respostas
    for i in range(10):
        dut.input.value = i
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)
        sb.add_received(int(dut.output.value))

    sb.check()
```

### Driver e Monitor

```python
class Driver:
    """Envia transações para o DUT"""
    def __init__(self, dut):
        self.dut = dut

    async def send(self, data):
        self.dut.valid.value = 1
        self.dut.data.value = data
        await RisingEdge(self.dut.clk)
        while not self.dut.ready.value:
            await RisingEdge(self.dut.clk)
        self.dut.valid.value = 0

class Monitor:
    """Observa saídas do DUT"""
    def __init__(self, dut, callback):
        self.dut = dut
        self.callback = callback

    async def run(self):
        while True:
            await RisingEdge(self.dut.clk)
            if self.dut.out_valid.value:
                self.callback(int(self.dut.out_data.value))

@cocotb.test()
async def test_com_driver_monitor(dut):
    results = []

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    driver = Driver(dut)
    monitor = Monitor(dut, lambda x: results.append(x))

    cocotb.start_soon(monitor.run())

    # Envia dados
    for i in range(10):
        await driver.send(i)

    await ClockCycles(dut.clk, 5)  # Espera pipeline

    # Verifica resultados
    assert results == list(range(10))
```

### Cobertura funcional simples

```python
class Coverage:
    def __init__(self):
        self.bins = {}

    def sample(self, name, value, bins):
        if name not in self.bins:
            self.bins[name] = {b: 0 for b in bins}

        for b in bins:
            if isinstance(b, range) and value in b:
                self.bins[name][b] += 1
            elif value == b:
                self.bins[name][b] += 1

    def report(self):
        for name, bins in self.bins.items():
            print(f"\n{name}:")
            for b, count in bins.items():
                status = "HIT" if count > 0 else "MISS"
                print(f"  {b}: {count} ({status})")

@cocotb.test()
async def test_com_cobertura(dut):
    cov = Coverage()
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    for _ in range(1000):
        val = random.randint(0, 255)
        dut.input.value = val
        await RisingEdge(dut.clk)

        # Amostra cobertura
        cov.sample("input_ranges", val, [
            range(0, 64),
            range(64, 128),
            range(128, 192),
            range(192, 256)
        ])

    cov.report()
```

---

## 14. Boas Práticas

### 1. Use funções auxiliares

```python
async def reset_dut(dut, cycles=2):
    """Reset padronizado"""
    dut.rst.value = 1
    await ClockCycles(dut.clk, cycles)
    dut.rst.value = 0
    await FallingEdge(dut.clk)

async def apply_and_check(dut, inputs, expected):
    """Aplica entradas e verifica saída"""
    for signal, value in inputs.items():
        getattr(dut, signal).value = value
    await Timer(10, unit="ns")
    for signal, value in expected.items():
        assert int(getattr(dut, signal).value) == value
```

### 2. Evite race conditions

```python
# RUIM - pode ter race condition
@cocotb.test()
async def test_ruim(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await RisingEdge(dut.clk)
    # Lê imediatamente após rising edge - valor pode não estar estável
    valor = int(dut.data.value)

# BOM - espera falling edge para ler
@cocotb.test()
async def test_bom(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)  # Espera valor estabilizar
    valor = int(dut.data.value)
```

### 3. Use logging

```python
@cocotb.test()
async def test_com_log(dut):
    dut._log.info("Iniciando teste")
    dut._log.debug(f"Valor de entrada: {dut.a.value}")
    dut._log.warning("Atenção: valor próximo do limite")
    dut._log.error("Erro detectado!")
```

### 4. Docstrings descritivas

```python
@cocotb.test()
async def test_overflow_handling(dut):
    """
    Verifica comportamento de overflow do contador.

    Condições testadas:
    - Contador em valor máximo (0xFF)
    - Incremento com enable ativo
    - Deve voltar a 0x00 sem travar
    """
    pass
```

### 5. Parametrize testes

```python
import itertools

TEST_CASES = [
    (0, 0, 0),
    (1, 1, 2),
    (255, 1, 0),  # overflow
]

@cocotb.test()
async def test_parametrizado(dut):
    for a, b, expected in TEST_CASES:
        dut.a.value = a
        dut.b.value = b
        await Timer(10, unit="ns")

        result = int(dut.sum.value)
        assert result == expected, f"{a} + {b}: esperado {expected}, obtido {result}"
```

---

## 15. Debugging

### Verificando sinais X e Z

```python
@cocotb.test()
async def test_sinais_indefinidos(dut):
    await Timer(1, unit="ns")

    # Verifica se sinal é resolvível (não é X nem Z)
    if not dut.sinal.value.is_resolvable:
        dut._log.warning(f"Sinal indefinido: {dut.sinal.value.binstr}")

    # Força valor conhecido
    dut.sinal.value = 0
```

### Imprimindo estado do DUT

```python
def print_state(dut):
    """Imprime estado atual do DUT"""
    print(f"""
    === Estado do DUT ===
    clk     = {dut.clk.value}
    rst     = {dut.rst.value}
    input   = {int(dut.input.value):08b} ({int(dut.input.value)})
    output  = {int(dut.output.value):08b} ({int(dut.output.value)})
    """)

@cocotb.test()
async def test_debug(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    for i in range(5):
        dut.input.value = i
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)
        print_state(dut)
```

### Usando waveforms

```bash
# Gera waveform
make WAVES=1 run

# Visualiza com GTKWave
gtkwave dump.fst &
```

### Assert com mensagens detalhadas

```python
def assert_equal(actual, expected, msg=""):
    """Assert com mensagem formatada"""
    assert actual == expected, \
        f"{msg}\n  Esperado: {expected} ({expected:#x})\n  Obtido:   {actual} ({actual:#x})"

@cocotb.test()
async def test_com_assert_detalhado(dut):
    dut.a.value = 5
    dut.b.value = 3
    await Timer(10, unit="ns")

    assert_equal(
        int(dut.sum.value),
        8,
        "Falha na adição 5 + 3"
    )
```

---

## 16. Referência Rápida

### Triggers mais usados

| Trigger | Descrição |
|---------|-----------|
| `Timer(time, unit="ns")` | Espera por tempo |
| `RisingEdge(signal)` | Borda de subida |
| `FallingEdge(signal)` | Borda de descida |
| `Edge(signal)` | Qualquer transição |
| `ClockCycles(clk, n)` | N ciclos de clock |
| `First(*triggers)` | Primeiro trigger (OR) |
| `Combine(*triggers)` | Todos triggers (AND) |

### Atribuição de sinais

```python
dut.sinal.value = 42        # Inteiro
dut.sinal.value = 0xFF      # Hexadecimal
dut.sinal.value = 0b1010    # Binário
dut.sinal.value = "1010"    # String binária
```

### Leitura de sinais

```python
int(dut.sinal.value)        # Como inteiro
dut.sinal.value.binstr      # Como string binária
dut.sinal.value.is_resolvable  # Verifica X/Z
```

### Clock

```python
from cocotb.clock import Clock
cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
```

### Logging

```python
dut._log.info("Mensagem informativa")
dut._log.debug("Debug")
dut._log.warning("Aviso")
dut._log.error("Erro")
```

### Comandos Make

```bash
make run                        # Executa testes
make WAVES=1 run               # Com waveforms
make COCOTB_TESTCASE=test_x run # Teste específico
make clean                      # Limpa build
```

---

## Recursos Adicionais

- **Documentação oficial**: https://docs.cocotb.org/
- **GitHub**: https://github.com/cocotb/cocotb
- **Exemplos**: https://github.com/cocotb/cocotb/tree/master/examples

---

*Tutorial criado para uso com Verilator e SystemVerilog. Adaptável para outros simuladores e linguagens HDL.*
