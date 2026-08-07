# Trabalho 4 — Regras de Associação Apriori

Este diretório será desenvolvido de forma sequencial, somente após autorização
expressa para cada etapa. O objetivo é identificar regras de associação entre
características de clientes pelo algoritmo Apriori do WEKA.

## Estado atual

- Etapa 0: auditoria concluída.
- Etapa 1: estrutura documental mínima criada.
- Etapa 2: análise exploratória dos 13 atributos concluída; a seleção dos oito
  atributos permanece pendente de aprovação.
- Etapa 3: proposta de discretização concluída, validada e autorizada para
  aplicação na Etapa 4.
- Etapa 4: base discretizada CSV e ARFF gerada e validada, com oito atributos
  nominais e 10.000 registros.
- Etapa 5: validação formal aprovada e frequências dos 27 itens calculadas.
- Etapa 6: opções do Apriori auditadas na instalação real do WEKA 3.8.7; não
  houve mineração de dados.
- Etapa 6B: representação binária transacional criada e validada para tornar o
  uso obrigatório de `-Z` compatível com os itens discretizados.
- Etapa 7: concluída com ressalvas. Após autorização, a ordenação por Lift e a
  pontuação mínima 0,00 identificaram suporte efetivo de 0,01 com 36 regras de
  três itens em exploração; a execução obrigatória com `-N 30` foi preservada
  separadamente. Aguarda-se aprovação do suporte para a Etapa 8.
- Etapa 8: execução final real concluída no WEKA 3.8.7, com `-N 30`, suporte
  efetivo 0,01, Lift, `-C 0,00`, `-I` e `-Z`; a saída, os itemsets e a
  configuração estão preservados integralmente.
- Etapa 9: regras e itemsets extraídos para CSV por parser próprio, com as
  métricas efetivamente informadas pelo WEKA e validação de contagens.
- Etapa 10: conjunto fechado formal gerado e auditado; 5.072 dos 5.119 itemsets
  permaneceram fechados, e as regras foram relacionadas aos itemsets fechados.
- Etapa 11: Top 20 de regras fechadas com exatamente três itens selecionado por
  Lift, com suporte e confiança como desempate.
- Etapa 12: Top 20 classificado com justificativas em regras óbvias,
  interessantes e uma novidade preliminar, sem atribuição causal.
- Etapa 13: quatro gráficos acadêmicos gerados e inspecionados a partir do Top
  20, das métricas reais e da classificação justificada.
- Etapa 14: relatório detalhado criado em Markdown e DOCX, com capa, folha de
  rosto, sumário provisório, resultados auditáveis, tabelas e figuras. A revisão
  ABNT e o PDF permanecem reservados às etapas seguintes.
- Etapa 15: revisão estrutural ABNT aplicada ao DOCX, incluindo A4, margens,
  Times New Roman, espaçamento, recuos, cabeçalhos de tabelas, títulos de
  figuras, numeração e campo de sumário automático.
- As bases semânticas foram preservadas. A única execução no WEKA até aqui foi
  a busca experimental de suporte da Etapa 7 sobre a representação binária.

## Fonte candidata confirmada na auditoria

`../trabalho_3_clusterizacao/data/amostras/base_amostra_10000_analise.csv`

A origem contém 10.000 registros e valores originais não ponderados, porém
preserva `ROW_ID_AMOSTRA`, `SK_ID_CURR` e `TARGET` apenas para rastreabilidade.
Essas colunas não poderão compor a futura base de Apriori.

Consulte `docs/plano_execucao.md` antes de qualquer execução.
