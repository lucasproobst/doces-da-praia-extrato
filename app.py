# -*- coding: utf-8 -*-
"""
Doces da Praia - Calcular Extrato
=================================

Aplicativo de desktop (Windows) para carregar um extrato bancário e calcular
o total de PIX recebidos.

Este arquivo cuida APENAS da interface gráfica (a "tela"). Toda a lógica de
leitura e cálculo fica no pacote 'extrato_pix', o que mantém o código
organizado e fácil de ajustar.

Para rodar:   python app.py
"""

import os
import sys
import threading

# ---------------------------------------------------------------------------
# Importação da biblioteca de interface (customtkinter). Se ela não estiver
# instalada, mostramos uma mensagem amigável em vez de um erro técnico.
# ---------------------------------------------------------------------------
try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox, ttk
    import tkinter as tk
except Exception as erro:  # pragma: no cover
    print("ERRO: não foi possível carregar a interface gráfica.")
    print("Instale as dependências com:  pip install -r requirements.txt")
    print("Detalhe técnico:", erro)
    sys.exit(1)

from extrato_pix import __app_name__, __version__
from extrato_pix import atualizador
from extrato_pix import config
from extrato_pix import digitador
from extrato_pix.extrator import processar_arquivo
from extrato_pix.exportar import exportar
from extrato_pix.leitores import formatos_suportados
from extrato_pix.registro import CAMINHO_LOG, configurar as configurar_log, log
from extrato_pix.valores import formatar_brl


# ===========================================================================
# PALETA DE CORES — tema "Doces da Praia" (praia + doces)
# Cada cor é uma tupla (modo claro, modo escuro) entendida pelo customtkinter.
# ===========================================================================
OCEANO        = ("#0EA5A4", "#0EA5A4")   # turquesa (cor principal)
OCEANO_HOVER  = ("#0D9488", "#0D9488")
OCEANO_FUNDO  = ("#0F766E", "#134E4A")   # verde-mar profundo (card do total)
CORAL         = ("#FB7185", "#FB7185")   # coral/doce (botão exportar)
CORAL_HOVER   = ("#F43F5E", "#F43F5E")
AREIA         = ("#FFF8F1", "#0B1620")   # fundo geral (areia / noite)
CARTAO        = ("#FFFFFF", "#152230")   # fundo dos cartões
TEXTO         = ("#0F172A", "#E2E8F0")   # texto principal
TEXTO_SUAVE   = ("#64748B", "#94A3B8")   # texto secundário
BRANCO        = ("#FFFFFF", "#FFFFFF")
BORDA         = ("#E7E0D7", "#1F2D3D")


