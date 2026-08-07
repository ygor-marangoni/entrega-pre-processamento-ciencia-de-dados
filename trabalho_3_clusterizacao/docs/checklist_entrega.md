# Checklist da entrega

## Processo

- [x] Auditoria inicial concluída sem alteração destrutiva dos trabalhos anteriores.
- [x] Estrutura isolada do Trabalho 3 criada.
- [x] `p1.py` e `p2.py` preservados em `scripts/` e `scripts/originais/`.
- [x] Amostra reproduzível de 10.000 registros validada com seed 42.
- [x] Atributos, pesos, transformações e Hopkins documentados.
- [x] Exportações reais do WEKA validadas para DBSCAN, SimpleKMeans e EM.
- [x] Bases mescladas, métricas, gráficos e interpretação comercial concluídos.
- [x] Relatório ABNT revisado em Markdown, DOCX e PDF.

## Arquivos para entrega

- [x] Relatório PDF: `relatorio/relatorio_clusterizacao_abnt.pdf`.
- [x] Relatório DOCX: `relatorio/relatorio_clusterizacao_abnt.docx`.
- [x] Relatório-fonte: `relatorio/relatorio_clusterizacao.md`.
- [x] Base final usada no WEKA: `data/preparadas/base_clusterizacao_final.arff`.
- [x] Base final preparada em CSV: `data/preparadas/base_clusterizacao_final.csv`.
- [x] Base DBSCAN: `data/clusterizadas_weka/base_clusterizada_dbscan.arff`.
- [x] Base SimpleKMeans: `data/clusterizadas_weka/base_clusterizada_kmeans_final.csv`.
- [x] Base EM: `data/clusterizadas_weka/base_clusterizada_em_final.csv`.
- [x] `p1.py`, `p2.py` e scripts próprios `02` a `11`.
- [x] Configurações finais e testes dos três métodos.
- [x] Resultados reais da Estatística de Hopkins.
- [x] Tabelas, comparativos e gráficos utilizados no relatório.
- [x] Fontes e referências bibliográficas incluídas no relatório.
- [x] `README_TRABALHO_3.md` atualizado.

## Validações finais

- [x] PDF abre corretamente, possui 32 páginas A4 e numeração do corpo de 1 a 29.
- [x] DOCX abre como pacote válido, sem comentários ou alterações controladas.
- [x] Auditoria de acessibilidade do DOCX: 0 achados altos, médios ou baixos.
- [x] As 32 páginas do relatório foram renderizadas e inspecionadas visualmente.
- [x] Bases finais e bases de análise possuem exatamente 10.000 registros.
- [x] Exportações clusterizadas contêm a coluna `cluster`.
- [x] A base usada no WEKA não contém `TARGET`, `SK_ID_CURR` ou `ROW_ID_AMOSTRA`.
- [x] `TARGET` aparece somente na camada posterior de análise.
- [x] Scripts Python possuem sintaxe válida e arquivos JSON são legíveis.
- [x] Valores centrais do relatório coincidem com Hopkins e comparativos salvos.
- [x] Nenhum arquivo da entrega está vazio.
- [x] Nomes e referências de arquivos estão consistentes.
- [x] Nenhum resultado foi inventado ou simulado.
- [x] Nenhum arquivo temporário permanece dentro de `trabalho_3_clusterizacao/`.

Revisão final executada em 21/07/2026, fuso `America/Sao_Paulo`.
