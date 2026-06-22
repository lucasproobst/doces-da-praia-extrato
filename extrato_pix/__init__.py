"""
Pacote 'extrato_pix' — motor de leitura e cálculo de PIX recebidos.

Organização (cada arquivo tem UMA responsabilidade, para facilitar ajustes):

    config.py      -> ⚙️  Configurações ajustáveis (palavras-chave, regex, etc.)
    normalize.py   ->     Normalização de texto (remove acentos / maiúsculas)
    valores.py     ->     Reconhecimento e formatação de valores em R$ (padrão BR)
    leitores.py    ->     Leitura dos arquivos (PDF, CSV, XLSX/XLS, TXT) -> linhas
    extrator.py    ->     Motor que junta tudo e devolve o resultado
    exportar.py    ->     Exportação do resultado em .csv ou .txt

Para adaptar ao formato do SEU banco, normalmente basta editar 'config.py'.
"""

__version__ = "1.7.2"
__app_name__ = "Doces da Praia - Calcular Extrato"
