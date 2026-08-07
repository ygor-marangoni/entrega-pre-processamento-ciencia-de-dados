# Relatório de validação final — Trabalho 3

Data da auditoria: 21 de julho de 2026.

## Status geral

**APROVADO COM RESSALVAS**

O trabalho está tecnicamente consistente e os resultados centrais são reproduzíveis. A ressalva remanescente é documental: as saídas textuais brutas do WEKA não foram preservadas. Os ARFFs comprovam o uso real do AddCluster, os algoritmos, as configurações e as atribuições, mas não permitem revalidar avisos, convergência, tempos, SSE ou log-likelihood exibidos na interface. O caso mais sensível é o log-likelihood `-0,29589` do EM K=10, mantido como valor transcrito e explicitamente marcado como não comprovado.

## Fase 1 — auditoria sem modificações

A matriz requisito × evidência registrou 90 verificações: 74 `OK`, 13 `DIVERGENTE` e três `NÃO COMPROVADO`. Não houve inconsistência crítica real. Os dois falsos positivos iniciais sobre distância euclidiana e AddCluster foram corrigidos no próprio auditor antes da fase de correção.

Os artefatos originais dessa fase permanecem em:

- `resultados/validacao_final/auditoria_final.md`;
- `resultados/validacao_final/checks_validacao.csv`;
- `resultados/validacao_final/inconsistencias_encontradas.csv`.

## Inconsistências e tratamento

### Críticas

Nenhuma.

### Altas

- Evidência do joelho do DBSCAN ausente: **resolvida** pela reprodução da curva do sexto vizinho, do algoritmo geométrico e do gráfico. O ponto foi reproduzido em `epsilon = 0,274264329675521`, arredondado no WEKA para `0,274264329676`, percentil 94,3794%.
- Justificativa de K=9 no SimpleKMeans incompleta: **resolvida** com as métricas de K=8, K=9 e K=10 e com a descrição do compromisso entre Silhouette, Davies-Bouldin, Calinski-Harabasz, equilíbrio, interpretação e comparabilidade.
- Uso de IA não documentado: **resolvido** com subseção metodológica factual.
- EM K=10 e diagnósticos brutos do WEKA: **não comprovados**. O ARFF valida a execução e os dez rótulos, mas o log bruto não existe no repositório. O relatório e a configuração foram corrigidos para não afirmar falha ou convergência inferior sem evidência.

### Médias

- Descrição da ordem da amostra, redação das sete colunas, referências, afirmação de dispersão, cabeçalho `Limiar` e legibilidade da Figura 11: **resolvidas**.
- O SHA-256 da base de origem já constava no relatório; o apontamento inicial de ausência era um erro do auditor e foi corrigido antes da consolidação da Fase 1.

### Baixas

- Nomenclatura `completa`, precisão excessiva de epsilon no corpo, eixo monetário e falta de CSV final do DBSCAN: **resolvidas**. O CSV do DBSCAN é identificado como conversão fiel do ARFF original, e não como nova exportação do WEKA.

## Backups

Os relatórios anteriores e os arquivos textuais alterados foram preservados em `relatorio/backup_pre_validacao_final_20260721/`. Nenhuma base bruta nem exportação válida do WEKA foi alterada.

## Resultados confirmados

### Base de origem

- Caminho: `../trabalho_1_preprocessamento/data/base_final_preprocessada.csv`.
- Registros: 307.511.
- Colunas: 41.
- Tamanho: 60.943.180 bytes.
- SHA-256: `651062c36ef1bd2b70b41f7c516386fdd8006d3eab0f9984ca7718d5f29ef861`.
- `SK_ID_CURR` e `TARGET`: presentes.

### Amostra

- 10.000 registros, sem reposição, `random_state=42`.
- Reprodução temporária integralmente igual ao arquivo oficial.
- `ROW_ID_AMOSTRA` e `SK_ID_CURR` únicos.
- SHA-256 da base de análise: `fbc3e8d592bf406b65c93e445f7849a68685eccd7637689344d68a78404a3b22`.
- SHA-256 da base sem campos protegidos: `aac7843e20c7f29f10730bc4cc6de057305a8c3867ba63a132f613ff87942fd6`.

### Atributos e transformações

Foram confirmados exclusivamente `AMT_CREDIT`, `CNT_CHILDREN`, `FLAG_OWN_CAR_COD`, `AGE_YEARS`, `CREDIT_INCOME_RATIO` e `SER_CREDITOS_ATIVOS`, com pesos 6, 4, 1, 5, 7 e 5. A transformação foi recalculada para os 10.000 registros; a diferença máxima ficou abaixo de `1e-10`. `FLAG_OWN_CAR_COD` foi recuperado de `0/1` para o nominal `N/Y`, preservado no WEKA e codificado temporariamente como `0/1` apenas nas métricas Python.

