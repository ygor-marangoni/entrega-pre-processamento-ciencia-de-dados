# Análise técnica dos métodos — Etapa 12

## Escopo das métricas

As métricas foram calculadas sobre os seis atributos transformados usados na
clusterização. `FLAG_OWN_CAR_COD_TRANSFORMADO` foi representado por 0/1, mantendo
distância unitária entre as categorias. `TARGET`, `SK_ID_CURR` e
`ROW_ID_AMOSTRA` não participaram das distâncias.

Silhouette foi estimada por amostra reproduzível de 3.000 registros com seed
42. Davies–Bouldin e Calinski–Harabasz foram calculados sobre todos os registros
e rótulos válidos. No DBSCAN, os 296 ruídos foram excluídos somente dessas
métricas e permaneceram descritos separadamente.

| Método | Silhouette | Davies–Bouldin | Calinski–Harabasz | Menor grupo | Maior grupo | Ruídos |
|---|---:|---:|---:|---:|---:|---:|
| DBSCAN | 0,085904 | 1,855622 | 1.031,784 | 6 | 4.759 | 296 |
| SimpleKMeans | 0,263382 | 1,380971 | 3.106,870 | 525 | 1.992 | 0 |
| EM | 0,109936 | 1,504642 | 1.862,177 | 257 | 4.359 | 0 |

## Comparação

SimpleKMeans apresentou a maior Silhouette, o menor Davies–Bouldin e o maior
Calinski–Harabasz nesta configuração. Também apresentou a distribuição de
tamanhos mais equilibrada, com entropia normalizada de 0,960189.

DBSCAN preservou 296 ruídos, equivalentes a 2,96% da base, mas também formou
microgrupos de 48, 49 e 6 registros. A razão entre o maior e o menor cluster foi
793,17, indicando forte desequilíbrio. Os ruídos apresentaram crédito, relação
crédito/renda e quantidade de créditos ativos acima da maior parte dos grupos,
mas sua interpretação comercial pertence à Etapa 13.

EM apresentou resultados geométricos intermediários e um grupo dominante com
4.359 registros, ou 43,59% da base. Sua razão entre maior e menor grupo foi
16,96 e a entropia de tamanhos foi 0,809238.

## TARGET posterior

A taxa global de `TARGET=1` na amostra é 8,23%. As proporções por cluster foram
calculadas apenas depois da atribuição dos grupos. Elas não alteraram os modelos
e não devem ser interpretadas como validação supervisionada da clusterização.

## Limitações

- Silhouette foi amostral para evitar matriz de distâncias quadrática completa.
- EM foi avaliado por rótulos rígidos exportados pelo `AddCluster`, embora o
  método produza probabilidades internamente.
- Métricas geométricas não medem diretamente utilidade comercial.
- Mais clusters ou menor quantidade de ruído não tornam um método
  automaticamente superior.
- A interpretação dos perfis e das oportunidades será realizada somente na
  Etapa 13.

