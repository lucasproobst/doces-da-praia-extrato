# -*- coding: utf-8 -*-
"""
Registro de eventos e erros (arquivo de log).

Sempre que o programa abrir, processar um arquivo ou der algum erro, ele anota
o que aconteceu em um arquivo de texto. Assim, se algo der errado (inclusive na
hora de instalar/abrir), dá para abrir esse log e ver o motivo.

Local do log:
    Windows : C:\\Users\\SEU_USUARIO\\AppData\\Local\\DocesDaPraia\\doces_da_praia.log
    Outros  : ~/DocesDaPraia/doces_da_praia.log
"""

import logging
import os
import sys


def pasta_dados():
    """Pasta (gravável) onde guardamos o log e configurações do usuário."""
    base = os.environ.get("LOCALAPPDATA") if os.name == "nt" else None
    base = base or os.path.expanduser("~")
    pasta = os.path.join(base, "DocesDaPraia")
    try:
        os.makedirs(pasta, exist_ok=True)
    except Exception:
        # Se não conseguir criar (ex.: permissão), usa a pasta atual.
        pasta = os.path.abspath(".")
    return pasta


CAMINHO_LOG = os.path.join(pasta_dados(), "doces_da_praia.log")

# Logger usado em todo o programa.
log = logging.getLogger("doces_da_praia")

_configurado = False


def configurar():
    """Liga a gravação do log em arquivo. Pode ser chamada várias vezes."""
    global _configurado
    if _configurado:
        return CAMINHO_LOG

    log.setLevel(logging.INFO)
    try:
        manipulador = logging.FileHandler(CAMINHO_LOG, encoding="utf-8")
        manipulador.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        log.addHandler(manipulador)
    except Exception:
        pass  # nunca deixar o log derrubar o programa

    # Registra também qualquer erro inesperado que não tenha sido tratado.
    def _capturar_erro(tipo, valor, tb):
        log.error("Erro nao tratado", exc_info=(tipo, valor, tb))
        sys.__excepthook__(tipo, valor, tb)

    sys.excepthook = _capturar_erro
    _configurado = True
    log.info("=== Log iniciado ===")
    return CAMINHO_LOG
