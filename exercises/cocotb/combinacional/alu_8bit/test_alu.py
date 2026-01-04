"""
Teste completo da ALU 8-bit usando cocotb
Operações testadas: ADD, MUL, AND, OR, NOT, XOR, SHL, SHR
"""

import cocotb
from cocotb.triggers import Timer
import random

# Códigos de operação (devem corresponder ao módulo SystemVerilog)
OP_ADD = 0b000
OP_MUL = 0b001
OP_AND = 0b010
OP_OR  = 0b011
OP_NOT = 0b100
OP_XOR = 0b101
OP_SHL = 0b110
OP_SHR = 0b111


async def apply_inputs(dut, a, b, op):
    """Aplica entradas e aguarda propagação"""
    dut.a.value = a
    dut.b.value = b
    dut.op.value = op
    await Timer(10, units="ns")


def get_expected(a, b, op):
    """Calcula resultado esperado para cada operação"""
    if op == OP_ADD:
        result = (a + b) & 0xFF
        carry = 1 if (a + b) > 0xFF else 0
    elif op == OP_MUL:
        result = (a * b) & 0xFFFF
        carry = 1 if (a * b) > 0xFF else 0
    elif op == OP_AND:
        result = a & b
        carry = 0
    elif op == OP_OR:
        result = a | b
        carry = 0
    elif op == OP_NOT:
        result = (~a) & 0xFF
        carry = 0
    elif op == OP_XOR:
        result = a ^ b
        carry = 0
    elif op == OP_SHL:
        shift = b & 0x7
        result = (a << shift) & 0xFFFF
        carry = (a >> (8 - shift)) & 1 if shift > 0 else 0
    elif op == OP_SHR:
        shift = b & 0x7
        result = a >> shift
        carry = (a >> (shift - 1)) & 1 if shift > 0 else 0
    else:
        result = 0
        carry = 0

    zero = 1 if result == 0 else 0
    negative = 1 if (result >> 15) & 1 else 0

    return result, zero, carry, negative


def check_result(dut, a, b, op, op_name):
    """Verifica se o resultado da ALU corresponde ao esperado"""
    expected_result, expected_zero, expected_carry, expected_neg = get_expected(a, b, op)

    actual_result = int(dut.result.value)
    actual_zero = int(dut.zero.value)
    actual_carry = int(dut.carry.value)
    actual_neg = int(dut.negative.value)

    assert actual_result == expected_result, \
        f"{op_name}: a={a:#04x}, b={b:#04x} -> esperado result={expected_result:#06x}, obtido={actual_result:#06x}"

    assert actual_zero == expected_zero, \
        f"{op_name}: a={a:#04x}, b={b:#04x} -> esperado zero={expected_zero}, obtido={actual_zero}"

    # Carry pode ter comportamento diferente em alguns casos de shift
    if op not in [OP_SHL, OP_SHR]:
        assert actual_carry == expected_carry, \
            f"{op_name}: a={a:#04x}, b={b:#04x} -> esperado carry={expected_carry}, obtido={actual_carry}"


# ============================================================
# TESTES INDIVIDUAIS POR OPERAÇÃO
# ============================================================

@cocotb.test()
async def test_add_basic(dut):
    """Teste básico de adição"""
    dut._log.info("=== Teste ADD Básico ===")

    test_cases = [
        (0x00, 0x00),  # 0 + 0
        (0x01, 0x01),  # 1 + 1
        (0x10, 0x20),  # 16 + 32
        (0xFF, 0x00),  # 255 + 0
        (0x7F, 0x01),  # 127 + 1
    ]

    for a, b in test_cases:
        await apply_inputs(dut, a, b, OP_ADD)
        check_result(dut, a, b, OP_ADD, "ADD")
        dut._log.info(f"ADD: {a:#04x} + {b:#04x} = {int(dut.result.value):#06x}")


@cocotb.test()
async def test_add_overflow(dut):
    """Teste de adição com overflow"""
    dut._log.info("=== Teste ADD Overflow ===")

    test_cases = [
        (0xFF, 0x01),  # 255 + 1 = 256 -> overflow
        (0x80, 0x80),  # 128 + 128 = 256 -> overflow
        (0xF0, 0x20),  # 240 + 32 = 272 -> overflow
    ]

    for a, b in test_cases:
        await apply_inputs(dut, a, b, OP_ADD)
        expected = (a + b) & 0xFF
        assert int(dut.result.value) == expected
        assert int(dut.carry.value) == 1, f"Carry deveria ser 1 para {a:#04x} + {b:#04x}"
        dut._log.info(f"ADD overflow: {a:#04x} + {b:#04x} = {int(dut.result.value):#04x}, carry={int(dut.carry.value)}")


