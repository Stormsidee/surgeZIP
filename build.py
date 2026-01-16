import sys
import os
import shutil
import subprocess

def build_project():
    # Создаем папки
    os.makedirs("dist", exist_ok=True)
    os.makedirs("installer", exist_ok=True)
    
    print("1. Установка зависимостей...")
    subprocess.run([sys.executable, "-m", "pip", "install", "PyQt5", "pywin32", "pyinstaller"])
    
    print("2. Сборка в .exe...")
    # PyInstaller
    subprocess.run([
        "pyinstaller",
        "--windowed",
        "--onefile",
        "--icon=icon.ico",  # Нужно создать иконку
        "--name=ModernArchiver",
        "--add-data=zip_module.py;.",
        "--add-data=archive_manager.py;.",
        "main.py"
    ])
    
    print("3. Копирование файлов...")
    if os.path.exists("dist/ModernArchiver.exe"):
        shutil.copy("dist/ModernArchiver.exe", "installer/")
    
    print("4. Создание установщика...")
    print("Для создания установщика:")
    print("1. Установите Inno Setup с официального сайта")
    print("2. Запустите Inno Setup Compiler")
    print("3. Откройте файл installer.iss")
    print("4. Нажмите 'Build'")
    
    print("\nГотово! Установщик можно создать в папке 'installer'")

if __name__ == "__main__":
    build_project()