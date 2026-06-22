# -*- coding: utf-8 -*-
"""
Atualização automática via GitHub.

Como funciona:
  1. Ao abrir, o programa pergunta ao GitHub qual é o último "commit" (mudança)
     do repositório configurado em config.UPDATE_REPO.
  2. Se for diferente do que está instalado, baixa o código mais recente
     (um .zip do repositório) e substitui os arquivos locais.
  3. Se houver dependências novas, instala-as. Depois o programa reabre.

Observações:
  - Só funciona ao rodar "da fonte" (com Python). No .exe empacotado o código
    fica embutido e não dá para trocar os arquivos — nesse caso é ignorado.
  - Tudo é protegido: se estiver sem internet ou der qualquer erro, o programa
    simplesmente continua com a versão atual (nada trava).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

from .config import UPDATE_ATIVO, UPDATE_BRANCH, UPDATE_REPO
from .registro import log, pasta_dados

_API_COMMIT = "https://api.github.com/repos/{repo}/commits/{branch}"
_URL_ZIP = "https://codeload.github.com/{repo}/zip/refs/heads/{branch}"

# Arquivos da RAIZ do projeto que devem ser atualizados.
_ARQUIVOS_RAIZ = [
    "app.py",
    "make_icon.py",
    "requirements.txt",
    "installer.iss",
    "GERAR_INSTALADOR.bat",
    "INSTALAR.bat",
    "README.md",
]


def _rodando_empacotado():
    """True quando estamos dentro do .exe (PyInstaller)."""
    return getattr(sys, "frozen", False)


def _raiz_projeto():
    """Pasta onde ficam o app.py e o pacote extrato_pix/."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _arquivo_versao():
    return os.path.join(pasta_dados(), "versao_instalada.txt")


def _ler_versao_local():
    try:
        with open(_arquivo_versao(), encoding="utf-8") as arquivo:
            return arquivo.read().strip()
    except Exception:
        return ""


def _salvar_versao_local(sha):
    try:
        with open(_arquivo_versao(), "w", encoding="utf-8") as arquivo:
            arquivo.write(sha)
    except Exception:
        log.exception("Não foi possível salvar a versão instalada")


def _configurado():
    return bool(UPDATE_ATIVO and UPDATE_REPO and "/" in UPDATE_REPO)


def verificar(timeout=8):
    """Consulta o GitHub. Devolve o SHA do último commit se houver novidade;
    caso contrário (ou em erro/sem internet), devolve None."""
    if not _configurado() or _rodando_empacotado():
        return None
    try:
        url = _API_COMMIT.format(repo=UPDATE_REPO, branch=UPDATE_BRANCH)
        requisicao = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "DocesDaPraia-Updater",
            },
        )
        with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
            dados = json.load(resposta)
        sha = dados.get("sha", "")
        if sha and sha != _ler_versao_local():
            log.info("Atualização disponível (commit %s).", sha[:8])
            return sha
        return None
    except Exception:
        log.info("Verificação de atualização ignorada (sem internet ou erro).")
        return None


def aplicar(sha, timeout=60):
    """Baixa o código novo e substitui os arquivos locais. Devolve True se ok."""
    if not _configurado() or _rodando_empacotado():
        return False
    try:
        raiz = _raiz_projeto()
        requirements_antes = _ler_texto(os.path.join(raiz, "requirements.txt"))

        url = _URL_ZIP.format(repo=UPDATE_REPO, branch=UPDATE_BRANCH)
        with tempfile.TemporaryDirectory() as temporaria:
            caminho_zip = os.path.join(temporaria, "atualizacao.zip")
            requisicao = urllib.request.Request(
                url, headers={"User-Agent": "DocesDaPraia-Updater"}
            )
            with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
                with open(caminho_zip, "wb") as arquivo:
                    shutil.copyfileobj(resposta, arquivo)

            with zipfile.ZipFile(caminho_zip) as zip_arquivo:
                zip_arquivo.extractall(temporaria)

            # O zip do GitHub extrai para uma pasta tipo "repo-main/".
            pastas = [
                os.path.join(temporaria, item)
                for item in os.listdir(temporaria)
                if os.path.isdir(os.path.join(temporaria, item))
            ]
            if not pastas:
                return False
            origem = pastas[0]
            _copiar_codigo(origem, raiz)

        # Se as dependências mudaram, instala as novas.
        requirements_depois = _ler_texto(os.path.join(raiz, "requirements.txt"))
        if requirements_depois and requirements_depois != requirements_antes:
            _instalar_dependencias(raiz)

        _salvar_versao_local(sha)
        log.info("Atualização aplicada com sucesso (commit %s).", sha[:8])
        return True
    except Exception:
        log.exception("Falha ao aplicar a atualização")
        return False


def reiniciar():
    """Reabre o programa para passar a usar o código novo."""
    try:
        python = sys.executable
        script = os.path.join(_raiz_projeto(), "app.py")
        os.execv(python, [python, script])
    except Exception:
        log.exception("Não foi possível reiniciar automaticamente")


# ---------------------------------------------------------------------------
# Auxiliares internos
# ---------------------------------------------------------------------------
def _ler_texto(caminho):
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            return arquivo.read()
    except Exception:
        return ""


def _copiar_codigo(origem, destino):
    """Copia os arquivos de código do 'origem' (baixado) para o 'destino' (local)."""
    # Arquivos da raiz.
    for nome in _ARQUIVOS_RAIZ:
        caminho_origem = os.path.join(origem, nome)
        if os.path.exists(caminho_origem):
            # shutil.copy define a data de modificação para "agora", garantindo
            # que o Python recompile (não use cache antigo).
            shutil.copy(caminho_origem, os.path.join(destino, nome))

    # Pacote extrato_pix/ (apenas os .py).
    pacote_origem = os.path.join(origem, "extrato_pix")
    pacote_destino = os.path.join(destino, "extrato_pix")
    if os.path.isdir(pacote_origem):
        os.makedirs(pacote_destino, exist_ok=True)
        for nome in os.listdir(pacote_origem):
            if nome.endswith(".py"):
                shutil.copy(
                    os.path.join(pacote_origem, nome),
                    os.path.join(pacote_destino, nome),
                )

    # Remove caches antigos para forçar o uso do código novo.
    for pasta_cache in (
        os.path.join(destino, "__pycache__"),
        os.path.join(pacote_destino, "__pycache__"),
    ):
        shutil.rmtree(pasta_cache, ignore_errors=True)


def _instalar_dependencias(raiz):
    """Instala dependências novas, em segundo plano, sem abrir janela preta."""
    try:
        log.info("Instalando dependências novas após atualização...")
        criar_sem_janela = {}
        if os.name == "nt":
            criar_sem_janela["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r",
             os.path.join(raiz, "requirements.txt")],
            check=False,
            **criar_sem_janela,
        )
    except Exception:
        log.exception("Falha ao instalar dependências após atualização")
