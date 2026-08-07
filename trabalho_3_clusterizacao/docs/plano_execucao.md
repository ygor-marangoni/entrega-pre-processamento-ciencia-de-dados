# Plano de execução

## Regras permanentes

- Executar somente a etapa expressamente autorizada.
- Preservar `SK_ID_CURR`, `TARGET` e a ordem em bases auxiliares rastreáveis.
- Nunca usar `SK_ID_CURR` ou `TARGET` no cálculo de distância.
- Não sobrescrever tentativas ou resultados anteriores.
- Não inventar Hopkins nem resultados do WEKA.
- Interromper a execução diante de erro ou decisão metodológica não aprovada.

## Etapas

0. Auditar o repositório e a base.
1. Criar a estrutura isolada e preservar os scripts originais.
2. Criar amostra reproduzível de 10.000 registros.
3. Analisar e propor atributos e pesos.
4. Gerar a primeira base ponderada aprovada.
5. Calcular Hopkins para a primeira tentativa.
6. Registrar ajustes, uma tentativa por autorização.
7. Converter a configuração final para ARFF.
8. Executar e validar DBSCAN exportado pelo WEKA.
9. Executar e validar SimpleKMeans.
10. Executar e validar EM.
11. Validar e mesclar as três exportações reais.
12. Analisar clusters e métricas.
13. Produzir interpretação comercial sustentada pelos dados.
14. Gerar o relatório ABNT.
15. Revisar os arquivos de entrega.

## Ajustes decorrentes da auditoria

- A base original usa ponto e vírgula como separador.
- Campos categóricos codificados não devem ser tratados automaticamente como
  distâncias numéricas.
- A geração virtual de Hopkins deverá receber seed explícita.
- Outliers e atributos muito esparsos deverão ser avaliados antes dos pesos.

