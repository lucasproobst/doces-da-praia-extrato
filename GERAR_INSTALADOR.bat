@echo off
setlocal enableextensions enabledelayedexpansion
title Doces da Praia - Gerar instalador do Windows

REM =====================================================================
REM   Doces da Praia - Calcular Extrato
REM   GERA TUDO automaticamente no Windows (basta DAR UM DUPLO CLIQUE).
REM   Se faltar o Python ou o Inno Setup, o proprio arquivo os instala
REM   automaticamente (via winget) - sem o usuario precisar fazer nada.
REM =====================================================================

cd /d "%~dp0"

REM Arquivo de log: tudo que acontecer (e qualquer erro) fica registrado aqui.
set "LOG=%~dp0build_log.txt"
echo Doces da Praia - registro de geracao do instalador> "%LOG%"
echo Iniciado em %DATE% %TIME%>> "%LOG%"
echo.>> "%LOG%"

echo.
echo ============================================================
echo   Doces da Praia - Calcular Extrato
echo   Gerador automatico do instalador para Windows
echo ============================================================
echo.
echo  (Um registro detalhado esta sendo salvo em build_log.txt)
echo.

REM ---- 1) Garante o Python -------------------------------------------
echo [1/6] Verificando o Python...
call :garante_python

set "PYCMD="
python --version >nul 2>&1 && set "PYCMD=python"
if not defined PYCMD ( py -3 --version >nul 2>&1 && set "PYCMD=py -3" )

if not defined PYCMD (
    echo.
    echo  O Python foi instalado agora, mas o Windows so reconhece o novo
    echo  programa em uma NOVA janela.
    echo.
    echo  >> Por favor, FECHE esta janela e clique no arquivo NOVAMENTE. <<
    echo.
    pause
    exit /b 1
)
for /f "delims=" %%v in ('%PYCMD% --version') do echo  Usando: %%v

REM ---- 2) Ambiente virtual -------------------------------------------
echo.
echo [2/6] Preparando ambiente virtual (.venv)...
if not exist ".venv\Scripts\python.exe" (
    %PYCMD% -m venv .venv
    if errorlevel 1 goto erro
)
set "PY=.venv\Scripts\python.exe"

REM ---- 3) Dependencias -----------------------------------------------
echo.
echo [3/6] Instalando dependencias (na primeira vez pode demorar)...
"%PY%" -m pip install --upgrade pip >> "%LOG%" 2>&1
"%PY%" -m pip install -r requirements.txt >> "%LOG%" 2>&1
if errorlevel 1 goto erro

REM ---- 4) Icone ------------------------------------------------------
echo.
echo [4/6] Gerando o icone do programa...
"%PY%" make_icon.py >> "%LOG%" 2>&1
if errorlevel 1 goto erro

REM ---- 5) Executavel (PyInstaller) -----------------------------------
echo.
echo [5/6] Compilando o executavel (.exe)... aguarde, pode levar alguns minutos.
"%PY%" -m PyInstaller --noconfirm --onefile --windowed ^
  --name "Doces da Praia - Calcular Extrato" ^
  --icon "assets\icon.ico" ^
  --add-data "assets\icon.ico;assets" ^
  --collect-all customtkinter ^
  --collect-all pdfplumber ^
  --collect-all pdfminer ^
  --collect-all openpyxl ^
  --collect-all fpdf ^
  app.py >> "%LOG%" 2>&1
if errorlevel 1 goto erro

if not exist "dist\Doces da Praia - Calcular Extrato.exe" (
    echo  ERRO: o executavel nao foi gerado.
    goto erro
)
echo  OK: dist\Doces da Praia - Calcular Extrato.exe

REM ---- 6) Instalador (Inno Setup) ------------------------------------
echo.
echo [6/6] Gerando o instalador com o Inno Setup...
call :detecta_iscc
if defined ISCC goto compila_inno

