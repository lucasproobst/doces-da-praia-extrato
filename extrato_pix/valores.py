# -*- coding: utf-8 -*-
"""
Reconhecimento e formatação de valores monetários no padrão brasileiro.

Padrão BR:  ponto = milhar  |  vírgula = decimal
Exemplos:   1.234,56   |   R$ 1.234,56   |   1.000.000,00   |   12,00
"""

import re

from .config import REGEX_VALOR

# Compila a expressão regular uma única vez (mais rápido).
_PADRAO_VALOR = re.compile(REGEX_VALOR, re.IGNORECASE)


def texto_para_float(texto_valor):
    """Converte um valor em TEXTO (padrão BR) para número (float).

    Exemplos:
        "R$ 1.234,56" -> 1234.56
        "12,00"        -> 12.0
        "1.000.000,00" -> 1000000.0
    """
    # Mantém só dígitos, ponto, vírgula e sinal de menos.
    limpo = re.sub(r"[^\d.,-]", "", str(texto_valor))

    # Remove os pontos (milhar) e troca a vírgula decimal por ponto.
    limpo = limpo.replace(".", "").replace(",", ".")

    try:
        # abs(): tratamos como entrada (crédito), sempre positivo.
        return abs(float(limpo))
    except ValueError:
        return 0.0


def encontrar_valores(texto):
    """Devolve TODOS os valores monetários encontrados no texto, em ordem.

    Retorna uma lista de floats. Ex.: "PIX 1.234,56 saldo 10.000,00"
    -> [1234.56, 10000.0]
    """
    return [texto_para_float(m.group(0)) for m in _PADRAO_VALOR.finditer(str(texto))]


def formatar_numero_br(numero):
    """Formata um número no padrão brasileiro, SEM o "R$".

    Ex.: 1234.5 -> "1.234,50"
    """
    # Primeiro formata no padrão americano (1,234.50) e depois "inverte"
    # os separadores para o padrão brasileiro (1.234,50).
    americano = f"{float(numero):,.2f}"
    return americano.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_brl(numero):
    """Formata um número como moeda brasileira COM "R$".

    Ex.: 1234.5 -> "R$ 1.234,50"
    """
    return f"R$ {formatar_numero_br(numero)}"
