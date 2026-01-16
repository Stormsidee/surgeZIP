import zipfile
import os
from datetime import datetime
from pathlib import Path

class ZipArchiver:
    @staticmethod
    def get_archive_contents(zip_path, current_path=""):
        """
        Получить содержимое указанного пути в архиве
        Возвращает: {'folders': [], 'files': []}
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # Получаем все элементы в текущем пути
                items = {}
                
                for file_info in zipf.infolist():
                    # Преобразуем путь в правильный формат
                    filepath = file_info.filename
                    
                    # Убираем начальный слэш если есть
                    if filepath.startswith('/'):
                        filepath = filepath[1:]
                    
                    # Проверяем, принадлежит ли файл текущему пути
                    if current_path == "":
                        # Корневой уровень
                        if '/' not in filepath or filepath.endswith('/'):
                            # Это корневой файл или папка
                            parts = filepath.rstrip('/').split('/')
                            if len(parts) == 1:
                                # Файл или папка в корне
                                name = parts[0]
                                if file_info.filename.endswith('/'):
                                    # Папка
                                    items.setdefault('folders', []).append({
                                        'name': name,
                                        'full_path': file_info.filename,
                                        'date': datetime(*file_info.date_time)
                                    })
                                else:
                                    # Файл
                                    items.setdefault('files', []).append({
                                        'name': name,
                                        'full_path': file_info.filename,
                                        'size': file_info.file_size,
                                        'compressed_size': file_info.compress_size,
                                        'date': datetime(*file_info.date_time)
                                    })
                    else:
                        # Вложенный путь
                        if filepath.startswith(current_path):
                            # Убираем текущий путь из имени
                            relative_path = filepath[len(current_path):]
                            
                            if relative_path == "":
                                continue
                                
                            parts = relative_path.rstrip('/').split('/')
                            if len(parts) == 1:
                                # Файл или папка в текущем пути
                                name = parts[0]
                                if name == "":
                                    continue
                                    
                                if file_info.filename.endswith('/'):
                                    # Папка
                                    items.setdefault('folders', []).append({
                                        'name': name,
                                        'full_path': file_info.filename,
                                        'date': datetime(*file_info.date_time)
                                    })
                                else:
                                    # Файл
                                    items.setdefault('files', []).append({
                                        'name': name,
                                        'full_path': file_info.filename,
                                        'size': file_info.file_size,
                                        'compressed_size': file_info.compress_size,
                                        'date': datetime(*file_info.date_time)
                                    })
                
                return items
                
        except Exception as e:
            print(f"Ошибка при чтении архива: {e}")
            return {'folders': [], 'files': [], 'error': str(e)}
    
    @staticmethod
    def get_flat_structure(zip_path):
        """
        Получить плоскую структуру архива для отображения
        Возвращает список всех элементов с их путями
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                structure = []
                
                for file_info in zipf.infolist():
                    filename = file_info.filename.rstrip('/')
                    is_dir = file_info.filename.endswith('/')
                    
                    structure.append({
                        'name': os.path.basename(filename) if not is_dir else os.path.basename(filename.rstrip('/')),
                        'full_path': file_info.filename,
                        'is_dir': is_dir,
                        'size': 0 if is_dir else file_info.file_size,
                        'date': datetime(*file_info.date_time)
                    })
                
                return structure
        except Exception as e:
            print(f"Ошибка: {e}")
            return []
    
    @staticmethod
    def list_directory(zip_path, dir_path=""):
        """
        Показать содержимое указанной директории
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                folders = set()
                files = []
                
                # Нормализуем путь
                if dir_path and not dir_path.endswith('/'):
                    dir_path += '/'
                
                for file_info in zipf.infolist():
                    filepath = file_info.filename
                    
                    # Проверяем, находится ли файл в указанной директории
                    if dir_path == "":
                        # Корневая директория
                        if '/' not in filepath:
                            # Файл в корне
                            if not file_info.filename.endswith('/'):
                                files.append({
                                    'name': filepath,
                                    'full_path': filepath,
                                    'size': file_info.file_size,
                                    'date': datetime(*file_info.date_time)
                                })
                        else:
                            # Папка в корне
                            first_folder = filepath.split('/')[0]
                            if file_info.filename.endswith('/'):
                                folders.add(first_folder)
                    else:
                        # Проверяем вложенность
                        if filepath.startswith(dir_path):
                            relative_path = filepath[len(dir_path):]
                            if relative_path == "":
                                continue
                                
                            # Разделяем на части
                            parts = relative_path.rstrip('/').split('/')
                            
                            if len(parts) == 1:
                                # Файл или папка в текущей директории
                                name = parts[0]
                                if name == "":
                                    continue
                                    
                                if file_info.filename.endswith('/'):
                                    # Это папка
                                    folders.add(name)
                                else:
                                    # Это файл
                                    files.append({
                                        'name': name,
                                        'full_path': filepath,
                                        'size': file_info.file_size,
                                        'date': datetime(*file_info.date_time)
                                    })
                
                return {
                    'folders': sorted(list(folders)),
                    'files': sorted(files, key=lambda x: x['name'])
                }
                
        except Exception as e:
            print(f"Ошибка при чтении директории: {e}")
            return {'folders': [], 'files': []}