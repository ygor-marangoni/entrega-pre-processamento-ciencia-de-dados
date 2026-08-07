# Análise exploratória dos atributos candidatos

## Escopo e método

A análise usa `C:/Users/drz/Desktop/Faculdade/CD/entrega_preprocessamento_ciencia_dados/trabalho_3_clusterizacao/data/amostras/base_amostra_10000_analise.csv`, com 10.000 registros selecionados na Etapa 2 usando seed 42.
`ROW_ID_AMOSTRA`, `SK_ID_CURR` e `TARGET` não foram analisados como atributos de agrupamento.
Possíveis outliers numéricos foram sinalizados pela regra de 1,5 × IQR. Para campos nominais ou ordinais, a contagem mecânica de IQR não deve ser interpretada como anomalia.
Nenhuma base ponderada foi gerada e Hopkins não foi executado.

## Visão geral

| Atributo | Tipo semântico | Ausentes | Únicos | Zeros | Mediana | Assimetria | Outliers IQR |
|---|---|---:|---:|---:|---:|---:|---:|
| `AMT_CREDIT` | numérico contínuo | 0 | 1815 | 0 | 512.721,00 | 1,27 | 217 |
| `AMT_INCOME_TOTAL` | numérico contínuo | 0 | 294 | 0 | 148.500,00 | 99,02 | 469 |
| `CNT_CHILDREN` | numérico discreto | 0 | 6 | 6961 | 0,00 | 1,72 | 160 |
| `FLAG_OWN_CAR_COD` | nominal binário | 0 | 2 | 6605 | 0,00 | 0,68 | 0 |
| `AGE_YEARS` | numérico contínuo | 0 | 3959 | 0 | 43,14 | 0,12 | 0 |
| `CREDIT_INCOME_RATIO` | numérico contínuo | 0 | 4962 | 0 | 3,28 | 1,71 | 324 |
| `REGION_RATING_CLIENT` | ordinal | 0 | 3 | 0 | 2,00 | 0,08 | 2584 |
| `SER_CREDITOS_ATIVOS` | numérico discreto | 0 | 17 | 2956 | 1,00 | 1,47 | 108 |
| `SER_DIVIDA_ATRASADA` | numérico contínuo | 0 | 88 | 9880 | 0,00 | 59,77 | 120 |
| `NAME_FAMILY_STATUS_COD` | nominal codificado | 0 | 6 | 1 | 2,00 | 1,07 | 540 |

## Análise preliminar por atributo

### AMT_CREDIT

- Papel de negócio: Valor do crédito contratado; representa o porte da operação.
- Tipo indicado no p1: **Numérico**.
- Faixa observada: 45.000,00 a 3.600.000,00; mediana 512.721,00.
- Ausentes: 0; zeros: 0 (0,00%).
- Assimetria: 1,27; possíveis outliers por IQR: 217 (2,17%).
- Cuidado: Pode apresentar cauda à direita e valores elevados.

### AMT_INCOME_TOTAL

- Papel de negócio: Capacidade financeira declarada do cliente.
- Tipo indicado no p1: **Numérico**.
- Faixa observada: 27.000,00 a 117.000.000,00; mediana 148.500,00.
- Ausentes: 0; zeros: 0 (0,00%).
- Assimetria: 99,02; possíveis outliers por IQR: 469 (4,69%).
- Cuidado: Possui outliers extremos; Min-Max pode comprimir a maioria dos registros.

### CNT_CHILDREN

- Papel de negócio: Composição familiar e possíveis necessidades de mobilidade.
- Tipo indicado no p1: **Numérico**.
- Faixa observada: 0,00 a 5,00; mediana 0,00.
- Ausentes: 0; zeros: 6961 (69,61%).
- Assimetria: 1,72; possíveis outliers por IQR: 160 (1,60%).
- Cuidado: Muitos zeros e poucos valores altos; é uma contagem, não uma categoria nominal.

### FLAG_OWN_CAR_COD

- Papel de negócio: Distingue clientes com e sem carro, diretamente útil para segmentação comercial.
- Tipo indicado no p1: **Nominal**.
- Faixa observada: 0,00 a 1,00; mediana 0,00.
- Ausentes: 0; zeros: 6605 (66,05%).
- Assimetria: 0,68; possíveis outliers por IQR: 0 (0,00%).
- Cuidado: O código 0/1 deve ser declarado nominal ou recuperado como N/Y.

### AGE_YEARS

- Papel de negócio: Representa o estágio de vida do cliente.
- Tipo indicado no p1: **Numérico**.
- Faixa observada: 21,07 a 68,99; mediana 43,14.
- Ausentes: 0; zeros: 0 (0,00%).
- Assimetria: 0,12; possíveis outliers por IQR: 0 (0,00%).
- Cuidado: Baixo risco metodológico, desde que normalizado.

### CREDIT_INCOME_RATIO

- Papel de negócio: Expressa o crédito em relação à renda e facilita interpretar comprometimento financeiro.
- Tipo indicado no p1: **Numérico**.
- Faixa observada: 0,00 a 35,48; mediana 3,28.
- Ausentes: 0; zeros: 0 (0,00%).
- Assimetria: 1,71; possíveis outliers por IQR: 324 (3,24%).
- Cuidado: É derivado de crédito e renda; peso excessivo pode duplicar a dimensão financeira.

### REGION_RATING_CLIENT

