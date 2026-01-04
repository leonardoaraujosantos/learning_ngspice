import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge


@cocotb.test()
async def test_counter_0_59(dut):
    """Teste do contador 0 a 59"""

    # Cria clock de 10ns
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Reset inicial (muda sinais na falling edge para evitar race conditions)
    dut.rst.value = 1
    await RisingEdge(dut.clk)  # Aplica reset, count ← 0
    await FallingEdge(dut.clk)  # Espera estabilizar

    # Verifica que count está em 0 após reset
    assert int(dut.count.value) == 0, \
        f"Após reset, esperado 0, obtido {int(dut.count.value)}"

    # Libera reset na falling edge
    dut.rst.value = 0

    # Verifica contagem de 1 a 59
    for expected in range(1, 60):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)  # Espera valor estabilizar
        assert int(dut.count.value) == expected, \
            f"Esperado {expected}, obtido {int(dut.count.value)}"

    # Após 59 → deve voltar para 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert int(dut.count.value) == 0, \
        "Contador não voltou para 0 após 59"
