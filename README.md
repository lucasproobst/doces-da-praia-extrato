# 🍬 Doces da Praia — Calcular Extrato

Aplicativo de **desktop para Windows** que carrega um extrato bancário
(PDF, CSV, XLSX/XLS ou TXT) e calcula o **total de PIX recebidos**, mostrando a
lista de transações para conferência e permitindo exportar o resultado.

O parser é **modular e ajustável**: se o seu banco usar um formato diferente,
você consegue adaptar editando um único arquivo (`extrato_pix/config.py`),
sem precisar mexer no resto do código.

---

## 📑 Índice

1. [Como funciona](#-como-funciona)
2. [Estrutura do projeto](#-estrutura-do-projeto)
3. [Passo 1 — Rodar pelo Python (desenvolvimento)](#-passo-1--rodar-pelo-python-desenvolvimento)
4. [Passo 2 — Gerar o executável (.exe)](#-passo-2--gerar-o-executável-exe)
5. [Passo 3 — Gerar o instalador (setup.exe)](#-passo-3--gerar-o-instalador-setupexe)
6. [Como ajustar o parser para o seu banco](#-como-ajustar-o-parser-para-o-seu-banco)
7. [Solução de problemas](#-solução-de-problemas)

---

## 🔎 Como funciona

1. Você clica em **“Selecionar extrato”** e escolhe o arquivo.
2. O programa lê **todo o conteúdo**, linha por linha (no caso de planilhas,
   cada linha da tabela vira um registro).
3. Em cada linha, procura a descrição contendo (ignorando acentos e
   maiúsculas/minúsculas):
   - `PIX RECEBIDO`
   - `CREDITO PIX COBRANCA`
4. Para cada linha encontrada, extrai o **valor em R$** (formato brasileiro,
   ex.: `1.234,56`), considerando o valor da **mesma linha**.
5. Soma tudo e mostra o **TOTAL em destaque**, a **quantidade** e a **lista**.
6. Você pode **exportar** o resultado em **Excel (.xlsx)**, **PDF**, **CSV** ou **TXT**.

> Quando há mais de um número na linha (ex.: valor da transação **e** saldo),
> o programa usa o **primeiro** por padrão — normalmente é o valor da transação.
> Isso é configurável (veja a seção de ajustes).

---

## 📁 Estrutura do projeto

```
ExtratoDp/
├── app.py                 # Interface gráfica (a "tela") + ponto de entrada
├── make_icon.py           # Gera o ícone assets/icon.ico
├── GERAR_INSTALADOR.bat   # ⭐ Duplo clique no Windows: gera .exe + instalador
├── installer.iss          # Script do Inno Setup (gera o instalador)
├── requirements.txt       # Lista de dependências
├── README.md              # Este arquivo
├── exemplos/
│   └── extrato_exemplo.txt   # Extrato de teste
└── extrato_pix/           # ⭐ Núcleo do programa (lógica de leitura/cálculo)
    ├── config.py          # ⚙️ AJUSTES (palavras-chave, valores) — edite aqui
    ├── normalize.py       # Remove acentos / maiúsculas
    ├── valores.py         # Reconhece e formata valores em R$
    ├── leitores.py        # Lê PDF / CSV / XLSX / XLS / TXT
    ├── extrator.py        # Motor que junta tudo
    └── exportar.py        # Exporta para .csv / .txt
```

---

## ▶ Passo 1 — Rodar pelo Python (desenvolvimento)

Use esta forma para testar rapidamente antes de gerar o `.exe`.

**Pré-requisitos:** [Python 3.10 ou superior](https://www.python.org/downloads/)
(na instalação, marque **“Add Python to PATH”**).

```bash
# 1) (Recomendado) crie um ambiente virtual
python -m venv .venv
.venv\Scripts\activate           # no Windows
# source .venv/bin/activate      # no macOS/Linux

# 2) Instale as dependências
pip install -r requirements.txt

# 3) (Opcional) gere o ícone
python make_icon.py

# 4) Rode o aplicativo
python app.py
```

Para testar, use o arquivo `exemplos/extrato_exemplo.txt` (resultado esperado:
**6 transações**, total **R$ 17.541,34**).

---

## 🛠 Passo 2 — Gerar o executável e o instalador (TUDO de uma vez)

> ⚠️ Isto **precisa ser feito numa máquina Windows**. O `.exe` é específico do
> Windows e **não pode ser gerado no Mac/Linux** (não existe compilação cruzada).

### ⭐ Forma recomendada — um único duplo clique

Dê um **duplo clique em `GERAR_INSTALADOR.bat`**. Ele faz tudo sozinho:

1. Verifica o Python — e **instala automaticamente** (via `winget`) se não houver
2. Cria o ambiente virtual
3. Instala as dependências
4. Gera o ícone
5. Compila o executável (`.exe`) com PyInstaller
6. Gera o instalador (`setup.exe`) com o Inno Setup —
   **instalando o próprio Inno Setup sozinho** (via `winget`) se você não tiver

> 🔁 Se o Python tiver acabado de ser instalado, o Windows só o reconhece numa
> **nova janela** — nesse caso o `.bat` avisa para você fechar e clicar de novo
> (apenas uma vez). Do resto ele cuida sozinho.

No final você terá:

```
dist\Doces da Praia - Calcular Extrato.exe     <- programa que roda sozinho
instalador\DocesDaPraia-Setup.exe              <- instalador para distribuir
```

> 💡 O `.exe` em `dist\` já funciona sozinho, sem instalar nada. O
> `DocesDaPraia-Setup.exe` é o instalador “bonitinho” para entregar a outras
> pessoas (cria atalhos no Menu Iniciar e na Área de Trabalho).

### Forma manual (caso prefira fazer passo a passo)

**Comando exato do PyInstaller:**

```bat
pyinstaller --noconfirm --onefile --windowed ^
  --name "Doces da Praia - Calcular Extrato" ^
  --icon "assets\icon.ico" ^
  --add-data "assets\icon.ico;assets" ^
  --collect-all customtkinter ^
  --collect-all pdfplumber ^
  --collect-all pdfminer ^
  --collect-all openpyxl ^
  --collect-all fpdf ^
  app.py
```

> O `^` quebra o comando em várias linhas no Prompt de Comando do Windows.
> No **PowerShell**, troque `^` por crase (`` ` ``) no fim de cada linha.

**Gerar o instalador:** instale o [Inno Setup](https://jrsoftware.org/isdl.php),
abra o arquivo **`installer.iss`** e clique em **Build → Compile** (`Ctrl + F9`).

---

## 🧪 Modo linha de comando (opcional)

O programa também roda **sem abrir a janela**, útil para automação ou teste rápido:

```bat
REM apenas mostrar o resultado no console:
"Doces da Praia - Calcular Extrato.exe" caminho\do\extrato.pdf

REM processar e JA exportar (formato definido pela extensao de saida):
"Doces da Praia - Calcular Extrato.exe" caminho\do\extrato.pdf  resultado.xlsx
"Doces da Praia - Calcular Extrato.exe" caminho\do\extrato.csv  resultado.pdf

REM testar com o exemplo embutido:
"Doces da Praia - Calcular Extrato.exe" --selftest
```

Durante o desenvolvimento, equivale a `python app.py caminho\do\extrato.pdf resultado.xlsx`.

---

## ⚙️ Como ajustar o parser para o seu banco

O layout dos extratos muda de banco para banco. Quase todos os ajustes ficam em
um único arquivo: **`extrato_pix/config.py`**. Abra-o em qualquer editor de texto.

### 1) Adicionar/alterar as palavras-chave
Se o seu banco descreve o PIX de outra forma, acrescente o texto à lista:

```python
PALAVRAS_CHAVE = [
    "PIX RECEBIDO",
    "CREDITO PIX COBRANCA",
    "TRANSFERENCIA RECEBIDA PIX",   # <- exemplo
]
```
> Não precisa se preocupar com acentos ou maiúsculas — a comparação já ignora os dois.

### 2) Escolher qual valor usar quando há vários na linha
Se o seu extrato mostra o **saldo antes** do valor da transação, troque para `"ultimo"`:

```python
SELECAO_VALOR = "primeiro"   # opções: "primeiro", "ultimo", "maior", "menor"
```

### 3) Valor na linha de baixo (PDFs que “quebram” a descrição)
Se em alguns PDFs o valor aparece na linha seguinte à descrição:

```python
LINHAS_LOOKAHEAD = 1   # 0 = só a mesma linha (padrão)
```

### 4) Formato de valor diferente
Em último caso, é possível ajustar a expressão que reconhece valores
(`REGEX_VALOR`). O padrão já cobre o formato brasileiro (`1.234,56`,
`R$ 1.234,56`, etc.).

Depois de editar, salve e rode de novo (`python app.py`) ou recompile o `.exe`.

---

## 🩹 Solução de problemas

| Problema | Solução |
|---|---|
| **“Nenhuma transação encontrada”** | O texto da descrição no seu banco é diferente. Ajuste `PALAVRAS_CHAVE` em `extrato_pix/config.py`. |
| **Valor errado (pegou o saldo)** | Troque `SELECAO_VALOR` para `"ultimo"` ou `"menor"` em `config.py`. |
| **Linhas em vermelho na lista** | A linha tem a palavra-chave, mas o valor não foi reconhecido. Confira o formato do valor ou ajuste `REGEX_VALOR`. |
| **Erro ao ler `.xls`** | Confirme que o `xlrd` foi instalado (`pip install xlrd`). |
| **PDF “escaneado” (imagem) não lê nada** | PDFs que são fotos/imagens não têm texto. Seria necessário OCR (não incluído). Exporte o extrato em CSV/Excel/TXT pelo banco. |
| **PyInstaller: erro “module not found”** | Acrescente `--collect-all NOME_DO_MODULO` ao comando do PyInstaller. |
| **Antivírus reclama do `.exe`** | É um falso-positivo comum em programas feitos com PyInstaller. Assine o executável ou crie uma exceção no antivírus. |

---

## 📋 Formatos aceitos

- **PDF** (`.pdf`) — extratos com texto (não escaneados)
- **CSV** (`.csv`) — separador `;` ou `,` (detectado automaticamente)
- **Excel** (`.xlsx`, `.xls`)
- **Texto** (`.txt`)

---

Feito com 🍬 para a **Doces da Praia**.
