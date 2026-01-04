module bcd_counter_formal;

  // Clock global formal
  (* gclk *) logic clk;

  // Entradas livres
  (* anyseq *) logic rst;
  (* anyseq *) logic en;

  logic [3:0] q;

  bcd_counter dut (
    .clk(clk),
    .rst(rst),
    .en(en),
    .q(q)
  );

  // ----------------------------
  // Controle do $past
  // ----------------------------
  logic past_valid = 1'b0;
  always_ff @(posedge clk)
    past_valid <= 1'b1;

  // ----------------------------
  // ASSUMPTIONS (ambiente)
  // ----------------------------

  // Garante que o sistema começa em reset
  initial assume(rst);

  // Reset só pode acontecer no início
  always_ff @(posedge clk)
    if (past_valid && $past(!rst))
      assume(!rst);

  // ----------------------------
  // ASSERTIONS
  // ----------------------------

  // A1) q sempre no intervalo BCD (após o reset inicial)
  always_ff @(posedge clk)
    if (past_valid)
      assert(q <= 4'd9);

  // A2) Reset síncrono domina
  always_ff @(posedge clk) begin
    if (past_valid && $past(rst)) begin
      assert(q == 4'd0);
    end
  end

  // A3/A4) Regras de transição
  always_ff @(posedge clk) begin
    if (past_valid &&
        !$past(rst) &&   // reset NÃO estava ativo
        !rst) begin     // reset NÃO está ativo agora

      // en=0 -> segura
      if (!$past(en))
        assert(q == $past(q));

      // en=1 -> incrementa / wrap
      if ($past(en)) begin
        if ($past(q) == 4'd9)
          assert(q == 4'd0);
        else
          assert(q == $past(q) + 4'd1);
      end

    end
  end

  // ----------------------------
  // COVER
  // ----------------------------

  always_ff @(posedge clk)
    cover(q == 4'd9);

  always_ff @(posedge clk)
    if (past_valid)
      cover($past(q) == 4'd9 && $past(en) && !rst && q == 4'd0);

endmodule
