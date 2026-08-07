#faz o selecao de campos, atribui pesos e reescala
import pandas as pd
import numpy as np
import math
import os

def processar_csv():
    # 1. Solicita o nome do arquivo
    nome_arquivo = input("Digite o nome do arquivo .csv (com a extensão): ")
    
    if not os.path.exists(nome_arquivo):
        print("Erro: Arquivo não encontrado.")
        return

    try:
        df = pd.read_csv(nome_arquivo)
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return

    colunas = df.columns.tolist()
    pesos = {}
    tipos = {}
    colunas_mantidas = []

    print("\n" + "="*50)
    print("ANÁLISE CAMPO A CAMPO")
    print("="*50)

    # 2 e 3. Interação campo a campo (amostra, peso e tipo)
    for col in colunas:
        print(f"\n--- Campo: {col} ---")
        
        # Pega uma amostra de até 3 registros (ignorando valores nulos para mostrar dados reais)
        amostra = df[col].dropna().head(3).tolist()
        print(f"Amostra de dados: {amostra}")
        
        # Solicita o peso
        while True:
            try:
                peso_str = input(f"Peso para '{col}' (Inteiro de 0 a 10): ")
                peso = int(peso_str)
                if 0 <= peso <= 10:
                    break
                else:
                    print("Por favor, digite um valor entre 0 e 10.")
            except ValueError:
                print("Entrada inválida. Digite um número inteiro.")
        
        # Se o peso for 0, pula a solicitação de tipo e vai para o próximo campo
        if peso == 0:
            print(f"-> Campo '{col}' será descartado.")
            continue
            
        pesos[col] = peso
        colunas_mantidas.append(col)
        
        # Solicita o tipo (assumindo 3 como padrão)
        print("\nTipos disponíveis:")
        print("[1] Nominal  - Mantém original")
        print("[2] Ordinal  - Enumera de 0 a N e multiplica pela raiz do peso")
        print("[3] Numérico - Reescala (Min-Max) e multiplica pela raiz do peso")
        
        while True:
            tipo = input(f"Tipo do campo '{col}' (Pressione ENTER para [3] Numérico): ").strip()
            
            if tipo == "":
                tipo = '3'  # Define Numérico como padrão
                
            if tipo in ['1', '2', '3']:
                tipos[col] = tipo
                print(f"-> Tipo definido como: {tipo}")
                break
            else:
                print("Opção inválida. Digite 1, 2, 3 ou apenas aperte ENTER.")

    # Filtra o dataframe apenas com as colunas que receberam peso > 0
    df_processado = df[colunas_mantidas].copy()

    print("\n" + "="*50)
    print("PROCESSANDO DADOS...")
    print("="*50)

    # 4. Tratamento da escala e tipos
    for col in colunas_mantidas:
        tipo = tipos[col]
        raiz_peso = math.sqrt(pesos[col])

        if tipo == '1':
            # Nominal: Mantenha como está
            pass

        elif tipo == '2':
            # Ordinal: numeração de 0 à maior ordem
            df_processado[col] = pd.Categorical(df_processado[col], ordered=True).codes
            df_processado[col] = df_processado[col].astype(float) * raiz_peso

        elif tipo == '3':
            # Numérico: reescala e multiplica
            df_processado[col] = pd.to_numeric(df_processado[col], errors='coerce')
            val_min = df_processado[col].min()
            val_max = df_processado[col].max()
            
            if val_max != val_min:
                df_processado[col] = (df_processado[col] - val_min) / (val_max - val_min)
            else:
                df_processado[col] = 0.0 
                
            df_processado[col] = df_processado[col] * raiz_peso

    # 5. Salva a nova base com "p" no final
    nome_base, ext = os.path.splitext(nome_arquivo)
    novo_nome = f"{nome_base}p{ext}"
    
    df_processado.to_csv(novo_nome, index=False)
    print(f"\nProcesso concluído com sucesso!")
    print(f"Arquivo salvo como: {novo_nome}")

if __name__ == "__main__":
    processar_csv()