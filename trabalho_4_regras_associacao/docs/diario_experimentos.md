# Diário de experimentos — Trabalho 4

## Etapa 0 — Auditoria do repositório

- Situação: concluída antes da criação deste diretório.
- Fonte candidata confirmada: `base_amostra_10000_analise.csv`.
- Evidência: os 10.000 registros e todos os campos foram conferidos contra a
  base final do Trabalho 1; os valores são originais e não ponderados.
- Restrição registrada: `ROW_ID_AMOSTRA`, `SK_ID_CURR` e `TARGET` não poderão
  participar do Apriori.
- Base excluída como entrada direta: `base_clusterizacao_final.csv`, pois usa
  Min-Max e multiplicação por raiz do peso nos atributos numéricos.

## Etapa 1 — Estrutura inicial

- Situação: documentação mínima criada.
- Não houve processamento de dados, discretização, seleção de atributos, uso
  do WEKA ou execução de Apriori.

## Etapa 2 — Análise de candidatos

- Situação: concluída; a escolha dos oito atributos permanece sujeita a
  aprovação expressa.
- Foram examinados 13 candidatos em 10.000 registros, sem alterar a base de
  origem. Foram geradas estatísticas descritivas, frequências categóricas,
  histogramas e boxplots.
- Recomendação: `AMT_CREDIT`, `AMT_INCOME_TOTAL`, `AGE_YEARS`, `CNT_CHILDREN`,
  `FLAG_OWN_CAR_COD`, `NAME_FAMILY_STATUS_COD`, `SER_CREDITOS_ATIVOS` e
  `PREV_TAXA_REJEICAO`.
- Principais descartes: `CREDIT_INCOME_RATIO` é derivado de crédito e renda;
  `SER_DIVIDA_ATRASADA` possui 98,80% de zeros; `REGION_RATING_CLIENT` tem
  apenas três níveis e 74,16% na categoria dominante.
- Foi identificada correlação de Spearman de 0,7657 entre
  `SER_CREDITOS_ATIVOS` e `SER_QTDE_EMPRESTIMOS` e de 0,5488 entre
  `PREV_QTDE_TENTATIVAS` e `PREV_TAXA_REJEICAO`, apoiando a retenção de uma
  variável de cada par para reduzir redundância.
- Limitações observadas: renda tem assimetria muito alta (99,018857) e máximo
  de R$ 117.000.000; a categoria `Unknown` de estado familiar aparece uma vez
  (0,01%) e exigirá decisão explícita na discretização; a taxa de rejeição tem
  67,71% de zeros semânticos.
- A geração dos gráficos emitiu avisos não bloqueantes do cache externo do
  Matplotlib sem comprometer os três PNGs; também há aviso de depreciação de
  opção de boxplot que não altera os resultados atuais.

## Etapa 3 — Projeto das faixas de discretização

- Situação: concluída; aplicação das faixas na base final ainda depende de
  aprovação expressa.
- A autorização para iniciar esta etapa foi registrada como aprovação dos oito
  atributos recomendados na Etapa 2, exclusivamente para o projeto das faixas.
- Foram simuladas 27 categorias para os oito atributos recomendados, apenas em
  memória, sobre a mesma amostra original de 10.000 registros.
- Crédito e renda usam os quartis reais P25, P50 e P75. Os cortes de renda
  evitam intervalos de mesma largura, inadequados diante do máximo de
  R$ 117.000.000 e da forte assimetria observada.
- As cinco faixas semânticas de idade variaram de 12,18% a 26,60% da amostra.
- `CNT_CHILDREN`, `SER_CREDITOS_ATIVOS` e `PREV_TAXA_REJEICAO` receberam
  rótulos para seus zeros reais, respectivamente `SEM_FILHOS`,
  `SEM_CREDITOS_ATIVOS` e `SEM_REJEICAO_PREVIA`.
- `FLAG_OWN_CAR_COD` foi recuperado como `SEM_CARRO`/`COM_CARRO`.
- O único registro `Unknown` de estado familiar foi agrupado com separado e
  viúvo para evitar uma categoria com 0,01% da amostra.
