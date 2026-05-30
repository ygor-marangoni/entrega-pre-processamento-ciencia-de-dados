# Apêndice - Consultas feitas à LLM

Este apêndice registra as consultas feitas a uma LLM durante o desenvolvimento do trabalho de Ciência de Dados sobre pré-processamento de bases de crédito. As respostas foram usadas como apoio para organização, implementação e revisão, mas os resultados finais foram conferidos diretamente nos arquivos gerados, no código-fonte e nos resumos estatísticos.

## Consulta 1 - Entendimento do enunciado e definição do objetivo

**Prompt enviado:**

> Tenho um trabalho de Ciência de Dados sobre pré-processamento. As bases são `emprestimos.csv`, `serasa.csv` e `emprestimos_anteriores.csv`. Preciso gerar uma base final para Machine Learning, agregando dados externos e internos por `SK_ID_CURR`, tratar dados ausentes, codificar variáveis categóricas, cuidar do desbalanceamento e criar uma métrica usando 10 campos finais. Gere o processo, o código-fonte e os arquivos finais.

**Resposta recebida:**

O trabalho deve ser entendido como uma etapa de preparação de dados, e não como uma etapa de treinamento de modelo. O objetivo principal é transformar três bases separadas em uma única base final, organizada por cliente, adequada para uma futura etapa de Machine Learning.

A base `emprestimos.csv` deve ser usada como base principal ou base âncora. Ela contém a chave `SK_ID_CURR`, a variável alvo `TARGET` e os principais dados demográficos e financeiros do cliente. A variável `TARGET` deve ser preservada sem alteração, pois representa o atributo de classificação:

- `0`: cliente saudável ou sem dificuldade de pagamento;
- `1`: cliente com risco ou dificuldade de pagamento.

As bases `serasa.csv` e `emprestimos_anteriores.csv` não devem ser unidas diretamente à base principal, porque elas podem conter várias linhas para o mesmo cliente. Antes da junção, essas bases precisam ser agregadas por `SK_ID_CURR`. Assim, cada cliente fica com apenas uma linha de resumo em cada base auxiliar.

Para a base Serasa, recomenda-se criar campos agregados como:

- quantidade de empréstimos anteriores no bureau;
- soma da dívida atrasada;
- quantidade de créditos ativos;
- média ou máximo de dias relacionados a crédito;
- soma da dívida total;
- soma do crédito total;
- quantidade de prorrogações.

Para a base de empréstimos anteriores, recomenda-se criar campos como:

- quantidade de tentativas anteriores;
- quantidade de solicitações recusadas;
- taxa de rejeição;
- soma do valor solicitado;
- soma do valor aprovado;
- razão entre valor aprovado e valor solicitado;
- quantidade de solicitações com seguro;
- quantidade de vezes em que o cliente era repetidor.

Depois das agregações, deve ser feita uma junção à esquerda entre a base principal e as bases agregadas. A junção à esquerda é adequada porque preserva todos os registros da base principal, mesmo quando um cliente não possui histórico externo ou interno.

Para o tratamento de dados, a recomendação é:

- preencher campos agregados ausentes com zero, pois a ausência de histórico pode ser interpretada como ausência de registros anteriores;
- preencher variáveis numéricas da base principal com a mediana, reduzindo o efeito de valores extremos;
- preencher variáveis categóricas ausentes com `Unknown`;
- transformar variáveis categóricas em códigos numéricos;
- salvar um dicionário de codificação para permitir rastreabilidade.

Também é recomendável transformar `DAYS_BIRTH` em idade em anos, criando uma variável mais interpretável, como `AGE_YEARS`. Outra variável útil é a razão entre crédito e renda, como `CREDIT_INCOME_RATIO`, calculada por `AMT_CREDIT / AMT_INCOME_TOTAL`.

A base final deve conter apenas:

- `SK_ID_CURR`;
- `TARGET`;
- variáveis selecionadas da base principal;
- variáveis agregadas da base Serasa;
- variáveis agregadas da base de empréstimos anteriores;
- variáveis novas criadas durante o pré-processamento.

