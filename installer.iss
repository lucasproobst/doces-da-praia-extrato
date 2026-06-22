; ===========================================================================
;  Script Inno Setup - "Doces da Praia - Calcular Extrato"
;  Gera um instalador (setup.exe) a partir do .exe criado pelo PyInstaller.
;
;  Como usar:
;    1) Instale o Inno Setup:  https://jrsoftware.org/isdl.php
;    2) Gere antes o executavel (build.bat), criando "dist\...exe".
;    3) Abra ESTE arquivo no Inno Setup e clique em "Compile" (Ctrl+F9).
;    4) O instalador aparecera na pasta "instalador\DocesDaPraia-Setup.exe".
; ===========================================================================

#define MyAppName "Doces da Praia - Calcular Extrato"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Doces da Praia"
#define MyAppExeName "Doces da Praia - Calcular Extrato.exe"

[Setup]
; AppId identifica o programa de forma unica (nao mude depois de publicar).
AppId={{8E5C2A91-4F7B-4D2E-9A36-7C1B0E5D9A22}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Doces da Praia
DefaultGroupName=Doces da Praia
DisableProgramGroupPage=yes
OutputDir=instalador
OutputBaseFilename=DocesDaPraia-Setup
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Instala em Arquivos de Programas; pede permissao de administrador.
PrivilegesRequired=admin

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar um atalho na Área de Trabalho"; \
    GroupDescription: "Atalhos adicionais:"

[Files]
; O executavel gerado pelo PyInstaller (modo --onefile -> um unico arquivo).
Source: "dist\Doces da Praia - Calcular Extrato.exe"; DestDir: "{app}"; Flags: ignoreversion
; (Opcional) exemplos de extrato para teste:
Source: "exemplos\*"; DestDir: "{app}\exemplos"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Oferece abrir o programa logo apos a instalacao.
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir o {#MyAppName} agora"; \
    Flags: nowait postinstall skipifsilent
