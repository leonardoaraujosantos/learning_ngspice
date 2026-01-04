module counter_0_59 (
    input  logic        clk,
    input  logic        rst,
    output logic [5:0]  count
);

    always_ff @(posedge clk) begin
        if (rst) begin
            count <= 6'd0;
        end else begin
            if (count == 6'd59)
                count <= 6'd0;
            else
                count <= count + 6'd1;
        end
    end

endmodule
