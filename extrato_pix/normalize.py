# -*- coding: utf-8 -*-
"""
Normalização de texto.

Objetivo: comparar descrições IGNORANDO acentos e maiúsculas/minúsculas.
Assim "Crédito Pix Cobrança" e "CREDITO PIX COBRANCA" passam a ser idênticos.
"""

import unicodedata


def normalizar(texto):
    """Remove acentos e converte para MAIÚSCULAS.

    Exemplos:
        "Crédito Pix Cobrança" -> "CREDITO PIX COBRANCA"
        "pix recebido"          -> "PIX RECEBIDO"
    """
    if texto is None:
        return ""

    # NFKD separa cada letra acentuada em (letra base + acento).
    decomposto = unicodedata.normalize("NFKD", str(texto))

    # Mantém apenas os caracteres "base", descartando os acentos (combining).
    sem_acento = "".join(
        caractere
        for caractere in decomposto
        if not unicodedata.combining(caractere)
    )

    # Maiúsculas + tira espaços nas pontas para comparação consistente.
    return sem_acento.upper().strip()