- Validações: oito atributos; 10.000 rótulos válidos por atributo; nenhuma
  categoria ausente; nenhuma categoria abaixo de 1% ou 5%; nenhum zero
  numérico usado como categoria.

## Etapa 4 — Geração da base discretizada

- Situação: concluída.
- Foram gerados `data/discretizadas/base_apriori_discretizada.csv` e o ARFF
  auxiliar de mesmo nome, a partir das faixas aprovadas na Etapa 3.
- A base possui exatamente 10.000 registros e oito atributos nominais:
  `FAIXA_CREDITO`, `FAIXA_RENDA`, `FAIXA_IDADE`, `CATEGORIA_FILHOS`,
  `POSSE_CARRO`, `SITUACAO_FAMILIAR`, `FAIXA_CREDITOS_ATIVOS` e
  `FAIXA_TAXA_REJEICAO`.
- Não há `SK_ID_CURR`, `TARGET`, `ROW_ID_AMOSTRA`, `cluster`, pesos,
  normalização Min-Max, raiz de peso, valores vazios, marcadores ausentes ou
  zero numérico como categoria.
- A ordem foi preservada pela transformação indexada da amostra de origem. A
  sequência original de `ROW_ID_AMOSTRA`, mantida apenas na origem auxiliar,
  gerou SHA-256 `2ec321e75e28488b83455ba9b64a2ec00fe9470188b0bc6060d837aa56272f5d`
  quando serializada com separador `|`.
- O ARFF foi validado sem WEKA: possui oito declarações nominais, 10.000 linhas
  de dados e nenhum marcador `?`.

## Etapa 5 — Validação da base Apriori

- Situação: concluída e aprovada em todos os dez controles registrados em
  `resultados/discretizacao/validacao_base.csv`.
- A comparação independente recompôs as categorias a partir da amostra de
  origem e confirmou a mesma sequência de 10.000 registros no CSV salvo.
- Foram calculadas as frequências dos 27 itens nominais. Cada atributo soma
  exatamente 10.000 ocorrências; os suportes individuais variam de 10,34%
  (`CATEGORIA_FILHOS=DOIS_OU_MAIS_FILHOS`) a 73,04%
  (`SITUACAO_FAMILIAR=CASADO_OU_UNIAO_CIVIL`).
- A base continua sem valores ausentes, campos protegidos, atributos numéricos
  ou representações numéricas de zero.
- Nenhum WEKA ou Apriori foi executado nesta etapa.

## Etapa 6 — Auditoria das opções do Apriori no WEKA

- Situação: concluída.
- A consulta real à classe `weka.core.Version` confirmou WEKA 3.8.7 no JAR
  `C:\Program Files\Weka-3-8-7\weka.jar`; o Java em uso foi OpenJDK Temurin
  17.0.20.
- A ajuda real de `weka.associations.Apriori -h` confirmou `-N`, `-M`, `-U`,
  `-D`, `-I` e `-Z`, com os padrões respectivos de 10 regras, suporte mínimo
  inferior 0,1, superior 1,0, delta 0,05, itemsets desativados e zero não
  tratado como ausente.
- Não há opção nativa listada para limitar regras a exatamente três itens.
  A saída integral será preservada e o tamanho será verificado posteriormente
  pela soma dos itens de antecedente e consequente.
- Nenhuma base foi fornecida ao Apriori nesta etapa; não houve mineração,
  itemsets ou regras geradas.

## Etapa 7 — Busca do suporte (interrompida antes de executar)

- Situação: bloqueada por incompatibilidade metodológica confirmada na
  implementação real do WEKA 3.8.7.
- A opção obrigatória `-Z` trata como ausente o primeiro valor de **todo**
  atributo nominal, independentemente do texto que representa a categoria.
- Os primeiros valores declarados no ARFF atual são categorias reais, como
  `CREDITO_ALTO`, `COM_CARRO` e `CASADO_OU_UNIAO_CIVIL`. Minerar com `-Z`
  eliminaria essas observações e distorceria os suportes.
- Nenhum teste de suporte, itemset ou regra foi executado; portanto, não há
  resultados artificiais ou tentativas a preservar nesta etapa.
- É necessária orientação explícita para conciliar `treatZeroAsMissing=true`
  com os oito atributos nominais sem transformar categorias reais em ausentes.

