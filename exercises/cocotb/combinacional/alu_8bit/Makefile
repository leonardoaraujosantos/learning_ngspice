# ============================================================
# Makefile - ALU 8-bit - cocotb + Verilator + SystemVerilog
# ============================================================

SIM ?= verilator
TOPLEVEL_LANG ?= verilog

TOPLEVEL ?= alu_8bit
COCOTB_TEST_MODULES ?= test_alu

SIM_BUILD ?= sim_build
VERILOG_SOURCES += $(PWD)/alu_8bit.sv

# Flags extras para o Verilator
EXTRA_ARGS += --sv --timescale 1ns/1ps -Wall

# Waves: quando WAVES=1, habilita tracing no compile
ifeq ($(WAVES),1)
  EXTRA_ARGS += --trace --trace-fst --trace-structs
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: run waves cleanall showwaves

run: sim

waves:
	rm -rf $(SIM_BUILD)
	@$(MAKE) WAVES=1 sim
	@$(MAKE) showwaves

showwaves:
	@echo "Wave files:"
	@find . -maxdepth 3 \( -name "*.fst" -o -name "*.vcd" \) -print || true

cleanall:: clean
	rm -rf $(SIM_BUILD) __pycache__ *.vcd *.fst *.ghw *.xml