echo  Inno Setup nao encontrado. Instalando automaticamente...
where winget >nul 2>&1
if errorlevel 1 goto sem_inno
winget install -e --id JRSoftware.InnoSetup --accept-source-agreements --accept-package-agreements >> "%LOG%" 2>&1
call :detecta_iscc
if defined ISCC goto compila_inno
goto sem_inno

:compila_inno
echo  Usando: !ISCC!
"!ISCC!" installer.iss >> "%LOG%" 2>&1
if errorlevel 1 goto erro
goto sucesso

REM --------------------------------------------------------------------
:sucesso
echo.
echo ============================================================
echo   PRONTO! Tudo gerado com sucesso.
echo.
echo   Programa standalone (roda sozinho, sem instalar):
echo       dist\Doces da Praia - Calcular Extrato.exe
echo.
echo   Instalador para distribuir/instalar:
echo       instalador\DocesDaPraia-Setup.exe
echo ============================================================
echo.
pause
exit /b 0

REM --------------------------------------------------------------------
:sem_python
echo.
echo ------------------------------------------------------------
echo  Nao foi possivel instalar o Python automaticamente
echo  (o 'winget' nao esta disponivel neste Windows).
echo.
echo  Instale o Python manualmente em:
echo      https://www.python.org/downloads/
echo  (marque "Add Python to PATH") e rode este arquivo novamente.
echo ------------------------------------------------------------
echo.
pause
exit /b 1

REM --------------------------------------------------------------------
:sem_inno
echo.
echo ------------------------------------------------------------
echo  AVISO: nao foi possivel usar o Inno Setup automaticamente.
echo.
echo  Mas o PROGRAMA JA ESTA PRONTO e funciona sozinho (sem instalar):
echo      dist\Doces da Praia - Calcular Extrato.exe
echo.
echo  Para gerar TAMBEM o instalador (setup.exe):
echo    1) Instale o Inno Setup: https://jrsoftware.org/isdl.php
echo    2) Rode este arquivo novamente.
echo ------------------------------------------------------------
echo.
pause
exit /b 0

REM --------------------------------------------------------------------
:erro
echo.
echo ============================================================
echo  *** Ocorreu um erro durante a geracao. ***
echo.
echo  Foi salvo um registro detalhado em:
echo      %LOG%
echo.
echo  Abra o arquivo "build_log.txt" para ver o motivo, ou envie-o
echo  para o suporte que a gente identifica o problema.
echo ============================================================
echo.
pause
exit /b 1

REM ====================================================================
REM  SUB-ROTINAS
REM ====================================================================

REM  Garante que o Python exista; se nao, instala via winget.
:garante_python
python --version >nul 2>&1 && goto :eof
py -3 --version >nul 2>&1 && goto :eof
echo  Python nao encontrado. Instalando automaticamente (pode pedir confirmacao)...
where winget >nul 2>&1
if errorlevel 1 goto sem_python
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements >> "%LOG%" 2>&1
REM Torna o Python visivel JA nesta janela (sem precisar reabrir):
set "PATH=%PATH%;%LocalAppData%\Programs\Python\Python312;%LocalAppData%\Programs\Python\Python312\Scripts"
set "PATH=%PATH%;%LocalAppData%\Programs\Python\Python313;%LocalAppData%\Programs\Python\Python311"
call :refresh_path
goto :eof

REM  Reconstroi o PATH a partir do registro (pega programas recem-instalados).
:refresh_path
for /f "skip=2 tokens=2,*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "PATH_SYS=%%b"
for /f "skip=2 tokens=2,*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "PATH_USR=%%b"
if defined PATH_SYS set "PATH=%PATH_SYS%"
if defined PATH_USR set "PATH=%PATH%;%PATH_USR%"
goto :eof

REM  Procura o compilador do Inno Setup (ISCC.exe).
:detecta_iscc
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 5\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 5\ISCC.exe"
if not defined ISCC for /f "delims=" %%i in ('where iscc 2^>nul') do set "ISCC=%%i"
goto :eof
