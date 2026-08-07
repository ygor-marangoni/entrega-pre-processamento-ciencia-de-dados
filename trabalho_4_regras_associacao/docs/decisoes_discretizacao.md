# Decisões de discretização — Etapa 3

## Situação

Esta é uma proposta simulada sobre a amostra original de 10.000 registros. Nenhuma base Apriori foi criada nesta etapa. A aplicação efetiva das faixas depende de aprovação expressa.

## Princípios aplicados

- Não foram usados intervalos de mesma largura.
- Crédito e renda usam quartis reais para resistir às caudas e aos outliers; renda possui máximo de R$ 117.000.000.
- Idade usa grupos de ciclo de vida e foi comparada aos quartis, mantendo todas as faixas acima de 12% da amostra.
- Contagens e taxas preservam zero real como rótulo nominal, requisito indispensável antes do futuro `treatZeroAsMissing=true`.
- Códigos categóricos foram recuperados em rótulos e não são tratados como magnitudes numéricas.
- A categoria familiar `Unknown` (um registro) foi incorporada a `SEPARADO_VIUVO_OU_NAO_INFORMADO`, eliminando categoria menor que 1%.

## Validação de frequências simuladas

| Atributo | Categorias | Menor categoria | Maior categoria | Razão maior/menor |
|---|---:|---:|---:|---:|
| AMT_CREDIT | 4 | 24.45% | 25.55% | 1.04 |
| AMT_INCOME_TOTAL | 4 | 17.39% | 32.79% | 1.89 |
| AGE_YEARS | 5 | 12.18% | 26.60% | 2.18 |
| CNT_CHILDREN | 3 | 10.34% | 69.61% | 6.73 |
| FLAG_OWN_CAR_COD | 2 | 33.95% | 66.05% | 1.95 |
| NAME_FAMILY_STATUS_COD | 3 | 11.98% | 73.04% | 6.10 |
| SER_CREDITOS_ATIVOS | 3 | 26.98% | 43.46% | 1.61 |
| PREV_TAXA_REJEICAO | 3 | 15.27% | 67.71% | 4.43 |

Nenhuma categoria simulada ficou abaixo de 5% da amostra; portanto, não há exceção de baixa frequência a justificar nesta proposta.

## Decisão pendente

A lista de oito atributos e as faixas descritas em `resultados/discretizacao/proposta_faixas.csv` foi posteriormente autorizada e aplicada na geração da base discretizada.

## Representação técnica binária posterior

As faixas e categorias aprovadas não foram modificadas após a discretização.
Entretanto, para compatibilidade com `treatZeroAsMissing=true` no WEKA 3.8.7,
cada uma das 27 categorias foi representada adicionalmente por uma coluna
binária `{0,1}`. Essa codificação é apenas técnica: `0` significa que o item
não ocorre na transação e `1` que ele ocorre. Ela não constitui uma nova
discretização nem uma nova seleção de atributos; as oito dimensões conceituais
permanecem inalteradas.
