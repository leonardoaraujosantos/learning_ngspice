-- MUX 4:1 de 8 bits em VHDL
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity mux4 is
    port (
        sel : in  std_logic_vector(1 downto 0);
        a   : in  std_logic_vector(7 downto 0);
        b   : in  std_logic_vector(7 downto 0);
        c   : in  std_logic_vector(7 downto 0);
        d   : in  std_logic_vector(7 downto 0);
        y   : out std_logic_vector(7 downto 0)
    );
end mux4;

architecture behavioral of mux4 is
begin
    process(sel, a, b, c, d)
    begin
        case sel is
            when "00" => y <= a;
            when "01" => y <= b;
            when "10" => y <= c;
            when "11" => y <= d;
            when others => y <= (others => '0');
        end case;
    end process;
end behavioral;