def _recurso(caminho_relativo):
    """Resolve o caminho de um arquivo de recurso (ícone), funcionando tanto
    ao rodar pelo Python quanto dentro do .exe gerado pelo PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base, caminho_relativo)


class AppExtrato(ctk.CTk):
    """Janela principal do aplicativo."""

    def __init__(self):
        super().__init__()

        # Estado interno
        self.resultado = None        # último resultado processado
        self.caminho_atual = None    # caminho do arquivo carregado

        # Configuração da janela ------------------------------------------------
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        self.title(__app_name__)
        self.geometry("980x700")
        self.minsize(880, 620)
        self.configure(fg_color=AREIA)
        self._definir_icone()

        # Layout em grade: cabeçalho (0), corpo (1), rodapé (2)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._montar_cabecalho()
        self._montar_corpo()
        self._montar_rodape()

        self._atualizar_total(0.0, 0)
        self._definir_status("Pronto. Clique em “Selecionar extrato” para começar.")

        # Verifica se há uma versão nova no GitHub (em segundo plano).
        threading.Thread(target=self._verificar_atualizacao, daemon=True).start()

    # =======================================================================
    # ÍCONE
    # =======================================================================
    def _definir_icone(self):
        try:
            caminho_icone = _recurso(os.path.join("assets", "icon.ico"))
            if os.path.exists(caminho_icone):
                self.iconbitmap(caminho_icone)
        except Exception:
            pass  # ícone é opcional; o app funciona sem ele

    # =======================================================================
    # CABEÇALHO
    # =======================================================================
    def _montar_cabecalho(self):
        cabecalho = ctk.CTkFrame(self, fg_color=OCEANO_FUNDO, corner_radius=0, height=92)
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.grid_propagate(False)
        cabecalho.grid_columnconfigure(1, weight=1)

        # Emblema/ícone à esquerda
        emblema = ctk.CTkLabel(
            cabecalho, text="🍬", font=ctk.CTkFont(size=40), text_color=BRANCO
        )
        emblema.grid(row=0, column=0, rowspan=2, padx=(24, 12), pady=16)

        titulo = ctk.CTkLabel(
            cabecalho,
            text="Doces da Praia",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=BRANCO,
        )
        titulo.grid(row=0, column=1, sticky="sw", padx=2, pady=(20, 0))

        subtitulo = ctk.CTkLabel(
            cabecalho,
            text="Calcular Extrato  •  some o total de PIX recebidos",
            font=ctk.CTkFont(size=13),
            text_color=("#CCFBF1", "#99F6E4"),
        )
        subtitulo.grid(row=1, column=1, sticky="nw", padx=2, pady=(0, 18))

        # Botão de alternar tema (claro/escuro) à direita
        self.botao_tema = ctk.CTkButton(
            cabecalho,
            text="🌙  Tema escuro",
            width=130,
            height=32,
            fg_color="#0B5B54",
            hover_color="#0A4F49",
            text_color=BRANCO,
            font=ctk.CTkFont(size=12),
            command=self._alternar_tema,
        )
        self.botao_tema.grid(row=0, column=2, rowspan=2, padx=24)

    # =======================================================================
    # CORPO
    # =======================================================================
    def _montar_corpo(self):
        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        corpo.grid_columnconfigure(0, weight=1)
        corpo.grid_rowconfigure(1, weight=1)

        # ---- Faixa superior: ações (esquerda) + total (direita) ----
        topo = ctk.CTkFrame(corpo, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew")
        topo.grid_columnconfigure(0, weight=0)
        topo.grid_columnconfigure(1, weight=1)

        self._montar_cartao_acoes(topo)
        self._montar_cartao_total(topo)

        # ---- Lista de transações ----
        self._montar_cartao_lista(corpo)

    def _montar_cartao_acoes(self, mae):
        cartao = ctk.CTkFrame(
            mae, fg_color=CARTAO, corner_radius=18, border_width=1, border_color=BORDA
        )
        cartao.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        cartao.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(
            cartao, text="Ações", font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXTO_SUAVE,
        )
        titulo.grid(row=0, column=0, sticky="w", padx=22, pady=(20, 10))

        self.botao_selecionar = ctk.CTkButton(
            cartao,
            text="📂   Selecionar extrato",
            height=48,
            corner_radius=12,
            fg_color=OCEANO,
            hover_color=OCEANO_HOVER,
            text_color=BRANCO,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.selecionar_extrato,
        )
        self.botao_selecionar.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 10))

        self.botao_exportar = ctk.CTkButton(
            cartao,
            text="💾   Exportar resultado",
            height=48,
            corner_radius=12,
            fg_color=CORAL,
            hover_color=CORAL_HOVER,
            text_color=BRANCO,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.exportar_resultado,
            state="disabled",
        )
        self.botao_exportar.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 10))

        self.botao_telecon = ctk.CTkButton(
            cartao,
            text="⌨️   Lançar no Telecon",
            height=48,
            corner_radius=12,
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            text_color=BRANCO,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.abrir_telecon,
            state="disabled",
        )
        self.botao_telecon.grid(row=3, column=0, sticky="ew", padx=22, pady=(0, 14))

        formatos = ", ".join(e.replace(".", "").upper() for e in formatos_suportados())
        ctk.CTkLabel(
            cartao,
            text=f"Formatos aceitos:\n{formatos}",
            font=ctk.CTkFont(size=11),
            text_color=TEXTO_SUAVE,
            justify="left",
        ).grid(row=4, column=0, sticky="w", padx=22, pady=(0, 6))

        self.rotulo_arquivo = ctk.CTkLabel(
            cartao,
            text="Nenhum arquivo selecionado",
            font=ctk.CTkFont(size=12),
            text_color=TEXTO,
            wraplength=240,
            justify="left",
        )
        self.rotulo_arquivo.grid(row=5, column=0, sticky="w", padx=22, pady=(0, 20))

    def _montar_cartao_total(self, mae):
        cartao = ctk.CTkFrame(mae, fg_color=OCEANO_FUNDO, corner_radius=18)
        cartao.grid(row=0, column=1, sticky="nsew")
        cartao.grid_columnconfigure(0, weight=1)
        cartao.grid_rowconfigure(0, weight=1)
        cartao.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            cartao,
            text="TOTAL DE PIX RECEBIDO",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#A7F3D0", "#A7F3D0"),
        ).grid(row=1, column=0, pady=(30, 2))

        self.rotulo_total = ctk.CTkLabel(
            cartao,
            text="R$ 0,00",
            font=ctk.CTkFont(size=52, weight="bold"),
            text_color=BRANCO,
        )
        self.rotulo_total.grid(row=2, column=0, pady=(0, 4))

        self.rotulo_quantidade = ctk.CTkLabel(
            cartao,
            text="0 transação encontrada",
            font=ctk.CTkFont(size=15),
            text_color=("#CCFBF1", "#CCFBF1"),
        )
        self.rotulo_quantidade.grid(row=3, column=0, pady=(0, 30), sticky="n")

    def _montar_cartao_lista(self, mae):
        cartao = ctk.CTkFrame(
            mae, fg_color=CARTAO, corner_radius=18, border_width=1, border_color=BORDA
        )
        cartao.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        cartao.grid_columnconfigure(0, weight=1)
        cartao.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            cartao,
            text="Transações encontradas  ·  confira manualmente",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXTO_SUAVE,
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(18, 8))

        # Área da tabela (ttk.Treeview estilizado para combinar com o tema)
        moldura = ctk.CTkFrame(cartao, fg_color="transparent")
        moldura.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        moldura.grid_columnconfigure(0, weight=1)
        moldura.grid_rowconfigure(0, weight=1)

        self._estilizar_tabela()

        self.tabela = ttk.Treeview(
            moldura,
            columns=("descricao", "valor"),
            show="headings",
            style="Doces.Treeview",
            selectmode="browse",
        )
        self.tabela.heading("descricao", text="Descrição", anchor="w")
        self.tabela.heading("valor", text="Valor (R$)", anchor="e")
        self.tabela.column("descricao", anchor="w", width=560, minwidth=240)
        self.tabela.column("valor", anchor="e", width=150, minwidth=120, stretch=False)
        self.tabela.grid(row=0, column=0, sticky="nsew")

        # Cores alternadas das linhas + destaque para valor não reconhecido
        # (definidas conforme o tema atual — claro ou escuro).
        self._configurar_tags_tabela()

        rolagem = ttk.Scrollbar(moldura, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        rolagem.grid(row=0, column=1, sticky="ns")

    def _estilizar_tabela(self):
        """Aplica um estilo agradável ao ttk.Treeview, combinando com o tema."""
        escuro = ctk.get_appearance_mode() == "Dark"
        fundo = "#152230" if escuro else "#FFFFFF"
        texto = "#E2E8F0" if escuro else "#0F172A"
        selecao = "#134E4A" if escuro else "#CCFBF1"

        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except Exception:
            pass
        estilo.configure(
            "Doces.Treeview",
            background=fundo,
            fieldbackground=fundo,
            foreground=texto,
            rowheight=30,
            borderwidth=0,
            font=("Segoe UI", 11),
        )
        estilo.configure(
            "Doces.Treeview.Heading",
            background="#0F766E",
            foreground="#FFFFFF",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padding=(8, 6),
        )
        estilo.map("Doces.Treeview.Heading", background=[("active", "#0D9488")])
        estilo.map(
            "Doces.Treeview",
            background=[("selected", selecao)],
            foreground=[("selected", texto)],
        )

    def _configurar_tags_tabela(self):
        """Define as cores das linhas da tabela conforme o tema atual."""
        if ctk.get_appearance_mode() == "Dark":
            par, impar, sem_valor = "#1B2A3A", "#152230", "#F87171"
        else:
            par, impar, sem_valor = "#F8FAFC", "#FFFFFF", "#DC2626"
        self.tabela.tag_configure("par", background=par)
        self.tabela.tag_configure("impar", background=impar)
        self.tabela.tag_configure("sem_valor", foreground=sem_valor)

    # =======================================================================
    # RODAPÉ / BARRA DE STATUS
    # =======================================================================
    def _montar_rodape(self):
        rodape = ctk.CTkFrame(self, fg_color=CARTAO, corner_radius=0, height=40,
                              border_width=1, border_color=BORDA)
        rodape.grid(row=2, column=0, sticky="ew")
        rodape.grid_propagate(False)
        rodape.grid_columnconfigure(0, weight=1)

        self.rotulo_status = ctk.CTkLabel(
            rodape, text="", font=ctk.CTkFont(size=12), text_color=TEXTO_SUAVE,
            anchor="w",
        )
        self.rotulo_status.grid(row=0, column=0, sticky="ew", padx=16)

        self.barra_progresso = ctk.CTkProgressBar(
            rodape, width=160, height=8, progress_color=OCEANO
        )
        self.barra_progresso.grid(row=0, column=1, padx=(8, 8))
        self.barra_progresso.set(0)
        self.barra_progresso.grid_remove()  # só aparece durante o processamento

        ctk.CTkLabel(
            rodape, text=f"v{__version__}", font=ctk.CTkFont(size=11),
            text_color=TEXTO_SUAVE,
        ).grid(row=0, column=2, sticky="e", padx=16)

    # =======================================================================
    # AÇÕES
    # =======================================================================
    def selecionar_extrato(self):
        """Abre a janela para o usuário escolher o arquivo do extrato."""
        padroes = " ".join("*" + e for e in formatos_suportados())
        caminho = filedialog.askopenfilename(
            title="Selecione o extrato bancário",
            filetypes=[
                ("Todos os formatos aceitos", padroes),
                ("PDF", "*.pdf"),
                ("CSV", "*.csv"),
                ("Excel", "*.xlsx *.xls"),
                ("Texto", "*.txt"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if not caminho:
            return

        self.caminho_atual = caminho
        self.rotulo_arquivo.configure(text=os.path.basename(caminho))
        self._definir_status(f"Processando “{os.path.basename(caminho)}”…")
        self._iniciar_processamento()

        # Processa em segundo plano para não "travar" a janela.
        threading.Thread(
            target=self._processar_em_thread, args=(caminho,), daemon=True
        ).start()

    def _processar_em_thread(self, caminho):
        try:
            log.info("Processando arquivo: %s", caminho)
            resultado = processar_arquivo(caminho)
            log.info(
                "Concluído: %d transação(ões), total R$ %.2f",
                resultado.quantidade, resultado.total,
            )
            self.after(0, lambda: self._mostrar_resultado(resultado))
        except Exception as erro:
            log.exception("Falha ao processar o arquivo: %s", caminho)
            mensagem = str(erro)
            self.after(0, lambda: self._mostrar_erro(mensagem))

    def _mostrar_resultado(self, resultado):
        self.resultado = resultado
        self._finalizar_processamento()

        # Atualiza a tabela
        self.tabela.delete(*self.tabela.get_children())
        for indice, transacao in enumerate(resultado.transacoes):
            tags = ["par" if indice % 2 == 0 else "impar"]
            if not transacao.valor_encontrado:
                tags.append("sem_valor")
            self.tabela.insert(
                "",
                "end",
                values=(transacao.descricao, formatar_brl(transacao.valor)),
                tags=tags,
            )

        self._atualizar_total(resultado.total, resultado.quantidade)
        estado = "normal" if resultado.quantidade else "disabled"
        self.botao_exportar.configure(state=estado)
        self.botao_telecon.configure(state=estado)

        if resultado.quantidade == 0:
            self._definir_status(
                "Nenhuma transação de PIX recebido encontrada. "
                "Dica: ajuste as palavras-chave em extrato_pix/config.py."
            )
            messagebox.showinfo(
                "Sem resultados",
                "Não encontramos transações de PIX recebido neste arquivo.\n\n"
                "Se você tem certeza de que existem, o formato do seu banco pode ser "
                "diferente. Abra o arquivo extrato_pix/config.py e ajuste as "
                "palavras-chave ou o padrão de valor.",
                parent=self,
            )
        else:
            aviso = ""
            if resultado.total_sem_valor:
                aviso = (
                    f"  ({resultado.total_sem_valor} sem valor reconhecido — "
                    "em vermelho na lista)"
                )
            self._definir_status(
                f"Concluído: {resultado.quantidade} transação(ões), "
                f"total {formatar_brl(resultado.total)}.{aviso}"
            )

    def _mostrar_erro(self, mensagem):
        self._finalizar_processamento()
        self._definir_status("Ocorreu um erro ao ler o arquivo.")
        messagebox.showerror(
            "Erro ao ler o arquivo",
            "Não foi possível processar este arquivo.\n\n"
            f"Detalhe técnico:\n{mensagem}\n\n"
            f"Um registro do erro foi salvo em:\n{CAMINHO_LOG}",
            parent=self,
        )

    def exportar_resultado(self):
        """Salva o resultado atual em .csv ou .txt."""
        if not self.resultado or not self.resultado.transacoes:
            messagebox.showinfo(
                "Exportar",
                "Não há nada para exportar. Selecione um extrato primeiro.",
                parent=self,
            )
            return

        nome_sugerido = "pix_recebidos"
        if self.caminho_atual:
            base = os.path.splitext(os.path.basename(self.caminho_atual))[0]
            nome_sugerido = f"pix_recebidos_{base}"

        caminho = filedialog.asksaveasfilename(
            title="Salvar resultado",
            defaultextension=".xlsx",
            initialfile=nome_sugerido + ".xlsx",
            filetypes=[
                ("Excel (.xlsx)", "*.xlsx"),
                ("PDF (.pdf)", "*.pdf"),
                ("CSV (para Excel)", "*.csv"),
                ("Texto (.txt)", "*.txt"),
            ],
        )
        if not caminho:
            return

        try:
            exportar(self.resultado, caminho)
            log.info("Exportado para: %s", caminho)
            self._definir_status(f"Resultado salvo em “{os.path.basename(caminho)}”.")
            messagebox.showinfo(
                "Exportado com sucesso",
                f"O resultado foi salvo em:\n{caminho}",
                parent=self,
            )
        except Exception as erro:
            log.exception("Falha ao exportar para: %s", caminho)
            messagebox.showerror(
                "Erro ao exportar",
                f"Não foi possível salvar o arquivo.\n\n{erro}\n\n"
                f"Um registro do erro foi salvo em:\n{CAMINHO_LOG}",
                parent=self,
            )

    # =======================================================================
    # LANÇAR NO TELECON (robô de digitação)
    # =======================================================================
    def abrir_telecon(self):
        """Abre o painel que explica e inicia o lançamento automático."""
        if not self.resultado or not self.resultado.transacoes:
            messagebox.showinfo(
                "Lançar no Telecon",
                "Não há lançamentos. Selecione um extrato primeiro.",
                parent=self,
            )
            return

        total = self.resultado.quantidade
        janela = ctk.CTkToplevel(self)
        janela.title("Lançar no Telecon")
        janela.geometry("560x430")
        janela.transient(self)
        janela.after(50, janela.lift)
        janela.after(80, janela.grab_set)

        ctk.CTkLabel(
            janela, text="⌨️  Lançar no Telecon",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=(20, 6))

        instrucoes = (
            "O robô vai DIGITAR cada PIX na tela de novo lançamento do Telecon.\n\n"
            "Antes de começar:\n"
            "1) Abra o Telecon na tela de NOVO LANÇAMENTO, com o cursor no\n"
            "    primeiro campo.\n"
            "2) Escolha abaixo. Vai aparecer uma contagem regressiva — nesse\n"
            "    tempo, CLIQUE na janela do Telecon.\n\n"
            "⚠️  Para ABORTAR a qualquer momento, jogue o mouse para o\n"
            "     CANTO SUPERIOR ESQUERDO da tela.\n\n"
            "Dica: teste com 1 lançamento primeiro e confira no Telecon antes\n"
            "de lançar a lista inteira."
        )
        ctk.CTkLabel(
            janela, text=instrucoes, justify="left",
            font=ctk.CTkFont(size=13), text_color=TEXTO,
        ).pack(padx=24, pady=4, anchor="w")

        # Status de calibração + botão de calibrar
        faltando = digitador.pontos_faltando()
        ctk.CTkLabel(
            janela,
            text=("⚠️  Pontos não calibrados — clique em Calibrar primeiro."
                  if faltando else "✓  Pontos já calibrados."),
            font=ctk.CTkFont(size=12),
            text_color=("#C0392B" if faltando else "#0F766E"),
        ).pack(pady=(2, 2))

        ctk.CTkButton(
            janela, text="📍  Calibrar pontos (ensinar posições)",
            width=320, height=40, corner_radius=12,
            fg_color="#F59E0B", hover_color="#D97706", text_color=BRANCO,
            command=lambda: (janela.destroy(), self._calibrar_telecon()),
        ).pack(pady=(2, 8))

        botoes = ctk.CTkFrame(janela, fg_color="transparent")
        botoes.pack(pady=10)

        primeira = [self.resultado.transacoes[0]]
        todas = list(self.resultado.transacoes)

        ctk.CTkButton(
            botoes, text="🧪  Testar com 1", width=150, height=44, corner_radius=12,
            fg_color=OCEANO, hover_color=OCEANO_HOVER,
            command=lambda: self._preparar_lancamento(janela, primeira),
        ).grid(row=0, column=0, padx=6)

        ctk.CTkButton(
            botoes, text=f"🚀  Lançar todos ({total})", width=180, height=44,
            corner_radius=12, fg_color="#7C3AED", hover_color="#6D28D9",
            command=lambda: self._preparar_lancamento(janela, todas),
        ).grid(row=0, column=1, padx=6)

        ctk.CTkButton(
            botoes, text="Cancelar", width=110, height=44, corner_radius=12,
            fg_color="#94A3B8", hover_color="#64748B",
            command=janela.destroy,
        ).grid(row=0, column=2, padx=6)

    def _preparar_lancamento(self, janela, transacoes):
        if digitador.pontos_faltando():
            janela.destroy()
            messagebox.showwarning(
                "Calibrar primeiro",
                "Antes de lançar, clique em “Calibrar pontos” para ensinar onde\n"
                "ficam o ícone de flechas e o botão Gravar.",
                parent=self,
            )
            self._calibrar_telecon()
            return
        janela.destroy()
        self._travar_botoes(True)
        self._contagem_telecon(int(config.TELECON_CONTAGEM_REGRESSIVA), transacoes)

    def _calibrar_telecon(self):
        """Ensina ao robô a posição de cada ponto (mouse + ESPAÇO).

        Calibra APENAS os pontos que ainda faltam (assim, ao adicionar um ponto
        novo, você só ensina esse). Se já estiver tudo calibrado, recalibra tudo.
        """
        faltando = digitador.pontos_faltando()
        pontos = faltando if faltando else list(config.TELECON_PONTOS)
        if not pontos:
            messagebox.showinfo("Calibrar", "Não há pontos para calibrar.", parent=self)
            return
        nomes = config.TELECON_PONTOS_NOMES

        win = ctk.CTkToplevel(self)
        win.title("Calibrar Telecon")
        win.geometry("580x300")
        win.transient(self)
        win.attributes("-topmost", True)
        win.after(50, win.lift)
        win.after(120, win.focus_force)

        estado = {"i": 0}

        titulo = ctk.CTkLabel(win, text="", font=ctk.CTkFont(size=16, weight="bold"))
        titulo.pack(pady=(22, 6))
        instr = ctk.CTkLabel(
            win, text="", font=ctk.CTkFont(size=15), justify="center", wraplength=520
        )
        instr.pack(pady=10, padx=20)
        ctk.CTkLabel(
            win,
            text="Passe o MOUSE sobre o alvo (sem clicar) e aperte a tecla ESPAÇO.\n"
                 "(ESC cancela)",
            font=ctk.CTkFont(size=12), text_color=TEXTO_SUAVE, justify="center",
        ).pack(pady=10)

        def mostrar():
            nome = pontos[estado["i"]]
            legivel = nomes.get(nome, nome)
            titulo.configure(text=f"Ponto {estado['i'] + 1} de {len(pontos)}")
            instr.configure(text=f"Posicione o mouse sobre:\n\n➡️  {legivel}")

        def capturar(_evento=None):
            nome = pontos[estado["i"]]
            try:
                x, y = digitador.posicao_atual_do_mouse()
            except digitador.RoboIndisponivelError as erro:
                win.destroy()
                self._erro_telecon(str(erro))
                return
            digitador.salvar_ponto(nome, x, y)
            estado["i"] += 1
            if estado["i"] >= len(pontos):
                win.destroy()
                self._definir_status("✓ Telecon calibrado. Já pode lançar (teste com 1).")
                messagebox.showinfo(
                    "Calibração concluída",
                    "Posições salvas!\n\nAgora abra o Telecon e use\n"
                    "“Lançar no Telecon → Testar com 1” para conferir.",
                    parent=self,
                )
                return
            mostrar()

        win.bind("<space>", capturar)
        win.bind("<Escape>", lambda _e: win.destroy())
        mostrar()

    def _contagem_telecon(self, segundos, transacoes):
        if segundos > 0:
            self._definir_status(
                f"➡️  Vá para o TELECON agora! Começando em {segundos}s…  "
                "(mouse no canto p/ abortar)"
            )
            self.after(1000, lambda: self._contagem_telecon(segundos - 1, transacoes))
            return
        self._definir_status("Lançando no Telecon…")
        threading.Thread(
            target=self._rodar_lancamento, args=(transacoes,), daemon=True
        ).start()

    def _rodar_lancamento(self, transacoes):
        def progresso(indice, total):
            self.after(0, lambda: self._definir_status(
                f"Lançando no Telecon… {indice}/{total}"
            ))
        try:
            feitos = digitador.lancar_varios(transacoes, ao_progredir=progresso)
            self.after(0, lambda: self._fim_lancamento(feitos, len(transacoes)))
        except digitador.RoboIndisponivelError as erro:
            mensagem = str(erro)
            self.after(0, lambda: self._erro_telecon(mensagem))
        except Exception as erro:
            log.exception("Erro no lançamento automático")
            mensagem = str(erro)
            self.after(0, lambda: self._erro_telecon(mensagem))

    def _fim_lancamento(self, feitos, total):
        self._travar_botoes(False)
        self._definir_status(f"✓ Lançamento concluído: {feitos}/{total} enviados ao Telecon.")
        messagebox.showinfo(
            "Lançamento concluído",
            f"Foram lançados {feitos} de {total} no Telecon.\n\n"
            "Confira no Telecon se ficou tudo certo.",
            parent=self,
        )

    def _erro_telecon(self, mensagem):
        self._travar_botoes(False)
        self._definir_status("Não foi possível lançar no Telecon.")
        messagebox.showerror(
            "Lançar no Telecon",
            f"{mensagem}\n\nUm registro foi salvo em:\n{CAMINHO_LOG}",
            parent=self,
        )

    def _travar_botoes(self, travar):
        estado = "disabled" if travar else "normal"
        self.botao_selecionar.configure(state="disabled" if travar else "normal")
        self.botao_exportar.configure(state=estado)
        self.botao_telecon.configure(state=estado)

    # =======================================================================
    # AUXILIARES DE INTERFACE
    # =======================================================================
    def _atualizar_total(self, total, quantidade):
        self.rotulo_total.configure(text=formatar_brl(total))
        palavra = "transação encontrada" if quantidade == 1 else "transações encontradas"
        self.rotulo_quantidade.configure(text=f"{quantidade} {palavra}")

    def _definir_status(self, texto):
        self.rotulo_status.configure(text=texto)

    def _iniciar_processamento(self):
        self.botao_selecionar.configure(state="disabled")
        self.botao_exportar.configure(state="disabled")
        self.barra_progresso.grid()
        self.barra_progresso.configure(mode="indeterminate")
        self.barra_progresso.start()

    def _finalizar_processamento(self):
        self.barra_progresso.stop()
        self.barra_progresso.grid_remove()
        self.botao_selecionar.configure(state="normal")

    def _alternar_tema(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("light")
            self.botao_tema.configure(text="🌙  Tema escuro")
        else:
            ctk.set_appearance_mode("dark")
            self.botao_tema.configure(text="☀️  Tema claro")
        # Reaplica o estilo e as cores das linhas para acompanhar o tema.
        self._estilizar_tabela()
        self._configurar_tags_tabela()

    # =======================================================================
    # ATUALIZAÇÃO AUTOMÁTICA (via GitHub)
    # =======================================================================
    def _verificar_atualizacao(self):
        """Roda em segundo plano: se houver versão nova, baixa e oferece reabrir."""
        sha = atualizador.verificar()
        if not sha:
            return
        self.after(0, lambda: self._definir_status("Baixando atualização…"))
        if atualizador.aplicar(sha):
            self.after(0, self._oferecer_reinicio)
        else:
            self.after(0, lambda: self._definir_status(
                "Não foi possível atualizar agora. Tentaremos na próxima vez."
            ))

    def _oferecer_reinicio(self):
        self._definir_status("✓ Atualização instalada.")
        reabrir = messagebox.askyesno(
            "Atualização disponível",
            "Uma versão mais nova do programa foi instalada.\n\n"
            "Deseja reabrir agora para aplicar as novidades?",
            parent=self,
        )
        if reabrir:
            log.info("Reiniciando para aplicar atualização.")
            self.destroy()
            atualizador.reiniciar()


def _executar_cli(argumentos):
    """Modo linha de comando (sem janela). Útil para automação e para testar
    o executável gerado. Uso:

        app.exe caminho_do_extrato.pdf       -> processa e mostra no console
        app.exe --selftest                   -> processa o exemplo embutido
    """
    if argumentos[0] == "--selftest":
        caminho = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "exemplos", "extrato_exemplo.txt"
        )
        saida = argumentos[1] if len(argumentos) > 1 else None
    else:
        caminho = argumentos[0]
        saida = argumentos[1] if len(argumentos) > 1 else None

    if not os.path.exists(caminho):
        print(f"Arquivo não encontrado: {caminho}")
        return 2

    resultado = processar_arquivo(caminho)
    print(f"Arquivo    : {os.path.basename(resultado.arquivo)}")
    print(f"Transações : {resultado.quantidade}")
    print(f"TOTAL      : {formatar_brl(resultado.total)}")
    print("-" * 60)
    for transacao in resultado.transacoes:
        print(f"  {formatar_brl(transacao.valor):>14}  |  {transacao.descricao}")

    # Opcional: 2º argumento = caminho de saída (.xlsx/.pdf/.csv/.txt)
    if saida:
        exportar(resultado, saida)
        print(f"Exportado para: {saida}")
    return 0


def main():
    configurar_log()
    log.info("Iniciando %s v%s", __app_name__, __version__)

    # Se vier um argumento na linha de comando, roda sem abrir a janela.
    argumentos = [a for a in sys.argv[1:] if a]
    if argumentos:
        sys.exit(_executar_cli(argumentos))

    try:
        app = AppExtrato()
        app.mainloop()
    except Exception:
        # Registra qualquer falha grave de inicialização e mostra ao usuário.
        log.exception("Falha grave ao iniciar a interface")
        try:
            messagebox.showerror(
                "Erro ao iniciar",
                "O programa encontrou um erro ao abrir.\n\n"
                f"Um registro foi salvo em:\n{CAMINHO_LOG}",
            )
        except Exception:
            print(f"Erro ao iniciar. Veja o log em: {CAMINHO_LOG}")
        sys.exit(1)


if __name__ == "__main__":
    main()