Campos brutos usados apenas para agregação, como `SK_ID_BUREAU`, `SK_ID_PREV`, `CREDIT_ACTIVE` e `NAME_CONTRACT_STATUS`, não precisam permanecer na base final.

Para o desbalanceamento, a base deve registrar a proporção das classes de `TARGET`. Como o objetivo do trabalho é pré-processamento, não é necessário alterar a distribuição original da base. Para uma etapa futura de modelagem, deve-se usar divisão estratificada, métricas adequadas para classes desbalanceadas e técnicas como `class_weight`, oversampling ou undersampling apenas no conjunto de treino.

Por fim, a métrica de risco pode ser criada em uma cópia da base final. Ela deve usar 10 campos finais, aplicar normalização e combinar os campos com pesos. Campos em que valores maiores indicam menor risco, como renda e scores externos, devem ter a escala invertida.

## Consulta 2 - Escolha dos campos e agregações

**Prompt enviado:**

> Quais campos devo selecionar das três bases para cumprir o enunciado? Quero usar os obrigatórios e alguns campos extras suficientes para deixar a base final robusta, mas sem carregar colunas desnecessárias.

**Resposta recebida:**

Na base `emprestimos.csv`, os campos obrigatórios são:

- `SK_ID_CURR`;
- `TARGET`;
- `AMT_INCOME_TOTAL`;
- `AMT_CREDIT`;
- `NAME_EDUCATION_TYPE`;
- `DAYS_BIRTH`.

Além desses, é recomendável escolher mais de três campos adicionais para enriquecer a base. Uma seleção robusta inclui:

- `CODE_GENDER`;
- `FLAG_OWN_CAR`;
- `FLAG_OWN_REALTY`;
- `CNT_CHILDREN`;
- `NAME_INCOME_TYPE`;
- `NAME_FAMILY_STATUS`;
- `NAME_HOUSING_TYPE`;
- `FLAG_MOBIL`;
- `FLAG_EMP_PHONE`;
- `FLAG_EMAIL`;
- `OCCUPATION_TYPE`;
- `REGION_RATING_CLIENT`;
- `ORGANIZATION_TYPE`;
- `EXT_SOURCE_1`;
- `EXT_SOURCE_2`;
- `EXT_SOURCE_3`.

Essa seleção atende ao enunciado e adiciona variáveis demográficas, financeiras e de score externo. O campo `DAYS_BIRTH` deve ser convertido para idade em anos, pois a idade em dias negativos é menos intuitiva para análise.

Na base `serasa.csv`, os campos mínimos para leitura devem ser:

- `SK_ID_CURR`;
- `SK_ID_BUREAU`;
- `CREDIT_ACTIVE`;
- `AMT_CREDIT_SUM_OVERDUE`.

Esses campos permitem criar os três agregados obrigatórios:

- `SER_QTDE_EMPRESTIMOS`: contagem de `SK_ID_BUREAU`;
- `SER_DIVIDA_ATRASADA`: soma de `AMT_CREDIT_SUM_OVERDUE`;
- `SER_CREDITOS_ATIVOS`: contagem de linhas em que `CREDIT_ACTIVE` é `Active`.

Para atender ao pedido de pelo menos mais três campos agregados, podem ser usados:

- `DAYS_CREDIT`;
- `CREDIT_DAY_OVERDUE`;
- `AMT_CREDIT_MAX_OVERDUE`;
- `CNT_CREDIT_PROLONG`;
- `AMT_CREDIT_SUM`;
- `AMT_CREDIT_SUM_DEBT`.

Com esses campos, podem ser criados:

- `SER_DAYS_CREDIT_MEDIO`;
- `SER_DIAS_ATRASO_MAX`;
- `SER_CREDITO_TOTAL`;
- `SER_DIVIDA_TOTAL`;
- `SER_MAX_OVERDUE`;
- `SER_QTDE_PRORROGACOES`.

Na base `emprestimos_anteriores.csv`, os campos obrigatórios para agregação são:

- `SK_ID_CURR`;
- `SK_ID_PREV`;
- `NAME_CONTRACT_STATUS`;
- `AMT_APPLICATION`;
- `AMT_CREDIT`.

Com eles, podem ser criados:

- `PREV_QTDE_TENTATIVAS`;
- `PREV_QTDE_REJEITADAS`;
- `PREV_TAXA_REJEICAO`;
- `PREV_VALOR_SOLICITADO_TOTAL`;
- `PREV_VALOR_APROVADO_TOTAL`;
- `PREV_RAZAO_APROVADO_SOLICITADO`.

Para atender ao pedido de pelo menos mais dois campos, podem ser usados:

- `NAME_CLIENT_TYPE`;
- `NFLAG_INSURED_ON_APPROVAL`.

Com esses campos, podem ser criados:

- `PREV_QTDE_CLIENTE_REPETIDOR`;
- `PREV_QTDE_COM_SEGURO`.

Também é possível usar o próprio `NAME_CONTRACT_STATUS` para criar `PREV_QTDE_CANCELADO`, que ajuda a diferenciar cancelamentos de rejeições.

## Consulta 3 - Estratégia de tratamento de ausentes e categóricas

**Prompt enviado:**

> Como devo tratar os valores ausentes e as variáveis categóricas para deixar a base final robusta? O trabalho é simples, mas precisa ser reprodutível.

**Resposta recebida:**

Para este tipo de trabalho, a solução mais adequada é usar regras simples, explicáveis e fáceis de reproduzir. O objetivo é mostrar domínio do pré-processamento, sem criar um pipeline excessivamente complexo.

Para campos agregados das bases auxiliares, valores ausentes aparecem quando um cliente da base principal não tem registro correspondente na base Serasa ou na base de empréstimos anteriores. Nesse caso, preencher com zero é uma escolha coerente, porque significa que não há histórico registrado naquele conjunto de dados.

Exemplos:

- se `SER_QTDE_EMPRESTIMOS` está ausente, preencher com `0`;
- se `SER_DIVIDA_ATRASADA` está ausente, preencher com `0`;
- se `PREV_QTDE_TENTATIVAS` está ausente, preencher com `0`;
- se `PREV_TAXA_REJEICAO` está ausente, preencher com `0`.

Para variáveis numéricas da base principal, a mediana é uma boa escolha. A mediana é mais resistente a outliers do que a média, o que é importante em variáveis financeiras como renda e valor de crédito.

Exemplos de variáveis numéricas:

- `AMT_INCOME_TOTAL`;
- `AMT_CREDIT`;
- `AGE_YEARS`;
- `EXT_SOURCE_1`;
- `EXT_SOURCE_2`;
- `EXT_SOURCE_3`;
- `CREDIT_INCOME_RATIO`.

Para variáveis categóricas, uma abordagem simples é:

1. substituir ausentes por `Unknown`;
2. transformar cada categoria em um código numérico;
3. salvar um dicionário com o mapeamento entre categoria e código.

O dicionário é importante porque evita perda de rastreabilidade. Sem ele, não seria possível saber posteriormente o que significa cada número.

A base final deve ficar sem células vazias. Isso facilita o uso em modelos de Machine Learning, que geralmente não aceitam valores ausentes diretamente.

## Consulta 4 - Métrica de risco com 10 campos finais

**Prompt enviado:**

> Preciso criar uma métrica usando 10 campos finais. Como posso montar uma métrica simples de risco de 0 a 100 usando pesos e normalização?

**Resposta recebida:**

Uma métrica de risco simples pode ser criada combinando variáveis financeiras, scores externos e histórico de crédito. O ideal é usar apenas campos que já estejam na base final, pois o enunciado pede uma métrica usando 10 campos finais.

Uma proposta de 10 campos é:

1. `AMT_INCOME_TOTAL`;
2. `AMT_CREDIT`;
3. `CREDIT_INCOME_RATIO`;
4. `EXT_SOURCE_1`;
5. `EXT_SOURCE_2`;
6. `EXT_SOURCE_3`;
7. `SER_QTDE_EMPRESTIMOS`;
8. `SER_DIVIDA_ATRASADA`;
9. `SER_CREDITOS_ATIVOS`;
10. `PREV_TAXA_REJEICAO`.

Antes de combinar os campos, é recomendável normalizar cada variável para uma escala comum, de 0 a 1. Como variáveis financeiras podem ter outliers, uma normalização robusta usando os percentis 1% e 99% é mais estável do que usar mínimo e máximo absolutos.

