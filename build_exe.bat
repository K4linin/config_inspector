@echo off
echo =========================================
echo  Config Inspector — сборка в .exe
echo =========================================
echo.

REM Проверяем наличие Python
python --version 2>nul
if errorlevel 1 (
    echo [ОШИБКА] Python не найден. Установи Python 3.11+ с python.org
    pause
    exit /b 1
)

REM Устанавливаем зависимости
echo [1/3] Устанавливаем зависимости...
pip install PyQt6 pyinstaller --quiet
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости
    pause
    exit /b 1
)

echo [2/3] Запускаем PyInstaller...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "ConfigInspector" ^
    --hidden-import="PyQt6.QtCore" ^
    --hidden-import="PyQt6.QtGui" ^
    --hidden-import="PyQt6.QtWidgets" ^
    --hidden-import="PyQt6.sip" ^
    main.py

if errorlevel 1 (
    echo [ОШИБКА] PyInstaller завершился с ошибкой
    pause
    exit /b 1
)

echo.
echo [3/3] Готово!
echo EXE файл находится в папке: dist\ConfigInspector.exe
echo.
pause
