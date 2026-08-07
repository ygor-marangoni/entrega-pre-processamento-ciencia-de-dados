# Resultado do DBSCAN — Etapa 8

## Execução real

As bases foram geradas pelo WEKA 3.8.7 com o filtro
`weka.filters.unsupervised.attribute.AddCluster` e o pacote oficial
`optics_dbScan` 1.0.6. Nenhuma coluna de cluster foi produzida manualmente.

A entrada foi `data/preparadas/base_clusterizacao_final.arff`, com 10.000
registros e seis atributos. O filtro acrescentou o atributo nominal `cluster`.

## Definição dos parâmetros

Foi calculada somente a curva de distância ao sexto vizinho para orientar o
parâmetro do WEKA. O joelho geométrico ocorreu em `epsilon = 0,274264329676`, no
percentil 94,38%. Foram testados valores abaixo, no ponto e acima do joelho:

- teste 01: `epsilon = 0,25`;
- teste 02: `epsilon = 0,274264329676`;
- teste 03: `epsilon = 0,30`.

Todos utilizaram `minPoints = 6` e
`weka.core.EuclideanDistance -R first-last -D`. A opção `-D` desativa a
normalização interna do WEKA, pois os atributos já foram reescalados e
ponderados por `sqrt(peso)` na Etapa 4. O DBSCAN dessa implementação não possui
parâmetro de seed.

## Comparação

| Teste | Epsilon | Clusters | Ruídos | Percentual de ruídos | Tempo |
|---|---:|---:|---:|---:|---:|
| 01 | 0,25 | 9 | 396 | 3,96% | 7,805 s |
| 02 | 0,274264329676 | 9 | 296 | 2,96% | 7,740 s |
| 03 | 0,30 | 9 | 217 | 2,17% | 6,491 s |

## Configuração de referência

O teste 02 foi escolhido como referência por usar o valor derivado do joelho
da curva. Ele reduz o ruído observado no teste 01 sem selecionar o maior raio
somente para absorver mais pontos. O arquivo foi preservado com o nome do teste
e copiado para `base_clusterizada_dbscan.arff`.

O resultado contém nove clusters e 296 ruídos. Há grupos muito pequenos, como
`cluster9` com seis registros, além de `cluster7` e `cluster8` com 48 e 49
registros. Essa fragmentação deverá ser considerada na comparação posterior.
Os nove grupos são apenas uma referência para os testes de K-Means e EM, não um
“K perfeito”.

