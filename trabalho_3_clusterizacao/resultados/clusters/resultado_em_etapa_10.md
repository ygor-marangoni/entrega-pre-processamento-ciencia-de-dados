# Resultado do EM — Etapa 10

Foram executadas três configurações reais pelo filtro `AddCluster` do WEKA
3.8.7. Todas utilizaram seed 42, máximo de 100 iterações, dez inicializações
K-Means internas, desvio padrão mínimo `1e-6` e uma thread.

| K | Log-likelihood | Menor grupo | Maior grupo | Tempo AddCluster |
|---:|---:|---:|---:|---:|
| 8 | 2,54478 | 257 | 4.406 | 2,786 s |
| 9 | 2,56187 | 257 | 4.359 | 3,300 s |
| 10 | -0,29589 | 583 | 2.016 | 3,394 s |

K=9 foi escolhido por apresentar o maior log-likelihood registrado entre K=8 e
K=9 e permitir comparação com DBSCAN e K-Means. O valor de K=10 é anômalo e
foi transcrito durante a execução; o ARFF comprova a configuração e os dez
rótulos, mas o log textual bruto do WEKA não foi preservado para confirmar
convergência, avisos ou a linha exata. Portanto, K=10 permanece inconclusivo na
comparação probabilística, embora suas atribuições possam ser avaliadas pelas
métricas geométricas posteriores.

O grupo dominante do EM K=9 contém 4.359 registros, ou 43,59% da amostra. Logo,
a escolha por log-likelihood não implica que a distribuição seja automaticamente
superior às demais; compactação, separação e interpretação ainda serão avaliadas.

O ARFF e o CSV de K=9 foram preservados com seus nomes de teste e copiados como
`base_clusterizada_em_final.arff` e `base_clusterizada_em_final.csv`.
