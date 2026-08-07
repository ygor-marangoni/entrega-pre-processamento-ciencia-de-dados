# Diário de experimentos

## Etapa 0 — Auditoria

- Base auditada: 307.511 registros e 41 colunas.
- Separador identificado: `;`.
- Todos os dez atributos candidatos estavam presentes.
- Nenhum valor de Hopkins foi calculado.

## Etapa 1 — Estrutura

- Estrutura inicial criada.
- `p1.py` e `p2.py` copiados sem alteração para `scripts/originais/`.
- `p1.py` e `p2.py` da raiz movidos para `scripts/`, pois pertencem ao Trabalho 3.
- Trabalho 1 separado em diretório próprio.
- Nenhuma base amostral ou ponderada foi criada.

## Etapa 2 — Amostra reproduzível

- Data de geração: 2026-07-21T20:01:21-03:00.
- Origem: `trabalho_1_preprocessamento/data/base_final_preprocessada.csv`.
- Amostragem sem reposição: 10.000 de 307.511 registros.
- Seed e `random_state`: 42.
- `ROW_ID_AMOSTRA`: posição 1-based na base de origem.
- Base completa: 10.000 linhas e 40 colunas, sem `SK_ID_CURR` e `TARGET`.
- Base de análise: 10.000 linhas e 42 colunas, com `SK_ID_CURR` e `TARGET`.
- Hash da base completa: `aac7843e20c7f29f10730bc4cc6de057305a8c3867ba63a132f613ff87942fd6`.
- Hash da base de análise: `fbc3e8d592bf406b65c93e445f7849a68685eccd7637689344d68a78404a3b22`.
- Segunda geração temporária produziu os mesmos hashes nos dois CSVs.
- Nenhum atributo foi selecionado e Hopkins não foi executado.

## Etapa 3 — Análise exploratória e proposta

- Etapa 2 revalidada antes da análise; hashes, ordem e colunas protegidas permaneceram corretos.
- Amostra analisada: 10.000 registros.
- Atributos candidatos analisados: 10.
- Ausentes nos candidatos: zero.
- Saídas gráficas: 10 histogramas e 10 boxplots, inspecionados visualmente.
- `AMT_INCOME_TOTAL` apresentou mediana 148.500, máximo 117 milhões e assimetria 99,02; foi mantido como alternativa porque o Min-Max seria dominado pelo extremo.
- `SER_DIVIDA_ATRASADA` apresentou 98,80% de zeros e assimetria 59,77; foi mantido como alternativa de baixo peso.
- Proposta principal pendente: `AMT_CREDIT` (6), `CNT_CHILDREN` (4), `FLAG_OWN_CAR_COD` (1, nominal), `AGE_YEARS` (5), `CREDIT_INCOME_RATIO` (7) e `SER_CREDITOS_ATIVOS` (5).
- Alternativas: `AMT_INCOME_TOTAL` (4), `REGION_RATING_CLIENT` (3, ordinal), `SER_DIVIDA_ATRASADA` (2) e `NAME_FAMILY_STATUS_COD` (1, nominal).
- No p1 original, peso nominal maior que zero funciona como inclusão e não reescala a distância; os nominais receberam peso 1.
- Nenhuma base ponderada foi gerada e Hopkins não foi executado.

## Etapa 4 — Base ponderada da tentativa 01

- Configuração aprovada: `AMT_CREDIT` (6), `CNT_CHILDREN` (4), `FLAG_OWN_CAR_COD` (1, nominal), `AGE_YEARS` (5), `CREDIT_INCOME_RATIO` (7) e `SER_CREDITOS_ATIVOS` (5).
- Registros: 10.000; atributos na base preparada: 6.
- Numéricos: Min-Max multiplicado por `sqrt(peso)`, conforme o `p1.py` original.
- Nominal: `FLAG_OWN_CAR_COD` recuperado de 0/1 para N/Y e preservado sem multiplicação pela raiz do peso.
- Valores ausentes encontrados e imputados: zero.
- `SK_ID_CURR`, `TARGET` e `ROW_ID_AMOSTRA` não foram incluídos na base preparada.
- A ordem foi preservada e vinculada à base auxiliar pelo hash da sequência de `ROW_ID_AMOSTRA`.
- Hash da base preparada: `00fb8f3e1fe9524694acac5e46eafebdc1bee8e358fde2eaa38267ac57baeac8`.
- Hash da configuração: `358fe8a9f08e80ad3103d169df2404d48eef09bf1614dc0676c83a28c550498f`.
- Hopkins não foi executado.

