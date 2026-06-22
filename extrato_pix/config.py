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
# 7) LANÇAR NO TELECON (digitação automática / robô)
# ---------------------------------------------------------------------------
# O robô preenche a tela de "novo lançamento" do Telecon para CADA PIX.
# Ajuste a SEQUÊNCIA abaixo para bater com a ORDEM DOS CAMPOS do seu Telecon.
#
# Cada item é uma AÇÃO (uma tupla):
#   ("campo", "valor")     -> escreve o VALOR do PIX
#   ("campo", "descricao") -> escreve a descrição (o texto da linha do extrato)
#   ("campo", "data")      -> escreve a data encontrada na linha (se houver)
#   ("texto", "QUALQUER")  -> escreve um texto fixo (ex.: uma categoria/conta)
#   ("tecla", "tab")       -> aperta Tab     (mudar de campo)
#   ("tecla", "enter")     -> aperta Enter   (confirmar/salvar)
#   ("tecla", "f2")        -> aperta uma tecla (f2, esc, down, etc.)
#   ("esperar", 0.3)       -> espera X segundos (use se a tela for lenta)
#
# >>> EXEMPLO (AJUSTE para o seu caso!): digita o valor, Tab, a descrição, Enter
TELECON_SEQUENCIA = [
    ("campo", "valor"),
    ("tecla", "tab"),
    ("campo", "descricao"),
    ("tecla", "enter"),
]

# Como o valor deve ser escrito no Telecon:
#   "1234,56"   -> sem ponto de milhar, vírgula decimal (mais comum p/ digitar)
#   "1.234,56"  -> com ponto de milhar
#   "1234.56"   -> ponto decimal (padrão americano)
TELECON_FORMATO_VALOR = "1234,56"

# Forma de preencher cada campo:
#   "colar"   -> usa Ctrl+V (RÁPIDO e aceita acentos) — recomendado
#   "digitar" -> digita tecla por tecla (use se o Telecon não aceitar colar)
TELECON_METODO = "colar"

# Velocidades (em segundos). Diminua para ir mais rápido; aumente se o
# Telecon "perder" caracteres.
TELECON_PAUSA_TECLA = 0.0       # pausa entre teclas (só no modo "digitar")
TELECON_PAUSA_ENTRE_ACOES = 0.05  # pausa entre uma ação e a próxima
TELECON_PAUSA_ENTRE_LANCAMENTOS = 0.2  # pausa entre um PIX e o próximo
TELECON_CONTAGEM_REGRESSIVA = 5  # segundos antes de começar (p/ clicar no Telecon)
