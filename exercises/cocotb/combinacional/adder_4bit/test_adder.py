"""
Teste do Adder 4-bit usando cocotb
"""

import cocotb
from cocotb.triggers import Timer


async def apply_inputs(dut, a, b, cin):
    """Aplica entradas e aguarda propagação"""
    dut.a.value = a
    dut.b.value = b
    dut.cin.value = cin
    await Timer(10, unit="ns")


@cocotb.test()
async def test_basic_addition(dut):
    """Teste de adições básicas"""
    dut._log.info("=== Teste Adições Básicas ===")

    test_cases = [
        (0, 0, 0),   # 0 + 0 + 0 = 0
        (1, 1, 0),   # 1 + 1 = 2
        (5, 3, 0),   # 5 + 3 = 8
        (7, 7, 0),   # 7 + 7 = 14
        (0xF, 0, 0), # 15 + 0 = 15
    ]

    for a, b, cin in test_cases:
        await apply_inputs(dut, a, b, cin)
        expected_sum = (a + b + cin) & 0xF
        expected_cout = 1 if (a + b + cin) > 0xF else 0

        assert int(dut.sum.value) == expected_sum, \
            f"Sum: esperado {expected_sum}, obtido {int(dut.sum.value)}"
        assert int(dut.cout.value) == expected_cout, \
            f"Cout: esperado {expected_cout}, obtido {int(dut.cout.value)}"

        dut._log.info(f"{a} + {b} + {cin} = {int(dut.sum.value)}, cout={int(dut.cout.value)}")


@cocotb.test()
async def test_carry_in(dut):
    """Teste com carry in"""
    dut._log.info("=== Teste Carry In ===")

    test_cases = [
        (0, 0, 1),   # 0 + 0 + 1 = 1
        (1, 1, 1),   # 1 + 1 + 1 = 3
        (7, 7, 1),   # 7 + 7 + 1 = 15
        (0xF, 0, 1), # 15 + 0 + 1 = 16 -> overflow
    ]

    for a, b, cin in test_cases:
        await apply_inputs(dut, a, b, cin)
        expected_sum = (a + b + cin) & 0xF
        expected_cout = 1 if (a + b + cin) > 0xF else 0

        assert int(dut.sum.value) == expected_sum
        assert int(dut.cout.value) == expected_cout

        dut._log.info(f"{a} + {b} + {cin} = {int(dut.sum.value)}, cout={int(dut.cout.value)}")


@cocotb.test()
async def test_overflow(dut):
    """Teste de overflow (carry out)"""
    dut._log.info("=== Teste Overflow ===")

    overflow_cases = [
        (0xF, 0x1, 0),  # 15 + 1 = 16 -> cout=1, sum=0
        (0xF, 0xF, 0),  # 15 + 15 = 30 -> cout=1, sum=14
        (0x8, 0x8, 0),  # 8 + 8 = 16 -> cout=1, sum=0
        (0xF, 0xF, 1),  # 15 + 15 + 1 = 31 -> cout=1, sum=15
    ]

    for a, b, cin in overflow_cases:
        await apply_inputs(dut, a, b, cin)

        assert int(dut.cout.value) == 1, \
            f"Cout deveria ser 1 para {a} + {b} + {cin}"

        expected_sum = (a + b + cin) & 0xF
        assert int(dut.sum.value) == expected_sum

        dut._log.info(f"Overflow: {a} + {b} + {cin} = {int(dut.sum.value)}, cout=1")


@cocotb.test()
async def test_exhaustive(dut):
    """Teste exaustivo de todas as combinações"""
    dut._log.info("=== Teste Exaustivo (todas combinações) ===")

    errors = 0
    for a in range(16):
        for b in range(16):
            for cin in range(2):
                await apply_inputs(dut, a, b, cin)

                expected_sum = (a + b + cin) & 0xF
                expected_cout = 1 if (a + b + cin) > 0xF else 0

                if int(dut.sum.value) != expected_sum:
                    errors += 1
                    dut._log.error(f"ERRO: {a}+{b}+{cin} sum={int(dut.sum.value)}, esperado={expected_sum}")

                if int(dut.cout.value) != expected_cout:
                    errors += 1
                    dut._log.error(f"ERRO: {a}+{b}+{cin} cout={int(dut.cout.value)}, esperado={expected_cout}")

    assert errors == 0, f"Encontrados {errors} erros no teste exaustivo"
    dut._log.info(f"Teste exaustivo: 512 combinações testadas com sucesso!")