## Etapa 5 — Hopkins da tentativa 01

- Base: `data/preparadas/base_clusterizacao_tentativa_01.csv`.
- Hash da base: `00fb8f3e1fe9524694acac5e46eafebdc1bee8e358fde2eaa38267ac57baeac8`.
- Base Hopkins: 10.000 registros.
- Amostra real: 100 registros; amostra virtual: 100 registros.
- Seed da amostragem e da geração virtual: 42.
- Distância: euclidiana mista; nominal One-Hot multiplicado por `1/sqrt(2)`.
- Soma das distâncias virtuais `u`: 115,886456441970.
- Soma das distâncias reais `w`: 7,168507999202.
- Hopkins: `0,941745479089`.
- Limiar exigido: 0,7; decisão: configuração aprovada para preparação do WEKA.
- Reprodutibilidade confirmada em duas execuções internas e por recálculo independente com `scipy.spatial.distance.cdist`.
- `scikit-learn` 1.9.0 utilizado.
- `n_jobs=1` foi usado porque o paralelismo do p2 original foi bloqueado pelo ambiente Windows; o valor matemático não é alterado.
- Nenhum campo ou peso foi ajustado e a Etapa 6 não foi iniciada.

## Etapa 6 — Formalização da configuração final

- Hopkins da tentativa 01 revalidado: `0,941745479089`, superior ao limiar 0,7.
- Nenhum atributo, tipo ou peso foi alterado.
- Nenhuma tentativa 02 foi criada.
- `base_clusterizacao_tentativa_01.csv` foi preservada e copiada como `base_clusterizacao_final.csv`.
- `configuracao_tentativa_01.csv` foi preservada e copiada como `configuracao_final.csv`.
- Hash da base final: `00fb8f3e1fe9524694acac5e46eafebdc1bee8e358fde2eaa38267ac57baeac8`.
- Hash da configuração final: `358fe8a9f08e80ad3103d169df2404d48eef09bf1614dc0676c83a28c550498f`.
- Conversão ARFF e preparação do WEKA não foram iniciadas.

## Etapa 7 — Conversão para ARFF e preparação do WEKA

- Entrada: `data/preparadas/base_clusterizacao_final.csv`.
- Configuração: `resultados/configuracoes/configuracao_final.csv`.
- Saída: `data/preparadas/base_clusterizacao_final.arff`.
- Registros: 10.000; atributos: 6.
- Tipos: cinco atributos `numeric` e `FLAG_OWN_CAR_COD` nominal `{N,Y}`.
- `SK_ID_CURR`, `TARGET` e `ROW_ID_AMOSTRA` permanecem ausentes.
- Ordem e valores comparados integralmente com o CSV por um segundo parser ARFF.
- Hash do ARFF: `65fa29f4c6d45fc0f0cb9799c2da630757b7718cc11c2e7f453700de932038a3`.
- Procedimento do filtro `AddCluster` documentado em `docs/instrucoes_weka.md`.
- Nenhum algoritmo de clusterização foi executado ou simulado.

## Etapa 8 — DBSCAN no WEKA

- Ambiente: WEKA 3.8.7 e pacote oficial `optics_dbScan` 1.0.6.
- Filtro real: `weka.filters.unsupervised.attribute.AddCluster`.
- Entrada: `data/preparadas/base_clusterizacao_final.arff`.
- Distância: `weka.core.EuclideanDistance -R first-last -D`.
- A opção `-D` desativou a normalização interna para preservar os pesos já aplicados.
- `minPoints`: 6 em todos os testes; seed não aplicável nesta implementação.
- Curva do sexto vizinho: joelho em `epsilon = 0,274264329676`.
- Teste 01: `epsilon = 0,25`; 9 clusters; 396 ruídos; 3,96%; 7,805 s.
- Teste 02: `epsilon = 0,274264329676`; 9 clusters; 296 ruídos; 2,96%; 7,740 s.
- Teste 03: `epsilon = 0,30`; 9 clusters; 217 ruídos; 2,17%; 6,491 s.
- Teste 02 escolhido como referência por corresponder ao joelho da curva.
- Base escolhida preservada como teste 02 e copiada para `base_clusterizada_dbscan.arff`.
- As seis colunas originais, os 10.000 registros e a ordem foram validados após a exportação.
- Os nove grupos são referência para testes posteriores, não um “K perfeito”.

