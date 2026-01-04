
// Comparador de 8 bits
module comparator (
    input  logic [7:0] a,
    input  logic [7:0] b,
    output logic       eq,    // a == b
    output logic       gt,    // a > b
    output logic       lt     // a < b
);

    assign eq = (a == b);
    assign gt = (a > b);
    assign lt = (a < b);

endmodule
