# UNIVERSIDADE FEDERAL DE UBERLÂNDIA
# FACULDADE DE COMPUTAÇÃO

**Gil Antony Borba**  
**Raphael Muniz Varela**  
**Victor Leal**  
**Ygor Marangoni**

# RELATÓRIO DE CLASSIFICAÇÃO PARA CONCESSÃO DE CRÉDITO

Trabalho Prático 2 apresentado à disciplina de Ciência de Dados da Universidade Federal de Uberlândia, como requisito parcial de avaliação.

Professor: Carlos Cesar Mansur Tuma

Monte Carmelo - MG  
2026

---

# SUMÁRIO

1. Introdução  
2. Descrição do problema  
3. Descrição da tarefa de classificação  
4. Descrição da base utilizada  
5. Pré-processamento herdado do Trabalho 1  
6. Métodos de classificação  
7. Configurações das execuções  
8. Resultados da base completa  
9. Seleção de atributos com J48  
10. Resultados da base reduzida  
11. Comparação dos resultados  
12. Análise crítica  
13. Conclusão  
14. Referências  
15. Apêndices  

## 1. Introdução

Este relatório apresenta o Trabalho Prático 2 da disciplina de Ciência de Dados, cujo foco foi aplicar e comparar métodos de classificação sobre a base final gerada no Trabalho Prático 1. A tarefa foi executada no WEKA real, via `weka.jar`, com validação cruzada de 10 folds.

## 2. Descrição do problema

O problema tratado é uma classificação binária para concessão de crédito. A variável alvo é `TARGET`, em que `0` representa cliente saudável e `1` representa cliente de risco. Como a classe `1` é minoritária, a análise não pode depender apenas da acurácia.

## 3. Descrição da tarefa de classificação

Foram executadas duas rodadas. Na primeira, os classificadores usaram a base completa. Na segunda, os classificadores foram reexecutados com uma base reduzida formada pelos atributos encontrados na árvore J48.

## 4. Descrição da base utilizada

A base usada foi `base_final_preprocessada.csv`, produzida no Trabalho 1. O campo `SK_ID_CURR` foi removido por ser apenas identificador. A variável `TARGET` foi mantida como última coluna e usada como classe no WEKA.

| Item | Valor |
|---|---:|
| Registros | 307.511 |
| Atributos de entrada | 39 |
| Classe | `TARGET` |
| Classe 0 | 282.686 (91,93%) |
| Classe 1 | 24.825 (8,07%) |

## 5. Pré-processamento herdado do Trabalho 1

O Trabalho 2 não refez o pré-processamento. Foram reaproveitadas as etapas do Trabalho 1: integração das três bases, agregação dos históricos externo e interno, tratamento de ausentes, codificação de categorias e geração da base final.

## 6. Métodos de classificação

Foram avaliados cinco classificadores do WEKA: J48, RandomForest, IBk, NaiveBayes e BayesNet. O J48 também foi usado para auxiliar na seleção de atributos relevantes.

## 7. Configurações das execuções

As execuções foram feitas por linha de comando com `java -Xmx8g -cp weka.jar`, validação cruzada com 10 folds, classe na última coluna e seed 42. As configurações específicas foram: J48 com `-C 0.25 -M 2`, RandomForest com `-I 100 -S 42`, IBk com `-K 5`, NaiveBayes padrão e BayesNet padrão na primeira tentativa.

O BayesNet da base completa foi concluido em nova tentativa com configuracao ajustada para reduzir consumo de memoria: ADTree desativada, busca K2 com no maximo 1 pai e SimpleEstimator com alpha 1.0. A execucao continuou sendo feita no WEKA real com validacao cruzada de 10 folds.

Na base reduzida, o BayesNet tambem foi executado com a configuracao ajustada para manter a comparacao viavel computacionalmente.

## 8. Resultados da base completa

| Método | Base | Acurácia | TP Rate classe 1 | FP Rate classe 1 | Precision classe 1 | Recall classe 1 | F-Measure classe 1 | ROC Area classe 1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| J48 | Completa | 90.6807 | 0.087 | 0.021 | 0.264 | 0.087 | 0.131 | 0.589 |
| RandomForest | Completa | 91.9382 | 0.005 | 0 | 0.579 | 0.005 | 0.01 | 0.734 |
| IBk | Completa | 91.3551 | 0.035 | 0.009 | 0.25 | 0.035 | 0.062 | 0.598 |
| NaiveBayes | Completa | 87.8684 | 0.144 | 0.057 | 0.182 | 0.144 | 0.16 | 0.685 |
| BayesNet | Completa | 88.4089 | 0.245 | 0.06 | 0.265 | 0.245 | 0.255 | 0.729 |

### 8.1 Matrizes de confusão da base completa

**J48**: `a      b   <-- classified as | 276701   5985 |      a = 0 | 22673   2152 |      b = 1`

**RandomForest**: `a      b   <-- classified as | 282596     90 |      a = 0 | 24701    124 |      b = 1`

**IBk**: `a      b   <-- classified as | 280049   2637 |      a = 0 | 23947    878 |      b = 1`

**NaiveBayes**: `a      b   <-- classified as | 266642  16044 |      a = 0 | 21262   3563 |      b = 1`

**BayesNet**: `a      b   <-- classified as | 265773  16913 |      a = 0 | 18731   6094 |      b = 1`

## 9. Seleção de atributos com J48

Os atributos abaixo foram extraídos da árvore gerada pelo J48 na primeira rodada.

