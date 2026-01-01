// Priority Encoder 8-to-3
// Combinational circuit - returns the index of the highest priority bit set
// Priority: bit 7 (highest) to bit 0 (lowest)

module priority_encoder (
  input  logic [7:0] in,      // 8 input lines
  output logic [2:0] out,     // 3-bit encoded output
  output logic       valid    // high if any input is active
);

  always_comb begin
    valid = |in;  // valid if any bit is set

    casez (in)
      8'b1???????: out = 3'd7;
      8'b01??????: out = 3'd6;
      8'b001?????: out = 3'd5;
      8'b0001????: out = 3'd4;
      8'b00001???: out = 3'd3;
      8'b000001??: out = 3'd2;
      8'b0000001?: out = 3'd1;
      8'b00000001: out = 3'd0;
      default:     out = 3'd0;  // no input active
    endcase
  end

endmodule
