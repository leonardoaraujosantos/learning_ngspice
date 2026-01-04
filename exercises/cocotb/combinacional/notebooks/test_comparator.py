
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_equal(dut):
    """Testa a == b"""
    dut.a.value = 100
    dut.b.value = 100
    await Timer(10, unit="ns")
    
    assert int(dut.eq.value) == 1, "eq deveria ser 1"
    assert int(dut.gt.value) == 0, "gt deveria ser 0"
    assert int(dut.lt.value) == 0, "lt deveria ser 0"
    dut._log.info("100 == 100: OK")

@cocotb.test()
async def test_greater(dut):
    """Testa a > b"""
    dut.a.value = 200
    dut.b.value = 100
    await Timer(10, unit="ns")
    
    assert int(dut.eq.value) == 0, "eq deveria ser 0"
    assert int(dut.gt.value) == 1, "gt deveria ser 1"
    assert int(dut.lt.value) == 0, "lt deveria ser 0"
    dut._log.info("200 > 100: OK")

@cocotb.test()
async def test_less(dut):
    """Testa a < b"""
    dut.a.value = 50
    dut.b.value = 100
    await Timer(10, unit="ns")
    
    assert int(dut.eq.value) == 0, "eq deveria ser 0"
    assert int(dut.gt.value) == 0, "gt deveria ser 0"
    assert int(dut.lt.value) == 1, "lt deveria ser 1"
    dut._log.info("50 < 100: OK")

@cocotb.test()
async def test_exhaustive(dut):
    """Testa todas combinacoes de 0-15"""
    for a in range(16):
        for b in range(16):
            dut.a.value = a
            dut.b.value = b
            await Timer(1, unit="ns")
            
            assert int(dut.eq.value) == (1 if a == b else 0)
            assert int(dut.gt.value) == (1 if a > b else 0)
            assert int(dut.lt.value) == (1 if a < b else 0)
    
    dut._log.info("256 testes exaustivos passaram!")