## Etapa 6B — Codificação binária transacional

- Situação: concluída. A correção metodológica autorizada criou uma
  representação técnica adicional, sem modificar as bases discretizadas
  semânticas.
- A entrada `data/discretizadas/base_apriori_discretizada.csv` permanece com
  SHA-256 `a7444cbdadd0891837c7bf5f29c40e36eb68a5e7cf6a480b50d8435044c5a1a9`.
- O one-hot encoding confirmou programaticamente 27 categorias e gerou 27
  atributos binários `{0,1}` para 10.000 registros.
- Cada linha possui exatamente oito valores `1`, um para cada dimensão
  conceitual; a reconstrução nominal linha a linha corresponde à base de
  origem na mesma ordem.
- As frequências das 27 colunas binárias são exatamente iguais às frequências
  já validadas das categorias nominais. Exemplos: `SEM_FILHOS=6961`,
  `SEM_CARRO=6605`, `COM_CARRO=3395` e
  `CASADO_OU_UNIAO_CIVIL=7304`.
- O ARFF técnico possui 27 declarações `{0,1}`, 10.000 linhas e nenhum `?`.
  Assim, `-Z` passa a ignorar apenas itens ausentes (`0`) e considera itens
  presentes (`1`).
- Nenhum Apriori, busca de suporte, itemset ou regra foi executado nesta
  correção; a Etapa 7 continua parada até nova autorização.

## Etapa 7 — Busca do `lowerBoundMinSupport` na representação binária

- Situação: bloqueada após busca real e auditável, sem um
  `lowerBoundMinSupport` candidato que satisfaça simultaneamente os requisitos.
- A entrada usada exclusivamente foi
  `data/preparadas/base_apriori_binaria.arff`, cuja codificação `{0,1}` torna
  `-Z` semanticamente correto: `0` é ausência de item e `1` é presença.
  As bases nominais discretizadas não foram usadas nem modificadas.
- Foram preservadas 21 tentativas em `resultados/apriori/testes_suporte/`, cada
  uma com a saída integral do WEKA e a configuração correspondente. O resumo
  consolidado é `resultados/apriori/testes_suporte/resumo_testes_suporte.csv`.
- Todas as execuções classificadas como finais usaram obrigatoriamente `-N 30`,
  confiança `-C 0.90`, a métrica padrão, `-I` e `-Z`. As execuções com `-N 200`
  e `-N 1000` foram exclusivamente exploratórias e estão identificadas como
  tal, sem substituir a execução final exigida.
- A busca percorreu suporte efetivo de 0,50 a 0,01, incluindo janelas de
  suporte e controles com `upperBoundMinSupport` fixado. Em cada teste foram
  registrados itemsets, número de regras, regras com exatamente três itens e
  tempos de execução.
- O maior resultado com `-N 30` foi de quatro regras de três itens: isso
  ocorreu em suportes efetivos entre 0,10 e 0,02. Em 0,02 o WEKA retornou as
  30 regras solicitadas, mas apenas quatro tinham exatamente três itens. Em
  0,01 retornou 30 regras, porém nenhuma tinha exatamente três itens.
- A exploração ampliada confirmou que reduzir suporte, mantendo `-C 0.90`, não
  resolve o requisito: com suporte efetivo 0,02 e `-N 200` houve 13 regras de
  três itens; com suporte efetivo 0,01, `-N 200` teve uma e `-N 1000` teve duas.
  As regras mais bem classificadas passam a ter quatro ou mais itens.
- A instalação Java exigiu a opção de compatibilidade
  `--add-opens java.base/java.lang=ALL-UNNAMED` para evitar a falha de reflexão
  do WEKA 3.8.7 no Java 17. A primeira tentativa que exibiu esse aviso também
  foi preservada; as seguintes registram a execução compatível.
- Não foi alterada silenciosamente a confiança mínima, a métrica de ordenação
  nem qualquer outra configuração analítica. Como tais mudanças podem alterar
  materialmente o conjunto de regras, a etapa requer autorização explícita
  antes de novos testes.

### Retomada autorizada e resultado final da Etapa 7