## Etapa 9 — SimpleKMeans

- Autorização conjunta recebida para executar sequencialmente as Etapas 9 e 10.
- Testes: K=8, K=9 e K=10; seed 42; inicialização aleatória `init=0`.
- Máximo de iterações: 500; uma thread; opção `-fast` desativada.
- Distância: `weka.core.EuclideanDistance -R first-last -D`.
- K=8: 37 iterações; SSE 2386,976059874797; grupos entre 583 e 1.992 registros.
- K=9: 62 iterações; SSE 2284,489341365910; grupos entre 525 e 1.992 registros.
- K=10: 57 iterações; SSE 2172,711624193117; grupos entre 459 e 1.987 registros.
- K=9 escolhido como compromisso: maior Silhouette entre os três K, alta entropia dos tamanhos, comparabilidade com o DBSCAN e ausência de cotovelo claro no SSE.
- ARFFs gerados pelo `AddCluster`; CSVs exportados pelo `CSVSaver` do WEKA com 17 casas.

## Etapa 11 — Validação e junção das exportações

- Scripts criados: `07_validar_exportacao_weka.py` e `08_mesclar_clusters.py`.
- DBSCAN, SimpleKMeans e EM confirmados com 10.000 registros e sete colunas no total: seis atributos de entrada e `cluster`.
- Os seis atributos de entrada foram comparados integralmente com a base preparada.
- Ordem, nomes, valores e quantidade de registros permaneceram inalterados.
- DBSCAN: nove clusters e 296 ruídos; K-Means e EM: nove clusters sem ausentes.
- Bases auxiliares geradas em `data/analise/`, cada uma com 10.000 linhas e 49 colunas.
- Valores transformados receberam o sufixo `_TRANSFORMADO` para não substituir os originais.
- `TARGET` foi preservado apenas para análise posterior e não participou do agrupamento.

## Etapa 12 — Análise técnica dos clusters

- Scripts criados: `09_analisar_clusters.py` e `10_gerar_graficos.py`.
- Perfis calculados por método e cluster: quantidade, percentual, médias, medianas, desvios, carro, filhos, idade, renda, crédito, crédito/renda, créditos ativos, dívida, TARGET posterior e possíveis outliers IQR.
- Métricas calculadas na base transformada: Silhouette amostral de 3.000 registros com seed 42, Davies–Bouldin, Calinski–Harabasz, distância média ao centro e dispersão interna.
- DBSCAN excluiu somente os 296 ruídos das métricas geométricas e os descreveu separadamente.
- DBSCAN: Silhouette 0,085904; Davies–Bouldin 1,855622; Calinski–Harabasz 1031,784233.
- SimpleKMeans: Silhouette 0,263382; Davies–Bouldin 1,380971; Calinski–Harabasz 3106,870163.
- EM: Silhouette 0,109936; Davies–Bouldin 1,504642; Calinski–Harabasz 1862,177065.
- SimpleKMeans apresentou o melhor resultado relativo nas métricas internas avaliadas entre as três atribuições finais, sem conclusão comercial automática.
- Dez gráficos foram gerados e inspecionados visualmente em `relatorio/imagens/clusters/`.
- Nenhuma interpretação comercial final foi iniciada.

## Etapa 10 — EM

- Testes: K=8, K=9 e K=10; seed 42; máximo de 100 iterações.
- Dez inicializações K-Means internas; desvio padrão mínimo `1e-6`; uma thread.
- K=8: log-likelihood 2,54478; grupos entre 257 e 4.406; 2,786 s.
- K=9: log-likelihood 2,56187; grupos entre 257 e 4.359; 3,300 s.
- K=10: log-likelihood -0,29589; grupos entre 583 e 2.016; 3,394 s.
- K=9 escolhido pelo maior log-likelihood registrado entre K=8 e K=9 e pela comparabilidade com os outros métodos.
- O valor de K=10 é anômalo e foi transcrito do WEKA; o ARFF comprova a execução e os rótulos, mas o log textual bruto não foi preservado para confirmar convergência ou avisos.
- ARFFs gerados pelo `AddCluster`; CSVs exportados pelo `CSVSaver` do WEKA com 17 casas.

As futuras tentativas devem registrar data, atributos, tipos, pesos, seed,
Hopkins, justificativa e decisão, sem sobrescrever entradas anteriores.

## Etapa 13 — Interpretação comercial

