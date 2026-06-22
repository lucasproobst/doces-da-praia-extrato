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
# De quanto em quanto tempo (segundos) o app verifica atualizações enquanto
# está aberto — assim você não precisa fechar e abrir para atualizar.
UPDATE_INTERVALO_SEGUNDOS = 120

# ---------------------------------------------------------------------------
# 7) LANÇAR NO TELECON (robô — digitação automática)
# ---------------------------------------------------------------------------
# No Telecon, cada PIX exige: clicar no ícone de flechas -> digitar data ->
# conta BANRISUL -> digitar o valor -> Gravar (e a tela fecha, repetindo tudo).
# Como há CLIQUES em ícones, o robô usa "pontos calibrados": você ENSINA uma
# vez onde fica cada ponto (botão "Calibrar" no app), e ele repete sozinho.

# Pontos que você vai calibrar (ensinar a posição na tela). Como a tela volta
# ao topo após Gravar, abrimos a transferência por uma conta SEMPRE VISÍVEL no
# topo e escolhemos "Transferir de = CARTÕES A RECEBER" pelo dropdown (assim
# nunca é preciso rolar).
TELECON_PONTOS = [
    "flechas", "transferir_de", "item_cartoes",
    "transferir_para", "item_banrisul",
    "campo_data", "valor", "gravar", "confirmar_sim",
]

# Nomes amigáveis mostrados na hora de calibrar cada ponto.
TELECON_PONTOS_NOMES = {
    "flechas": "o BOTÃO DO MEIO (as flechas de transferência) numa linha do "
               "TOPO, sempre visível (ex.: a 1ª conta) — não precisa rolar",
    "transferir_de": "o campo 'Transferir de' (clique na SETINHA do dropdown)",
    "item_cartoes": "a opção CARTÕES A RECEBER na lista que abre do 'Transferir de'",
    "transferir_para": "o campo 'Transferir para' (clique na SETINHA do dropdown)",
    "item_banrisul": "a opção BANRISUL na lista que abre do 'Transferir para'",
    "campo_data": "o campo DATA — clique EM CIMA DO DIA (os 2 primeiros números)",
    "valor": "o campo VALOR (onde aparece 0,00)",
    "gravar": "o botão GRAVAR",
    "confirmar_sim": "o botão SIM na pergunta de confirmação da transferência",
}

# MACRO repetida para CADA PIX (Transferência CARTÕES A RECEBER -> BANRISUL).
# Ações: ("clicar","ponto") | ("data_anterior","") | ("campo","valor") |
#        ("hotkey","ctrl+a") | ("tecla","tab") | ("texto","ABC") | ("esperar",0.5)
#
# "data_anterior" digita a data do extrato MENOS 1 DIA (ex.: extrato 22/06 -> 21/06).
TELECON_MACRO = [
    ("duplo_clicar", "flechas"),    # 2 cliques no botão do meio -> abre a transferência
    ("esperar", 0.9),
    ("clicar", "transferir_de"),    # abre dropdown da conta de ORIGEM
    ("esperar", 0.4),
    ("clicar", "item_cartoes"),     # escolhe CARTÕES A RECEBER
    ("esperar", 0.3),
    ("clicar", "transferir_para"),  # abre dropdown da conta de DESTINO
    ("esperar", 0.4),
    ("clicar", "item_banrisul"),    # escolhe BANRISUL
    ("esperar", 0.3),
    ("clicar", "campo_data"),       # foca a DATA
    ("tecla", "home"),              # vai para o início (segmento do dia)
    ("data_anterior", ""),          # digita a data (1 dia antes — ver TELECON_DATA_BASE)
    ("esperar", 0.2),
    ("clicar", "valor"),            # foca o campo do valor
    ("hotkey", "ctrl+a"),           # seleciona o 0,00 que está lá
    ("campo", "valor"),             # escreve o valor do PIX (substitui)
    ("esperar", 0.2),
    ("clicar", "gravar"),           # grava
    ("esperar", 0.7),               # espera a pergunta de confirmação aparecer
    ("clicar", "confirmar_sim"),    # responde SIM na confirmação
    ("esperar", 1.1),               # espera fechar tudo antes do próximo PIX
]

# Qual data o robô digita na transferência (sempre 1 dia ANTES):
#   "hoje"    -> a data de HOJE menos 1 dia (ex.: hoje 22 -> lança 21) [padrão]
#   "extrato" -> a data da linha do extrato menos 1 dia
TELECON_DATA_BASE = "hoje"

# O que o robô digita no campo de data:
#   "dia"      -> muda SÓ o dia (mês e ano ficam como já estão) [padrão]
#   "completa" -> digita a data inteira (dia, mês e ano)
# Obs.: como o campo não "anda" sozinho entre dia/mês/ano, o modo "dia" é o
#       mais seguro (o sistema já mostra o mês/ano corretos por padrão).
TELECON_DATA_MODO = "dia"

# Pausa (segundos) entre cada NÚMERO da data. Aumente se a data sair errada
# (campo "se perde" quando digita rápido). Diminua para ir mais rápido.
TELECON_PAUSA_DATA = 0.18

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
