# Entrega — Trabalho de Ciência de Dados: Pré-processamento

Este repositório contém a entrega do trabalho de Ciência de Dados sobre **pré-processamento de dados para análise de risco de crédito**.

O objetivo do projeto é unir informações de três bases diferentes, realizar tratamento dos dados, criar agregações, codificar variáveis categóricas, gerar uma base final para modelagem e construir uma métrica simples de risco.

> Organização atual: bases e artefatos de dados estão em `data/`, scripts em
> `scripts/`, resumos em `resultados/`, o material visual em `relatorio/` e o
> apêndice em `docs/`. Execute os comandos abaixo a partir deste diretório.

---

## Bases utilizadas

O projeto utiliza três arquivos CSV de entrada:

```text
emprestimos.csv
serasa.csv
emprestimos_anteriores.csv
```

A base `emprestimos.csv` é a base principal, contendo os dados demográficos e a variável alvo `TARGET`.

As bases `serasa.csv` e `emprestimos_anteriores.csv` são usadas para gerar variáveis agregadas sobre o histórico externo e interno dos clientes.

---

## Arquivos do projeto

1. `scripts/app.py`  
   Aplicação web em Streamlit para executar o pré-processamento de forma visual.

2. `scripts/preprocessamento_credito.py`  
   Código-fonte principal usado para reproduzir todo o pré-processamento.

3. `requirements_trabalho_1.txt`  
   Lista das dependências necessárias para executar o projeto.

4. `sqlite_comandos.sql`  
   Comandos SQL básicos para conferência da base final no SQLite.

5. `relatorio_preprocessamento.docx`  
   Relatório textual do pré-processamento realizado.

6. `apendice_consultas_llm.md`  
   Registro das consultas feitas à LLM e das respostas recebidas.

7. `dicionario_codificacao_categorias.csv`  
   Dicionário com os códigos usados para transformar variáveis categóricas em valores numéricos.

8. `resumo_estatistico_preprocessamento.csv`  
   Resumo com informações sobre quantidade de registros, desbalanceamento, valores ausentes e estatísticas da métrica.

---

## Arquivos gerados após a execução

Após executar o projeto, os seguintes arquivos são gerados:

```text
base_final_preprocessada.csv
base_final_com_metrica.csv
dicionario_codificacao_categorias.csv
resumo_estatistico_preprocessamento.csv
resumo_processamento.json
preprocessamento_credito.db
```

Descrição dos principais arquivos gerados:

1. `base_final_preprocessada.csv`  
   Base final para modelagem, com dados demográficos selecionados, agregações das bases Serasa e empréstimos anteriores, imputação de ausentes e variáveis categóricas codificadas.

2. `base_final_com_metrica.csv`  
   Cópia da base final contendo a métrica `METRICA_RISCO_0_100` e a classificação `CLASSE_METRICA`.

3. `dicionario_codificacao_categorias.csv`  
   Dicionário com os códigos usados para transformar variáveis categóricas em valores numéricos.

4. `resumo_estatistico_preprocessamento.csv`  
   Resumo com quantidades, desbalanceamento, valores ausentes e estatísticas da métrica.

5. `resumo_processamento.json`  
   Resumo estruturado do processamento, contendo informações da base final, contagem das classes, campos finais, estatística de Hopkins e faixas da métrica.

6. `preprocessamento_credito.db`  
   Banco SQLite com a tabela `base_final_metrica`.

---

## Observação sobre os arquivos de entrada

As bases brutas podem ser grandes. Por isso, elas não devem ser enviadas diretamente para o GitHub caso ultrapassem o limite de tamanho permitido.

Arquivos de entrada:

```text
emprestimos.csv
serasa.csv
emprestimos_anteriores.csv
```

Para executar o projeto corretamente, coloque esses três arquivos na pasta do projeto ou informe o caminho da pasta usando o parâmetro `--base-dir`.

Estrutura esperada:

```text
trabalho_1_preprocessamento/
├── data/
│   ├── emprestimos.csv
│   ├── serasa.csv
│   ├── emprestimos_anteriores.csv
│   └── base_final_preprocessada.csv
├── scripts/
│   ├── app.py
│   └── preprocessamento_credito.py
├── resultados/
├── relatorio/
├── docs/
└── requirements_trabalho_1.txt
```

---

## Pré-requisitos

Para executar o projeto, é necessário ter o Python instalado.

Versão recomendada:

```text
Python 3.10 ou superior
```

As bibliotecas necessárias estão listadas no arquivo:

```text
requirements_trabalho_1.txt
```

---

## Como instalar as dependências

No terminal, dentro da pasta do projeto, execute:

```bash
pip install -r requirements_trabalho_1.txt
```

Opcionalmente, é possível criar um ambiente virtual antes da instalação.

No Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements_trabalho_1.txt
```

No Linux ou macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements_trabalho_1.txt
```

---

## Como executar pelo terminal

Com os três arquivos CSV dentro da pasta do projeto, execute:

```bash
python scripts/preprocessamento_credito.py --base-dir data
```

Caso os arquivos CSV estejam em outra pasta, use o parâmetro `--base-dir`:

```bash
python scripts/preprocessamento_credito.py --base-dir "CAMINHO_DA_PASTA"
```