- A interpretação foi baseada nos resumos reais de DBSCAN, SimpleKMeans e EM.
- A referência global da amostra foi registrada para evitar rótulos relativos sem
  comparação quantitativa.
- Jovens sem carro foram confirmados pelo K-Means (`cluster7`, 1.124 registros,
  29,83 anos e 12,72% de `TARGET=1`) e pelo EM (`cluster7`, 1.293 registros,
  29,15 anos e 12,99%).
- Famílias com filhos e sem carro apareceram no DBSCAN (`cluster6`), K-Means
  (`cluster1`) e EM (`cluster5`), com diferentes faixas de renda.
- Grupos de crédito alto e relação crédito/renda próxima ou superior a 8 foram
  tratados como oportunidade condicionada à capacidade de pagamento.
- O `cluster9` do K-Means, com 5,23 créditos ativos em média, foi associado a
  revisão de relacionamento e prevenção de sobre-endividamento.
- Os 296 ruídos do DBSCAN foram destinados à investigação individual, sem
  associação automática a fraude ou inadimplência.
- Microgrupos do DBSCAN com 48, 49 e 6 registros foram explicitamente marcados
  como frágeis para campanhas.
- `TARGET` permaneceu posterior e descritivo; não participou da clusterização.
- Resultado: `resultados/comparativos/interpretacao_comercial.md`.
- Nenhum arquivo de relatório da Etapa 14 foi criado durante a Etapa 13.

## Etapa 14 — Relatório ABNT

- O relatório foi criado em Markdown e DOCX sem gerar PDF definitivo.
- Foram consolidadas as 24 partes exigidas, incluindo métodos, configurações
  reais do WEKA, resultados, comparação, perfis, aplicações, limitações,
  referências e apêndices.
- O documento registra a origem no Trabalho 1, amostra de 10.000 registros,
  seed 42, exclusão de `SK_ID_CURR`, uso apenas posterior de `TARGET`, seis
  atributos, pesos, transformações e Hopkins `0,941745479089`.
- As configurações e os resultados reais de DBSCAN, SimpleKMeans e EM foram
  transcritos dos artefatos validados das Etapas 8 a 13.
- Foram incorporadas oito tabelas e doze figuras preexistentes, sem inventar
  resultados ou simular execuções.
- O DOCX foi formatado em A4, com margens 3/3/2/2 cm, Times New Roman 12,
  alinhamento justificado, espaçamento 1,5, cabeçalho e numeração de páginas.
- O sumário foi materializado com 24 entradas e páginas verificadas.
- A renderização de controle produziu 32 páginas físicas, sendo três
  pré-textuais e 29 numeradas; todas foram inspecionadas visualmente.
- Os artefatos temporários de renderização não integram a entrega.
- Arquivos: `relatorio/relatorio_clusterizacao.md`,
  `relatorio/relatorio_clusterizacao_abnt.docx` e
  `scripts/11_gerar_relatorio.py`.

## Etapa 15 — Revisão final e entrega

- Foi criada cópia de segurança dos arquivos que seriam alterados antes da
  revisão final.
- O gerador do DOCX passou a registrar título e descrição alternativa nas doze
  figuras; a auditoria de acessibilidade terminou com zero achados altos,
  médios ou baixos.
- A paginação foi corrigida para usar campos `PAGE` reais com reinício por
  seção, evitando perda visual do primeiro algarismo em páginas de dois dígitos.
- O apêndice foi corrigido para indicar scripts próprios `02` a `11`; a Etapa 0
  foi uma auditoria sem criação de script.
- O DOCX final foi regenerado e convertido em PDF definitivo.
- O PDF possui 32 páginas A4; a sequência do corpo foi validada de 1 a 29.
- Todas as 32 páginas foram renderizadas e inspecionadas visualmente.
- O pacote passou por 80 verificações automáticas sem erros: existência e
  preenchimento, 10.000 registros, colunas obrigatórias, ausência de
  identificadores na base do WEKA, sintaxe Python, JSON, cópias de `p1.py` e
  `p2.py`, referências do relatório e consistência dos principais resultados.
- O checklist final foi concluído e os artefatos temporários de QA foram
  removidos do repositório.
- Arquivos finais do relatório: `relatorio/relatorio_clusterizacao.md`,
  `relatorio/relatorio_clusterizacao_abnt.docx` e
  `relatorio/relatorio_clusterizacao_abnt.pdf`.
