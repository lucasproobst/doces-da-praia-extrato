# -*- coding: utf-8 -*-
"""
Robô de digitação (RPA) para lançar os PIX no Telecon.

Como o Telecon só aceita digitação manual, este módulo SIMULA o teclado:
para cada PIX, ele preenche os campos da tela de "novo lançamento" seguindo a
sequência definida em config.TELECON_SEQUENCIA.

SEGURANÇA:
  - Há uma contagem regressiva antes de começar (tempo de clicar no Telecon).
  - "Botão de pânico": jogue o mouse para o CANTO SUPERIOR ESQUERDO da tela
    para abortar na hora (recurso FAILSAFE do pyautogui).
  - Sempre teste com 1 lançamento antes de soltar a lista inteira.

Observação: as bibliotecas pyautogui/pyperclip são importadas só quando o robô
é usado, para não atrasar a abertura do programa.
"""

import re
import time

from .config import (
    TELECON_FORMATO_VALOR,
    TELECON_METODO,
    TELECON_PAUSA_ENTRE_ACOES,
    TELECON_PAUSA_ENTRE_LANCAMENTOS,
    TELECON_PAUSA_TECLA,
    TELECON_SEQUENCIA,
)
from .registro import log
from .valores import formatar_numero_br

_DATA_RE = re.compile(r"\b(\d{2}/\d{2}/\d{2,4})\b")


class RoboIndisponivelError(Exception):
    """Disparado quando o pyautogui/pyperclip não estão instalados."""


def _carregar_libs():
    """Importa pyautogui e pyperclip (com mensagem amigável se faltarem)."""
    try:
        import pyautogui
        import pyperclip
    except Exception as erro:  # ImportError ou erro de display
        raise RoboIndisponivelError(
            "As bibliotecas de automação não estão disponíveis.\n"
            "Rode novamente o INSTALAR.bat para instalar as dependências."
        ) from erro
    pyautogui.FAILSAFE = True   # mouse no canto superior esquerdo = abortar
    pyautogui.PAUSE = 0          # controlamos as pausas manualmente
    return pyautogui, pyperclip


# ---------------------------------------------------------------------------
# Conversões de cada campo em texto
# ---------------------------------------------------------------------------
def _formatar_valor(valor):
    if TELECON_FORMATO_VALOR == "1.234,56":
        return formatar_numero_br(valor)               # 1.234,56
    if TELECON_FORMATO_VALOR == "1234.56":
        return f"{valor:.2f}"                            # 1234.56
    return formatar_numero_br(valor).replace(".", "")   # 1234,56 (sem milhar)


def _extrair_data(descricao):
    achado = _DATA_RE.search(descricao or "")
    return achado.group(1) if achado else ""


def _texto_do_campo(qual, transacao):
    if qual == "valor":
        return _formatar_valor(transacao.valor)
    if qual == "descricao":
        return str(transacao.descricao)
    if qual == "data":
        return _extrair_data(transacao.descricao)
    return ""


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------
def _escrever(pyautogui, pyperclip, texto):
    """Escreve um texto no campo atual (por colar ou digitar)."""
    if not texto:
        return
    if TELECON_METODO == "digitar":
        pyautogui.write(texto, interval=TELECON_PAUSA_TECLA)
    else:  # "colar" (padrão): rápido e aceita acentos
        pyperclip.copy(texto)
        pyautogui.hotkey("ctrl", "v")


def _executar_acao(pyautogui, pyperclip, acao, transacao):
    tipo, valor = acao
    if tipo == "campo":
        _escrever(pyautogui, pyperclip, _texto_do_campo(valor, transacao))
    elif tipo == "texto":
        _escrever(pyautogui, pyperclip, str(valor))
    elif tipo == "tecla":
        pyautogui.press(str(valor).lower())
    elif tipo == "esperar":
        time.sleep(float(valor))
    else:
        log.warning("Ação desconhecida na sequência do Telecon: %r", acao)


def lancar_um(transacao):
    """Lança UMA transação (assume que o Telecon já está na tela certa)."""
    pyautogui, pyperclip = _carregar_libs()
    for acao in TELECON_SEQUENCIA:
        _executar_acao(pyautogui, pyperclip, acao, transacao)
        if TELECON_PAUSA_ENTRE_ACOES:
            time.sleep(TELECON_PAUSA_ENTRE_ACOES)


def lancar_varios(transacoes, parar_evento=None, ao_progredir=None):
    """Lança uma lista de transações, uma após a outra.

    parar_evento : threading.Event opcional; se .is_set(), interrompe.
    ao_progredir : função opcional chamada como ao_progredir(indice, total).
    Retorna a quantidade efetivamente lançada.
    """
    pyautogui, pyperclip = _carregar_libs()
    total = len(transacoes)
    feitos = 0
    try:
        for indice, transacao in enumerate(transacoes, start=1):
            if parar_evento is not None and parar_evento.is_set():
                log.info("Lançamento interrompido pelo usuário em %d/%d.", feitos, total)
                break
            for acao in TELECON_SEQUENCIA:
                _executar_acao(pyautogui, pyperclip, acao, transacao)
                if TELECON_PAUSA_ENTRE_ACOES:
                    time.sleep(TELECON_PAUSA_ENTRE_ACOES)
            feitos += 1
            if ao_progredir is not None:
                ao_progredir(indice, total)
            if TELECON_PAUSA_ENTRE_LANCAMENTOS:
                time.sleep(TELECON_PAUSA_ENTRE_LANCAMENTOS)
    except Exception:
        # FailSafe (mouse no canto) cai aqui também — abortar é esperado.
        log.exception("Lançamento automático interrompido (erro ou botão de pânico).")
    log.info("Lançados %d de %d no Telecon.", feitos, total)
    return feitos