Exemplo no Windows:

```powershell
python scripts/preprocessamento_credito.py --base-dir "C:\Users\SeuUsuario\Desktop\entrega_preprocessamento_ciencia_dados\trabalho_1_preprocessamento\data"
```

Durante a execução, o programa exibirá as etapas do processamento:

```text
1/9 Lendo base principal...
2/9 Agregando Serasa...
3/9 Agregando empréstimos anteriores...
4/9 Juntando bases...
5/9 Tratando ausentes e codificando categóricas...
6/9 Criando métrica ponderada...
7/9 Calculando estatística de Hopkins...
8/9 Salvando CSVs...
9/9 Criando banco SQLite...
Concluído
```

Ao final, os arquivos processados serão criados na mesma pasta das bases de entrada.

---

## Como executar pela interface web

O projeto também possui uma interface web feita com Streamlit.

Para abrir a aplicação, execute:

```bash
streamlit run scripts/app.py
```

Depois disso, o navegador será aberto com a interface do projeto.

Na tela da aplicação:

1. Informe a pasta onde estão os arquivos de entrada:

```text
emprestimos.csv
serasa.csv
emprestimos_anteriores.csv
```

2. Clique no botão:

```text
Rodar processamento
```

3. Aguarde a execução do pré-processamento.

4. Após a conclusão, a aplicação exibirá os arquivos gerados e permitirá o download diretamente pela interface.

---

## Sobre o pré-processamento realizado

O pipeline realiza as seguintes etapas:

1. Leitura da base principal `emprestimos.csv`.
2. Seleção dos campos demográficos relevantes.
3. Agregação da base `serasa.csv` por cliente.
4. Agregação da base `emprestimos_anteriores.csv` por cliente.
5. Junção das três bases usando a chave `SK_ID_CURR`.
6. Criação da variável `AGE_YEARS` a partir de `DAYS_BIRTH`.
7. Criação da variável `CREDIT_INCOME_RATIO`.
8. Tratamento de valores ausentes.
9. Codificação de variáveis categóricas.
10. Criação da base final pré-processada.
11. Criação da métrica `METRICA_RISCO_0_100` usando 10 campos finais.
12. Classificação da métrica em `Baixo`, `Medio` e `Alto`.
13. Cálculo da estatística de Hopkins.
14. Exportação dos arquivos finais em CSV, JSON e SQLite.

---

## Campos utilizados na métrica de risco

A métrica `METRICA_RISCO_0_100` foi construída com os seguintes campos:

```text
AMT_INCOME_TOTAL
AMT_CREDIT
CREDIT_INCOME_RATIO
EXT_SOURCE_1
EXT_SOURCE_2
EXT_SOURCE_3
SER_QTDE_EMPRESTIMOS
SER_DIVIDA_ATRASADA
SER_CREDITOS_ATIVOS
PREV_TAXA_REJEICAO
```

A métrica foi normalizada em uma escala de 0 a 100.

Quanto maior o valor da métrica, maior é o risco estimado de acordo com os critérios definidos no pré-processamento.

A classificação da métrica foi dividida em três faixas:

```text
Baixo
Medio
Alto
```

---

## Banco SQLite

O script gera automaticamente o banco:

```text
preprocessamento_credito.db
```

Dentro dele, é criada a tabela:

```text
base_final_metrica
```

Essa tabela contém a base final com a métrica de risco.

Exemplo de consulta SQL:

```sql
SELECT 
    SK_ID_CURR,
    TARGET,
    METRICA_RISCO_0_100,
    CLASSE_METRICA
FROM base_final_metrica
LIMIT 10;
```

Outro exemplo de consulta para verificar a quantidade de registros por classe da métrica:

```sql
SELECT 
    CLASSE_METRICA,
    COUNT(*) AS quantidade
FROM base_final_metrica
GROUP BY CLASSE_METRICA;
```

---

## Observação sobre GitHub

O GitHub possui limite de tamanho para arquivos enviados diretamente ao repositório. Como algumas bases brutas podem ultrapassar esse limite, recomenda-se não versionar os arquivos originais:

```text
emprestimos.csv
serasa.csv
emprestimos_anteriores.csv
```

Também é recomendável evitar versionar arquivos muito pesados gerados localmente, como bancos `.db`, caso ultrapassem o limite permitido.

Exemplo de `.gitignore` recomendado:

```gitignore
emprestimos.csv
serasa.csv
emprestimos_anteriores.csv

*.db
*.sqlite
*.sqlite3

__pycache__/
*.pyc
.venv/
```

---

## Como reproduzir a entrega

Para reproduzir a entrega completa:

1. Baixe ou clone este repositório.
2. Coloque as três bases CSV na pasta do projeto.
3. Instale as dependências:

```bash
pip install -r requirements_trabalho_1.txt
```

4. Execute o script principal:

```bash
python scripts/preprocessamento_credito.py --base-dir data
```

ou execute pela interface web:

```bash
streamlit run scripts/app.py
```

5. Confira os arquivos gerados na pasta do projeto.

---

## Autor

Trabalho desenvolvido para a disciplina de Ciência de Dados, com foco na etapa de pré-processamento de dados.
