# Resultado do SimpleKMeans — Etapa 9

Foram executadas três configurações reais pelo filtro `AddCluster` do WEKA
3.8.7. Todas utilizaram seed 42, inicialização aleatória `init=0`, no máximo 500
iterações, uma thread e `weka.core.EuclideanDistance -R first-last -D`.

A opção `-D` desativou a segunda normalização do WEKA e preservou os pesos
incorporados na base da Etapa 4. A opção `-fast` não foi utilizada, permitindo o
cálculo da soma dos erros quadráticos.

| K | Iterações | SSE | Menor grupo | Maior grupo | Tempo AddCluster |
|---:|---:|---:|---:|---:|---:|
| 8 | 37 | 2386,976059874797 | 583 | 1.992 | 1,816 s |
| 9 | 62 | 2284,489341365910 | 525 | 1.992 | 1,255 s |
| 10 | 57 | 2172,711624193117 | 459 | 1.987 | 1,149 s |

O SSE diminuiu 4,29% de K=8 para K=9 e 4,89% de K=9 para K=10. Como não há
um cotovelo claro nesse intervalo e todos os grupos mantêm tamanho utilizável,
K=9 foi escolhido como compromisso: apresentou a maior Silhouette dos três
testes, alta entropia de tamanhos e comparação direta com os nove grupos densos
do DBSCAN. K=8 liderou em Calinski-Harabasz e K=10 em Davies-Bouldin; por isso,
a escolha não afirma que nove seja o número perfeito de clusters.

O ARFF e o CSV de K=9 foram preservados com seus nomes de teste e copiados como
`base_clusterizada_kmeans_final.arff` e `base_clusterizada_kmeans_final.csv`.
