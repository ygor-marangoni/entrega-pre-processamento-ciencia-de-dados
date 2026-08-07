# Auditoria das opções do Apriori no WEKA — Etapa 6

## Evidência da instalação real

A auditoria foi executada em 7 de agosto de 2026, sem fornecer base de dados ao
Apriori e sem gerar regras.

- Java em execução: OpenJDK Temurin 17.0.20.
- `weka.jar`: `C:\Program Files\Weka-3-8-7\weka.jar`.
- Versão informada pelo comando real `weka.core.Version`: **3.8.7**.
- Classe consultada: `weka.associations.Apriori`.

O script reprodutível desta auditoria é
`scripts/06_preparar_weka.py`. Ele executa apenas a consulta de versão e a
ajuda `-h`; não recebe a base Apriori como entrada.

## Opções confirmadas pela ajuda real

| Requisito | Opção real | Padrão informado pelo WEKA | Uso futuro autorizado |
|---|---|---|---|
| Número de regras | `-N <required number of rules output>` | 10 | Execução final: `-N 30`. |
| Métrica de ordenação | `-T <0=confidence \| 1=lift \| 2=leverage \| 3=Conviction>` | confiança (`0`) | A métrica padrão é confiança; mudança eventual deverá ser registrada. |
| Pontuação mínima | `-C <minimum metric score of a rule>` | 0,9 | Parâmetro a preservar e registrar em cada experimento. |
| Delta de suporte | `-D <delta for minimum support>` | 0,05 | Redução progressiva do suporte nas buscas. |
| Limite superior de suporte | `-U <upper bound for minimum support>` | 1,0 | Registrar em cada tentativa. |
| `lowerBoundMinSupport` | `-M <lower bound for minimum support>` | 0,1 | Variar somente na Etapa 7. |
| `outputItemSets` | `-I` | desativado | Obrigatório: ativar. |
| `treatZeroAsMissing` | `-Z` | desativado | Obrigatório: ativar. |
| Progresso | `-V` | desativado | Opcional para acompanhamento. |
| Regras de classe | `-A` e `-c` | desativado; classe final | Não usar: não haverá atributo de classe. |

A ajuda também confirmou `-S` (teste de significância), `-R` (remoção de
colunas inteiramente ausentes) e `-B` (delimitadores de texto). Eles não são
requisitos do enunciado e não serão alterados sem registro explícito.

## Saída integral da ajuda real

```text
General options:

-t <training file>
    The name of the training file.
-g <name of graph file>
    Outputs the graph representation (if supported) of the associator to a file.

Options specific to Apriori:

-N <required number of rules output>
    The required number of rules. (default = 10)
-T <0=confidence | 1=lift | 2=leverage | 3=Conviction>
    The metric type by which to rank rules. (default = confidence)
-C <minimum metric score of a rule>
    The minimum confidence of a rule. (default = 0.9)
-D <delta for minimum support>
    The delta by which the minimum support is decreased in each iteration. (default = 0.05)
-U <upper bound for minimum support>
    Upper bound for minimum support. (default = 1.0)
-M <lower bound for minimum support>
    The lower bound for the minimum support. (default = 0.1)
-S <significance level>
    If used, rules are tested for significance at the given level. Slower. (default = no significance testing)
-I
    If set the itemsets found are also output. (default = no)
-R
    Remove columns that contain all missing values (default = no)
-V
    Report progress iteratively. (default = no)
-A
    If set class association rules are mined. (default = no)
-Z
    Treat zero (i.e. first value of nominal attributes) as missing
-B <toString delimiters>
    If used, two characters to use as rule delimiters in the result of toString.
-c <the class index>
    The class index. (default = last)
```

## Requisito de regras com três itens

A ajuda real não lista nenhuma opção para impor diretamente
`|antecedente| + |consequente| = 3`. Assim, a contagem será feita sobre a união
dos itens de cada regra, não sobre o tamanho isolado do antecedente.

Nas Etapas 7 a 9, a saída integral do WEKA será preservada e um parser
registrará o total de itens de cada regra. Serão aceitas como regras de três
itens somente as que tiverem essa soma igual a três. Se uma execução
exploratória precisar de `-N` maior que 30 para localizar 30 regras válidas,
ela será preservada e identificada explicitamente como exploratória. A
execução final obrigatória permanecerá com `-N 30`; ela não será apresentada
como substituta da exploração.

Nenhuma sintaxe de mineração foi inferida além das opções listadas acima. A
execução do algoritmo permanece vedada até a etapa autorizada.

## Limitação crítica identificada antes dos testes de suporte

Na Etapa 7, a inspeção da implementação instalada (`weka.associations.Apriori`
e `weka.associations.AprioriItemSet`) confirmou o texto interno da opção `-Z`:

```text
If enabled, zero (that is, the first value of a nominal) is treated in the
same way as a missing value.
```

