# Interpretação comercial dos clusters — Etapa 13

## Escopo e cautelas

Esta análise usa os valores originais das bases de análise geradas na Etapa 11
e os resumos calculados na Etapa 12. Os agrupamentos foram formados sem
`TARGET`, `SK_ID_CURR` ou `ROW_ID_AMOSTRA`. A variável `TARGET` aparece aqui
somente como descrição posterior dos grupos e não demonstra causalidade nem
transforma a clusterização em modelo de risco.

As oportunidades propostas são hipóteses de segmentação. Antes de uma campanha
real, elas exigem validação de capacidade de pagamento, elegibilidade, retorno,
regras de crédito, tratamento justo e estabilidade em novas amostras.

## Referência da amostra

A amostra contém 10.000 clientes. As referências globais usadas nas comparações
são:

| Indicador | Média global |
|---|---:|
| Crédito (`AMT_CREDIT`) | R$ 601.383 |
| Renda (`AMT_INCOME_TOTAL`) | R$ 180.554 |
| Filhos | 0,43 |
| Idade | 43,94 anos |
| Relação crédito/renda | 3,97 |
| Créditos ativos | 1,75 |
| Dívida atrasada | R$ 81,47 |
| Posse de carro | 33,95% |
| `TARGET=1` posterior | 8,23% |

O estado civil modal da amostra é casado, com 6.344 registros (63,44%). Ele
também é a moda de todos os clusters e, isoladamente, discrimina pouco os
perfis.

## Perfis recorrentes entre métodos

### 1. Jovens sem carro e com maior proporção posterior de `TARGET`

Este é o padrão comercial mais consistente entre SimpleKMeans e EM:

- SimpleKMeans, `cluster7`: 1.124 clientes (11,24%), idade média de 29,83 anos,
  nenhum cliente com carro, crédito médio de R$ 467.191, renda média de
  R$ 160.112 e `TARGET=1` de 12,72%.
- EM, `cluster7`: 1.293 clientes (12,93%), idade média de 29,15 anos, nenhum
  cliente com carro, crédito médio de R$ 392.933, renda média de R$ 153.309 e
  `TARGET=1` de 12,99%.

Os dois métodos identificam um público jovem, sem carro e com crédito abaixo da
média global. O perfil pode ser testado para produtos de entrada, educação
financeira, crédito de menor valor e soluções de mobilidade acessível. Uma
campanha de financiamento automotivo só seria defensável com entrada, prazo e
parcela compatíveis, pois a proporção posterior de `TARGET=1` está cerca de
4,5 pontos percentuais acima da média global. Posse de carro igual a zero não
prova intenção de compra.

### 2. Famílias com filhos e baixa posse de carro

O padrão aparece com diferentes níveis de renda:

- DBSCAN, `cluster6`: 477 clientes (4,77%), dois filhos em média, nenhum com
  carro, idade média de 35,81 anos, renda média de R$ 151.097, crédito médio de
  R$ 540.272 e `TARGET=1` de 8,60%.
- SimpleKMeans, `cluster1`: 583 clientes (5,83%), 2,19 filhos em média, apenas
  0,69% com carro, idade média de 35,95 anos, renda média de R$ 151.838, crédito
  médio de R$ 564.761 e `TARGET=1` de 8,75%.
- EM, `cluster5`: 1.181 clientes (11,81%), 1,59 filho em média, nenhum com
  carro, idade média de 36,65 anos, renda média de R$ 259.839, crédito médio de
  R$ 621.634 e `TARGET=1` de 9,06%.

DBSCAN e K-Means descrevem um núcleo muito semelhante de famílias jovens, sem
carro e com renda abaixo da média. O EM agrega um público de renda maior. Há
base para testar comunicação de mobilidade familiar, veículo popular ou
seminovo, crédito para despesas familiares e parcerias com revendas, sempre
segmentando a oferta pela renda. O grupo do EM não deve receber automaticamente
a mesma proposta financeira dos grupos de renda próxima a R$ 151 mil.

### 3. Crédito alto e forte comprometimento da renda

Três grupos grandes apresentam crédito médio superior a R$ 1,2 milhão e relação
crédito/renda próxima ou superior a 8:

- SimpleKMeans, `cluster2`: 765 clientes (7,65%), crédito médio de R$ 1.240.253,
  renda média de R$ 181.989, relação 8,09 e `TARGET=1` de 7,71%.
