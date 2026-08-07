# Análise de atributos candidatos — Etapa 2

## Base analisada

- Origem: `trabalho_3_clusterizacao/data/amostras/base_amostra_10000_analise.csv`.
- Registros: 10.000; separador: `;`.
- A leitura é exclusivamente exploratória: nenhuma linha ou valor foi alterado.
- `TARGET`, `SK_ID_CURR` e `ROW_ID_AMOSTRA` não foram analisados como candidatos e não integrarão o Apriori.

## Oito atributos recomendados — sujeitos a aprovação

### AMT_CREDIT

- Motivo: Incluído por representar diretamente o porte do crédito solicitado.
- Distribuição observada: 1815 valores/categorias; zeros = 0.00%; concentração dominante = 3.52%.
- Vantagem: acrescenta uma dimensão interpretável ao perfil do cliente.
- Risco: assimetria = 1.270873; outliers pelo IQR = 2.170000% quando aplicável.
- Discretização provável: Faixas robustas por percentis/quartis, avaliando a cauda superior.

### AMT_INCOME_TOTAL

- Motivo: Incluído por ser indicador central da capacidade econômica do cliente.
- Distribuição observada: 294 valores/categorias; zeros = 0.00%; concentração dominante = 11.48%.
- Vantagem: acrescenta uma dimensão interpretável ao perfil do cliente.
- Risco: assimetria = 99.018857; outliers pelo IQR = 4.690000% quando aplicável.
- Discretização provável: Faixas por percentis, com atenção explícita aos extremos de renda.

### AGE_YEARS

- Motivo: Incluído para representar estágio de vida com interpretação direta.
- Distribuição observada: 3959 valores/categorias; zeros = 0.00%; concentração dominante = 0.11%.
- Vantagem: acrescenta uma dimensão interpretável ao perfil do cliente.
- Risco: assimetria = 0.124488; outliers pelo IQR = 0.000000% quando aplicável.
- Discretização provável: Comparar grupos etários semânticos com quartis observados.

### CNT_CHILDREN

- Motivo: Incluído por sintetizar composição familiar em poucas categorias naturais.
- Distribuição observada: 6 valores/categorias; zeros = 69.61%; concentração dominante = 69.61%.
- Vantagem: acrescenta uma dimensão interpretável ao perfil do cliente.
- Risco: assimetria = 1.719320; outliers pelo IQR = 1.600000% quando aplicável.
- Discretização provável: Agrupar em sem filhos, um filho e dois ou mais, se as frequências confirmarem.

### FLAG_OWN_CAR_COD

- Motivo: Incluído como dimensão patrimonial simples e comercialmente interpretável.
- Distribuição observada: 2 valores/categorias; zeros = 66.05%; concentração dominante = 66.05%.
- Vantagem: acrescenta uma dimensão interpretável ao perfil do cliente.
- Risco: assimetria = ; outliers pelo IQR = % quando aplicável.
- Discretização provável: Recuperar como SEM_CARRO e COM_CARRO; não manter códigos numéricos.

### NAME_FAMILY_STATUS_COD

- Motivo: Incluído para complementar a composição familiar com rótulos recuperados.
- Distribuição observada: 6 valores/categorias; zeros = 0.01%; concentração dominante = 63.44%.
- Vantagem: acrescenta uma dimensão interpretável ao perfil do cliente.
- Risco: assimetria = ; outliers pelo IQR = % quando aplicável.
- Discretização provável: Usar categorias nominais do dicionário; fundir somente categorias raras justificadas.

### SER_CREDITOS_ATIVOS

- Motivo: Incluído por medir intensidade do relacionamento de crédito ativo.
- Distribuição observada: 17 valores/categorias; zeros = 29.56%; concentração dominante = 29.56%.
- Vantagem: acrescenta uma dimensão interpretável ao perfil do cliente.
- Risco: assimetria = 1.472207; outliers pelo IQR = 1.080000% quando aplicável.
- Discretização provável: Criar faixas a partir de zero semântico e agrupamentos frequentes positivos.

### PREV_TAXA_REJEICAO

- Motivo: Incluído por trazer histórico de rejeição em dimensão distinta de renda e crédito.
- Distribuição observada: 133 valores/categorias; zeros = 67.71%; concentração dominante = 67.71%.
- Vantagem: acrescenta uma dimensão interpretável ao perfil do cliente.
- Risco: assimetria = 1.809534; outliers pelo IQR = 8.280000% quando aplicável.
- Discretização provável: Separar zero semântico de faixas positivas definidas por percentis e frequência.

## Cinco atributos descartados — sujeitos a revisão

### CREDIT_INCOME_RATIO

- Motivo: Descartado por ser derivado matematicamente de crédito e renda, já incluídos.
- Distribuição observada: 4962 valores/categorias; zeros = 0.00%; concentração dominante = 1.61%.
- Risco/decisão: Sua inclusão tenderia a produzir associações estruturalmente óbvias.

### REGION_RATING_CLIENT

- Motivo: Descartado por ter baixa granularidade e risco de concentração dominante.
- Distribuição observada: 3 valores/categorias; zeros = 0.00%; concentração dominante = 74.16%.
- Risco/decisão: Pode limitar a diversidade das regras frente a atributos de perfil e histórico.

### SER_QTDE_EMPRESTIMOS

- Motivo: Descartado para reduzir sobreposição com SER_CREDITOS_ATIVOS no histórico Serasa.
- Distribuição observada: 36 valores/categorias; zeros = 13.86%; concentração dominante = 13.86%.
- Risco/decisão: Permanece como alternativa caso a etapa de discretização revele baixa utilidade do atributo incluído.

### PREV_QTDE_TENTATIVAS

- Motivo: Descartado para evitar sobreposição com PREV_TAXA_REJEICAO, que resume o resultado das tentativas.
- Distribuição observada: 37 valores/categorias; zeros = 5.55%; concentração dominante = 17.48%.
- Risco/decisão: A taxa preserva melhor a comparabilidade entre diferentes volumes de tentativas.

### SER_DIVIDA_ATRASADA

- Motivo: Descartado devido à concentração esperada em zero, a ser confirmada pelas estatísticas.
- Distribuição observada: 88 valores/categorias; zeros = 98.80%; concentração dominante = 98.80%.
- Risco/decisão: A categoria dominante poderia produzir regras frequentes, porém pouco informativas.

## Observações metodológicas

- `CREDIT_INCOME_RATIO` não é recomendado porque já é função de `AMT_CREDIT` e `AMT_INCOME_TOTAL`; incluí-lo pode produzir regras tautológicas.
- Zeros ainda são valores originais nesta etapa. Se um zero tiver significado real, a etapa de discretização deverá convertê-lo em rótulo nominal, pois o Apriori será configurado posteriormente com `treatZeroAsMissing=true`.
- As categorias de carro e estado familiar foram interpretadas com o dicionário do Trabalho 1; códigos não serão tratados como grandezas numéricas.
- Esta recomendação não gera a base final: a escolha dos oito atributos depende de aprovação expressa.