- Com autorização expressa, foram acrescentados 11 testes, totalizando 32
  tentativas preservadas. Foram avaliadas as métricas Lift, Leverage e
  Conviction, além de diferentes valores de pontuação mínima.
- A configuração que atendeu ao critério exploratório foi: ordenação por Lift
  (`-T 1`), pontuação mínima `-C 0.00`, suporte inferior e superior ambos em
  `0.01`, `-I` e `-Z` ativos. Com `-N 2000`, o WEKA retornou 1.504 regras, das
  quais 36 têm exatamente três itens. Portanto, há mais de 30 regras válidas
  no suporte efetivo de 0,01.
- A execução obrigatória correspondente com `-N 30` foi preservada em
  `param_autorizado_lift_c000_s001_n30`. Ela retornou 30 regras, todas com
  cinco ou seis itens. Isto decorre da ordenação por Lift: as primeiras regras
  classificadas não são necessariamente as de três itens. Essa execução não
  substitui nem invalida a seleção das 36 regras de três itens identificadas
  na saída exploratória.
- A divergência entre `-N 30` e a necessidade de filtrar por tamanho é uma
  limitação operacional do Apriori do WEKA 3.8.7, pois a ajuda real não fornece
  opção para restringir diretamente o total de itens da regra. A distinção
  entre execução obrigatória e exploratória permanece explícita e auditável.
- Houve uma falha de serialização somente ao registrar a distribuição de
  tamanhos da tentativa exploratória `N=2000`; a execução do WEKA já havia
  terminado e sua saída integral havia sido salva. O metadado foi então
  reconstruído dessa mesma saída, sem repetir ou sobrescrever a tentativa.

## Etapa 8 — Execução final do Apriori

- Situação: concluída. A execução foi realizada no WEKA 3.8.7 com suporte
  inferior e superior de 0,01, delta de 0,01, ordenação por Lift (`-T 1`),
  pontuação mínima `-C 0.00`, `-N 30`, `-I` e `-Z`.
- A saída integral original foi preservada em
  `resultados/apriori/execucao_final/resultado_apriori_final.txt`; a extração
  literal do trecho de itemsets está em `itemsets_apriori_final.txt` e a
  configuração efetiva, com métricas observadas, está em
  `configuracao_apriori_final.json`.
- O WEKA retornou 30 regras e 5.119 itemsets: 27 em L(1), 309 em L(2), 1.405
  em L(3), 2.103 em L(4), 1.093 em L(5), 176 em L(6) e seis em L(7). O tempo
  interno informado foi 4,22 segundos.
- As 30 regras retornadas têm cinco ou seis itens (12 e 18 regras,
  respectivamente). Esse fato é preservado, não corrigido manualmente, e será
  considerado na Etapa 9 ao distinguir a saída final da saída exploratória que
  contém as 36 regras de três itens.

## Etapa 9 — Parse das regras e itemsets

- Situação: concluída. O script `scripts/07_analisar_saida_apriori.py` lê as
  saídas textuais preservadas do WEKA e não recalcula confiança, Lift,
  Leverage ou Conviction. O suporte relativo no CSV é a conversão explícita do
  suporte absoluto informado pelo WEKA, dividido pelas 10.000 transações.
- `resultados/regras/regras_apriori_completas.csv` contém as 30 regras da
  execução final, nos campos solicitados. Há 12 regras com cinco itens e 18
  com seis itens; não existem regras de três itens nessa saída obrigatória.
- `resultados/itemsets/itemsets_apriori.csv` contém os 5.119 itemsets da saída
  final, com tamanho e suportes absoluto e relativo. Não foram encontrados
  itemsets duplicados ou campos vazios.
- Foi criado também `resultados/regras/regras_apriori_exploratorias_completas.csv`
  exclusivamente para rastreabilidade da execução exploratória aprovada na
  Etapa 7. Ele contém 1.504 regras, incluindo 36 de exatamente três itens, e
  não representa uma seleção ou ordenação final.
- O script foi compilado e as contagens extraídas foram confrontadas com as
  saídas originais: 30 regras finais, 1.504 exploratórias e 5.119 itemsets.

## Etapa 10 — Construção do conjunto fechado

