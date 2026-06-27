# Trabalho Prático 2 - Classificação com WEKA

Este diretório contém a estrutura do Trabalho Prático 2 de Ciência de Dados. O trabalho usa a base final do Trabalho 1 e executa os classificadores reais do WEKA via `weka.jar`.

Não há substituição por scikit-learn ou execução alternativa em Python. Os scripts Python apenas preparam arquivos, chamam o WEKA por linha de comando, extraem métricas dos `.txt` gerados e atualizam o relatório.

## 1. Base utilizada

A base principal é:

```text
../base_final_preprocessada.csv
```

Regras aplicadas:

- `SK_ID_CURR` foi removido porque é identificador.
- `TARGET` foi mantido como classe.
- `TARGET` foi colocado como última coluna.
- `TARGET` foi declarado no ARFF como `{0,1}`.
- A base `base_final_com_metrica.csv` não é usada como base principal.

Arquivos preparados:

```text
data/base_weka_completa.csv
data/base_weka_completa.arff
```

## 2. Verificar Java

No PowerShell:

```powershell
java -version
where.exe java
```

Neste ambiente, o Java encontrado foi:

```text
java version "1.8.0_491"
Java(TM) SE Runtime Environment (build 1.8.0_491-b10)
Java HotSpot(TM) 64-Bit Server VM (build 25.491-b10, mixed mode)
```

Caminho encontrado:

```text
C:\Program Files (x86)\Common Files\Oracle\Java\java8path\java.exe
```

Se `java -version` falhar, o Java provavelmente está instalado mas fora do `PATH`. Corrija o `PATH` ou informe o executável Java manualmente usando `--java`.

## 3. Localizar o WEKA

Execute:

```powershell
cd trabalho_2_classificacao/scripts
python localizar_weka.py
```

O script procura `weka.jar` em caminhos comuns, como:

```text
C:\Program Files\Weka-3-8-6\weka.jar
C:\Program Files\Weka-3-8-7\weka.jar
C:\Program Files\Weka-3-9\weka.jar
C:\Program Files\Weka-3-9-6\weka.jar
C:\Program Files\Weka-3-9-7\weka.jar
```

Também salva:

```text
../weka_config.json
```

Se o `weka.jar` não for encontrado, instale o WEKA ou informe o caminho manualmente.

## 4. Preparar a base completa

```powershell
cd trabalho_2_classificacao/scripts
python preparar_bases_weka.py
```

Saídas:

```text
../data/base_weka_completa.csv
../data/base_weka_completa.arff
```

## 5. Rodar o pipeline completo

Se `weka_config.json` já tiver o caminho do WEKA:

```powershell
python pipeline_trabalho_2.py
```

Com caminho manual:

```powershell
python pipeline_trabalho_2.py --weka-jar "C:/Program Files/Weka-3-8-6/weka.jar" --max-memory 8g
```

Se faltar memória:

```powershell
python pipeline_trabalho_2.py --weka-jar "C:/Program Files/Weka-3-8-6/weka.jar" --max-memory 10g
```

O pipeline executa:

1. verifica Java e WEKA;
2. prepara a base completa;
3. roda J48, RandomForest, IBk, NaiveBayes e BayesNet na base completa;
4. extrai atributos relevantes do J48;
5. gera a base reduzida;
6. roda os cinco métodos na base reduzida;
7. extrai métricas;
8. gera gráficos;
9. atualiza o relatório Markdown e DOCX.

## 6. Rodar a primeira rodada manualmente

```powershell
python executar_weka.py --weka-jar "C:/Program Files/Weka-3-8-6/weka.jar" --base "../data/base_weka_completa.arff" --saida "../resultados/rodada_1_base_completa" --max-memory 8g
```

Arquivos esperados:

```text
../resultados/rodada_1_base_completa/J48.txt
../resultados/rodada_1_base_completa/RandomForest.txt
../resultados/rodada_1_base_completa/IBk.txt
../resultados/rodada_1_base_completa/NaiveBayes.txt
../resultados/rodada_1_base_completa/BayesNet.txt
```

## 7. Extrair atributos do J48

```powershell
python extrair_atributos_j48.py
```

Saída:

```text
../resultados/atributos_relevantes_j48.txt
```

Se a extração automática não funcionar, abra `../resultados/rodada_1_base_completa/J48.txt`, copie os atributos que aparecem nos nós da árvore para `atributos_relevantes_j48.txt`, um por linha, e rode:

```powershell
python extrair_atributos_j48.py --usar-manual
```

Isso gera:

```text
../data/base_weka_reduzida.csv
../data/base_weka_reduzida.arff
```

## 8. Rodar a segunda rodada manualmente

```powershell
python executar_weka.py --weka-jar "C:/Program Files/Weka-3-8-6/weka.jar" --base "../data/base_weka_reduzida.arff" --saida "../resultados/rodada_2_base_reduzida" --max-memory 8g
```

## 9. Gerar tabelas, gráficos e relatório

```powershell
python gerar_tabelas_relatorio.py
python gerar_graficos_resultados.py
python atualizar_relatorio.py
```

Saídas:

```text
../resultados/resultados_classificacao.csv
../resultados/comparativo_metricas.csv
../relatorio/imagens/comparativo_acuracia.png
../relatorio/imagens/comparativo_recall_classe_1.png
../relatorio/imagens/comparativo_fmeasure_classe_1.png
../relatorio/imagens/comparativo_roc_area.png
../relatorio/relatorio_classificacao.md
../relatorio/relatorio_classificacao_abnt.docx
```

## 10. Exportar para PDF

Opções recomendadas:

1. Abrir `relatorio/relatorio_classificacao_abnt.docx` no Word e exportar como PDF.
2. Abrir o Markdown no VS Code/Typora/Obsidian e exportar para PDF.
3. Usar Google Docs: enviar o `.docx`, revisar formatação e baixar como PDF.

## 11. Arquivos para entregar

Entregar no Moodle:

- relatório PDF;
- arquivos `.txt` reais do WEKA das duas rodadas;
- `resultados/resultados_classificacao.csv`;
- `resultados/comparativo_metricas.csv`;
- `resultados/atributos_relevantes_j48.txt`;
- scripts usados;
- se necessário, bases `.arff` geradas localmente.

## 12. Observações importantes

- Não inventar resultados.
- Não preencher métricas manualmente sem execução.
- Não usar `SK_ID_CURR` como atributo.
- Não usar `base_final_com_metrica.csv` como base principal.
- Se o IBk demorar muito, registrar o tempo ou a falha no `.log`; não substituir por outro método.
- Se algum método falhar, o `.log` será salvo na pasta da rodada.
