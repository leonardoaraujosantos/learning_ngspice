module mini_alu_formal;

  (* anyseq *) logic [3:0] a;
  (* anyseq *) logic [3:0] b;
  (* anyseq *) logic [1:0] op;

  logic [3:0] y;
  logic z, n, c;

  mini_alu dut (.*);

  // SPEC de referência
  logic [4:0] ref_add;
  logic [4:0] ref_sub;
  logic [3:0] ref_y;
  logic       ref_c;   // borrow em SUB, carry em ADD
  logic       ref_z;
  logic       ref_n;

  always_comb begin
    ref_add = {1'b0, a} + {1'b0, b};
    ref_sub = {1'b0, a} - {1'b0, b};

    ref_y = 4'h0;
    ref_c = 1'b0;

    unique case (op)
      2'b00: begin // ADD
        ref_y = ref_add[3:0];
        ref_c = ref_add[4];              // carry
      end

      2'b01: begin // SUB (borrow = 1 quando a<b)
        ref_y = ref_sub[3:0];
        ref_c = (a < b);                 // definição clara e sem ambiguidades
      end

      2'b10: begin // AND
        ref_y = (a & b);
        ref_c = 1'b0;
      end

      2'b11: begin // XOR
        ref_y = (a ^ b);
        ref_c = 1'b0;
      end
    endcase

    ref_z = (ref_y == 4'd0);
    ref_n = ref_y[3];

    // ASSERT principal: DUT == SPEC
    assert(y == ref_y);
    assert(c == ref_c);
    assert(z == ref_z);
    assert(n == ref_n);
  end

  // Covers: gerar alguns casos interessantes
  always_comb begin
    // Overflow em ADD (carry=1)
    cover(op == 2'b00 && c == 1'b1);

    // Borrow em SUB (a<b)
    cover(op == 2'b01 && c == 1'b1);

    // Resultado zero em algum op
    cover(z == 1'b1);

    // Caso específico para visualizar
    cover(op == 2'b00 && a == 4'hF && b == 4'h1 && y == 4'h0 && c == 1'b1);
  end

endmodule
