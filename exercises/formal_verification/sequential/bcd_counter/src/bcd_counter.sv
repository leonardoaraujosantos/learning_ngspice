module bcd_counter (
  input  logic       clk,
  input  logic       rst,   // reset síncrono
  input  logic       en,
  output logic [3:0] q
);

  always_ff @(posedge clk) begin
    if (rst)
      q <= 4'd0;
    else if (en) begin
      if (q == 4'd9) q <= 4'd0;
      else          q <= q + 4'd1;
    end
  end

endmodule