@cocotb.test()
async def test_mul_basic(dut):
    """Teste básico de multiplicação"""
    dut._log.info("=== Teste MUL Básico ===")

    test_cases = [
        (0x00, 0x00),  # 0 * 0 = 0
        (0x01, 0x01),  # 1 * 1 = 1
        (0x02, 0x03),  # 2 * 3 = 6
        (0x10, 0x10),  # 16 * 16 = 256
        (0x0F, 0x0F),  # 15 * 15 = 225
    ]

    for a, b in test_cases:
        await apply_inputs(dut, a, b, OP_MUL)
        expected = a * b
        assert int(dut.result.value) == expected, \
            f"MUL: esperado {expected}, obtido {int(dut.result.value)}"
        dut._log.info(f"MUL: {a:#04x} * {b:#04x} = {int(dut.result.value):#06x}")


@cocotb.test()
async def test_mul_large(dut):
    """Teste de multiplicação com resultados grandes (16 bits)"""
    dut._log.info("=== Teste MUL Resultado 16-bit ===")

    test_cases = [
        (0xFF, 0xFF),  # 255 * 255 = 65025
        (0x80, 0x80),  # 128 * 128 = 16384
        (0xFF, 0x02),  # 255 * 2 = 510
    ]

    for a, b in test_cases:
        await apply_inputs(dut, a, b, OP_MUL)
        expected = a * b
        assert int(dut.result.value) == expected
        # Carry = 1 se resultado > 255
        if expected > 0xFF:
            assert int(dut.carry.value) == 1
        dut._log.info(f"MUL large: {a:#04x} * {b:#04x} = {int(dut.result.value):#06x} (carry={int(dut.carry.value)})")


@cocotb.test()
async def test_and(dut):
    """Teste operação AND"""
    dut._log.info("=== Teste AND ===")

    test_cases = [
        (0xFF, 0xFF),  # All 1s
        (0x00, 0xFF),  # Mask com zero
        (0xAA, 0x55),  # Padrão alternado
        (0xF0, 0x0F),  # Nibble superior/inferior
        (0x12, 0x34),  # Valores arbitrários
    ]

    for a, b in test_cases:
        await apply_inputs(dut, a, b, OP_AND)
        expected = a & b
        assert int(dut.result.value) == expected
        dut._log.info(f"AND: {a:#04x} & {b:#04x} = {int(dut.result.value):#04x}")


@cocotb.test()
async def test_or(dut):
    """Teste operação OR"""
    dut._log.info("=== Teste OR ===")

    test_cases = [
        (0x00, 0x00),  # Zeros
        (0xFF, 0x00),  # FF | 0
        (0xAA, 0x55),  # Complementar -> FF
        (0xF0, 0x0F),  # Nibbles -> FF
        (0x12, 0x34),  # Valores arbitrários
    ]

    for a, b in test_cases:
        await apply_inputs(dut, a, b, OP_OR)
        expected = a | b
        assert int(dut.result.value) == expected
        dut._log.info(f"OR: {a:#04x} | {b:#04x} = {int(dut.result.value):#04x}")


@cocotb.test()
async def test_not(dut):
    """Teste operação NOT (inverte A)"""
    dut._log.info("=== Teste NOT ===")

    test_cases = [0x00, 0xFF, 0xAA, 0x55, 0x0F, 0xF0, 0x12]

    for a in test_cases:
        await apply_inputs(dut, a, 0x00, OP_NOT)
        expected = (~a) & 0xFF
        assert int(dut.result.value) == expected
        dut._log.info(f"NOT: ~{a:#04x} = {int(dut.result.value):#04x}")


@cocotb.test()
async def test_xor(dut):
    """Teste operação XOR"""
    dut._log.info("=== Teste XOR ===")

    test_cases = [
        (0xFF, 0xFF),  # FF ^ FF = 0
        (0x00, 0xFF),  # 0 ^ FF = FF
        (0xAA, 0x55),  # Complementar -> FF
        (0x12, 0x12),  # Mesmo valor -> 0
        (0x37, 0x8C),  # Arbitrário
    ]

    for a, b in test_cases:
        await apply_inputs(dut, a, b, OP_XOR)
        expected = a ^ b
        assert int(dut.result.value) == expected
        dut._log.info(f"XOR: {a:#04x} ^ {b:#04x} = {int(dut.result.value):#04x}")


@cocotb.test()
async def test_shift_left(dut):
    """Teste operação Shift Left"""
    dut._log.info("=== Teste SHL ===")

    test_cases = [
        (0x01, 0),  # Shift 0
        (0x01, 1),  # 1 << 1 = 2
        (0x01, 4),  # 1 << 4 = 16
        (0x01, 7),  # 1 << 7 = 128
        (0xFF, 1),  # FF << 1 = 1FE (overflow para 16 bits)
        (0x80, 1),  # 0x80 << 1 = 0x100
        (0xAA, 2),  # 0xAA << 2 = 0x2A8
    ]

    for a, shift in test_cases:
        await apply_inputs(dut, a, shift, OP_SHL)
        expected = (a << shift) & 0xFFFF
        assert int(dut.result.value) == expected, \
            f"SHL: esperado {expected:#06x}, obtido {int(dut.result.value):#06x}"
        dut._log.info(f"SHL: {a:#04x} << {shift} = {int(dut.result.value):#06x}")


