-- Gerenciador de banco de dados utilizado: SQLite 3
-- Objetivo: armazenar e consultar a base final preprocessada com métrica.

-- Opção 1: comandos para executar no terminal do SQLite.
-- sqlite3 preprocessamento_credito.db
.mode csv
.separator ;
.headers on

DROP TABLE IF EXISTS base_final_metrica;
.import --skip 1 base_final_com_metrica.csv base_final_metrica

CREATE INDEX IF NOT EXISTS idx_base_final_sk
ON base_final_metrica (SK_ID_CURR);

-- Conferências básicas
SELECT COUNT(*) AS total_registros FROM base_final_metrica;
SELECT TARGET, COUNT(*) AS quantidade FROM base_final_metrica GROUP BY TARGET;
SELECT CLASSE_METRICA, COUNT(*) AS quantidade FROM base_final_metrica GROUP BY CLASSE_METRICA;

-- Exemplos de consulta
SELECT *
FROM base_final_metrica
LIMIT 10;

SELECT TARGET,
       ROUND(AVG(METRICA_RISCO_0_100), 2) AS media_metrica_risco
FROM base_final_metrica
GROUP BY TARGET;