A normalização pode seguir a fórmula:

```text
valor_normalizado = (valor - percentil_1) / (percentil_99 - percentil_1)
```

Valores abaixo do percentil 1% são truncados para 0, e valores acima do percentil 99% são truncados para 1.

Alguns campos devem ter a escala invertida, porque valores maiores representam menor risco:

- `AMT_INCOME_TOTAL`: renda maior tende a reduzir risco;
- `EXT_SOURCE_1`: score maior tende a reduzir risco;
- `EXT_SOURCE_2`: score maior tende a reduzir risco;
- `EXT_SOURCE_3`: score maior tende a reduzir risco.

Depois da normalização, os campos podem ser combinados por pesos. Uma distribuição possível é:

- `AMT_INCOME_TOTAL`: 0,08;
- `AMT_CREDIT`: 0,08;
- `CREDIT_INCOME_RATIO`: 0,15;
- `EXT_SOURCE_1`: 0,10;
- `EXT_SOURCE_2`: 0,15;
- `EXT_SOURCE_3`: 0,15;
- `SER_QTDE_EMPRESTIMOS`: 0,02;
- `SER_DIVIDA_ATRASADA`: 0,12;
- `SER_CREDITOS_ATIVOS`: 0,03;
- `PREV_TAXA_REJEICAO`: 0,12.

A soma dos pesos deve ser 1. O resultado final pode ser multiplicado por 100, criando uma métrica de 0 a 100:

```text
METRICA_RISCO_0_100 = soma_dos_campos_normalizados_ponderados * 100
```

Também é útil criar uma classificação da métrica:

- `Baixo`: de 0 a 33;
- `Medio`: acima de 33 até 66;
- `Alto`: acima de 66 até 100.

Essa métrica não substitui um modelo estatístico ou de Machine Learning. Ela serve como exercício de construção de indicador, explicável e reprodutível.

## Consulta 5 - Banco de dados e comandos SQL

**Prompt enviado:**

> O enunciado pede informações sobre o gerenciador de banco de dados e todos os comandos usados. Como posso registrar isso usando SQLite?

**Resposta recebida:**

Uma solução adequada é usar SQLite 3, porque ele não exige servidor, gera um único arquivo `.db` e é simples de reproduzir. A base final com métrica pode ser salva em um banco chamado `preprocessamento_credito.db`, em uma tabela chamada `base_final_metrica`.

No código Python, a biblioteca `sqlite3` pode criar o banco e gravar a tabela usando `pandas.to_sql`. Depois, pode ser criado um índice sobre `SK_ID_CURR`, pois essa é a chave principal de referência dos clientes.

Os comandos SQL que devem ser registrados no apêndice ou em arquivo separado são:

```sql
-- Gerenciador de banco de dados utilizado: SQLite 3
-- Objetivo: armazenar e consultar a base final preprocessada com métrica.

.mode csv
.separator ;
.headers on

DROP TABLE IF EXISTS base_final_metrica;
.import --skip 1 base_final_com_metrica.csv base_final_metrica

CREATE INDEX IF NOT EXISTS idx_base_final_sk
ON base_final_metrica (SK_ID_CURR);

SELECT COUNT(*) AS total_registros FROM base_final_metrica;
SELECT TARGET, COUNT(*) AS quantidade FROM base_final_metrica GROUP BY TARGET;
SELECT CLASSE_METRICA, COUNT(*) AS quantidade FROM base_final_metrica GROUP BY CLASSE_METRICA;

SELECT *
FROM base_final_metrica
LIMIT 10;

SELECT TARGET,
       ROUND(AVG(METRICA_RISCO_0_100), 2) AS media_metrica_risco
FROM base_final_metrica
GROUP BY TARGET;
```

Esses comandos permitem importar, indexar e conferir a base. Mesmo que o banco seja criado diretamente pelo Python, manter o arquivo `sqlite_comandos.sql` ajuda na documentação e na reprodutibilidade.

## Consulta 6 - Estrutura do relatório de pré-processamento

**Prompt enviado:**