- EM, `cluster4`: 410 clientes (4,10%), crédito médio de R$ 1.408.533, renda
  média de R$ 208.684, relação 7,95, posse de carro de 99,76% e `TARGET=1` de
  6,34%.
- EM, `cluster8`: 343 clientes (3,43%), crédito médio de R$ 1.312.665, renda
  média de R$ 174.701, relação 9,22, nenhum cliente com carro e `TARGET=1` de
  7,58%.

As taxas posteriores de `TARGET=1` não estão acima da média, mas o
comprometimento é elevado. Esses grupos podem ser relevantes para revisão de
limites, refinanciamento, portabilidade ou relacionamento de alto valor. A
relação crédito/renda deve impedir a interpretação simplista de que crédito
alto significa capacidade livre para nova dívida.

### 4. Clientes maduros com menor proporção posterior de `TARGET`

Há recorrência de grupos mais velhos com taxas posteriores abaixo de 8,23%:

- SimpleKMeans, `cluster3`: 1.582 clientes (15,82%), idade média de 60,63 anos,
  crédito médio de R$ 466.607, nenhum com carro e `TARGET=1` de 5,31%.
- SimpleKMeans, `cluster8`: 1.390 clientes (13,90%), idade média de 52,69 anos,
  todos com carro, crédito médio de R$ 760.528 e `TARGET=1` de 5,47%.
- EM, `cluster3`: 4.359 clientes (43,59%), idade média de 54,44 anos, 19,02% com
  carro, crédito médio de R$ 565.019 e `TARGET=1` de 6,49%.

Os grupos podem sustentar ofertas de relacionamento, renovação ou manutenção
de produtos existentes, com comunicação adaptada ao estágio de vida. O
`cluster3` do EM é muito amplo e deve ser subdividido por posse de carro e renda
antes de qualquer ação, pois reúne 43,59% da amostra.

### 5. Muitos créditos ativos e sinais de atenção financeira

O `cluster9` do SimpleKMeans contém 525 clientes (5,25%), com média de 5,23
créditos ativos, idade de 53,14 anos, crédito de R$ 613.678, dívida atrasada de
R$ 246,72 e `TARGET=1` de 9,71%. Em comparação, a amostra possui 1,75 crédito
ativo e R$ 81,47 de dívida atrasada em média.

O perfil é mais coerente com revisão de relacionamento, consolidação de dívidas,
renegociação e prevenção de sobre-endividamento do que com concessão agressiva
de novo crédito. A diferença para a média é descritiva e não substitui uma
política de risco individual.

## Leitura específica do DBSCAN

O DBSCAN revela combinações muito nítidas de filhos e posse de carro:

- `cluster1`: 342 clientes, dois filhos, 100% com carro, idade de 36,38 anos e
  `TARGET=1` de 8,48%; pode ser explorado para manutenção, seguro ou troca de
  veículo familiar, não para primeira aquisição.
- `cluster2`: 2.099 clientes, sem filhos, 100% com carro, idade de 44,35 anos e
  `TARGET=1` de 6,96%; é um público amplo de proprietários para retenção e
  serviços ligados ao veículo.
- `cluster3`: 1.159 clientes, um filho, nenhum com carro, idade de 37,20 anos e
  `TARGET=1` de 9,58%; é compatível com a hipótese de mobilidade familiar, com
  cautela maior que a média.
- `cluster4`: 4.759 clientes, sem filhos, nenhum com carro, idade de 48,10 anos e
  `TARGET=1` de 8,30%; por representar 47,59% da amostra, é amplo demais para
  uma campanha única.
- `cluster5`: 765 clientes, um filho, 100% com carro, idade de 37,05 anos e
  `TARGET=1` de 7,97%; pode apoiar ações de relacionamento com famílias já
  motorizadas.
- `cluster6`: 477 clientes, dois filhos e nenhum com carro; é o núcleo familiar
  sem veículo descrito anteriormente.
- `cluster7` e `cluster8`: respectivamente 48 e 49 clientes, ambos com três
  filhos; o primeiro não possui carro e o segundo possui. Os tamanhos de 0,48%
  e 0,49% tornam qualquer conclusão frágil.
- `cluster9`: somente seis clientes, crédito médio de R$ 1.264.561 e relação
  crédito/renda de 11,09; deve ser tratado como microgrupo exploratório, nunca
  como segmento de campanha.

### Ruídos do DBSCAN