### Hopkins

- Execução 1: `0,9417454790893174`.
- Execução 2: `0,9417454790893174`.
- Base: 10.000; amostra real: 100; amostra virtual: 100; seed: 42.
- Toda aleatoriedade usa `numpy.random.default_rng(42)` no script próprio.

### WEKA e clusters

- DBSCAN: nove clusters + 296 ruídos = 10.000; maior grupo 4.759; menor grupo 6; razão 793,1667.
- SimpleKMeans final: K=9; nove grupos = 10.000; menor 525; maior 1.992; entropia 0,960189100688069.
- EM final: K=9; nove grupos = 10.000; menor 257; maior 4.359; entropia 0,809238375192612.
- Cada base final possui sete colunas no total: seis atributos de entrada e `cluster`.
- Os seis atributos foram comparados linha a linha com a base preparada e permaneceram iguais e na mesma ordem.
- As relações dos ARFFs contêm `weka.filters.unsupervised.attribute.AddCluster` e o clusterer correspondente.

### Métricas finais

| Método | Silhouette | Davies-Bouldin | Calinski-Harabasz | Entropia | Ruídos |
|---|---:|---:|---:|---:|---:|
| DBSCAN | 0,085903791278 | 1,855621973727 | 1.031,784233232448 | 0,663654154868 | 296 |
| SimpleKMeans | 0,263382438710 | 1,380971357097 | 3.106,870162537691 | 0,960189100688 | 0 |
| EM | 0,109936205875 | 1,504641820546 | 1.862,177065056076 | 0,809238375193 | 0 |

A maior diferença absoluta entre as métricas registradas e as recalculadas foi `2,273736754432321e-13`.

### TARGET e perfis

- Taxa global posterior de `TARGET = 1`: 8,23% (823 registros).
- `TARGET` não aparece na base preparada nem nas exportações usadas para formar clusters.
- `TARGET` foi adicionado somente nas bases de análise após a atribuição dos rótulos.
- Os perfis e taxas por cluster foram recalculados a partir de `resumo_dbscan.csv`, `resumo_kmeans.csv` e `resumo_em.csv`.
- O texto não trata ausência de carro como intenção, ruído como fraude, correlação como causalidade ou TARGET posterior como validação causal.

## Validação documental e visual

- DOCX: A4, margens 3 cm à esquerda e 2 cm à direita, oito tabelas, doze figuras e texto alternativo nas figuras.
- PDF: 35 páginas físicas, sendo três pré-textuais e 32 numeradas.
- Sumário conferido contra todas as 24 seções.
- As 35 páginas foram renderizadas e inspecionadas visualmente.
- Não foram encontrados texto cortado, tabela fora da margem, gráfico ilegível, caractere quebrado, página em branco ou numeração duplicada.
- `Limiar` foi abreviado para `Lim.` na Tabela 3; epsilon foi reduzido a quatro casas no corpo e mantido completo no apêndice; o eixo de crédito usa R$ milhões; a Figura 11 foi ampliada para três painéis verticais.

## Pendências humanas

1. Reabrir as configurações no WEKA e salvar logs ou capturas, especialmente para conferir o log-likelihood do EM K=10, os avisos e a convergência.
2. Confirmar a grafia do nome do professor, a identificação da turma e os dados institucionais da folha de rosto.
3. Confirmar se a política da disciplina exige declaração adicional de uso de IA além da subseção metodológica incluída.

## Comandos principais executados

- `python trabalho_3_clusterizacao/scripts/12_validar_entrega_final.py --sobrescrever`
- `python trabalho_3_clusterizacao/scripts/07_validar_exportacao_weka.py --sobrescrever`
- `python trabalho_3_clusterizacao/scripts/11_gerar_relatorio.py --sobrescrever`
- LibreOffice em modo headless para conversão DOCX → PDF.
- `python -m compileall -q trabalho_3_clusterizacao/scripts`
- Renderização das 35 páginas com `pypdfium2` e inspeção com folhas de contato.
- Verificações de PDF com `pdfplumber` e de DOCX com `python-docx`.

## Declaração

Nenhum resultado foi inventado. Todos os números do relatório possuem origem rastreável nas bases, nos ARFFs, nas configurações ou nos scripts. As bases anexadas correspondem aos resultados descritos. `TARGET` não participou da clusterização. DBSCAN, SimpleKMeans e EM foram realmente executados no WEKA pelo filtro AddCluster, conforme comprovado pelas relações dos ARFFs; somente os diagnósticos textuais não preservados permanecem como ressalva documental.
