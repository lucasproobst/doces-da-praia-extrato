# -*- coding: utf-8 -*-
"""
Leitura dos arquivos de extrato.

Cada formato (PDF, CSV, XLSX/XLS, TXT) é convertido para uma LISTA DE LINHAS
de texto. A partir daí, todo o resto do programa trabalha igual,
independentemente do formato original. Isso deixa o parser modular: para dar
suporte a um novo formato, basta criar uma função "_ler_xxx" e registrá-la em
LEITORES_POR_EXTENSAO.
"""

import math
import os

from .valores import formatar_numero_br


# ---------------------------------------------------------------------------
# Função pública: descobre o formato pela extensão e chama o leitor certo.
# ---------------------------------------------------------------------------
def ler_arquivo(caminho):
    """Lê o arquivo e devolve uma lista de linhas de texto (uma por registro)."""
    extensao = os.path.splitext(caminho)[1].lower()
    leitor = LEITORES_POR_EXTENSAO.get(extensao)
    if leitor is None:
        raise ValueError(
            f"Formato não suportado: '{extensao}'.\n"
            "Formatos aceitos: PDF, CSV, XLSX, XLS e TXT."
        )
    return leitor(caminho)


# ---------------------------------------------------------------------------
# Leitor de PDF (usa pdfplumber)
# ---------------------------------------------------------------------------
def _ler_pdf(caminho):
    import pdfplumber  # importado aqui para o programa abrir rápido

    linhas = []
    with pdfplumber.open(caminho) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text() or ""
            linhas.extend(texto.splitlines())
    return linhas


# ---------------------------------------------------------------------------
# Leitor de TXT (texto puro)
# ---------------------------------------------------------------------------
def _ler_txt(caminho):
    # Bancos brasileiros costumam usar utf-8 ou latin-1; tentamos em ordem.
    for codificacao in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with open(caminho, "r", encoding=codificacao) as arquivo:
                return arquivo.read().splitlines()
        except UnicodeDecodeError:
            continue
    # Último recurso: ignora caracteres problemáticos.
    with open(caminho, "r", encoding="latin-1", errors="ignore") as arquivo:
        return arquivo.read().splitlines()


# ---------------------------------------------------------------------------
# Leitor de CSV (usa pandas)
# ---------------------------------------------------------------------------
def _ler_csv(caminho):
    import pandas as pd

    # dtype=str  -> preserva valores como "1.234,56" exatamente como estão.
    # sep=None   -> detecta automaticamente se o separador é ';' ou ','.
    # header=None-> trata TODAS as linhas como dados (não perde a 1ª linha).
    for codificacao in ("utf-8-sig", "latin-1"):
        try:
            df = pd.read_csv(
                caminho,
                dtype=str,
                sep=None,
                engine="python",
                header=None,
                keep_default_na=False,
                encoding=codificacao,
            )
            return _dataframe_para_linhas(df)
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    # Se o pandas falhar por qualquer motivo, lê como texto puro.
    return _ler_txt(caminho)


# ---------------------------------------------------------------------------
# Leitor de Excel XLSX/XLS (usa pandas + openpyxl/xlrd)
# ---------------------------------------------------------------------------
def _ler_excel(caminho):
    import pandas as pd

    extensao = os.path.splitext(caminho)[1].lower()
    # .xlsx -> openpyxl   |   .xls -> xlrd (pandas escolhe sozinho com None)
    motor = "openpyxl" if extensao == ".xlsx" else None

    linhas = []
    # sheet_name=None lê TODAS as abas/planilhas do arquivo.
    planilhas = pd.read_excel(caminho, sheet_name=None, header=None, engine=motor)
    for _nome_aba, df in planilhas.items():
        linhas.extend(_dataframe_para_linhas(df))
    return linhas


# ---------------------------------------------------------------------------
# Auxiliares para planilhas (CSV/Excel)
# ---------------------------------------------------------------------------
def _dataframe_para_linhas(df):
    """Transforma cada LINHA da planilha em uma string única.

    As células são unidas por espaço. Números são formatados no padrão BR
    (1.234,56) para que o reconhecedor de valores funcione igual ao do PDF/TXT.
    """
    linhas = []
    for _indice, linha in df.iterrows():
        celulas = [_celula_para_texto(valor) for valor in linha.tolist()]
        texto = " ".join(parte for parte in celulas if parte)
        if texto.strip():
            linhas.append(texto)
    return linhas


def _celula_para_texto(valor):
    """Converte uma célula da planilha em texto, formatando números em BR."""
    if valor is None:
        return ""

    # Números (vindos do Excel) viram "1.234,56" para casar com o padrão BR.
    if isinstance(valor, bool):
        return ""  # ignora células booleanas (não são valores monetários)
    if isinstance(valor, float):
        if math.isnan(valor):
            return ""
        return formatar_numero_br(valor)
    if isinstance(valor, int):
        return formatar_numero_br(float(valor))

    return str(valor).strip()


# ---------------------------------------------------------------------------
# Mapa: extensão -> função leitora.
# Para suportar um novo formato, crie a função e registre-a aqui.
# ---------------------------------------------------------------------------
LEITORES_POR_EXTENSAO = {
    ".pdf": _ler_pdf,
    ".txt": _ler_txt,
    ".csv": _ler_csv,
    ".xlsx": _ler_excel,
    ".xls": _ler_excel,
}


def formatos_suportados():
    """Lista de extensões aceitas (usada na janela de seleção de arquivo)."""
    return sorted(LEITORES_POR_EXTENSAO.keys())