| Ordem | Atributo selecionado pelo J48 |
|---:|---|
| 1 | `SER_DIVIDA_ATRASADA` |
| 2 | `EXT_SOURCE_3` |
| 3 | `SER_QTDE_PRORROGACOES` |
| 4 | `EXT_SOURCE_2` |
| 5 | `FLAG_OWN_CAR_COD` |
| 6 | `PREV_QTDE_CANCELADO` |
| 7 | `SER_CREDITOS_ATIVOS` |
| 8 | `EXT_SOURCE_1` |
| 9 | `FLAG_EMP_PHONE` |
| 10 | `CNT_CHILDREN` |
| 11 | `REGION_RATING_CLIENT` |
| 12 | `NAME_HOUSING_TYPE_COD` |
| 13 | `CODE_GENDER_COD` |
| 14 | `ORGANIZATION_TYPE_COD` |
| 15 | `FLAG_EMAIL` |

## 10. Resultados da base reduzida

| Método | Base | Acurácia | TP Rate classe 1 | FP Rate classe 1 | Precision classe 1 | Recall classe 1 | F-Measure classe 1 | ROC Area classe 1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| J48 | Reduzida | 91.8312 | 0.019 | 0.003 | 0.381 | 0.019 | 0.036 | 0.586 |
| RandomForest | Reduzida | 91.6273 | 0.023 | 0.005 | 0.276 | 0.023 | 0.042 | 0.687 |
| IBk | Reduzida | 91.1701 | 0.043 | 0.012 | 0.239 | 0.043 | 0.073 | 0.602 |
| NaiveBayes | Reduzida | 90.4345 | 0.09 | 0.024 | 0.247 | 0.09 | 0.132 | 0.704 |
| BayesNet | Reduzida | 91.5086 | 0.068 | 0.01 | 0.361 | 0.068 | 0.114 | 0.726 |

## 11. Comparação dos resultados

| Método | Base | Acurácia | TP Rate classe 1 | FP Rate classe 1 | Precision classe 1 | Recall classe 1 | F-Measure classe 1 | ROC Area classe 1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| J48 | Completa | 90.6807 | 0.087 | 0.021 | 0.264 | 0.087 | 0.131 | 0.589 |
| RandomForest | Completa | 91.9382 | 0.005 | 0 | 0.579 | 0.005 | 0.01 | 0.734 |
| IBk | Completa | 91.3551 | 0.035 | 0.009 | 0.25 | 0.035 | 0.062 | 0.598 |
| NaiveBayes | Completa | 87.8684 | 0.144 | 0.057 | 0.182 | 0.144 | 0.16 | 0.685 |
| BayesNet | Completa | 88.4089 | 0.245 | 0.06 | 0.265 | 0.245 | 0.255 | 0.729 |

| Método | Base | Acurácia | TP Rate classe 1 | FP Rate classe 1 | Precision classe 1 | Recall classe 1 | F-Measure classe 1 | ROC Area classe 1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| J48 | Reduzida | 91.8312 | 0.019 | 0.003 | 0.381 | 0.019 | 0.036 | 0.586 |
| RandomForest | Reduzida | 91.6273 | 0.023 | 0.005 | 0.276 | 0.023 | 0.042 | 0.687 |
| IBk | Reduzida | 91.1701 | 0.043 | 0.012 | 0.239 | 0.043 | 0.073 | 0.602 |
| NaiveBayes | Reduzida | 90.4345 | 0.09 | 0.024 | 0.247 | 0.09 | 0.132 | 0.704 |
| BayesNet | Reduzida | 91.5086 | 0.068 | 0.01 | 0.361 | 0.068 | 0.114 | 0.726 |

## 12. Análise crítica

O melhor desempenho geral por acurácia foi obtido por RandomForest na base Completa (acurácia 91.9382). Para a classe `1`, mais importante neste problema por representar clientes de risco, o melhor desempenho observado foi BayesNet na base Completa (F-Measure classe 1 0.255; Recall 0.245).

Como a base é fortemente desbalanceada, a acurácia foi analisada com cautela. As métricas da classe `1`, principalmente Recall, F-Measure e ROC Area, são mais adequadas para avaliar a capacidade de identificar clientes de risco.

## 13. Conclusão

O trabalho executou os cinco métodos solicitados no WEKA, comparou os resultados na base completa e na base reduzida e utilizou o J48 para apoiar a seleção de atributos. A análise reforça que, em bases desbalanceadas, a escolha do melhor classificador deve considerar métricas específicas da classe minoritária.

## 14. Referências

HAN, J.; KAMBER, M.; PEI, J. Data Mining: Concepts and Techniques. 3. ed. Waltham: Morgan Kaufmann, 2011.

QUINLAN, J. R. C4.5: Programs for Machine Learning. San Mateo: Morgan Kaufmann, 1993.

WITTEN, I. H.; FRANK, E.; HALL, M. A.; PAL, C. J. Data Mining: Practical Machine Learning Tools and Techniques. 4. ed. Cambridge: Morgan Kaufmann, 2016.

## 15. Apêndices

### Apêndice A - Comandos utilizados

```bash
cd trabalho_2_classificacao/scripts
python localizar_weka.py
python pipeline_trabalho_2.py
```

### Apêndice B - Arquivos gerados

- `data/base_weka_completa.arff`
- `data/base_weka_reduzida.arff`
- `resultados/rodada_1_base_completa/*.txt`
- `resultados/rodada_2_base_reduzida/*.txt`
- `resultados/resultados_classificacao.csv`
- `resultados/comparativo_metricas.csv`
- `resultados/atributos_relevantes_j48.txt`