> Gere uma estrutura de relatório para documentar o pré-processamento, incluindo descrição das bases, campos selecionados, agregações, tratamento de ausentes, codificação, desbalanceamento, métrica e apêndices.

**Resposta recebida:**

O relatório pode ser estruturado da seguinte forma:

1. **Introdução**
   - Apresentar o objetivo do trabalho.
   - Explicar que a tarefa é construir uma base final a partir de três fontes.
   - Deixar claro que o foco é pré-processamento, não treinamento de modelo.

2. **Bases utilizadas**
   - Descrever `emprestimos.csv`, `serasa.csv` e `emprestimos_anteriores.csv`.
   - Informar o papel de cada uma.
   - Registrar a quantidade de registros de cada base.

3. **Seleção dos campos**
   - Listar os campos obrigatórios da base principal.
   - Explicar os campos extras selecionados.
   - Justificar o uso dos scores externos.

4. **Agregações**
   - Separar em duas subseções:
     - agregações da base Serasa;
     - agregações da base de empréstimos anteriores.
   - Mostrar os nomes dos campos criados e suas descrições.

5. **Tratamento e pré-processamento**
   - Explicar a junção por `SK_ID_CURR`.
   - Explicar o preenchimento de ausentes.
   - Explicar a transformação de `DAYS_BIRTH` em idade.
   - Explicar a criação de `CREDIT_INCOME_RATIO`.
   - Explicar a codificação categórica e o dicionário gerado.

6. **Desbalanceamento da variável alvo**
   - Mostrar a quantidade e o percentual de cada classe de `TARGET`.
   - Explicar que a base é desbalanceada.
   - Registrar que o balanceamento deve ser tratado com cuidado em uma etapa futura de modelagem.

7. **Métrica de risco**
   - Explicar os 10 campos usados.
   - Mostrar os pesos.
   - Explicar a normalização robusta.
   - Apresentar estatísticas da métrica e faixas de risco.

8. **Arquivos finais gerados**
   - Listar os CSVs finais.
   - Listar o banco SQLite.
   - Listar o código-fonte.
   - Listar os arquivos de resumo e apêndices.

9. **Conclusão**
   - Reforçar que a base final ficou preparada para Machine Learning.
   - Destacar a reprodutibilidade do processo.

10. **Referências**
    - Documentação do Python.
    - Documentação do pandas.
    - Documentação do SQLite.
    - Bases fornecidas na atividade.

11. **Apêndices**
    - Gerenciador de banco de dados e comandos SQL.
    - Código-fonte criado.
    - Consultas feitas à LLM.

Essa estrutura atende ao enunciado porque documenta o processo e permite que outra pessoa repita o trabalho posteriormente.

## Consulta 7 - Geração de um relatório HTML para apoio ao vídeo

**Prompt enviado:**

> Preciso de um relatório em HTML de todo o trabalho para a gente se basear na hora de fazer os vídeos. Quero que ele tenha roteiro, explicação das bases, pré-processamento, métrica, arquivos finais e falas sugeridas.

**Resposta recebida:**

Um relatório HTML para apoiar o vídeo deve ser mais direto e visual do que o relatório formal. Ele deve funcionar como roteiro de apresentação, com seções fáceis de navegar.

A estrutura recomendada é:

- cabeçalho com o título do trabalho;
- menu interno com links para as seções;
- resumo executivo;
- roteiro sugerido por tempo para vídeo de 5 a 10 minutos;
- descrição das três bases;
- explicação da variável `TARGET`;
- fluxo geral do processamento;
- tabelas de agregações;
- explicação dos tratamentos aplicados;
- desbalanceamento da variável alvo;
- métrica de risco com os 10 campos e pesos;
- lista dos arquivos finais;
- texto base para fala durante o vídeo;
- conclusão.

O HTML deve ter estilo limpo, boa legibilidade e tabelas claras. O menu pode usar rolagem suave para facilitar a navegação. A fonte Figtree pode ser usada para melhorar a aparência.

Para o vídeo, a mensagem central deve ser:

> O objetivo do trabalho foi pegar três bases de crédito separadas, agregar as informações por cliente, tratar dados ausentes e categóricos, analisar o desbalanceamento da variável alvo e gerar uma base final preparada para uma futura etapa de Machine Learning.

