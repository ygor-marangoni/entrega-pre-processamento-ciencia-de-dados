#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Localiza Java e weka.jar para execucao real dos classificadores WEKA."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = TRABALHO_DIR.parent
CONFIG_PATH = TRABALHO_DIR / "weka_config.json"

COMMON_WEKA_PATHS = [
    Path(r"C:\Program Files\Weka-3-8-6\weka.jar"),
    Path(r"C:\Program Files\Weka-3-8-7\weka.jar"),
    Path(r"C:\Program Files\Weka-3-9\weka.jar"),
    Path(r"C:\Program Files\Weka-3-9-6\weka.jar"),
    Path(r"C:\Program Files\Weka-3-9-7\weka.jar"),
    Path(r"C:\Program Files (x86)\Weka-3-8-6\weka.jar"),
    Path(r"C:\Program Files (x86)\Weka-3-8-7\weka.jar"),
    Path(r"C:\Program Files (x86)\Weka-3-9\weka.jar"),
    Path(r"C:\Program Files (x86)\Weka-3-9-6\weka.jar"),
    Path(r"C:\Program Files (x86)\Weka-3-9-7\weka.jar"),
]


def run_command(command: list[str]) -> tuple[int, str]:
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return completed.returncode, (completed.stdout + completed.stderr).strip()


def get_java_version(java_cmd: str = "java") -> tuple[str, str]:
    code, output = run_command([java_cmd, "-version"])
    if code != 0 and not output:
        raise RuntimeError("Java nao esta acessivel pelo PATH. Verifique a instalacao e a variavel PATH.")
    first_line = output.splitlines()[0] if output else "Versao nao identificada"
    return first_line, output


def find_java_path() -> str:
    code, output = run_command(["where.exe", "java"])
    if code == 0 and output:
        return output.splitlines()[0].strip()
    return "java"


def find_weka_jar() -> Path | None:
    for path in COMMON_WEKA_PATHS:
        if path.exists():
            return path

    search_roots = [
        Path(r"C:\Program Files"),
        Path(r"C:\Program Files (x86)"),
        PROJECT_ROOT,
        Path.home() / "Downloads",
        Path.home(),
    ]
    for root in search_roots:
        if not root.exists():
            continue
        try:
            matches = list(root.rglob("weka.jar"))
        except (PermissionError, OSError):
            continue
        if matches:
            return matches[0]
    return None


def write_config(java_cmd: str, java_version: str, weka_jar: Path | None, max_memory: str = "8g") -> None:
    config = {
        "java_cmd": java_cmd,
        "java_version": java_version,
        "weka_jar": str(weka_jar).replace("\\", "/") if weka_jar else "",
        "max_memory": max_memory,
    }
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    java_path = find_java_path()
    try:
        java_version, full_version = get_java_version("java")
        java_cmd = "java"
    except RuntimeError:
        if java_path != "java":
            java_version, full_version = get_java_version(java_path)
            java_cmd = java_path
        else:
            raise

    weka_jar = find_weka_jar()
    write_config(java_cmd, java_version, weka_jar)

    print("Java encontrado.")
    print(f"Comando Java: {java_cmd}")
    print(f"Caminho Java: {java_path}")
    print("Versao Java:")
    print(full_version)

    if weka_jar:
        print(f"weka.jar encontrado: {weka_jar}")
    else:
        print("weka.jar nao foi encontrado automaticamente.")
        print("Instale o WEKA ou informe manualmente o caminho no pipeline:")
        print('python pipeline_trabalho_2.py --weka-jar "C:/Program Files/Weka-3-8-6/weka.jar" --max-memory 8g')

    print(f"Configuracao salva em: {CONFIG_PATH}")


if __name__ == "__main__":
    main()
