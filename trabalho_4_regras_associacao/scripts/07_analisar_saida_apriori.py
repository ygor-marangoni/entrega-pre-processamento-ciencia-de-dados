"""Converte saídas textuais reais do Apriori/WEKA em tabelas auditáveis.

O WEKA 3.8.7 não exporta CSV de regras. Este script preserva os textos de
origem e extrai apenas as informações apresentadas neles, sem calcular métricas
novas. O campo ``suporte`` é relativo, obtido pela divisão do suporte absoluto
mostrado pelo WEKA pelo total de transações informado na linha de comando.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ITEM_RE = re.compile(r"([A-Z][A-Z0-9_]*__[A-Z0-9_]+)=1")
RULE_RE = re.compile(r"^\s*(\d+)\.\s+(.*?)\s+==>\s+(.*?)\s*$")
SUPPORT_RE = re.compile(r"\s(\d+)\s+conf:\(")
CONF_RE = re.compile(r"conf:\(([^)]+)\)")
LIFT_RE = re.compile(r"lift:\(([^)]+)\)")
LEVERAGE_RE = re.compile(r"lev:\(([^)]+)\)")
CONVICTION_RE = re.compile(r"conv:\(([^)]+)\)")
ITEMSET_SUPPORT_RE = re.compile(r"\s(\d+)\s*$")


def normalizar_numero(valor: str) -> str:
    """Mantém a métrica textual do WEKA, normalizando somente vírgula decimal."""
    return valor.strip().replace(",", ".")


def extrair_itens(texto: str) -> list[str]:
    return ITEM_RE.findall(texto)


def ler_regras(caminho: Path, total_transacoes: int) -> list[dict[str, object]]:
    """Extrai as linhas numeradas após ``Best rules found``."""
    regras: list[dict[str, object]] = []
    em_regras = False

    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if linha.strip() == "Best rules found:":
            em_regras = True
            continue
        if not em_regras:
            continue

        correspondencia = RULE_RE.match(linha)
        if not correspondencia:
            continue

        id_regra, lado_esquerdo, lado_direito = correspondencia.groups()
        itens_antecedente = extrair_itens(lado_esquerdo)
        itens_consequente = extrair_itens(lado_direito)
        suporte_match = SUPPORT_RE.search(lado_direito)
        conf_match = CONF_RE.search(lado_direito)
        lift_match = LIFT_RE.search(lado_direito)
        leverage_match = LEVERAGE_RE.search(lado_direito)
        conviction_match = CONVICTION_RE.search(lado_direito)

        if not itens_antecedente or not itens_consequente or not suporte_match:
            raise ValueError(f"Regra não interpretável na saída do WEKA: {linha}")
        if not all((conf_match, lift_match, leverage_match, conviction_match)):
            raise ValueError(f"Métrica ausente na saída do WEKA: {linha}")

        suporte_absoluto = int(suporte_match.group(1))
        regras.append(
            {
                "id_regra": int(id_regra),
                "antecedente": " + ".join(itens_antecedente),
                "consequente": " + ".join(itens_consequente),
                "itens_antecedente": len(itens_antecedente),
                "itens_consequente": len(itens_consequente),
                "total_itens": len(itens_antecedente) + len(itens_consequente),
                "suporte": f"{suporte_absoluto / total_transacoes:.6f}",
                "confianca": normalizar_numero(conf_match.group(1)),
                "lift": normalizar_numero(lift_match.group(1)),
                "leverage": normalizar_numero(leverage_match.group(1)),
                "conviction": normalizar_numero(conviction_match.group(1)),
            }
        )

    if not regras:
        raise ValueError(f"Nenhuma regra foi encontrada em {caminho}")
    return regras


def ler_itemsets(caminho: Path, total_transacoes: int) -> list[dict[str, object]]:
    """Extrai os itemsets listados em cada seção ``Large Itemsets L(k)``."""
    itemsets: list[dict[str, object]] = []
    em_itemsets = False

    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if re.match(r"^Large Itemsets L\(\d+\):$", linha.strip()):
            em_itemsets = True
            continue
        if linha.strip().startswith("Size of set of large itemsets"):
            em_itemsets = False
            continue
        if not em_itemsets:
            continue

        itens = extrair_itens(linha)
        suporte_match = ITEMSET_SUPPORT_RE.search(linha)
        if not itens or not suporte_match:
            continue

        suporte_absoluto = int(suporte_match.group(1))
        itemsets.append(
            {
                "itemset": " + ".join(itens),
                "tamanho": len(itens),
                "suporte_absoluto": suporte_absoluto,
                "suporte_relativo": f"{suporte_absoluto / total_transacoes:.6f}",
            }
        )

    if not itemsets:
        raise ValueError(f"Nenhum itemset foi encontrado em {caminho}")
    if len({registro['itemset'] for registro in itemsets}) != len(itemsets):
        raise ValueError("Foram encontrados itemsets duplicados na saída do WEKA.")
    return itemsets


def escrever_csv(caminho: Path, registros: list[dict[str, object]], campos: list[str]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, delimiter=";")
        escritor.writeheader()
        escritor.writerows(registros)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resultado", type=Path, required=True)
    parser.add_argument("--itemsets", type=Path)
    parser.add_argument("--saida-regras", type=Path, required=True)
    parser.add_argument("--saida-itemsets", type=Path)
    parser.add_argument("--total-transacoes", type=int, required=True)
    args = parser.parse_args()

    if args.total_transacoes <= 0:
        raise ValueError("O total de transações deve ser positivo.")
    if bool(args.itemsets) != bool(args.saida_itemsets):
        raise ValueError("Informe --itemsets e --saida-itemsets juntos, ou nenhum deles.")

    regras = ler_regras(args.resultado, args.total_transacoes)
    campos_regras = [
        "id_regra", "antecedente", "consequente", "itens_antecedente",
        "itens_consequente", "total_itens", "suporte", "confianca", "lift",
        "leverage", "conviction",
    ]
    escrever_csv(args.saida_regras, regras, campos_regras)

    quantidade_itemsets = 0
    if args.itemsets and args.saida_itemsets:
        itemsets = ler_itemsets(args.itemsets, args.total_transacoes)
        escrever_csv(
            args.saida_itemsets,
            itemsets,
            ["itemset", "tamanho", "suporte_absoluto", "suporte_relativo"],
        )
        quantidade_itemsets = len(itemsets)

    tamanhos = {}
    for regra in regras:
        tamanho = int(regra["total_itens"])
        tamanhos[tamanho] = tamanhos.get(tamanho, 0) + 1
    print(f"REGRAS={len(regras)}")
    print(f"DISTRIBUICAO_TAMANHOS={dict(sorted(tamanhos.items()))}")
    if args.itemsets:
        print(f"ITEMSETS={quantidade_itemsets}")


if __name__ == "__main__":
    main()