O texto base para apresentação pode seguir esta sequência:

1. apresentar o objetivo;
2. mostrar as três bases;
3. explicar por que foi necessário agregar Serasa e empréstimos anteriores;
4. explicar a junção por `SK_ID_CURR`;
5. explicar os tratamentos;
6. comentar o desbalanceamento;
7. apresentar a métrica;
8. encerrar mostrando os arquivos finais.

## Consulta 8 - Revisão final da entrega

**Prompt enviado:**

> Verifique novamente se esse pré-processamento abordou e realizou tudo da melhor forma possível, desde quantidade de arquivos gerados até as tabelas. Compare com o enunciado completo.

**Resposta recebida:**

A revisão deve verificar três níveis:

1. arquivos da entrega;
2. estrutura da base final;
3. aderência ao enunciado.

Os arquivos essenciais esperados são:

- fontes originais:
  - `emprestimos.csv`;
  - `serasa.csv`;
  - `emprestimos_anteriores.csv`;
- bases finais:
  - `base_final_preprocessada.csv`;
  - `base_final_com_metrica.csv`;
- documentação:
  - `relatorio_preprocessamento.docx`;
  - `apendice_consultas_llm.md`;
  - `README_ENTREGA.md`;
- código e comandos:
  - `preprocessamento_credito.py`;
  - `sqlite_comandos.sql`;
  - `requirements.txt`;
- banco:
  - `preprocessamento_credito.db`;
- arquivos auxiliares:
  - `dicionario_codificacao_categorias.csv`;
  - `resumo_estatistico_preprocessamento.csv`;
  - `resumo_processamento.json`;
  - `relatorio_video_preprocessamento.html`;
  - `app.py`.

A base final deve ser conferida para garantir:

- quantidade de linhas igual à base principal;
- ausência de duplicidade em `SK_ID_CURR`;
- ausência de células vazias após o tratamento;
- presença de `TARGET`;
- presença das variáveis demográficas selecionadas;
- presença dos campos agregados da base Serasa;
- presença dos campos agregados da base de empréstimos anteriores.

Os resultados encontrados foram:

- `base_final_preprocessada.csv`: 307.511 linhas;
- `base_final_com_metrica.csv`: 307.511 linhas;
- `preprocessamento_credito.db`: 307.511 linhas na tabela `base_final_metrica`;
- duplicidade em `SK_ID_CURR`: 0;
- células ausentes na base final: 0;
- colunas na base final: 41;
- colunas na base com métrica: 43.

A distribuição da variável alvo foi:

- `TARGET = 0`: 282.686 registros, 91,93%;
- `TARGET = 1`: 24.825 registros, 8,07%.

As agregações obrigatórias da base Serasa foram cumpridas:

- quantidade de empréstimos;
- dívida atrasada;
- créditos ativos.

Também foram criadas agregações adicionais:

- média de dias de crédito;
- máximo de dias em atraso;
- crédito total;
- dívida total;
- máximo valor em atraso;
- quantidade de prorrogações.

As agregações obrigatórias da base de empréstimos anteriores também foram cumpridas:

- quantidade de tentativas;
- taxa de rejeição;
- comparação entre valor solicitado e aprovado.

Também foram criadas variáveis extras:

- quantidade com seguro;
- quantidade de cliente repetidor;
- quantidade de cancelamentos.

A métrica de risco atende ao enunciado porque usa 10 campos finais, foi criada em uma cópia da base e gera uma pontuação de 0 a 100.

A estatística de Hopkins era opcional, pois o enunciado usa a expressão "se quiser". Após a revisão, ela foi adicionada como melhoria complementar, calculada sobre uma amostra da base final usando os 10 campos da métrica. O valor obtido foi aproximadamente 0,8450, indicando forte tendência de agrupamento nos campos avaliados.

Outro ponto de atenção identificado era formal: o apêndice de consultas à LLM deveria conter prompts e respostas completas, e não apenas respostas resumidas. Por isso, o apêndice foi expandido para registrar as consultas e respostas de forma mais detalhada.

## Consulta 9 - Melhoria do aplicativo Streamlit

**Prompt enviado:**

