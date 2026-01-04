# ============================================================
# Makefile - Adder 4-bit - cocotb + Verilator + SystemVerilog
# ============================================================

SIM ?= verilator
TOPLEVEL_LANG ?= verilog

TOPLEVEL ?= adder_4bit
COCOTB_TEST_MODULES ?= test_adder

SIM_BUILD ?= sim_build
VERILOG_SOURCES += $(PWD)/adder_4bit.sv

EXTRA_ARGS += --sv --timescale 1ns/1ps -Wall

ifeq ($(WAVES),1)
  EXTRA_ARGS += --trace --trace-fst --trace-structs
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: run waves cleanall

run: sim

waves:
	rm -rf $(SIM_BUILD)
	@$(MAKE) WAVES=1 sim

cleanall:: clean
	rm -rf $(SIM_BUILD) __pycache__ *.vcd *.fst *.ghw *.xml