- Situação: concluída. O script `scripts/08_gerar_conjunto_fechado.py` aplicou
  formalmente a definição de fechamento usando suporte absoluto: um itemset só
  foi removido se existisse superconjunto próprio com o mesmo suporte.
- Dos 5.119 itemsets, 5.072 são fechados e 47 não são fechados. A auditoria
  completa está em `resultados/conjunto_fechado/auditoria_fechamento.csv`; os
  subconjuntos estão separados em `itemsets_fechados.csv` e
  `itemsets_nao_fechados.csv`.
- Cada um dos 47 itens não fechados contém um superconjunto-testemunha e o
  motivo da exclusão. Por exemplo, o itemset formado por idade de 60 anos ou
  mais, sem carro, situação separada/viúva/não informada, um a dois créditos
  ativos e sem rejeição prévia tem suporte 100 e é subconjunto próprio do mesmo
  conjunto acrescido de `CATEGORIA_FILHOS__SEM_FILHOS`, também com suporte 100.
- Todas as 30 regras da execução final correspondem a itemsets fechados. Das
  1.504 regras exploratórias, 1.412 correspondem a itemsets fechados; as 36
  regras de três itens permanecem todas no conjunto fechado.
- Foram gerados `regras_conjunto_fechado.csv` para a saída final e
  `regras_exploratorias_conjunto_fechado.csv` para a saída exploratória. A
  separação preserva a origem das regras e não realiza ordenação ou seleção.
- A validação independente confirmou para todos os itemsets fechados a ausência
  de superconjunto com suporte igual, e para todos os não fechados a relação de
  subconjunto próprio com a testemunha registrada.

## Etapa 11 — Top 20 por Lift

- Situação: concluída. O script `scripts/09_selecionar_regras.py` utilizou
  somente as regras da execução exploratória que pertencem ao conjunto fechado,
  têm exatamente três itens e possuem métricas numéricas finitas.
- Havia 36 regras elegíveis. Elas foram ordenadas por Lift decrescente; empates
  foram resolvidos por suporte e, depois, por confiança, ambos decrescentes.
  As 20 primeiras foram registradas em `resultados/regras/top20_regras_lift.csv`.
- O Lift do Top 20 varia de 1,11 a 0,95. A presença de valores menores que um
  não foi ocultada: essas regras permanecem na tabela porque são as melhores
  vinte entre as 36 regras elegíveis conforme o critério solicitado. A
  interpretação será realizada somente na próxima etapa.
- A validação confirmou as 20 posições sequenciais, três itens em cada regra,
  vínculo de todas ao conjunto fechado, métricas finitas e ordenação correta.
- Um primeiro verificador auxiliar tentou contar o sufixo técnico `=1`; o
  parser já o havia removido dos nomes exibidos no CSV. A checagem foi corrigida
  para contar os identificadores de categoria, sem alterar a seleção ou seus
  arquivos.

## Etapa 12 — Regras óbvias, interessantes e novidades

- Situação: concluída. O script `scripts/10_analisar_regras.py` gerou
  `resultados/regras/analise_top20_regras.csv`, acrescentando uma classificação
  e uma justificativa individual para cada regra do Top 20.
- Foram classificadas 16 regras como ÓBVIA, três como INTERESSANTE e uma como
  NOVIDADE. A classificação não foi determinada automaticamente pelo Lift.
- Regras inversas ou diferentes direções do mesmo itemset foram tratadas como
  óbvias para não contar a mesma coocorrência repetidamente. Regras com Lift
  próximo de um, ou com confiança explicável pela categoria familiar dominante,
  também foram consideradas óbvias.
- A única novidade é preliminar: crédito muito alto combinado com situação
  familiar separada/viúva/não informada associado a um a dois créditos ativos
  (Lift 1,10; confiança 48%; suporte 1%). Ela reúne dimensões diferentes e não
  é uma relação construída por fórmula, mas não deve ser generalizada sem nova
  validação devido ao suporte baixo e ao Lift moderado.
- As regras interessantes têm Lift positivo, porém pequeno, e suporte de 1%;
  foram mantidas como hipóteses analíticas, não como recomendação causal ou
  operacional.