> A seção de arquivos gerados do aplicativo Streamlit ficou visualmente bagunçada. Dá para organizar de outra forma? Também, quando clico em baixar, ele volta para a tela inicial de processamento.

**Resposta recebida:**

A interface pode ser melhorada organizando os downloads em cartões, em vez de uma lista vertical simples. Cada cartão pode mostrar:

- nome do arquivo;
- descrição curta;
- tamanho do arquivo;
- botão de download.

No Streamlit, uma boa solução é usar `st.columns(2)` para criar uma grade com duas colunas e `st.container(border=True)` para criar cartões visuais.

O problema de voltar para a tela inicial ocorre porque o Streamlit reexecuta o script quando um botão é clicado. Para evitar que a área de resultados desapareça, é necessário guardar o estado do processamento em `st.session_state`.

Também é possível configurar o botão de download com:

```python
on_click="ignore"
```

Isso evita que o clique no download reinicie a interface.

O caminho padrão do aplicativo também pode ser melhorado para apontar diretamente para a pasta do projeto, usando:

```python
PROJECT_ROOT = Path(__file__).resolve().parent
```

Assim, o usuário não precisa digitar manualmente a pasta sempre que abrir o app.

## Consulta 10 - Correção visual e de codificação do HTML

**Prompt enviado:**

> Melhore o HTML. A parte do banco de dados ficou impossível de ler. O bloco SQL aparece quebrado. Também use a fonte Figtree, coloque rolagem suave e corrija o problema de UTF-8 em textos que aparecem com caracteres corrompidos.

**Resposta recebida:**

O problema visual do bloco SQL ocorre porque a regra CSS aplicada ao elemento `code` inline também afeta o `code` dentro de `pre`. Para corrigir, deve-se criar uma regra específica para `pre code`, removendo fundo, borda e padding herdados.

Uma correção adequada é:

```css
pre {
  overflow: auto;
  background: #101820;
  color: #eaf2f8;
  border-radius: 8px;
  padding: 16px;
  font-size: 13px;
  line-height: 1.45;
  border: 1px solid #203142;
  white-space: pre-wrap;
}

pre code {
  display: block;
  background: transparent;
  border: 0;
  border-radius: 0;
  padding: 0;
  color: inherit;
  font-family: Consolas, Monaco, monospace;
  white-space: pre-wrap;
}
```

Para usar a fonte Figtree, o HTML deve incluir:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

E no CSS:

```css
body {
  font-family: "Figtree", Arial, Helvetica, sans-serif;
}
```

Para rolagem suave:

```css
html {
  scroll-behavior: smooth;
}
```

Para ajustar a posição da rolagem em seções:

```css
section {
  scroll-margin-top: 46px;
}
```

O problema de textos com caracteres corrompidos é causado por mojibake, ou seja, leitura e escrita com codificação errada. A correção é salvar o arquivo novamente em UTF-8 real e conferir se não restam sequências típicas de erro de codificação.

Após a correção, os textos devem aparecer como:

- `agregações`;
- `variáveis numéricas`;
- `categóricas`;
- `Também`;
- `números`.

## Observação final sobre uso da LLM

As respostas da LLM foram usadas como apoio para:

- interpretar o enunciado;
- definir a estratégia de pré-processamento;
- organizar os campos selecionados;
- criar agregações;
- estruturar a métrica;
- organizar o relatório;
- revisar a entrega;
- melhorar a interface de apoio;
- corrigir o relatório HTML.

Todas as decisões foram conferidas nos arquivos finais gerados:

- `base_final_preprocessada.csv`;
- `base_final_com_metrica.csv`;
- `dicionario_codificacao_categorias.csv`;
- `resumo_estatistico_preprocessamento.csv`;
- `resumo_processamento.json`;
- `preprocessamento_credito.py`;
- `preprocessamento_credito.db`;
- `sqlite_comandos.sql`;
- `relatorio_preprocessamento.docx`;
- `relatorio_video_preprocessamento.html`.

Também foi feita conferência final para evitar erro de alucinação: a base final possui 307.511 registros, não possui `SK_ID_CURR` duplicado, não possui valores ausentes após o tratamento e preserva a distribuição da variável alvo.
