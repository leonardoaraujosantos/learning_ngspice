module adder4_formal;

  // Entradas livres para o solver
  (* anyseq *) logic [3:0] a;
  (* anyseq *) logic [3:0] b;
  (* anyseq *) logic       cin;

  logic [3:0] sum;
  logic       cout;

  adder4 dut (.*);

  // Especificação de referência (matemática)
  logic [4:0] ref;
  always_comb ref = {1'b0, a} + {1'b0, b} + cin;

  // ASSERT: DUT == spec
  always_comb begin
    assert({cout, sum} == ref);
  end

  // Covers úteis (para ver exemplos no trace)
  always_comb begin
    cover(a == 4'hF && b == 4'h1 && cin == 1'b0); // 15+1
    cover(sum == 4'h0 && cout == 1'b1);           // overflow
    cover(sum == 4'hA);                           // exemplo qualquer
  end

endmodule
