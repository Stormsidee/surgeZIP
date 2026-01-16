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
    
    # Путь к исполняемому файлу (после сборки в .exe)
    app_path = os.path.abspath(sys.argv[0])
    if not app_path.endswith('.exe'):
        # В режиме разработки используем python
        app_path = f'"{sys.executable}" "{app_path}"'
    
    # Расширения для регистрации
    extensions = {
        '.zip': 'ModernArchiver.ZIP',
        '.rar': 'ModernArchiver.RAR', 
        '.7z': 'ModernArchiver.7Z',
        '.tar': 'ModernArchiver.TAR',
        '.gz': 'ModernArchiver.GZ',
        '.bz2': 'ModernArchiver.BZ2'
    }
    
    try:
        # Основной ключ программы
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "ModernArchiver") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Файл ModernArchiver")
            winreg.SetValueEx(key, "FriendlyTypeName", 0, winreg.REG_SZ, "Архив ModernArchiver")
            
        # Команда открытия
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                            "ModernArchiver\\shell\\open\\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'{app_path} "%1"')
        
        # Иконка
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 
                            "ModernArchiver\\DefaultIcon") as key:
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
        
        print("Ассоциации файлов успешно зарегистрированы!")
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
    prog_ids = ['ModernArchiver', 'ModernArchiver.ZIP', 'ModernArchiver.RAR', 
                'ModernArchiver.7Z', 'ModernArchiver.TAR', 
                'ModernArchiver.GZ', 'ModernArchiver.BZ2']
    
    try:
        for ext in extensions:
            try:
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, ext)
            except:
                pass
        
        for prog_id in prog_ids:
            try:
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell\\open\\command")
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\DefaultIcon")
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell\\open")
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell")
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, prog_id)
            except:
                pass
        
        print("Ассоциации файлов удалены!")
        
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