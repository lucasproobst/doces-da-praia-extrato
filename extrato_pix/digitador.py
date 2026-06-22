# -*- coding: utf-8 -*-
"""
Robô de digitação (RPA) para lançar os PIX no Telecon.

O Telecon, para cada PIX, exige: clicar no ícone de flechas -> digitar a data ->
conta BANRISUL -> digitar o valor -> Gravar (a tela fecha e repete). Como há
CLIQUES em ícones, o robô usa "pontos calibrados": o usuário ensina uma vez onde
fica cada ponto (passando o mouse e apertando ESPAÇO), e o robô repete sozinho a
MACRO (config.TELECON_MACRO) para cada transação.

SEGURANÇA:
  - Contagem regressiva antes de começar.
  - "Botão de pânico": mouse no CANTO SUPERIOR ESQUERDO aborta na hora (FAILSAFE).
  - Teste sempre com 1 lançamento antes de soltar a lista inteira.

As libs pyautogui/pyperclip são importadas só quando o robô é usado.
"""

import json
import os
import re
import time
from datetime import datetime, timedelta

from .config import (
    TELECON_DATA_BASE,
    TELECON_DATA_MODO,
    TELECON_PAUSA_DATA,
    TELECON_FORMATO_VALOR,
    TELECON_MACRO,
    TELECON_METODO,
    TELECON_PAUSA_ENTRE_ACOES,
    TELECON_PAUSA_ENTRE_LANCAMENTOS,
    TELECON_PAUSA_TECLA,
    TELECON_PONTOS,
)
from .registro import log, pasta_dados
from .valores import formatar_numero_br

_DATA_RE = re.compile(r"\b(\d{2}/\d{2}/\d{2,4})\b")


class RoboIndisponivelError(Exception):
    """Disparado quando o pyautogui/pyperclip não estão instalados."""


def _carregar_libs():
    """Importa pyautogui e pyperclip (com mensagem amigável se faltarem)."""
    try:
        import pyautogui
        import pyperclip
    except Exception as erro:
        raise RoboIndisponivelError(
            "As bibliotecas de automação não estão disponíveis.\n"
            "Rode novamente o INSTALAR.bat para instalar as dependências."
        ) from erro
    pyautogui.FAILSAFE = True   # mouse no canto superior esquerdo = abortar
    pyautogui.PAUSE = 0
    return pyautogui, pyperclip


# ---------------------------------------------------------------------------
# Pontos calibrados (posições da tela), salvos entre sessões
# ---------------------------------------------------------------------------
def _arquivo_pontos():
    return os.path.join(pasta_dados(), "telecon_pontos.json")


