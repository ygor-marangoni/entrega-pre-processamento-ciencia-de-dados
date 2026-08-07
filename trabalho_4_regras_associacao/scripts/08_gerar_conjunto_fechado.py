"""Gera itemsets fechados e associa regras aos respectivos itemsets.

Definição aplicada: um itemset X é fechado quando não existe superconjunto
próprio Y com support(X) = support(Y). As comparações usam o suporte absoluto
extraído da saída real do WEKA para evitar diferenças de arredondamento.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


SEPARADOR_ITENS = " + "


@dataclass(frozen=True)
class Itemset:
    texto: str
    itens: frozenset[str]
    tamanho: int
    suporte_absoluto: int
    suporte_relativo: str


def abrir_csv(caminho: Path) -> list[dict[str, str]]:
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo, delimiter=";"))


def escrever_csv(caminho: Path, campos: list[str], linhas: list[dict[str, object]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, delimiter=";")
        escritor.writeheader()
        escritor.writerows(linhas)


def converter_itemsets(caminho: Path) -> list[Itemset]:
    registros: list[Itemset] = []
    vistos: set[frozenset[str]] = set()
    for linha in abrir_csv(caminho):
        itens = frozenset(linha["itemset"].split(SEPARADOR_ITENS))
        tamanho = int(linha["tamanho"])
        if len(itens) != tamanho:
            raise ValueError(f"Tamanho inconsistente no itemset: {linha['itemset']}")
        if itens in vistos:
            raise ValueError(f"Itemset duplicado: {linha['itemset']}")
        vistos.add(itens)
        registros.append(
            Itemset(
                texto=linha["itemset"],
                itens=itens,
                tamanho=tamanho,
                suporte_absoluto=int(linha["suporte_absoluto"]),
                suporte_relativo=linha["suporte_relativo"],
            )
        )
    if not registros:
        raise ValueError("A entrada não possui itemsets.")
    return registros


def identificar_fechados(itemsets: list[Itemset]) -> tuple[list[dict[str, object]], dict[frozenset[str], Itemset]]:
    """Compara somente itemsets com o mesmo suporte absoluto."""
    por_suporte: dict[int, list[Itemset]] = defaultdict(list)
    for itemset in itemsets:
        por_suporte[itemset.suporte_absoluto].append(itemset)

    auditoria: list[dict[str, object]] = []
    por_itens = {itemset.itens: itemset for itemset in itemsets}

    for suporte, grupo in sorted(por_suporte.items()):
        ordenados = sorted(grupo, key=lambda item: (item.tamanho, item.texto))
        for indice, itemset in enumerate(ordenados):
            testemunha = next(
                (
                    candidato
                    for candidato in ordenados[indice + 1 :]
                    if itemset.tamanho < candidato.tamanho
                    and itemset.itens < candidato.itens
                ),
                None,
            )
            fechado = testemunha is None
            auditoria.append(
                {
                    "itemset": itemset.texto,
                    "tamanho": itemset.tamanho,
                    "suporte_absoluto": suporte,
                    "suporte_relativo": itemset.suporte_relativo,
                    "fechado": "SIM" if fechado else "NAO",
                    "superconjunto_mesmo_suporte": "" if fechado else testemunha.texto,
                    "motivo": (
                        "Nenhum superconjunto próprio possui o mesmo suporte."
                        if fechado
                        else "Existe superconjunto próprio com o mesmo suporte."
                    ),
                }
            )
    return auditoria, por_itens


def itens_da_regra(regra: dict[str, str]) -> frozenset[str]:
    partes = regra["antecedente"].split(SEPARADOR_ITENS) + regra["consequente"].split(SEPARADOR_ITENS)
    itens = frozenset(partes)
    if len(itens) != int(regra["total_itens"]):
        raise ValueError(f"Regra com itens repetidos ou tamanho inconsistente: {regra['id_regra']}")
    return itens


def regras_fechadas(caminho: Path, por_itens: dict[frozenset[str], Itemset], auditoria: dict[frozenset[str], dict[str, object]]) -> tuple[list[dict[str, object]], int]:
    saida: list[dict[str, object]] = []
    total = 0
    for regra in abrir_csv(caminho):
        total += 1
        itens = itens_da_regra(regra)
        itemset = por_itens.get(itens)
        estado = auditoria.get(itens)
        if itemset is None or estado is None or estado["fechado"] != "SIM":
            continue
        saida.append(
            {
                **regra,
                "itemset_uniao": itemset.texto,
                "suporte_itemset_absoluto": itemset.suporte_absoluto,
                "suporte_itemset_relativo": itemset.suporte_relativo,
            }
        )
    return saida, total


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--itemsets", type=Path, required=True)
    parser.add_argument("--regras-finais", type=Path, required=True)
    parser.add_argument("--regras-exploratorias", type=Path, required=True)
    parser.add_argument("--saida-diretorio", type=Path, required=True)
    args = parser.parse_args()

    itemsets = converter_itemsets(args.itemsets)
    auditoria_linhas, por_itens = identificar_fechados(itemsets)
    auditoria_por_itens = {
        frozenset(linha["itemset"].split(SEPARADOR_ITENS)): linha
        for linha in auditoria_linhas
    }

    campos_auditoria = [
        "itemset", "tamanho", "suporte_absoluto", "suporte_relativo", "fechado",
        "superconjunto_mesmo_suporte", "motivo",
    ]
    fechados = [linha for linha in auditoria_linhas if linha["fechado"] == "SIM"]
    nao_fechados = [linha for linha in auditoria_linhas if linha["fechado"] == "NAO"]
    escrever_csv(args.saida_diretorio / "itemsets_fechados.csv", campos_auditoria, fechados)
    escrever_csv(args.saida_diretorio / "itemsets_nao_fechados.csv", campos_auditoria, nao_fechados)
    escrever_csv(args.saida_diretorio / "auditoria_fechamento.csv", campos_auditoria, auditoria_linhas)

    campos_regras = [
        "id_regra", "antecedente", "consequente", "itens_antecedente",
        "itens_consequente", "total_itens", "suporte", "confianca", "lift",
        "leverage", "conviction", "itemset_uniao", "suporte_itemset_absoluto",
        "suporte_itemset_relativo",
    ]
    regras_finais, total_finais = regras_fechadas(
        args.regras_finais, por_itens, auditoria_por_itens
    )
    regras_exploratorias, total_exploratorias = regras_fechadas(
        args.regras_exploratorias, por_itens, auditoria_por_itens
    )
    escrever_csv(args.saida_diretorio / "regras_conjunto_fechado.csv", campos_regras, regras_finais)
    escrever_csv(
        args.saida_diretorio / "regras_exploratorias_conjunto_fechado.csv",
        campos_regras,
        regras_exploratorias,
    )

    print(f"ITEMSETS_ANTES={len(itemsets)}")
    print(f"ITEMSETS_FECHADOS={len(fechados)}")
    print(f"ITEMSETS_NAO_FECHADOS={len(nao_fechados)}")
    print(f"REGRAS_FINAIS_FECHADAS={len(regras_finais)}/{total_finais}")
    print(f"REGRAS_EXPLORATORIAS_FECHADAS={len(regras_exploratorias)}/{total_exploratorias}")


if __name__ == "__main__":
    main()
