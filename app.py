import json
import subprocess
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
RUN_SCRIPT = PROJECT_ROOT / "preprocessamento_credito.py"

REQUIRED_FILES = ["emprestimos.csv", "serasa.csv", "emprestimos_anteriores.csv"]

OUTPUT_FILES = [
    (
        "base_final_preprocessada.csv",
        "Base final pronta para modelagem, com campos selecionados, agregados e codificados.",
    ),
    (
        "base_final_com_metrica.csv",
        "Copia da base final com a metrica de risco e a classe da metrica.",
    ),
    (
        "dicionario_codificacao_categorias.csv",
        "Dicionario das categorias textuais convertidas em codigos numericos.",
    ),
    (
        "resumo_estatistico_preprocessamento.csv",
        "Resumo com linhas, desbalanceamento, ausentes e estatisticas da metrica.",
    ),
    (
        "resumo_processamento.json",
        "Resumo estruturado do processamento para consulta e auditoria.",
    ),
    (
        "preprocessamento_credito.db",
        "Banco SQLite com a tabela base_final_metrica.",
    ),
]


def format_file_size(size_bytes):
    units = ["B", "KB", "MB", "GB"]
    size = float(size_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024


def get_available_outputs(base_path):
    available = []
    for filename, description in OUTPUT_FILES:
        filepath = base_path / filename
        if filepath.exists():
            available.append((filepath, description))
    return available


def render_outputs(base_path):
    available = get_available_outputs(base_path)
    if not available:
        return

    st.subheader("Arquivos gerados")
    st.caption("Baixe os principais arquivos criados pelo pipeline.")

    for index in range(0, len(available), 2):
        cols = st.columns(2)
        for col, item in zip(cols, available[index:index + 2]):
            filepath, description = item
            with col:
                with st.container(border=True):
                    st.markdown(f"**{filepath.name}**")
                    st.caption(description)
                    st.caption(f"Tamanho: {format_file_size(filepath.stat().st_size)}")
                    st.download_button(
                        label="Baixar arquivo",
                        data=filepath.read_bytes(),
                        file_name=filepath.name,
                        mime="application/octet-stream",
                        use_container_width=True,
                        key=f"download-{filepath.name}",
                        on_click="ignore",
                    )

    summary_path = base_path / "resumo_processamento.json"
    if summary_path.exists():
        st.subheader("Resumo do processamento")
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        st.json(summary)


st.set_page_config(page_title="Pre-processamento Credito", layout="wide")

if "processed_base_dir" not in st.session_state:
    st.session_state.processed_base_dir = None
if "last_stdout" not in st.session_state:
    st.session_state.last_stdout = ""
if "last_stderr" not in st.session_state:
    st.session_state.last_stderr = ""

st.title("Pre-processamento de Credito")
st.write(
    "Execute o pre-processamento pela web, com saida dos CSVs finais, resumo estatistico e banco SQLite."
)

base_dir = st.text_input(
    "Pasta com os arquivos de entrada",
    value=str(PROJECT_ROOT).replace("\\", "/"),
    help="Informe a pasta contendo emprestimos.csv, serasa.csv e emprestimos_anteriores.csv.",
)

if st.button("Rodar processamento"):
    base_path = Path(base_dir).expanduser()
    missing = [name for name in REQUIRED_FILES if not (base_path / name).exists()]

    if missing:
        st.session_state.processed_base_dir = None
        st.error("Arquivos ausentes na pasta informada: " + ", ".join(missing))
    else:
        with st.spinner("Executando o pre-processamento..."):
            proc = subprocess.run(
                [sys.executable, str(RUN_SCRIPT), "--base-dir", str(base_path)],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
            )

        st.session_state.last_stdout = proc.stdout.strip()[-2000:]
        st.session_state.last_stderr = proc.stderr.strip()[-2000:]

        if proc.returncode == 0:
            st.session_state.processed_base_dir = str(base_path)
        else:
            st.session_state.processed_base_dir = None
            st.error("Falha ao executar o pre-processamento.")
            st.code(proc.stdout)
            st.code(proc.stderr)

if st.session_state.processed_base_dir:
    current_base_path = Path(st.session_state.processed_base_dir)
    st.success("Processamento concluido com sucesso.")
    if st.session_state.last_stdout:
        st.code(st.session_state.last_stdout)
    if st.session_state.last_stderr:
        st.warning(st.session_state.last_stderr)
    render_outputs(current_base_path)
