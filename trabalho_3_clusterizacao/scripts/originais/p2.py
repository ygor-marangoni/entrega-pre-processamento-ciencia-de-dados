import pandas as pd
import numpy as np
import os
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder

def executar_hopkins_misto():
    # 1. Solicita o nome do arquivo
    nome_arquivo = input("Digite o nome do arquivo .csv (com a extensão): ")
    
    if not os.path.exists(nome_arquivo):
        print("Erro: Arquivo não encontrado.")
        return

    # Lê o arquivo original
    try:
        df = pd.read_csv(nome_arquivo)
        print(f"\nBase original carregada com sucesso. Total de registros: {len(df)}")
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return

    # 2. Cria a base amostral (limita a 10.000 registros)
    if len(df) > 10000:
        df_amostral = df.sample(n=10000, random_state=42).copy()
        print("-> Base amostral criada com 10.000 registros aleatórios.")
    else:
        df_amostral = df.copy()
        print("-> A base possui 10.000 registros ou menos. Utilizando a base completa.")

    n_amostral = len(df_amostral)
    tamanho_1_porcento = max(1, int(n_amostral * 0.01))

    # 3. Identifica colunas numéricas e nominais
    colunas_numericas = df_amostral.select_dtypes(include=[np.number]).columns.tolist()
    colunas_nominais = df_amostral.select_dtypes(exclude=[np.number]).columns.tolist()

    # 4. Cria a base real e virtual
    df_real = df_amostral.sample(n=tamanho_1_porcento, random_state=42).copy()

    dict_virtual = {}
    for col in df_amostral.columns:
        if col in colunas_numericas:
            min_val = df_amostral[col].min()
            max_val = df_amostral[col].max()
            dict_virtual[col] = np.random.uniform(min_val, max_val, tamanho_1_porcento)
        else:
            valores_possiveis = df_amostral[col].dropna().unique()
            dict_virtual[col] = np.random.choice(valores_possiveis, tamanho_1_porcento)
            
    df_virtual = pd.DataFrame(dict_virtual)

    print("\nResumo das Bases:")
    print(f"- Base Amostral: {n_amostral} registros")
    print(f"- Base Real:     {len(df_real)} registros")
    print(f"- Base Virtual:  {len(df_virtual)} registros")
    print(f"- Campos Numéricos: {len(colunas_numericas)}")
    print(f"- Campos Nominais:  {len(colunas_nominais)}")

    # 5. Processamento para Distância Euclidiana Mista (Equivalente ao HEOM)
    # Extrai os valores numéricos
    X_num_amostral = df_amostral[colunas_numericas].values if colunas_numericas else np.empty((n_amostral, 0))
    X_num_real = df_real[colunas_numericas].values if colunas_numericas else np.empty((tamanho_1_porcento, 0))
    X_num_virtual = df_virtual[colunas_numericas].values if colunas_numericas else np.empty((tamanho_1_porcento, 0))

    # Processa os nominais para que Distância Euclidiana = 1 se diferentes, 0 se iguais
    if colunas_nominais:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        encoder.fit(df_amostral[colunas_nominais])
        
        fator_escala = 1.0 / np.sqrt(2.0)
        
        X_nom_amostral = encoder.transform(df_amostral[colunas_nominais]) * fator_escala
        X_nom_real = encoder.transform(df_real[colunas_nominais]) * fator_escala
        X_nom_virtual = encoder.transform(df_virtual[colunas_nominais]) * fator_escala
        
        X_amostral = np.hstack((X_num_amostral, X_nom_amostral))
        X_real = np.hstack((X_num_real, X_nom_real))
        X_virtual = np.hstack((X_num_virtual, X_nom_virtual))
    else:
        X_amostral = X_num_amostral
        X_real = X_num_real
        X_virtual = X_num_virtual

    if X_amostral.shape[1] == 0:
        print("\nErro: Nenhuma coluna válida encontrada para cálculo.")
        return

    print("\nCalculando a Estatística de Hopkins incluindo todos os campos...")

    # 6. Executa a Estatística de Hopkins
    # A. Distância dos virtuais para a base (u)
    nn_amostral = NearestNeighbors(n_neighbors=1, metric='euclidean', n_jobs=-1)
    nn_amostral.fit(X_amostral)
    dist_u, _ = nn_amostral.kneighbors(X_virtual)
    u = dist_u[:, 0]

    # B. Distância dos reais para a base (w) - n_neighbors=2 para ignorar a si mesmo
    nn_real = NearestNeighbors(n_neighbors=2, metric='euclidean', n_jobs=-1)
    nn_real.fit(X_amostral)
    dist_w, _ = nn_real.kneighbors(X_real)
    w = dist_w[:, 1]

    # Fórmula Clássica de Hopkins
    soma_u = np.sum(u)
    soma_w = np.sum(w)

    if (soma_u + soma_w) == 0:
        hopkins_stat = 0.5
    else:
        hopkins_stat = soma_u / (soma_u + soma_w)

    # 7. Apresentação do Resultado
    print("\n" + "="*50)
    print("RESULTADO DA ESTATÍSTICA DE HOPKINS")
    print("="*50)
    print(f"H = {hopkins_stat:.5f}")
    
    print("\nInterpretação:")
    if hopkins_stat >= 0.7:
        print("H > 0.7: Alta probabilidade. Os dados possuem forte tendência de clusterização.")
    elif hopkins_stat <= 0.3:
        print("H < 0.3: Baixa probabilidade. Os dados tendem a ser regularmente espaçados (uniformes).")
    else:
        print("H próximo a 0.5: Os dados estão distribuídos de forma aleatória no espaço.")

if __name__ == "__main__":
    executar_hopkins_misto()