- Papel de negócio: Resume a classificação regional do cliente em três níveis ordenados.
- Tipo indicado no p1: **Ordinal**.
- Faixa observada: 1,00 a 3,00; mediana 2,00.
- Ausentes: 0; zeros: 0 (0,00%).
- Assimetria: 0,08; possíveis outliers por IQR: 2584 (25,84%).
- Cuidado: Baixa cardinalidade e forte concentração; a ordem precisa ser preservada.

### SER_CREDITOS_ATIVOS

- Papel de negócio: Quantidade de créditos ativos no histórico externo.
- Tipo indicado no p1: **Numérico**.
- Faixa observada: 0,00 a 17,00; mediana 1,00.
- Ausentes: 0; zeros: 2956 (29,56%).
- Assimetria: 1,47; possíveis outliers por IQR: 108 (1,08%).
- Cuidado: Contagem assimétrica com concentração em valores baixos.

### SER_DIVIDA_ATRASADA

- Papel de negócio: Valor de dívida atrasada observado no histórico externo.
- Tipo indicado no p1: **Numérico**.
- Faixa observada: 0,00 a 231.135,48; mediana 0,00.
- Ausentes: 0; zeros: 9880 (98,80%).
- Assimetria: 59,77; possíveis outliers por IQR: 120 (1,20%).
- Cuidado: Extremamente esparso e com outliers severos; pode separar apenas poucos casos extremos.

### NAME_FAMILY_STATUS_COD

- Papel de negócio: Representa o estado civil e pode complementar o perfil familiar.
- Tipo indicado no p1: **Nominal**.
- Faixa observada: 0,00 a 5,00; mediana 2,00.
- Ausentes: 0; zeros: 1 (0,01%).
- Assimetria: 1,07; possíveis outliers por IQR: 540 (5,40%).
- Cuidado: Os códigos 0 a 5 não possuem distância ou ordem natural e precisam voltar a rótulos nominais.

## Proposta para aprovação

Esta proposta é inicial e não autoriza a geração da base ponderada. Os pesos produzem efeito quadrático por meio da multiplicação por `sqrt(peso)` nos campos numéricos e ordinais. No `p1.py` original, atributos nominais são apenas preservados: seu peso decide inclusão ou exclusão, mas não multiplica a distância; por isso os nominais recebem peso 1 nesta proposta.
`AMT_INCOME_TOTAL` foi mantido como alternativa porque sua mediana é 148.500, mas o máximo de 117 milhões e a assimetria de aproximadamente 99 fariam o Min-Max obrigatório comprimir quase toda a amostra. A renda continuará presente na base auxiliar para caracterizar os clusters, mesmo se não participar da distância.

| Atributo | Papel | Tipo no p1 | Peso inicial | Justificativa | Problema principal |
|---|---|---|---:|---|---|
| `AMT_CREDIT` | principal | Numérico | 6 | Captura o porte do empréstimo e diferencia necessidades de crédito. | Pode apresentar cauda à direita e valores elevados. |
| `CNT_CHILDREN` | principal | Numérico | 4 | Acrescenta composição familiar e potencial necessidade de mobilidade. | Muitos zeros e poucos valores altos; é uma contagem, não uma categoria nominal. |
| `FLAG_OWN_CAR_COD` | principal | Nominal | 1 | Separa diretamente clientes com e sem veículo; no p1 original, peso nominal funciona apenas como inclusão. | O código 0/1 deve ser declarado nominal ou recuperado como N/Y. |
| `AGE_YEARS` | principal | Numérico | 5 | Distingue estágios de vida com boa interpretação comercial. | Baixo risco metodológico, desde que normalizado. |
| `CREDIT_INCOME_RATIO` | principal | Numérico | 7 | Resume comprometimento financeiro, com peso controlado por ser variável derivada. | É derivado de crédito e renda; peso excessivo pode duplicar a dimensão financeira. |
| `SER_CREDITOS_ATIVOS` | principal | Numérico | 5 | Adiciona intensidade do relacionamento de crédito externo sem o outlier extremo observado na renda. | Contagem assimétrica com concentração em valores baixos. |
| `AMT_INCOME_TOTAL` | alternativo | Numérico | 4 | É relevante para o perfil comercial, mas o máximo de 117 milhões comprime a escala Min-Max; permanece disponível para caracterização posterior. | Possui outliers extremos; Min-Max pode comprimir a maioria dos registros. |
| `REGION_RATING_CLIENT` | alternativo | Ordinal | 3 | Pode introduzir contexto regional, mas tem somente três níveis. | Baixa cardinalidade e forte concentração; a ordem precisa ser preservada. |
| `SER_DIVIDA_ATRASADA` | alternativo | Numérico | 2 | Possível indicador de comportamento, limitado pela forte concentração em zero. | Extremamente esparso e com outliers severos; pode separar apenas poucos casos extremos. |
| `NAME_FAMILY_STATUS_COD` | alternativo | Nominal | 1 | Pode enriquecer o perfil familiar após recuperação dos rótulos; no p1 original, peso nominal não reescala o campo. | Os códigos 0 a 5 não possuem distância ou ordem natural e precisam voltar a rótulos nominais. |

## Decisões que exigem aprovação

1. Aprovar ou alterar os seis atributos principais e seus pesos.
2. Confirmar que `FLAG_OWN_CAR_COD` será recuperado como rótulo nominal N/Y antes do WEKA.
3. Manter `NAME_FAMILY_STATUS_COD` apenas como alternativa e recuperar seus rótulos caso seja aprovado.
4. Confirmar se `AMT_INCOME_TOTAL` deve permanecer fora da distância devido ao outlier extremo, sendo usada apenas na interpretação posterior.
5. Avaliar Hopkins somente após a futura geração da base ponderada autorizada.
