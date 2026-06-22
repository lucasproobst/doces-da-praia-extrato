# Cria atalhos do "Doces da Praia" na Area de Trabalho e no Menu Iniciar.
# Chamado pelo INSTALAR.bat. Recebe a pasta do aplicativo como parametro.
param([string]$AppDir)

$shell   = New-Object -ComObject WScript.Shell
$pythonw = Join-Path $AppDir ".venv\Scripts\pythonw.exe"
$icon    = Join-Path $AppDir "assets\icon.ico"

function New-Atalho([string]$Caminho) {
    $lnk = $shell.CreateShortcut($Caminho)
    $lnk.TargetPath       = $pythonw
    $lnk.Arguments        = "app.py"
    $lnk.WorkingDirectory = $AppDir
    if (Test-Path $icon) { $lnk.IconLocation = $icon }
    $lnk.Description       = "Doces da Praia - Calcular Extrato"
    $lnk.Save()
}

$desktop = [Environment]::GetFolderPath('Desktop')
New-Atalho (Join-Path $desktop "Doces da Praia.lnk")

$menu = [Environment]::GetFolderPath('Programs')
New-Atalho (Join-Path $menu "Doces da Praia.lnk")

Write-Output "Atalhos criados em: $desktop e $menu"
