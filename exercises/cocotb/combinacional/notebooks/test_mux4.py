
import cocotb
from cocotb.triggers import Timer
import random

@cocotb.test()
async def test_mux_sel_a(dut):
    """Testa selecao de entrada A (sel=00)"""
    dut.sel.value = 0b00
    dut.a.value = 0xAA
    dut.b.value = 0xBB
    dut.c.value = 0xCC
    dut.d.value = 0xDD
    
    await Timer(10, unit="ns")
    
    assert int(dut.y.value) == 0xAA, f"Esperado 0xAA, obtido {hex(int(dut.y.value))}"
    dut._log.info(f"sel=00: y = {hex(int(dut.y.value))} (esperado 0xAA) OK")

@cocotb.test()
async def test_mux_sel_b(dut):
    """Testa selecao de entrada B (sel=01)"""
    dut.sel.value = 0b01
    dut.a.value = 0xAA
    dut.b.value = 0xBB
    dut.c.value = 0xCC
    dut.d.value = 0xDD
    
    await Timer(10, unit="ns")
    
    assert int(dut.y.value) == 0xBB, f"Esperado 0xBB, obtido {hex(int(dut.y.value))}"
    dut._log.info(f"sel=01: y = {hex(int(dut.y.value))} (esperado 0xBB) OK")

@cocotb.test()
async def test_mux_sel_c(dut):
    """Testa selecao de entrada C (sel=10)"""
    dut.sel.value = 0b10
    dut.a.value = 0xAA
    dut.b.value = 0xBB
    dut.c.value = 0xCC
    dut.d.value = 0xDD
    
    await Timer(10, unit="ns")
    
    assert int(dut.y.value) == 0xCC, f"Esperado 0xCC, obtido {hex(int(dut.y.value))}"
    dut._log.info(f"sel=10: y = {hex(int(dut.y.value))} (esperado 0xCC) OK")

@cocotb.test()
async def test_mux_sel_d(dut):
    """Testa selecao de entrada D (sel=11)"""
    dut.sel.value = 0b11
    dut.a.value = 0xAA
    dut.b.value = 0xBB
    dut.c.value = 0xCC
    dut.d.value = 0xDD
    
    await Timer(10, unit="ns")
    
    assert int(dut.y.value) == 0xDD, f"Esperado 0xDD, obtido {hex(int(dut.y.value))}"
    dut._log.info(f"sel=11: y = {hex(int(dut.y.value))} (esperado 0xDD) OK")

@cocotb.test()
async def test_mux_random(dut):
    """Testa MUX com valores aleatorios"""
    random.seed(42)
    
    for _ in range(20):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        d = random.randint(0, 255)
        sel = random.randint(0, 3)
        
        dut.a.value = a
        dut.b.value = b
        dut.c.value = c
        dut.d.value = d
        dut.sel.value = sel
        
        await Timer(10, unit="ns")
        
        expected = [a, b, c, d][sel]
        assert int(dut.y.value) == expected,             f"sel={sel}: esperado {expected}, obtido {int(dut.y.value)}"
    
    dut._log.info("20 testes aleatorios passaram!")
