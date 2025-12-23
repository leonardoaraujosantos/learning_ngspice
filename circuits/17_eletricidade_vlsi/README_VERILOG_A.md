# Modelos Verilog-A com OpenVAF

Este diretório contém exemplos de modelos customizados em Verilog-A compilados com OpenVAF para uso no ngspice.

## O que é Verilog-A?

**Verilog-A** é uma linguagem de descrição de hardware (HDL) para modelagem de circuitos analógicos e de sinal misto. Permite criar modelos comportamentais customizados de dispositivos eletrônicos.

**OpenVAF** é um compilador open-source que transforma código Verilog-A em módulos OSDI (Open Simulation Device Interface) que podem ser carregados dinamicamente pelo ngspice.

## Instalação do OpenVAF

### Linux (Ubuntu/Debian)
```bash
# Baixar release do OpenVAF
wget https://github.com/pascalkuthe/OpenVAF/releases/download/v23.5.0/openvaf_23.5.0_linux_amd64.tar.gz

# Extrair
tar -xzf openvaf_23.5.0_linux_amd64.tar.gz

# Mover para /usr/local/bin
sudo mv openvaf /usr/local/bin/

# Verificar instalação
openvaf --version
```

### Outras Plataformas
Veja: https://openvaf.semimod.de/

## Modelos Disponíveis

### 1. Resistor Não-Linear (`resistor_naolinear.va`)
- **Descrição**: Resistor com resistência dependente da tensão aplicada
- **Equação**: R(V) = R₀ × (1 + α×V²)
- **Parâmetros**:
  - `R0`: Resistência nominal (padrão: 1kΩ)
  - `alpha`: Coeficiente não-linear (padrão: 0.001 V⁻²)
  - `tc1`, `tc2`: Coeficientes de temperatura

### 2. Diodo Simples (`diodo_simples.va`)
- **Descrição**: Modelo de diodo baseado na equação de Shockley
- **Equação**: I = Is × (exp(V/(n×Vt)) - 1)
- **Parâmetros**:
  - `Is`: Corrente de saturação (padrão: 1e-14 A)
  - `n`: Coeficiente de emissão (padrão: 1.0)
  - `Rs`: Resistência série (padrão: 0Ω)
  - `Cj0`: Capacitância de junção (padrão: 0F)
  - `Vj`: Potencial de junção (padrão: 0.7V)
  - `m`: Coeficiente de gradação (padrão: 0.5)

### 3. Varactor (`varactor.va`)
- **Descrição**: Capacitor variável controlado por tensão
- **Equação**: C(V) = C₀ / (1 + V/Vj)^m
- **Parâmetros**:
  - `C0`: Capacitância em V=0 (padrão: 10pF)
  - `Vj`: Tensão de junção (padrão: 0.7V)
  - `m`: Coeficiente de gradação (padrão: 0.5)
  - `Cmin`, `Cmax`: Limites de capacitância

## Como Compilar

```bash
# Compilar um modelo
openvaf resistor_naolinear.va

# Isso gera o arquivo OSDI
# resistor_naolinear.osdi
```

## Como Usar no ngspice

### 1. No arquivo SPICE, carregar o modelo:
```spice
.pre_osdi resistor_naolinear.osdi
```

### 2. Instanciar o dispositivo:
```spice
* Sintaxe: Nome nó+ nó- nome_modelo parâmetros
Rnl in out resistor_naolinear R0=1k alpha=0.001
```

### 3. Executar simulação:
```bash
ngspice teste_resistor_naolinear.cir
```

## Circuitos de Teste

### 1. `teste_resistor_naolinear.cir`
- Testa o resistor não-linear
- Varre tensão de -10V a +10V
- Mostra curva I-V e resistência instantânea

**Executar:**
```bash
openvaf resistor_naolinear.va
ngspice teste_resistor_naolinear.cir
```

### 2. `teste_diodo.cir`
- Testa o diodo em retificador de meia onda
- Análise transiente e curva I-V DC

**Executar:**
```bash
openvaf diodo_simples.va
ngspice teste_diodo.cir
```

### 3. `vco_varactor.cir`
- VCO (oscilador) com varactor para sintonia
- Demonstra controle de frequência por tensão

**Executar:**
```bash
openvaf varactor.va
ngspice vco_varactor.cir
```

## Estrutura de um Modelo Verilog-A

```verilog
`include "constants.vams"
`include "disciplines.vams"

module nome_modelo(terminal1, terminal2);
    // Declaração dos terminais
    inout terminal1, terminal2;
    electrical terminal1, terminal2;

    // Parâmetros
    parameter real param1 = valor_default from (min:max);

    // Variáveis
    real variavel;

    analog begin
        // Equações do modelo
        variavel = V(terminal1, terminal2);
        I(terminal1, terminal2) <+ expressao;
    end
endmodule
```

## Recursos Verilog-A Importantes

### Operadores de Contribuição
- `<+` : Contribuição aditiva (soma correntes/tensões)
- `=`  : Atribuição de variável

### Funções do Sistema
- `V(n1, n2)` : Tensão entre nós
- `I(n1, n2)` : Corrente através do ramo
- `ddt(x)` : Derivada temporal (dx/dt)
- `idt(x)` : Integral temporal
- `$temperature` : Temperatura da simulação
- `$vt` : Tensão térmica (kT/q)
- `limexp(x)` : Exponencial limitada (evita overflow)

### Includes Padrão
- `constants.vams` : Constantes físicas (q, k, etc)
- `disciplines.vams` : Disciplinas elétricas, térmicas, etc

## Vantagens do Verilog-A

1. **Modelagem Customizada**: Crie modelos específicos não disponíveis em SPICE
2. **Portabilidade**: Código funciona em múltiplos simuladores
3. **Legibilidade**: Sintaxe clara e matemática direta
4. **Modularidade**: Modelos reutilizáveis
5. **Física Precisa**: Inclui efeitos térmicos, ruído, não-linearidades

## Limitações

1. **Performance**: Modelos Verilog-A podem ser mais lentos que modelos SPICE nativos
2. **Debugging**: Erros podem ser difíceis de rastrear
3. **Convergência**: Modelos mal escritos podem causar problemas de convergência

## Dicas de Modelagem

### 1. Use `limexp()` em vez de `exp()`
```verilog
// RUIM - pode overflow
I <+ Is * (exp(V/Vt) - 1);

// BOM - limitado
I <+ Is * (limexp(V/Vt) - 1);
```

### 2. Adicione pequenas condutâncias para convergência
```verilog
// Evita singularidades
I(p, n) <+ V(p, n) / 1e12;  // Gmin = 1pS
```

### 3. Limite valores extremos
```verilog
if (C < Cmin) C = Cmin;
if (C > Cmax) C = Cmax;
```

## Referências

- [Documentação OpenVAF](https://openvaf.semimod.de/)
- [Verilog-A Reference Manual](http://www.verilog-ams.com/)
- [ngspice OSDI Documentation](https://ngspice.sourceforge.io/ngspice-osdi.html)
- [Tutorial Verilog-A (PDF)](https://www.designers-guide.org/VerilogAMS/)

## Próximos Passos

Para aprender mais sobre Verilog-A:
1. Veja o tutorial completo em: `docs/tutorial_spice.md` (Seção 18)
2. Experimente modificar os parâmetros dos modelos
3. Crie seus próprios modelos customizados
4. Estude modelos complexos em repositórios como [VA-Models](https://github.com/Xyce/VA-Models)
