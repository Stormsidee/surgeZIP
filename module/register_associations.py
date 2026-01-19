import winreg
import os
import sys
import ctypes

def is_admin():
    """Проверка прав администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def register_file_associations():
    """Регистрация ассоциаций файлов в реестре Windows"""
    
    if not is_admin():
        print("Требуются права администратора!")
        # Перезапуск с правами администратора
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        return
    
    # Ищем скомпилированный exe файл
    app_path = None
    
    # Проверяем в текущей директории
    if os.path.exists("surgeZIP.exe"):
        app_path = os.path.abspath("surgeZIP.exe")
    # Проверяем в папке build
    elif os.path.exists("build/surgeZIP/surgeZIP.exe"):
        app_path = os.path.abspath("build/surgeZIP/surgeZIP.exe")
    # Если exe не найден, используем python
    else:
        main_py = os.path.abspath("main.py")
        app_path = f'"{sys.executable}" "{main_py}"'
        print("EXE файл не найден, используется Python для регистрации")
    
    # Расширения для регистрации
    extensions = {
        '.zip': 'surgeZIP.ZIP',
        '.rar': 'surgeZIP.RAR', 
        '.7z': 'surgeZIP.7Z',
        '.tar': 'surgeZIP.TAR',
        '.gz': 'surgeZIP.GZ',
        '.bz2': 'surgeZIP.BZ2'
    }
    
    try:
        # Основной ключ программы
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "surgeZIP") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Файл surgeZIP")
            winreg.SetValueEx(key, "FriendlyTypeName", 0, winreg.REG_SZ, "Архив surgeZIP")
            
        # Команда открытия
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                            "surgeZIP\\shell\\open\\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'{app_path} "%1"')
        
        # Иконка
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                            "surgeZIP\\DefaultIcon") as key:
            # Нужно будет указать путь к иконке .ico
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, app_path + ",0")
        
        # Регистрируем расширения
        for ext, prog_id in extensions.items():
            # Связываем расширение с нашей программой
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ext) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, prog_id)
            
            # Создаем запись для этого типа
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, prog_id) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, 
                                f"Архив {ext.upper()[1:]}")
            
            # Команда открытия для этого типа
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                                f"{prog_id}\\shell\\open\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'{app_path} "%1"')
            
            # Добавляем команду "Extract" в контекстное меню
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                                f"{prog_id}\\shell\\extract") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Open with surgeZIP")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, app_path if app_path.endswith('.exe') else f'"{app_path}"')
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                                f"{prog_id}\\shell\\extract\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'{app_path} "%1"')
            
            # Добавляем команду "Extract to" в контекстное меню
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                                f"{prog_id}\\shell\\extractto") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Extract to...")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, app_path if app_path.endswith('.exe') else f'"{app_path}"')
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                                f"{prog_id}\\shell\\extractto\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'{app_path} --extract-to "%1"')
        
        # Добавляем команду "Compress" в контекстное меню для всех файлов и папок
        # Для папок
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                            "Directory\\Background\\shell\\surgeZIPCompress") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Compress with surgeZIP")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, app_path + ",0")
        
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                            "Directory\\Background\\shell\\surgeZIPCompress\\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'{app_path} --compress %V')
        
        # Для файлов
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                            "*\\shell\\surgeZIPCompress") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Compress with surgeZIP")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, app_path + ",0")
        
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                            "*\\shell\\surgeZIPCompress\\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'{app_path} --compress "%1"')
        
        # Для папок (не background)
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                            "Directory\\shell\\surgeZIPCompress") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Compress with surgeZIP")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, app_path + ",0")
        
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                            "Directory\\shell\\surgeZIPCompress\\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'{app_path} --compress "%1"')
        
        print("Ассоциации файлов и контекстное меню успешно зарегистрированы!")
        print("Перезапустите проводник или компьютер для применения изменений.")
        
        # Обновляем проводник
        try:
            import subprocess
            subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'])
            subprocess.Popen('explorer.exe')
        except:
            pass
            
    except Exception as e:
        print(f"Ошибка при регистрации: {e}")

def unregister_file_associations():
    """Удаление ассоциаций файлов"""
    if not is_admin():
        print("Требуются права администратора!")
        return
    
    extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
    prog_ids = ['surgeZIP', 'surgeZIP.ZIP', 'surgeZIP.RAR', 
                'surgeZIP.7Z', 'surgeZIP.TAR', 
                'surgeZIP.GZ', 'surgeZIP.BZ2']
    
    try:
        for ext in extensions:
            try:
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, ext)
            except:
                pass
        
        for prog_id in prog_ids:
            try:
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell\\extractto\\command")
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell\\extractto")
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell\\open\\command")
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\DefaultIcon")
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell\\open")
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell")
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, prog_id)
            except:
                pass
        
        # Удаляем команды сжатия
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, "Directory\\Background\\shell\\surgeZIPCompress\\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, "Directory\\Background\\shell\\surgeZIPCompress")
        except:
            pass
        
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, "*\\shell\\surgeZIPCompress\\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, "*\\shell\\surgeZIPCompress")
        except:
            pass
        
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, "Directory\\shell\\surgeZIPCompress\\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, "Directory\\shell\\surgeZIPCompress")
        except:
            pass
        
        print("Ассоциации файлов и контекстное меню удалены!")
        
    except Exception as e:
        print(f"Ошибка при удалении: {e}")

if __name__ == "__main__":
    print("1 - Зарегистрировать ассоциации файлов")
    print("2 - Удалить ассоциации файлов")
    choice = input("Выберите действие: ")
    
    if choice == "1":
        register_file_associations()
    elif choice == "2":
        unregister_file_associations()