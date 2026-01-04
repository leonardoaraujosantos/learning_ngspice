// ============================================================
// ALU 8-bit - Unidade Lógica Aritmética
// Operações: ADD, MUL, AND, OR, NOT, XOR, SHIFT LEFT, SHIFT RIGHT
// ============================================================

module alu_8bit (
    input  logic [7:0]  a,          // Operando A
    input  logic [7:0]  b,          // Operando B
    input  logic [2:0]  op,         // Código da operação
    output logic [15:0] result,     // Resultado (16 bits para MUL)
    output logic        zero,       // Flag: resultado é zero
    output logic        carry,      // Flag: carry/overflow
    output logic        negative    // Flag: resultado negativo (bit mais significativo)
);

    // Códigos de operação
    localparam OP_ADD   = 3'b000;   // Adição
    localparam OP_MUL   = 3'b001;   // Multiplicação
    localparam OP_AND   = 3'b010;   // AND lógico
    localparam OP_OR    = 3'b011;   // OR lógico
    localparam OP_NOT   = 3'b100;   // NOT (inverte A)
    localparam OP_XOR   = 3'b101;   // XOR lógico
    localparam OP_SHL   = 3'b110;   // Shift Left (A << B[2:0])
    localparam OP_SHR   = 3'b111;   // Shift Right (A >> B[2:0])

    // Sinais intermediários
    logic [8:0]  add_result;
    logic [15:0] mul_result;

    // Cálculos intermediários
    assign add_result = {1'b0, a} + {1'b0, b};
    assign mul_result = a * b;

    // Lógica combinacional principal
    always_comb begin
        // Valores default
        result   = 16'd0;
        carry    = 1'b0;

        case (op)
            OP_ADD: begin
                result = {8'd0, add_result[7:0]};
                carry  = add_result[8];
            end

            OP_MUL: begin
                result = mul_result;
                carry  = |mul_result[15:8];  // Carry se resultado > 255
            end

            OP_AND: begin
                result = {8'd0, a & b};
            end

            OP_OR: begin
                result = {8'd0, a | b};
            end

            OP_NOT: begin
                result = {8'd0, ~a};
            end

            OP_XOR: begin
                result = {8'd0, a ^ b};
            end

            OP_SHL: begin
                result = {8'd0, a} << b[2:0];
                carry  = (b[2:0] != 0) ? a[8 - b[2:0]] : 1'b0;
            end

            OP_SHR: begin
                result = {8'd0, a >> b[2:0]};
                carry  = (b[2:0] != 0) ? a[b[2:0] - 1] : 1'b0;
            end

            default: begin
                result = 16'd0;
                carry  = 1'b0;
            end
        endcase
    end

    // Flags de status
    assign zero     = (result == 16'd0);
    assign negative = result[15];  // MSB indica sinal

endmodule
