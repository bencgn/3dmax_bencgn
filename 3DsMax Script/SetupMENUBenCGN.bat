@echo off
setlocal enabledelayedexpansion
color 0A
echo =======================================================
echo           BENCGNDEMO 3ds Max Menu Installer
echo =======================================================
echo.

set "sourceFile=%~dp0Menu.ms"

if not exist "!sourceFile!" (
    color 0C
    echo ERROR: Menu.ms not found in the current directory!
    echo Please make sure SetupMENUBenCGN.bat is in the same folder as Menu.ms.
    echo.
    pause
    exit /b 1
)

set "baseDir=%LOCALAPPDATA%\Autodesk\3dsMax"

if not exist "!baseDir!" (
    color 0C
    echo ERROR: 3ds Max configuration folder not found!
    echo.
    pause
    exit /b 1
)

set "copied=0"

echo Dang quet cac phien ban 3ds Max tren may...
for /d %%D in ("!baseDir!\*") do (
    set "targetDir=%%D\ENU\scripts\startup"
    if exist "!targetDir!" (
        echo [*] Da tim thay: "%%~nxD"
        copy /Y "!sourceFile!" "!targetDir!\BENCGNDEMO_Menu.ms" >nul
        set /a copied+=1
    )
)

echo.
if !copied! gtr 0 (
    echo [THANG CONG] Da cai dat Menu vao !copied! phien ban 3ds Max.
    echo Ban co the mo 3ds Max len, Menu BENCGNDEMO se tu dong xuat hien!
) else (
    color 0C
    echo [THAT BAI] Khong tim thay thu muc cai dat startup nao cua 3ds Max.
)
echo.
pause