- A validação foi executada lendo os CSVs em UTF-8. Um primeiro comparador
  auxiliar tratou cabeçalhos acentuados de modo incompatível com o console; a
  verificação Unicode foi repetida diretamente em Python e confirmou as 20
  posições, as classificações válidas e as justificativas não vazias, sem
  alterar os dados.

## Etapa 13 — Visualizações

- Situação: concluída. O script `scripts/11_gerar_graficos.py` produziu quatro
  imagens PNG em `relatorio/imagens/regras/`, todas em resolução adequada para
  inserção no relatório.
- `01_top20_lift.png` apresenta o ranking das 20 regras, a linha de referência
  Lift igual a um e a classificação das regras. `02_confianca_lift_classificacao.png`
  mostra a relação entre confiança e Lift, deixando explícita a concentração de
  métricas próximas da independência.
- `03_distribuicao_classificacao.png` sintetiza as 16 regras óbvias, três
  interessantes e uma novidade. `04_frequencia_itens_top20.png` apresenta os
  itens mais recorrentes no conjunto selecionado.
- O gráfico originalmente sugerido de suporte versus confiança não foi criado:
  todas as regras do Top 20 têm suporte de 1%, de modo que um eixo de suporte
  não acrescentaria informação visual. Foi usado o gráfico de confiança versus
  Lift, que diferencia efetivamente as regras sem alterar valores.
- Todas as imagens foram abertas para inspeção visual e validadas como PNGs.
  As resoluções variam de 2.196×1.489 a 3.629×2.010 pixels. Um comando inicial
  de pré-checagem de diretório foi corrigido antes da validação; como a pasta não
  possuía imagens, nenhum arquivo prévio foi sobrescrito.

## Etapa 14 — Relatório acadêmico

- Situação: concluída com ressalva de renderização. O script
  `scripts/12_gerar_relatorio.py` criou o relatório detalhado em Markdown e
  DOCX a partir dos CSVs e imagens auditáveis, sem inventar métricas.
- O relatório contém capa e folha de rosto com campos institucionais explícitos
  para preenchimento, sumário provisório, as 42 seções solicitadas, 32 testes
  de suporte, tabelas do Top 20, referências e apêndice de rastreabilidade.
- A versão DOCX contém 44 cabeçalhos estruturados, quatro tabelas e as quatro
  figuras geradas na Etapa 13. A versão Markdown contém as 42 seções
  obrigatórias e referências às mesmas figuras.
- O sumário automático, a paginação, a formatação ABNT definitiva e a produção
  do PDF não foram antecipados: pertencem às Etapas 15 e 16.
- Foi tentada a renderização obrigatória do DOCX pelo renderizador da habilidade
  de documentos. A primeira tentativa falhou por permissão do diretório
  temporário da sandbox; a repetição fora da sandbox chegou ao LibreOffice, mas
  falhou porque o executável `soffice` não está instalado neste ambiente. Por
  isso, nesta etapa foi feita validação estrutural do pacote DOCX, não inspeção
  visual de páginas. A limitação permanece registrada para a revisão final.

## Etapa 15 — Revisão final ABNT

- Situação: concluída com ressalva de renderização. O gerador do relatório foi
  atualizado e o DOCX foi regenerado com página A4, margens superior/esquerda
  de 3 cm, direita/inferior de 2 cm, Times New Roman 12, espaçamento 1,5,
  alinhamento justificado e recuo de primeira linha de 1,25 cm.
- Os títulos das tabelas permanecem acima dos dados e as fontes abaixo; os
  cabeçalhos receberam preenchimento cinza e as figuras receberam título acima
  e fonte abaixo. A numeração de página foi inserida no rodapé.
- Foi incluído campo TOC e a configuração para atualização de campos ao abrir o
  documento. A atualização efetiva de páginas do sumário dependerá de abrir o
  arquivo em editor compatível e atualizar os campos; isso será conferido na
  validação final quando houver ferramenta de renderização disponível.
- A validação estrutural confirmou as dimensões A4, as quatro margens, fonte,
  tamanho, espaçamento, recuo e presença do campo TOC. A inspeção visual não
  foi possível porque `soffice` e `WINWORD.EXE` não estão instalados neste
  ambiente; portanto, não foi gerado PDF nesta etapa.
