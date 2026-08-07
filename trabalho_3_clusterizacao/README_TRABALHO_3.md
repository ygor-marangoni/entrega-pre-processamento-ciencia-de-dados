# Trabalho 3 — Clusterização

Este diretório concentra a implementação sequencial do Trabalho Prático 3 de
Ciência de Dados. A fonte oficial é a base produzida no Trabalho 1:

```text
../trabalho_1_preprocessamento/data/base_final_preprocessada.csv
```

## Regra de execução

O desenvolvimento ocorre exclusivamente por etapas autorizadas. Cada etapa deve
ser implementada, validada, documentada e encerrada antes da seguinte. Não é
permitido antecipar amostras, Hopkins, execuções do WEKA, análises ou relatório.

## Estado atual

- Etapa 0: auditoria concluída com ressalvas.
- Etapa 1: estrutura inicial criada.
- Etapa 2: amostra reproduzível de 10.000 registros criada e validada.
- Etapa 3: análise exploratória concluída; proposta posteriormente aprovada.
- Etapa 4: atributos e pesos aprovados; base ponderada da tentativa 01 criada e validada.
- Etapa 5: Hopkins da tentativa 01 calculado em 0,941745479089; limiar 0,7 atingido.
- Etapa 6: ajustes dispensados; tentativa 01 copiada como configuração final.
- Etapa 7: base final convertida para ARFF e instruções do WEKA documentadas.
- Etapa 8: três execuções reais de DBSCAN realizadas no WEKA; teste 02 escolhido como referência.
- Etapa 9: SimpleKMeans executado para K=8, K=9 e K=10; K=9 escolhido.
- Etapa 10: EM executado para K=8, K=9 e K=10; K=9 escolhido.
- Etapa 11: três exportações finais validadas e mescladas com a base auxiliar.
- Etapa 12: perfis, métricas técnicas e gráficos dos clusters calculados.
- Etapa 13: perfis interpretados comercialmente com valores reais e ressalvas de uso.
- A Estatística de Hopkins foi executada somente para a tentativa 01 aprovada.
- Nenhum resultado de clusterização foi simulado.

Os arquivos `p1.py` e `p2.py` pertencem a este trabalho e estão em `scripts/`.
As versões originais do professor também estão preservadas, sem alterações, em
`scripts/originais/`.

## Amostra da Etapa 2

Os arquivos estão em `data/amostras/`. A base `completa` exclui `SK_ID_CURR` e
`TARGET`; a base `analise` preserva essas colunas somente para rastreabilidade e
análises posteriores. Ambas usam `ROW_ID_AMOSTRA`, separador `;` e seed 42.

## Configuração aprovada

Os seis atributos principais propostos são `AMT_CREDIT`, `CNT_CHILDREN`,
`FLAG_OWN_CAR_COD`, `AGE_YEARS`, `CREDIT_INCOME_RATIO` e
`SER_CREDITOS_ATIVOS`. A configuração foi aplicada somente após aprovação
expressa dos campos, tipos e pesos.

## Tentativa 01 preparada

A base `data/preparadas/base_clusterizacao_tentativa_01.csv` contém 10.000
registros e somente os seis atributos aprovados. Os campos numéricos foram
normalizados por Min-Max e multiplicados por `sqrt(peso)`. A posse de carro foi
recuperada como nominal `N/Y`.

## Hopkins da tentativa 01

O resultado real e reproduzível foi `H = 0,941745479089`. A tentativa 01
apresentou forte tendência de clusterização e não exige ajuste automático de
campos ou pesos. Os arquivos estão em `resultados/hopkins/`.

## Configuração final

Como a primeira tentativa atingiu o limiar, nenhuma tentativa adicional foi
executada. A base e a configuração originais foram preservadas e copiadas para
`data/preparadas/base_clusterizacao_final.csv` e
`resultados/configuracoes/configuracao_final.csv`.

## Preparação do WEKA

A Etapa 7 gerou `data/preparadas/base_clusterizacao_final.arff`, com 10.000
registros, cinco atributos numéricos e um nominal. O arquivo não contém
`SK_ID_CURR`, `TARGET` ou `ROW_ID_AMOSTRA`. As instruções de uso do filtro
`AddCluster` estão em `docs/instrucoes_weka.md`. Nenhuma clusterização foi
executada nesta etapa.

