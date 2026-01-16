import subprocess
import os
import zipfile
import tempfile

class ArchiveManager:
    def __init__(self, sevenzip_path=None):
        # Автоматический поиск 7-Zip
        self.sevenzip_path = sevenzip_path or self.find_7zip()
    
    def find_7zip(self):
        """Автоматический поиск 7-Zip в системе"""
        possible_paths = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe",
            r"C:\Program Files\7-Zip\7zG.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Если не найден, можно скачать или показать сообщение
        return None
    
    def extract_archive(self, archive_path, output_dir=None, password=None):
        """Распаковка любого архива через 7-Zip"""
        if output_dir is None:
            output_dir = os.path.splitext(archive_path)[0]
        
        os.makedirs(output_dir, exist_ok=True)
        
        if archive_path.endswith('.zip') and not password:
            # Используем встроенный zipfile для ZIP
            return self._extract_zip(archive_path, output_dir)
        elif self.sevenzip_path:
            # Используем 7-Zip для всех остальных форматов
            return self._extract_with_7zip(archive_path, output_dir, password)
        else:
            raise Exception("7-Zip не найден!")
    
    def _extract_zip(self, archive_path, output_dir):
        """Распаковка ZIP через zipfile"""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(output_dir)
            return True, f"Распаковано в: {output_dir}"
        except Exception as e:
            return False, str(e)
    
    def _extract_with_7zip(self, archive_path, output_dir, password=None):
        """Распаковка через 7-Zip"""
        cmd = [self.sevenzip_path, 'x', archive_path, f'-o{output_dir}']
        
        if password:
            cmd.append(f'-p{password}')
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                return True, f"Распаковано в: {output_dir}"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def create_archive(self, files, output_path, format='zip', compression_level=5):
        """Создание архива любого формата"""
        if format == 'zip':
            return self._create_zip(files, output_path)
        elif self.sevenzip_path:
            return self._create_with_7zip(files, output_path, format, compression_level)
        else:
            raise Exception("7-Zip не найден!")
    
    def _create_zip(self, files, output_path):
        """Создание ZIP архива"""
        from zip_module import ZipArchiver
        return ZipArchiver.create_zip(files, output_path)
    
    def _create_with_7zip(self, files, output_path, format, compression_level):
        """Создание архива через 7-Zip"""
        # Создаем временный файл со списком файлов
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for file_path in files:
                f.write(f'"{file_path}"\n')
            list_file = f.name
        
        cmd = [
            self.sevenzip_path, 
            'a',  # добавить в архив
            f'-t{format}',  # тип архива
            f'-mx{compression_level}',  # уровень сжатия
            output_path,
            f'@{list_file}'  # файл со списком
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Удаляем временный файл
            os.unlink(list_file)
            
            if result.returncode == 0:
                return True, f"Архив создан: {output_path}"
            else:
                return False, result.stderr
        except Exception as e:
            if os.path.exists(list_file):
                os.unlink(list_file)
            return False, str(e)
    
    def list_contents(self, archive_path):
        """Получение списка файлов в архиве"""
        if archive_path.endswith('.zip'):
            from zip_module import ZipArchiver
            return ZipArchiver.get_zip_info(archive_path)
        elif self.sevenzip_path:
            return self._list_with_7zip(archive_path)
        else:
            return {"error": "7-Zip не найден!"}
    
    def _list_with_7zip(self, archive_path):
        """Получение списка через 7-Zip"""
        cmd = [self.sevenzip_path, 'l', archive_path]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            return {"raw_output": result.stdout, "files": self._parse_7zip_output(result.stdout)}
        except Exception as e:
            return {"error": str(e)}
    
    def _parse_7zip_output(self, output):
        """Парсинг вывода 7-Zip"""
        # Здесь можно разобрать вывод 7-Zip
        # Возвращаем упрощенную структуру
        lines = output.split('\n')
        files = []
        
        for line in lines:
            if line.strip() and not line.startswith('-') and not line.startswith('Date'):
                parts = line.split()
                if len(parts) >= 4:
                    files.append({
                        "name": ' '.join(parts[5:]),
                        "size": parts[3],
                        "compressed": parts[2]
                    })
        
        return files