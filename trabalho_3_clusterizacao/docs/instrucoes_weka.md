# Instruções para clusterização no WEKA

## Base autorizada

Utilize exclusivamente:

```text
trabalho_3_clusterizacao/data/preparadas/base_clusterizacao_final.arff
```

Validação anterior à abertura no WEKA:

- 10.000 registros;
- 6 atributos;
- 5 atributos numéricos;
- `FLAG_OWN_CAR_COD` nominal, com categorias `{N,Y}`;
- sem `SK_ID_CURR`, `TARGET` ou `ROW_ID_AMOSTRA`;
- SHA-256: `65fa29f4c6d45fc0f0cb9799c2da630757b7718cc11c2e7f453700de932038a3`.

Não use `base_amostra_10000_analise.csv` no WEKA. Ela contém campos preservados
somente para rastreabilidade e análise posterior.

## 1. Abrir a base

1. Inicie o **WEKA GUI Chooser**.
2. Clique em **Explorer**.
3. Abra a aba **Preprocess**.
4. Clique em **Open file...**.
5. Selecione `base_clusterizacao_final.arff`.
6. Confirme na área **Current relation**:
   - `Instances: 10000`;
   - `Attributes: 6`.
7. Confira a lista de atributos. `FLAG_OWN_CAR_COD` deve aparecer como nominal;
   os outros cinco devem aparecer como numéricos.
8. Não defina atributo de classe. A base não possui `TARGET` e não é uma tarefa
   supervisionada.

Se quantidade, nomes ou tipos forem diferentes, interrompa a execução e não
salve uma nova base.

## 2. Selecionar o filtro AddCluster

1. Ainda em **Preprocess**, localize a seção **Filter**.
2. Clique em **Choose**.
3. Navegue por:

   ```text
   unsupervised > attribute > AddCluster
   ```

   O nome completo da classe é
   `weka.filters.unsupervised.attribute.AddCluster`.
4. Clique sobre o texto do filtro selecionado para abrir suas propriedades.
5. Na propriedade do clusterer, escolha o algoritmo autorizado para a etapa
   atual e configure seus parâmetros reais.

Não utilize resultados da aba **Cluster** como substitutos da base exportada
pelo filtro. O trabalho exige a coluna adicionada pelo **AddCluster**.

## 3. Configurar o algoritmo

As execuções são sequenciais:

1. DBSCAN, somente na Etapa 8;
2. SimpleKMeans, somente na Etapa 9;
3. EM, somente na Etapa 10.

Antes de clicar em **Apply**, registre em `docs/diario_experimentos.md` ou em
anotação auxiliar da etapa:

- método e identificação do teste;
- todos os parâmetros alterados;
- seed, quando disponível;
- distância utilizada;
- limite de iterações, quando aplicável;
- `epsilon` e `minPoints`, no DBSCAN.

Não ajuste configurações silenciosamente e não sobrescreva testes anteriores.

### Preservação dos pesos na distância

Nos algoritmos que utilizam `weka.core.EuclideanDistance`, abra as propriedades
da distância e defina `dontNormalize = true`, equivalente à opção `-D`. A base
já foi normalizada e multiplicada por `sqrt(peso)` na Etapa 4. Se o WEKA
normalizar novamente cada atributo, o efeito dos pesos pode ser reduzido ou
anulado. Mantenha todos os seis atributos selecionados (`first-last`).

## 4. Aplicar o filtro

1. Feche a janela de propriedades confirmando a configuração.
2. Clique em **Apply**.
3. Aguarde a conclusão real do processamento.
4. Confirme que a relação passou de 6 para 7 atributos.
5. Confirme a presença de uma nova coluna chamada exatamente `cluster`.
6. Selecione `cluster` e confira se existem rótulos atribuídos.
7. Não remova nem reordene registros ou atributos.

Se o WEKA apresentar erro, registre a mensagem completa e interrompa a etapa.
Não produza manualmente uma coluna `cluster`.

## 5. Salvar a base exportada

1. Clique em **Save...** na aba **Preprocess** depois que o filtro terminar.
2. Prefira ARFF para preservar os tipos dos atributos.
3. Use o nome correspondente à execução real, por exemplo:

   ```text
   data/clusterizadas_weka/base_clusterizada_dbscan_teste_01.arff
   data/clusterizadas_weka/base_clusterizada_kmeans_k3.arff
   data/clusterizadas_weka/base_clusterizada_em_k3.arff
   ```

4. Nunca substitua um teste anterior. Incremente o sufixo do teste ou o valor
   de `K`.
5. Não use o nome `final` antes de a configuração ser comparada e aprovada.

## 6. Conferência após salvar

Antes de considerar uma execução disponível, confirme:

- arquivo realmente criado pelo WEKA;
- 10.000 registros;
- 7 atributos;
- coluna `cluster` presente;
- seis atributos originais preservados;
- nenhuma coluna protegida adicionada;
- ordem dos registros aparentemente preservada;
- parâmetros e resultados registrados sem estimativas ou simulações.

Na etapa correspondente, o arquivo será validado por script antes de qualquer
análise ou junção com a base auxiliar.

## Referência técnica

Documentação da classe `AddCluster` do WEKA:

```text
https://weka.sourceforge.io/doc.dev/weka/filters/unsupervised/attribute/AddCluster.html
```