## DBSCAN no WEKA

A Etapa 8 utilizou o WEKA 3.8.7, o filtro `AddCluster` e o pacote oficial
`optics_dbScan` 1.0.6. Foram executados três testes com `minPoints = 6` e
`epsilon` 0,25, 0,274264329676 e 0,30. A normalização interna da distância foi
desativada para preservar os pesos aplicados na Etapa 4. O teste intermediário,
definido pelo joelho da curva do sexto vizinho, foi escolhido como referência.

## SimpleKMeans e EM

Com autorização expressa, as Etapas 9 e 10 foram executadas sequencialmente na
mesma rodada. Ambos os métodos foram testados com 8, 9 e 10 clusters. K=9 foi
escolhido no SimpleKMeans como compromisso entre Silhouette, equilíbrio e
comparabilidade, sem cotovelo claro de SSE no intervalo. No EM, K=9 apresentou
o maior log-likelihood registrado entre K=8 e K=9; o valor anômalo de K=10 não
pôde ser revalidado porque o log textual bruto do WEKA não foi preservado.
Todos os ARFFs foram preservados e exportados também para CSV pelo próprio WEKA.

## Validação, junção e análise técnica

As três exportações finais possuem 10.000 registros e sete colunas no total:
seis atributos de entrada e a coluna `cluster`. A junção preservou
`ROW_ID_AMOSTRA`, `SK_ID_CURR`, `TARGET`, valores
originais e valores transformados com sufixo `_TRANSFORMADO`.

Na comparação técnica, SimpleKMeans apresentou Silhouette 0,263382,
Davies–Bouldin 1,380971 e Calinski–Harabasz 3106,870163. DBSCAN apresentou 296
ruídos e microgrupos; EM apresentou um grupo dominante de 4.359 registros.

## Interpretação comercial

A Etapa 13 identificou como padrões recorrentes jovens sem carro, famílias com
filhos sem carro, clientes maduros com menor proporção posterior de `TARGET`,
clientes de crédito alto e forte comprometimento de renda, clientes com muitos
créditos ativos e casos fora do padrão isolados pelo DBSCAN. As oportunidades
e cautelas estão documentadas em
`resultados/comparativos/interpretacao_comercial.md`. Nenhuma interpretação
foi tratada como decisão automática de crédito.

## Relatório ABNT

A Etapa 14 consolidou exclusivamente resultados reais das etapas anteriores em
`relatorio/relatorio_clusterizacao.md` e
`relatorio/relatorio_clusterizacao_abnt.docx`. O documento possui capa, folha de
rosto, sumário, 24 seções obrigatórias, oito tabelas e doze figuras. A versão
DOCX usa papel A4, margens ABNT de 3 cm (superior/esquerda) e 2 cm
(inferior/direita), Times New Roman 12, texto justificado e espaçamento 1,5.

A renderização de controle resultou em 32 páginas físicas: três pré-textuais e
29 numeradas. Todas foram inspecionadas visualmente; o PDF de controle e as
imagens de página eram temporários e não fazem parte da Etapa 14. A versão PDF
para entrega permanece reservada à revisão final da Etapa 15.

## Revisão final e entrega

A Etapa 15 gerou o PDF definitivo em
`relatorio/relatorio_clusterizacao_abnt.pdf` a partir do mesmo DOCX validado.
O relatório final possui 32 páginas A4, sendo três pré-textuais e 29 páginas
numeradas. Todas as páginas foram renderizadas e inspecionadas visualmente.

A revisão confirmou 10.000 registros nas bases finais e de análise, presença de
`cluster` nas três exportações, ausência de `TARGET`, `SK_ID_CURR` e
`ROW_ID_AMOSTRA` na base destinada ao WEKA, integridade dos scripts e arquivos
JSON e correspondência dos principais valores do relatório com os resultados
salvos. A auditoria de acessibilidade do DOCX terminou sem achados.

O inventário completo para envio está em `docs/checklist_entrega.md`.
