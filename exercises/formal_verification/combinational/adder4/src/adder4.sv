module adder4 (
  input  logic [3:0] a,
  input  logic [3:0] b,
  input  logic       cin,
  output logic [3:0] sum,
  output logic       cout
);
  logic [4:0] full;

  always_comb begin
    full = {1'b0, a} + {1'b0, b} + cin;
    sum  = full[3:0];
    cout = full[4];
  end
endmodule
