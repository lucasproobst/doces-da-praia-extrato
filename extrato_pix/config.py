# -*- coding: utf-8 -*-
"""
⚙️  CONFIGURAÇÕES AJUSTÁVEIS DO LEITOR DE EXTRATO
=================================================

➡️  Este é o ÚNICO arquivo que você normalmente precisa editar para adaptar o
    programa ao formato do seu banco. Não é preciso saber programar: basta
    alterar as listas e os textos abaixo, sempre entre aspas.

    Depois de editar, salve o arquivo e rode/recompile o programa.
"""

# ---------------------------------------------------------------------------
# 1) PALAVRAS-CHAVE QUE IDENTIFICAM UM "PIX RECEBIDO"
# ---------------------------------------------------------------------------
# O programa procura, em cada linha do extrato, se a DESCRIÇÃO contém algum
# destes textos. A comparação IGNORA acentos e maiúsculas/minúsculas, então
# "Crédito Pix Cobrança" é tratado igual a "CREDITO PIX COBRANCA".
#
# Para reconhecer um novo padrão do seu banco, basta acrescentar uma linha
# nova na lista (lembre das aspas e da vírgula no final).
PALAVRAS_CHAVE = [
    "PIX RECEBIDO",
    "CREDITO PIX COBRANCA",
    # "TRANSFERENCIA RECEBIDA PIX",   # <- exemplo: descomente/edite se precisar
]

# ---------------------------------------------------------------------------
# 2) COMO RECONHECER UM VALOR EM DINHEIRO (formato brasileiro)
# ---------------------------------------------------------------------------
# Expressão regular (regex) que encontra valores como:
#     1.234,56   |   R$ 1.234,56   |   12,00   |   1.000.000,00
# Regra brasileira: ponto = separador de milhar, vírgula = separador decimal.
#
# Só altere se o seu extrato usar um formato bem diferente.
REGEX_VALOR = r"(?:R\$\s*)?-?(?:\d{1,3}(?:\.\d{3})+|\d+),\d{2}"

# ---------------------------------------------------------------------------
# 3) QUAL VALOR USAR QUANDO HÁ MAIS DE UM NÚMERO NA MESMA LINHA
# ---------------------------------------------------------------------------
# Muitos extratos mostram o valor da transação E o saldo na mesma linha,
# por exemplo:  "PIX RECEBIDO JOAO   1.234,56   10.000,00"
# Aqui você escolhe qual deles é o valor da transação:
#
#   "primeiro" -> usa o 1º número da linha  (PADRÃO; normalmente é o valor)
#   "ultimo"   -> usa o último número da linha (use se o saldo vier antes)
#   "maior"    -> usa o maior número da linha
#   "menor"    -> usa o menor número da linha
SELECAO_VALOR = "primeiro"

# ---------------------------------------------------------------------------
# 4) "OLHAR" LINHAS SEGUINTES QUANDO NÃO HÁ VALOR NA LINHA DA DESCRIÇÃO
# ---------------------------------------------------------------------------
# Em alguns PDFs a descrição "quebra" e o valor aparece na linha de baixo.
# Este número diz quantas linhas seguintes o programa pode olhar para
# encontrar o valor, caso ele não esteja na mesma linha da palavra-chave.
#
#   0 = considerar APENAS a mesma linha (PADRÃO, conforme especificação)
#   1, 2, ... = olhar 1, 2, ... linhas seguintes se necessário
LINHAS_LOOKAHEAD = 0

# ---------------------------------------------------------------------------
# 5) CONSIDERAR APENAS CRÉDITOS (ENTRADAS)
# ---------------------------------------------------------------------------
# As palavras-chave acima já representam ENTRADAS de dinheiro (PIX recebido),
# então normalmente isto fica como está. Mantido aqui para documentação.
APENAS_CREDITOS = True

# ---------------------------------------------------------------------------
# 6) ATUALIZAÇÃO AUTOMÁTICA (via GitHub)
# ---------------------------------------------------------------------------
# Quando ligado, ao abrir o programa ele verifica no GitHub se há uma versão
# mais nova do código e se atualiza sozinho (só funciona ao rodar "da fonte",
# com Python instalado — não no .exe empacotado).
UPDATE_ATIVO = True
UPDATE_REPO = "lucasproobst/doces-da-praia-extrato"  # usuario/repositorio
UPDATE_BRANCH = "main"

# ---------------------------------------------------------------------------
# 7) LANÇAR NO TELECON (robô — digitação automática)
# ---------------------------------------------------------------------------
# No Telecon, cada PIX exige: clicar no ícone de flechas -> digitar data ->
# conta BANRISUL -> digitar o valor -> Gravar (e a tela fecha, repetindo tudo).
# Como há CLIQUES em ícones, o robô usa "pontos calibrados": você ENSINA uma
# vez onde fica cada ponto (botão "Calibrar" no app), e ele repete sozinho.

# Pontos que você vai calibrar (ensinar a posição na tela). Liste aqui só os
# que a sua MACRO usa em ("clicar", "..."). As posições são gravadas pelo app.
TELECON_PONTOS = ["flechas", "gravar"]

# Nomes amigáveis mostrados na hora de calibrar cada ponto.
TELECON_PONTOS_NOMES = {
    "flechas": "o ÍCONE DE FLECHAS (o do meio), em 'cartões a receber'",
    "gravar": "o botão GRAVAR",
    "campo_data": "o campo da DATA",
    "campo_valor": "o campo do VALOR",
    "conta": "o campo/seta da CONTA (BANRISUL)",
}

# MACRO repetida para CADA PIX. Ações possíveis (tuplas):
#   ("clicar", "flechas")   -> clica num ponto calibrado
#   ("scroll", -500)        -> rola a tela (negativo = para baixo)
#   ("campo", "data")       -> escreve a data do PIX (extraída da linha)
#   ("campo", "valor")      -> escreve o valor do PIX
#   ("texto", "BANRISUL")   -> escreve um texto fixo
#   ("tecla", "tab")        -> aperta uma tecla (tab, enter, down, esc, ...)
#   ("esperar", 0.6)        -> espera X segundos (telas lentas)
#
# >>> PLACEHOLDER: vamos confirmar a ordem/Tabs exatos com as suas imagens.
#     (Assume que, ao abrir, o foco já cai no campo DATA; ajuste se não cair.)
TELECON_MACRO = [
    ("clicar", "flechas"),
    ("esperar", 0.7),
    ("campo", "data"),       # foco inicial no campo de data
    ("tecla", "tab"),        # -> conta (BANRISUL já vem selecionada: confere)
    ("tecla", "tab"),        # -> campo do valor
    ("campo", "valor"),
    ("clicar", "gravar"),
    ("esperar", 0.9),        # espera a tela fechar/reabrir
]

# Como o valor é digitado:  "1234,56" | "1.234,56" | "1234.56"
TELECON_FORMATO_VALOR = "1234,56"

# Forma de preencher campos de texto:
#   "colar"   -> Ctrl+V (rápido, aceita acento) — recomendado
#   "digitar" -> tecla por tecla
TELECON_METODO = "colar"

# Velocidades (segundos). Aumente se o Telecon "perder" cliques/caracteres.
TELECON_PAUSA_TECLA = 0.0
TELECON_PAUSA_ENTRE_ACOES = 0.08
TELECON_PAUSA_ENTRE_LANCAMENTOS = 0.3
TELECON_CONTAGEM_REGRESSIVA = 5
