from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QRubberBand, QApplication
from PyQt5.QtCore import Qt, QMimeData, QUrl, QRect, QPoint
from PyQt5.QtGui import QDrag, QMouseEvent
import os
import tempfile
import shutil
import zipfile

class DragDropTreeWidget(QTreeWidget):
    """QTreeWidget с поддержкой drag-and-drop файлов и папок + выделение области"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.archive_path = None
        self.setDragEnabled(True)
        self.setSelectionMode(QTreeWidget.ExtendedSelection)
        
        # Для выделения области
        self.rubber_band = None
        self.rubber_band_start = None
        self.drag_start_pos = None
        
        # Включаем отслеживание мыши для выделения области
        self.setMouseTracking(False)
        
    def set_archive_path(self, archive_path):
        """Установить путь к текущему архиву"""
        self.archive_path = archive_path
    
    def mousePressEvent(self, event):
        """Обработка нажатия мыши для выделения области"""
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()
            item = self.itemAt(event.pos())
            
            # Если клик не на элементе - начинаем выделение области
            if not item:
                self.rubber_band_start = event.pos()
                self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
                self.rubber_band.setGeometry(QRect(self.rubber_band_start, QPoint()))
                self.rubber_band.show()
            else:
                # Если клик на элементе - обычное поведение
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Обработка движения мыши для выделения области и начала drag-and-drop"""
        # Обработка выделения области
        if self.rubber_band and self.rubber_band_start:
            # Обновляем область выделения
            rect = QRect(self.rubber_band_start, event.pos()).normalized()
            self.rubber_band.setGeometry(rect)
            
            # Выделяем элементы внутри области
            self.clearSelection()
            for i in range(self.topLevelItemCount()):
                item = self.topLevelItem(i)
                rect_item = self.visualItemRect(item)
                if rect.intersects(rect_item):
                    item.setSelected(True)
        
        # Проверяем начало перетаскивания
        elif self.drag_start_pos and (event.pos() - self.drag_start_pos).manhattanLength() > 10:
            # Начинаем перетаскивание
            selected_items = self.selectedItems()
            if selected_items and self.archive_path:
                mime_data = self.prepare_drag_data(selected_items)
                if mime_data:
                    drag = QDrag(self)
                    drag.setMimeData(mime_data)
                    
                    # Устанавливаем курсор для перетаскивания
                    from PyQt5.QtGui import QCursor
                    drag.setDragCursor(QCursor(Qt.DragMoveCursor).pixmap(), Qt.MoveAction)
                    
                    drag.exec_(Qt.CopyAction)
                    
                    # Сбрасываем позиции
                    self.drag_start_pos = None
                    if self.rubber_band:
                        self.rubber_band.hide()
                        self.rubber_band = None
                    return
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Обработка отпускания мыши"""
        if self.rubber_band:
            self.rubber_band.hide()
            self.rubber_band = None
            self.rubber_band_start = None
        
        if self.drag_start_pos:
            self.drag_start_pos = None
        
        super().mouseReleaseEvent(event)
    
    def prepare_drag_data(self, selected_items):
        """Подготовить данные для перетаскивания выбранных элементов (файлов и папок)"""
        if not selected_items or not self.archive_path:
            return None
        
        # Собираем файлы и папки для перетаскивания
        files_to_drag = []
        folders_to_drag = []
        
        for item in selected_items:
            data = item.data(0, Qt.UserRole)
            if not data:
                continue
            
            if data.get('type') == 'file':
                files_to_drag.append(data['full_path'])
            elif data.get('type') == 'folder':
                folders_to_drag.append({
                    'name': data['name'],
                    'path': data['path'].rstrip('/') + '/'
                })
            # Игнорируем 'up' (..)
        
        if not files_to_drag and not folders_to_drag:
            return None
        
        # Создаем временную директорию
        temp_dir = tempfile.mkdtemp(prefix="archive_drag_")
        temp_files = []
        
        try:
            with zipfile.ZipFile(self.archive_path, 'r') as zipf:
                # Обрабатываем файлы
                for file_path in files_to_drag:
                    try:
                        # Извлекаем файл во временную директорию
                        temp_file_path = os.path.join(temp_dir, os.path.basename(file_path))
                        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
                        
                        with zipf.open(file_path) as source, open(temp_file_path, 'wb') as target:
                            target.write(source.read())
                        
                        temp_files.append(temp_file_path)
                    except Exception as e:
                        print(f"Ошибка при подготовке файла {file_path}: {e}")
                
                # Обрабатываем папки - ВАЖНО: извлекаем ВСЮ папку со структурой!
                for folder_data in folders_to_drag:
                    try:
                        folder_name = folder_data['name']
                        folder_path = folder_data['path']
                        
                        # Создаем папку во временной директории
                        temp_folder_path = os.path.join(temp_dir, folder_name)
                        os.makedirs(temp_folder_path, exist_ok=True)
                        
                        # Находим все файлы в этой папке (включая вложенные)
                        for file_info in zipf.infolist():
                            if file_info.filename.startswith(folder_path):
                                # Относительный путь внутри папки
                                relative_path = file_info.filename[len(folder_path):]
                                if relative_path and not file_info.filename.endswith('/'):
                                    # Полный путь во временной директории
                                    dest_path = os.path.join(temp_folder_path, relative_path)
                                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                                    
                                    # Извлекаем файл
                                    with zipf.open(file_info.filename) as source, open(dest_path, 'wb') as target:
                                        target.write(source.read())
                        
                        # Добавляем саму папку в список для перетаскивания
                        temp_files.append(temp_folder_path)
                    except Exception as e:
                        print(f"Ошибка при подготовке папки {folder_data['name']}: {e}")
            
            if temp_files:
                # Создаем MIME данные с URL файлов и папок
                mime_data = QMimeData()
                urls = [QUrl.fromLocalFile(f) for f in temp_files]
                mime_data.setUrls(urls)
                
                # Настраиваем очистку через 30 секунд
                self.cleanup_temp_dir(temp_dir)
                
                return mime_data
            else:
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            print(f"Ошибка при подготовке drag-and-drop: {e}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        return None
    
    def cleanup_temp_dir(self, temp_dir):
        """Очистить временную директорию через 30 секунд"""
        import threading
        import time
        
        def cleanup():
            time.sleep(30)  # Ждем 30 секунд (больше времени для перетаскивания)
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
        
        # Запускаем очистку в отдельном потоке
        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()