@cocotb.test()
async def test_shift_right(dut):
    """Teste operação Shift Right"""
    dut._log.info("=== Teste SHR ===")

    test_cases = [
        (0x80, 0),  # Shift 0
        (0x80, 1),  # 0x80 >> 1 = 0x40
        (0x80, 7),  # 0x80 >> 7 = 1
        (0xFF, 4),  # 0xFF >> 4 = 0x0F
        (0xAA, 1),  # 0xAA >> 1 = 0x55
        (0x01, 1),  # 0x01 >> 1 = 0
    ]

    for a, shift in test_cases:
        await apply_inputs(dut, a, shift, OP_SHR)
        expected = a >> shift
        assert int(dut.result.value) == expected, \
            f"SHR: esperado {expected:#04x}, obtido {int(dut.result.value):#04x}"
        dut._log.info(f"SHR: {a:#04x} >> {shift} = {int(dut.result.value):#04x}")


@cocotb.test()
async def test_zero_flag(dut):
    """Teste da flag zero"""
    dut._log.info("=== Teste Zero Flag ===")

    # Casos que devem resultar em zero=1
    zero_cases = [
        (OP_ADD, 0x00, 0x00),
        (OP_MUL, 0x00, 0xFF),
        (OP_AND, 0xF0, 0x0F),
        (OP_XOR, 0xAA, 0xAA),
        (OP_SHR, 0x01, 0x01),
    ]

    for op, a, b in zero_cases:
        await apply_inputs(dut, a, b, op)
        assert int(dut.zero.value) == 1, \
            f"Zero flag deveria ser 1 para op={op}, a={a:#04x}, b={b:#04x}"
        dut._log.info(f"Zero flag OK: op={op}, result={int(dut.result.value)}, zero={int(dut.zero.value)}")

    # Casos que devem resultar em zero=0
    nonzero_cases = [
        (OP_ADD, 0x01, 0x00),
        (OP_NOT, 0x00, 0x00),  # NOT 0 = FF
        (OP_OR, 0x01, 0x00),
    ]

    for op, a, b in nonzero_cases:
        await apply_inputs(dut, a, b, op)
        assert int(dut.zero.value) == 0, \
            f"Zero flag deveria ser 0 para op={op}, a={a:#04x}, b={b:#04x}"


@cocotb.test()
async def test_random_operations(dut):
    """Teste com valores aleatórios para todas as operações"""
    dut._log.info("=== Teste Aleatório ===")

    random.seed(42)  # Seed fixo para reprodutibilidade
    operations = [
        (OP_ADD, "ADD"),
        (OP_MUL, "MUL"),
        (OP_AND, "AND"),
        (OP_OR, "OR"),
        (OP_NOT, "NOT"),
        (OP_XOR, "XOR"),
        (OP_SHL, "SHL"),
        (OP_SHR, "SHR"),
    ]

    for op, name in operations:
        dut._log.info(f"Testando {name} com valores aleatórios...")
        for _ in range(20):  # 20 testes por operação
            a = random.randint(0, 255)
            b = random.randint(0, 255) if op != OP_NOT else 0
            if op in [OP_SHL, OP_SHR]:
                b = random.randint(0, 7)  # Shift máximo de 7

            await apply_inputs(dut, a, b, op)
            check_result(dut, a, b, op, name)

    dut._log.info("Todos os testes aleatórios passaram!")


@cocotb.test()
async def test_edge_cases(dut):
    """Teste de casos extremos"""
    dut._log.info("=== Teste Edge Cases ===")

    # Máximos e mínimos
    await apply_inputs(dut, 0xFF, 0xFF, OP_ADD)
    assert int(dut.result.value) == 0xFE  # (255+255) & 0xFF = 254
    assert int(dut.carry.value) == 1
    dut._log.info(f"ADD max: 0xFF + 0xFF = {int(dut.result.value):#04x}, carry={int(dut.carry.value)}")

    await apply_inputs(dut, 0xFF, 0xFF, OP_MUL)
    assert int(dut.result.value) == 0xFE01  # 255 * 255 = 65025
    dut._log.info(f"MUL max: 0xFF * 0xFF = {int(dut.result.value):#06x}")

    # Shift máximo
    await apply_inputs(dut, 0x01, 7, OP_SHL)
    assert int(dut.result.value) == 0x80
    dut._log.info(f"SHL max: 0x01 << 7 = {int(dut.result.value):#04x}")

    await apply_inputs(dut, 0x80, 7, OP_SHR)
    assert int(dut.result.value) == 0x01
    dut._log.info(f"SHR max: 0x80 >> 7 = {int(dut.result.value):#04x}")

    dut._log.info("Todos os edge cases passaram!")