def carregar_pontos():
    try:
        with open(_arquivo_pontos(), encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        # chaves -> tuplas (x, y)
        return {nome: tuple(pos) for nome, pos in dados.items()}
    except Exception:
        return {}


def salvar_ponto(nome, x, y):
    pontos = carregar_pontos()
    pontos[nome] = [int(x), int(y)]
    try:
        with open(_arquivo_pontos(), "w", encoding="utf-8") as arquivo:
            json.dump(pontos, arquivo)
        log.info("Ponto do Telecon calibrado: %s = (%d, %d)", nome, x, y)
    except Exception:
        log.exception("Não foi possível salvar o ponto calibrado")


def pontos_faltando():
    """Nomes de TELECON_PONTOS que ainda não foram calibrados."""
    pontos = carregar_pontos()
    return [nome for nome in TELECON_PONTOS if nome not in pontos]


def posicao_atual_do_mouse():
    """Posição atual do mouse (usada na calibração)."""
    pyautogui, _ = _carregar_libs()
    x, y = pyautogui.position()
    return int(x), int(y)


# ---------------------------------------------------------------------------
# Conversão dos campos do PIX em texto
# ---------------------------------------------------------------------------
def _formatar_valor(valor):
    if TELECON_FORMATO_VALOR == "1.234,56":
        return formatar_numero_br(valor)
    if TELECON_FORMATO_VALOR == "1234.56":
        return f"{valor:.2f}"
    return formatar_numero_br(valor).replace(".", "")   # 1234,56


def _extrair_data(descricao):
    achado = _DATA_RE.search(descricao or "")
    return achado.group(1) if achado else ""


def _data_anterior_digitos(descricao):
    """Data a ser digitada (sempre 1 dia ANTES), só com dígitos (ddmmaaaa).

    Conforme config.TELECON_DATA_BASE:
      "hoje"    -> data de hoje menos 1 dia (padrão)
      "extrato" -> data da linha do extrato menos 1 dia
    Ex.: hoje 22/06/2026 -> '21062026'.
    """
    if TELECON_DATA_BASE == "extrato":
        texto = _extrair_data(descricao)
        if not texto:
            return ""
        base = None
        for formato in ("%d/%m/%Y", "%d/%m/%y"):
            try:
                base = datetime.strptime(texto, formato)
                break
            except ValueError:
                continue
        if base is None:
            return ""
    else:  # "hoje" (padrão)
        base = datetime.now()
    return (base - timedelta(days=1)).strftime("%d%m%Y")


def _texto_do_campo(qual, transacao):
    if qual == "valor":
        return _formatar_valor(transacao.valor)
    if qual == "descricao":
        return str(transacao.descricao)
    if qual == "data":
        return _extrair_data(transacao.descricao)
    return ""


# ---------------------------------------------------------------------------
# Execução das ações
# ---------------------------------------------------------------------------
def _escrever(pyautogui, pyperclip, texto):
    if not texto:
        return
    if TELECON_METODO == "digitar":
        pyautogui.write(texto, interval=TELECON_PAUSA_TECLA)
    else:
        pyperclip.copy(texto)
        pyautogui.hotkey("ctrl", "v")


def _exigir_ponto(pontos, nome):
    ponto = pontos.get(nome)
    if not ponto:
        raise RoboIndisponivelError(
            f"O ponto '{nome}' ainda não foi calibrado. Use 'Calibrar' antes de lançar."
        )
    return ponto


def _executar_acao(pyautogui, pyperclip, pontos, acao, transacao):
    tipo, valor = acao
    if tipo == "campo":
        _escrever(pyautogui, pyperclip, _texto_do_campo(valor, transacao))
    elif tipo == "texto":
        _escrever(pyautogui, pyperclip, str(valor))
    elif tipo == "tecla":
        pyautogui.press(str(valor).lower())
    elif tipo == "hotkey":
        teclas = [t.strip().lower() for t in str(valor).replace("+", ",").split(",") if t.strip()]
        if teclas:
            pyautogui.hotkey(*teclas)
    elif tipo == "data_anterior":
        digitos = _data_anterior_digitos(transacao.descricao)
        if digitos and TELECON_DATA_MODO == "dia":
            digitos = digitos[:2]   # só o DIA (mês/ano ficam como estão)
        if digitos:
            # digita número por número, devagar, para o campo não se perder
            for caractere in digitos:
                pyautogui.press(caractere)
                time.sleep(TELECON_PAUSA_DATA)
    elif tipo == "clicar":
        ponto = _exigir_ponto(pontos, valor)
        pyautogui.click(ponto[0], ponto[1])
    elif tipo == "duplo_clicar":
        ponto = _exigir_ponto(pontos, valor)
        pyautogui.doubleClick(ponto[0], ponto[1])
    elif tipo == "scroll":
        pyautogui.scroll(int(valor))
    elif tipo == "esperar":
        time.sleep(float(valor))
    else:
        log.warning("Ação desconhecida na macro do Telecon: %r", acao)


def lancar_varios(transacoes, parar_evento=None, ao_progredir=None):
    """Lança uma lista de transações repetindo a MACRO para cada uma.

    parar_evento : threading.Event opcional; se .is_set(), interrompe.
    ao_progredir : função opcional chamada como ao_progredir(indice, total).
    Retorna a quantidade efetivamente lançada.
    """
    pyautogui, pyperclip = _carregar_libs()
    pontos = carregar_pontos()
    total = len(transacoes)
    feitos = 0
    try:
        for indice, transacao in enumerate(transacoes, start=1):
            if parar_evento is not None and parar_evento.is_set():
                log.info("Lançamento interrompido pelo usuário em %d/%d.", feitos, total)
                break
            for acao in TELECON_MACRO:
                _executar_acao(pyautogui, pyperclip, pontos, acao, transacao)
                if TELECON_PAUSA_ENTRE_ACOES:
                    time.sleep(TELECON_PAUSA_ENTRE_ACOES)
            feitos += 1
            if ao_progredir is not None:
                ao_progredir(indice, total)
            if TELECON_PAUSA_ENTRE_LANCAMENTOS:
                time.sleep(TELECON_PAUSA_ENTRE_LANCAMENTOS)
    except RoboIndisponivelError:
        raise
    except Exception:
        # FailSafe (mouse no canto) também cai aqui — abortar é esperado.
        log.exception("Lançamento automático interrompido (erro ou botão de pânico).")
    log.info("Lançados %d de %d no Telecon.", feitos, total)
    return feitos
