# -*- coding: utf-8 -*-
"""
Motor de extração.

Junta as peças (leitura -> normalização -> palavras-chave -> valor) e devolve
um 'Resultado' com a lista de transações, o total e a quantidade.
"""

from dataclasses import dataclass, field

from .config import (
    LINHAS_LOOKAHEAD,
    PALAVRAS_CHAVE,
    SELECAO_VALOR,
)
from .leitores import ler_arquivo
from .normalize import normalizar
from .valores import encontrar_valores


# ---------------------------------------------------------------------------
# Estruturas de dados do resultado
# ---------------------------------------------------------------------------
@dataclass
class Transacao:
    """Uma transação de PIX recebida, encontrada no extrato."""
    descricao: str          # texto original da linha (para conferência manual)
    valor: float            # valor já convertido para número
    valor_encontrado: bool  # True se o valor foi reconhecido na linha


@dataclass
class Resultado:
    """Resultado completo do processamento de um extrato."""
    arquivo: str
    transacoes: list = field(default_factory=list)

    @property
    def total(self):
        """Soma de todos os valores das transações encontradas."""
        return sum(t.valor for t in self.transacoes)

    @property
    def quantidade(self):
        """Quantidade de transações de PIX recebido encontradas."""
        return len(self.transacoes)

    @property
    def total_sem_valor(self):
        """Quantas linhas casaram com a palavra-chave mas não tinham valor."""
        return sum(1 for t in self.transacoes if not t.valor_encontrado)


# Pré-normaliza as palavras-chave uma única vez (sem acento, maiúsculas).
_PALAVRAS_NORMALIZADAS = [normalizar(p) for p in PALAVRAS_CHAVE]


# ---------------------------------------------------------------------------
# Funções internas
# ---------------------------------------------------------------------------
def _linha_tem_palavra_chave(linha_normalizada):
    """True se a linha (já normalizada) contém alguma das palavras-chave."""
    return any(palavra in linha_normalizada for palavra in _PALAVRAS_NORMALIZADAS)


def _selecionar_valor(valores):
    """Escolhe qual valor usar quando há vários números na mesma linha.

    A estratégia é definida em config.SELECAO_VALOR.
    """
    if not valores:
        return None
    if SELECAO_VALOR == "ultimo":
        return valores[-1]
    if SELECAO_VALOR == "maior":
        return max(valores)
    if SELECAO_VALOR == "menor":
        return min(valores)
    return valores[0]  # "primeiro" (padrão)


# ---------------------------------------------------------------------------
# Função pública principal
# ---------------------------------------------------------------------------
def processar_arquivo(caminho):
    """Lê o arquivo informado e devolve um 'Resultado' com os PIX recebidos."""
    linhas = ler_arquivo(caminho)
    return processar_linhas(linhas, caminho)


def processar_linhas(linhas, caminho="(memória)"):
    """Processa uma lista de linhas já lidas (útil para testes automatizados)."""
    resultado = Resultado(arquivo=caminho)

    total_linhas = len(linhas)
    for indice, linha in enumerate(linhas):
        linha_normalizada = normalizar(linha)

        # 1) A descrição contém uma das palavras-chave?
        if not _linha_tem_palavra_chave(linha_normalizada):
            continue

        # 2) Procura o(s) valor(es) na MESMA linha.
        valores = encontrar_valores(linha)

        # 3) (Opcional) Se não achou valor, olha as próximas linhas.
        passo = 1
        while not valores and passo <= LINHAS_LOOKAHEAD and (indice + passo) < total_linhas:
            valores = encontrar_valores(linhas[indice + passo])
            passo += 1

        # 4) Escolhe o valor da transação e registra.
        valor = _selecionar_valor(valores)
        resultado.transacoes.append(
            Transacao(
                descricao=str(linha).strip(),
                valor=valor if valor is not None else 0.0,
                valor_encontrado=valor is not None,
            )
        )

    return resultado
