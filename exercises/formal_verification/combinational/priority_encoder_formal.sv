// Formal verification for priority_encoder (combinational)
// For combinational circuits, we use immediate assertions
// or a formal clock to sample the logic

module priority_encoder_formal;

  // Formal clock (used to sample combinational logic)
  (* gclk *) logic clk;

  // Free input - solver explores all possible values
  (* anyconst *) logic [7:0] in;

  logic [2:0] out;
  logic       valid;

  priority_encoder dut (
    .in(in),
    .out(out),
    .valid(valid)
  );

  // ----------------------------
  // ASSERTIONS (properties)
  // ----------------------------

  // A1) valid should be high if and only if at least one input is set
  always_comb begin
    assert(valid == |in);
  end

  // A2) Output should be in valid range [0-7]
  always_comb begin
    assert(out <= 3'd7);
  end

  // A3) If valid, the corresponding input bit must be set
  always_comb begin
    if (valid)
      assert(in[out] == 1'b1);
  end

  // A4) If valid, no higher priority bit should be set
  //     (all bits above 'out' must be zero)
  always_comb begin
    if (valid) begin
      case (out)
        3'd7: ; // highest priority, nothing above
        3'd6: assert(in[7] == 1'b0);
        3'd5: assert(in[7:6] == 2'b00);
        3'd4: assert(in[7:5] == 3'b000);
        3'd3: assert(in[7:4] == 4'b0000);
        3'd2: assert(in[7:3] == 5'b00000);
        3'd1: assert(in[7:2] == 6'b000000);
        3'd0: assert(in[7:1] == 7'b0000000);
      endcase
    end
  end

  // A5) If no input is set, output should be 0 and valid low
  always_comb begin
    if (in == 8'b0) begin
      assert(out == 3'd0);
      assert(valid == 1'b0);
    end
  end

  // ----------------------------
  // COVER (reachability)
  // ----------------------------

  // Verify each output value is reachable
  always_comb begin
    cover(valid && out == 3'd0);
    cover(valid && out == 3'd1);
    cover(valid && out == 3'd2);
    cover(valid && out == 3'd3);
    cover(valid && out == 3'd4);
    cover(valid && out == 3'd5);
    cover(valid && out == 3'd6);
    cover(valid && out == 3'd7);
    cover(!valid);
  end

  // Cover specific interesting cases
  always_comb begin
    // Only one bit set
    cover(in == 8'b10000000 && out == 3'd7);
    cover(in == 8'b00000001 && out == 3'd0);

    // Multiple bits set - highest wins
    cover(in == 8'b11111111 && out == 3'd7);
    cover(in == 8'b00001111 && out == 3'd3);
  end

endmodule