Portanto, em atributos nominais o WEKA 3.8.7 não procura o texto `0`: ele trata
como ausente a categoria de índice zero, isto é, a **primeira categoria
declarada no ARFF**. Na base atual essas categorias são reais:

| Atributo | Primeira categoria nominal do ARFF | Efeito de `-Z` |
|---|---|---|
| `FAIXA_CREDITO` | `CREDITO_ALTO` | seria tratada como ausente |
| `FAIXA_RENDA` | `RENDA_ALTA` | seria tratada como ausente |
| `FAIXA_IDADE` | `IDADE_21_A_29` | seria tratada como ausente |
| `CATEGORIA_FILHOS` | `DOIS_OU_MAIS_FILHOS` | seria tratada como ausente |
| `POSSE_CARRO` | `COM_CARRO` | seria tratada como ausente |
| `SITUACAO_FAMILIAR` | `CASADO_OU_UNIAO_CIVIL` | seria tratada como ausente |
| `FAIXA_CREDITOS_ATIVOS` | `SEM_CREDITOS_ATIVOS` | seria tratada como ausente |
| `FAIXA_TAXA_REJEICAO` | `REJEICAO_PREVIA_ACIMA_25_PCT` | seria tratada como ausente |

Executar Apriori com `-Z` nessas condições descartaria observações
semanticamente válidas e violaria a decisão anterior de não tratar zeros reais
como ausentes. Nenhum teste de suporte foi executado sobre esse ARFF nominal.

## Correção metodológica — representação binária transacional

A primeira representação discretizada utiliza oito atributos nominais
multivalorados. Durante a auditoria do Apriori no WEKA 3.8.7, verificou-se que
`treatZeroAsMissing=true` (`-Z`) trata o primeiro valor nominal de cada
atributo como ausente. Como os primeiros valores eram categorias reais,
executar o algoritmo nesse formato distorceria os suportes.

Para atender ao requisito sem eliminar informação válida, foi criada a
representação binária transacional
`data/preparadas/base_apriori_binaria.arff`. Cada categoria discretizada passou
a representar um item binário independente, no qual `0` indica ausência e `1`
presença. Todas as 27 declarações do ARFF usam obrigatoriamente `{0,1}`, nessa
ordem. Assim, `-Z` ignora apenas itens ausentes e preserva os valores `1` como
itens presentes.

A transformação não altera as discretizações nem aumenta conceitualmente a
quantidade de características selecionadas: continuam existindo as oito
dimensões originais. As 27 colunas binárias constituem somente a representação
técnica de suas categorias para mineração de regras de associação.

As bases `data/discretizadas/base_apriori_discretizada.csv` e `.arff` foram
preservadas sem alterações como representação humana e interpretável. A base
binária possui 10.000 transações, 27 itens e exatamente oito valores `1` por
linha. Nenhum Apriori foi executado na correção.

## Registro da Etapa 7: execução experimental e limite encontrado

Os testes reais de suporte passaram a usar exclusivamente
`data/preparadas/base_apriori_binaria.arff`, com os parâmetros obrigatórios
`-N 30`, `-I` e `-Z`. No Java 17, o comando também requer
`--add-opens java.base/java.lang=ALL-UNNAMED` para compatibilidade de reflexão
com o WEKA 3.8.7.

Com a confiança padrão `-C 0.90` e a métrica padrão, foram preservadas 21
tentativas entre suporte efetivo 0,50 e 0,01. Nenhuma produziu 30 regras de
exatamente três itens. O máximo com `-N 30` foi quatro; em busca exploratória,
com `-N 200`, o máximo foi 13. O inventário completo está em
`resultados/apriori/testes_suporte/resumo_testes_suporte.csv`.

Por isso, não há ainda configuração final de Apriori e a Etapa 8 não pode ser
iniciada. Alterar `-C` ou a métrica de ordenação exigirá autorização explícita,
pois esses parâmetros não foram definidos pelo enunciado e afetam diretamente
quais regras são retornadas.

### Atualização após autorização

Após autorização do usuário, foram testadas Lift (`-T 1`), Leverage (`-T 2`) e
Conviction (`-T 3`), com diferentes pontuações mínimas. O candidato selecionado
para suporte é `lowerBoundMinSupport=0.01`, com `upperBoundMinSupport=0.01`,
`delta=0.01`, `-T 1`, `-C 0.00`, `-I` e `-Z`.

Na execução exploratória `-N 2000`, essa configuração gerou 1.504 regras e 36
regras de exatamente três itens. A execução separada, obrigatória, com `-N 30`
gerou 30 regras de cinco ou seis itens; o WEKA não possui filtro nativo para
priorizar tamanho total igual a três. As duas saídas são preservadas para que a
etapa posterior possa distinguir a configuração obrigatória da seleção técnica
das regras de três itens.
