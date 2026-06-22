@echo off
setlocal enableextensions enabledelayedexpansion
title Doces da Praia - Instalar (com atualizacao automatica)

REM =====================================================================
REM   Doces da Praia - Calcular Extrato
REM   INSTALA o programa no modo "atualizacao automatica":
REM     - garante o Python (instala via winget se faltar)
REM     - prepara as dependencias
REM     - cria atalhos na Area de Trabalho e no Menu Iniciar
REM   Depois disso, toda vez que abrir, o programa se atualiza sozinho
REM   pegando a ultima versao publicada no GitHub.
REM =====================================================================

cd /d "%~dp0"
set "APPDIR=%~dp0"
if "%APPDIR:~-1%"=="\" set "APPDIR=%APPDIR:~0,-1%"

set "LOG=%APPDIR%\install_log.txt"
echo Doces da Praia - registro de instalacao> "%LOG%"
echo Iniciado em %DATE% %TIME%>> "%LOG%"
echo.>> "%LOG%"

echo.
echo ============================================================
echo   Doces da Praia - Instalacao (atualizacao automatica)
echo ============================================================
echo  (Um registro detalhado esta sendo salvo em install_log.txt)
echo.

REM ---- 1) Python ----
echo [1/4] Verificando o Python...
call :garante_python
set "PYCMD="
python --version >nul 2>&1 && set "PYCMD=python"
if not defined PYCMD ( py -3 --version >nul 2>&1 && set "PYCMD=py -3" )
if not defined PYCMD (
    echo.
    echo  O Python foi instalado agora, mas so e reconhecido em uma NOVA janela.
    echo  >> Por favor, FECHE esta janela e clique no INSTALAR novamente. ^<^<
    echo.
    pause
    exit /b 1
)
for /f "delims=" %%v in ('%PYCMD% --version') do echo  Usando: %%v

REM ---- 2) Ambiente virtual + dependencias ----
echo.
echo [2/4] Preparando dependencias (na primeira vez pode demorar)...
if not exist ".venv\Scripts\python.exe" (
    %PYCMD% -m venv .venv >> "%LOG%" 2>&1
    if errorlevel 1 goto erro
)
set "PY=.venv\Scripts\python.exe"
"%PY%" -m pip install --upgrade pip >> "%LOG%" 2>&1
"%PY%" -m pip install -r requirements.txt >> "%LOG%" 2>&1
if errorlevel 1 goto erro

REM ---- 3) Icone ----
echo.
echo [3/4] Gerando o icone...
"%PY%" make_icon.py >> "%LOG%" 2>&1

REM ---- 4) Atalhos ----
echo.
echo [4/4] Criando atalhos (Area de Trabalho e Menu Iniciar)...
powershell -NoProfile -ExecutionPolicy Bypass -File "criar_atalho.ps1" "%APPDIR%" >> "%LOG%" 2>&1
if errorlevel 1 goto erro

echo.
echo ============================================================
echo   PRONTO! Instalacao concluida.
echo.
echo   - Foi criado o atalho "Doces da Praia" na Area de Trabalho.
echo   - Ao abrir, o programa verifica e baixa atualizacoes sozinho.
echo ============================================================
echo.

REM Abre o programa agora (sem janela preta).
set "PYW=%PY:python.exe=pythonw.exe%"
start "" "%PYW%" app.py
pause
exit /b 0

REM --------------------------------------------------------------------
:sem_python
echo.
echo ------------------------------------------------------------
echo  Nao foi possivel instalar o Python automaticamente
echo  (o 'winget' nao esta disponivel neste Windows).
echo  Instale manualmente em https://www.python.org/downloads/
echo  (marque "Add Python to PATH") e rode este arquivo de novo.
echo ------------------------------------------------------------
echo.
pause
exit /b 1

REM --------------------------------------------------------------------
:erro
echo.
echo ============================================================
echo  *** Ocorreu um erro durante a instalacao. ***
echo  Veja o arquivo de log:  %LOG%
echo ============================================================
echo.
pause
exit /b 1

REM ====================================================================
REM  SUB-ROTINAS
REM ====================================================================
:garante_python
python --version >nul 2>&1 && goto :eof
py -3 --version >nul 2>&1 && goto :eof
echo  Python nao encontrado. Instalando automaticamente (pode pedir confirmacao)...
where winget >nul 2>&1
if errorlevel 1 goto sem_python
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements >> "%LOG%" 2>&1
set "PATH=%PATH%;%LocalAppData%\Programs\Python\Python312;%LocalAppData%\Programs\Python\Python312\Scripts"
set "PATH=%PATH%;%LocalAppData%\Programs\Python\Python313;%LocalAppData%\Programs\Python\Python311"
call :refresh_path
goto :eof

:refresh_path
for /f "skip=2 tokens=2,*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "PATH_SYS=%%b"
for /f "skip=2 tokens=2,*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "PATH_USR=%%b"
if defined PATH_SYS set "PATH=%PATH_SYS%"
if defined PATH_USR set "PATH=%PATH%;%PATH_USR%"
goto :eof