Os 296 ruídos (2,96%) têm crédito médio de R$ 1.288.126, renda média de
R$ 211.088, relação crédito/renda de 8,02, 3,49 créditos ativos, dívida atrasada
média de R$ 782,92 e `TARGET=1` de 10,47%. Todos esses valores, exceto renda,
indicam afastamento relevante do perfil médio.

O uso mais defensável é uma fila de análise individual, verificação de qualidade
dos dados e investigação de casos fora do padrão. Ruído significa baixa
densidade na geometria escolhida, não fraude, inadimplência ou cliente ruim.

## Leitura específica do SimpleKMeans

Além dos perfis recorrentes, destacam-se:

- `cluster5`: 775 clientes, idade média de 32,68 anos, renda de R$ 308.534,
  nenhum com carro e `TARGET=1` de 11,48%; pode ser um público jovem de maior
  renda para produtos de relacionamento ou mobilidade, mas a taxa posterior
  recomenda avaliação de elegibilidade.
- `cluster6`: 1.992 clientes, 100% com carro, 0,78 filho, idade de 34,10 anos e
  `TARGET=1` de 9,04%; é o maior grupo do método e pode apoiar ofertas ligadas a
  veículo já existente.
- `cluster4`: 1.264 clientes, nenhum com carro, idade de 45,92 anos, crédito de
  R$ 409.094 e `TARGET=1` de 7,12%; descreve um perfil intermediário de menor
  crédito.

O SimpleKMeans fornece os grupos mais equilibrados e o melhor resultado relativo
nas métricas internas avaliadas na Etapa 12. Por isso, seus segmentos são os mais práticos para planejamento de
campanhas, sem que isso torne o método comercialmente superior em todos os
casos.

## Leitura específica do EM

Além dos perfis recorrentes, destacam-se:

- `cluster1`: 257 clientes, crédito médio de R$ 351.315, relação crédito/renda
  de 2,36, nenhum com carro e `TARGET=1` de 8,56%; é um pequeno grupo de menor
  exposição de crédito.
- `cluster2`: 891 clientes, 100% com carro, idade de 30,15 anos, relação
  crédito/renda de 2,55 e `TARGET=1` de 9,99%; pode apoiar relacionamento com
  proprietários jovens, com atenção à taxa posterior.
- `cluster6`: 436 clientes, 100% com carro, nenhum filho, 2,28 créditos ativos e
  `TARGET=1` de 7,57%; pode ser avaliado para retenção ou serviços associados.
- `cluster9`: 830 clientes, 1,61 filho, 100% com carro, idade de 38,70 anos e
  `TARGET=1` de 8,31%; representa famílias já motorizadas, próximas à média
  posterior da base.

Como o `cluster3` concentra 43,59% dos clientes, o EM produz uma segmentação
menos operacional que o K-Means para campanhas diretamente baseadas nos nove
rótulos rígidos.

## Recomendações de uso

1. Priorizar testes controlados nos dois perfis recorrentes: jovens sem carro e
   famílias com filhos sem carro.
2. Separar ofertas de aquisição de veículo das ofertas para quem já possui
   carro, como seguro, manutenção, refinanciamento e troca.
3. Aplicar análise de capacidade de pagamento aos grupos de relação
   crédito/renda elevada antes de qualquer oferta adicional.
4. Tratar muitos créditos ativos e ruídos do DBSCAN como sinais para revisão,
   não como autorização automática de recusa.
5. Medir conversão, inadimplência, retorno e estabilidade fora da amostra antes
   de institucionalizar qualquer segmento.
6. Não utilizar estado civil, idade ou composição familiar de forma
   discriminatória; esses campos devem apoiar entendimento agregado, respeitando
   regras aplicáveis e políticas de crédito justo.

## Conclusão

Os dados sustentam perfis comercialmente interpretáveis. Os mais consistentes
são jovens sem carro, famílias com filhos sem carro, proprietários de veículo em
diferentes estágios de vida, clientes com crédito alto e forte comprometimento,
clientes com muitos créditos ativos e casos fora do padrão identificados pelo
DBSCAN.

SimpleKMeans oferece a segmentação mais equilibrada e operacional nesta
amostra. DBSCAN agrega valor ao isolar ruídos e combinações específicas, e EM
confirma parte dos padrões, embora concentre 43,59% dos registros em um único
grupo. Nenhuma oportunidade deve ser convertida diretamente em decisão de
crédito sem validação adicional.
