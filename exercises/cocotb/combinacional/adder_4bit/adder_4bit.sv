// ============================================================
// Adder 4-bit - Somador simples de 4 bits com carry
// ============================================================

module adder_4bit (
    input  logic [3:0] a,       // Operando A
    input  logic [3:0] b,       // Operando B
    input  logic       cin,     // Carry in
    output logic [3:0] sum,     // Soma
    output logic       cout     // Carry out
);

    logic [4:0] result;

    assign result = {1'b0, a} + {1'b0, b} + {4'b0, cin};
    assign sum    = result[3:0];
    assign cout   = result[4];

endmodule
