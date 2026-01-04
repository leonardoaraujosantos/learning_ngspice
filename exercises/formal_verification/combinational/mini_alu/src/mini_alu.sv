module mini_alu (
  input  logic [3:0] a,
  input  logic [3:0] b,
  input  logic [1:0] op,   // 00 add, 01 sub, 10 and, 11 xor
  output logic [3:0] y,
  output logic       z,    // y == 0
  output logic       n,    // y[3]
  output logic       c     // carry (add) / no-borrow (sub)
);

  logic [4:0] tmp;

  always_comb begin
    tmp = 5'd0;
    unique case (op)
      2'b00: begin // ADD
        tmp = {1'b0, a} + {1'b0, b};
        y   = tmp[3:0];
        c   = tmp[4];      // carry-out
      end

      2'b01: begin // SUB (a - b)
        tmp = {1'b0, a} - {1'b0, b};
        y   = tmp[3:0];
        // Em subtração unsigned, tmp[4] indica borrow:
        // se a>=b => tmp[4]=0, se a<b => tmp[4]=1 (underflow/borrow)
        c   = tmp[4]; // borrow=1 quando a<b
      end

      2'b10: begin // AND
        y = a & b;
        c = 1'b0;
      end

      2'b11: begin // XOR
        y = a ^ b;
        c = 1'b0;
      end
    endcase

    z = (y == 4'd0);
    n = y[3];
  end

endmodule
