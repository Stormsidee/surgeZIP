from PyQt5.QtWidgets import (QTreeWidget, QTreeWidgetItem, QFileIconProvider,
                             QMenu, QAction, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QUrl
from PyQt5.QtGui import QIcon, QDrag
import os
import tempfile

class ArchiveTreeWidget(QTreeWidget):
    """Дерево файлов архива с поддержкой drag-and-drop"""
    fileDragged = pyqtSignal(list)  # Сигнал при перетаскивании файлов
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setSelectionMode(QTreeWidget.ExtendedSelection)
        
        # Иконки
        self.icon_provider = QFileIconProvider()
        self.folder_icon = self.icon_provider.icon(QFileIconProvider.Folder)
        self.file_icon = self.icon_provider.icon(QFileIconProvider.File)
        self.archive_icon = QIcon("icons/archive.ico") if os.path.exists("icons/archive.ico") else self.file_icon
        
        # Контекстное меню
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Двойной клик
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Хранилище данных о файлах
        self.file_data = {}
    
    def build_tree(self, archive_tree, current_path=""):
        """Построить дерево архива"""
        self.clear()
        self.file_data.clear()
        
        # Корневой элемент
        if current_path == "":
            root_item = QTreeWidgetItem(self)
            root_item.setText(0, archive_tree['name'])
            root_item.setIcon(0, self.archive_icon)
            root_item.setData(0, Qt.UserRole, {'type': 'archive', 'path': ''})
            self.addTopLevelItem(root_item)
            parent = root_item
        else:
            parent = self.currentItem() or self.topLevelItem(0)
        
        # Добавляем ".." для навигации вверх
        if current_path != "":
            up_item = QTreeWidgetItem(parent)
            up_item.setText(0, "[..]")
            up_item.setIcon(0, self.folder_icon)
            up_item.setData(0, Qt.UserRole, {'type': 'up', 'path': '..'})
        
        # Добавляем папки
        if 'children' in archive_tree:
            for folder_name, folder_data in archive_tree['children'].items():
                folder_item = QTreeWidgetItem(parent)
                folder_item.setText(0, f"[{folder_name}]")
                folder_item.setIcon(0, self.folder_icon)
                folder_item.setData(0, Qt.UserRole, {
                    'type': 'folder',
                    'name': folder_name,
                    'full_path': folder_data.get('full_path', ''),
                    'path': current_path + folder_name + '/'
                })
                self.file_data[current_path + folder_name + '/'] = folder_data
        
        # Добавляем файлы
        if 'files' in archive_tree:
            for file_data in archive_tree['files']:
                file_item = QTreeWidgetItem(parent)
                file_item.setText(0, file_data['name'])
                file_item.setIcon(0, self.file_icon)
                file_item.setData(0, Qt.UserRole, {
                    'type': 'file',
                    'name': file_data['name'],
                    'full_path': file_data['full_path'],
                    'size': file_data['size'],
                    'path': current_path + file_data['name']
                })
                self.file_data[current_path + file_data['name']] = file_data
        
        self.expandAll()
    
    def on_item_double_clicked(self, item, column):
        """Обработка двойного клика"""
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        
        if data['type'] == 'folder':
            # Переход в папку
            self.itemDoubleClicked.disconnect(self.on_item_double_clicked)
            self.build_tree(self.file_data[data['path']], data['path'])
            self.itemDoubleClicked.connect(self.on_item_double_clicked)
        elif data['type'] == 'up':
            # Навигация вверх
            self.navigate_up()
        elif data['type'] == 'file':
            # Извлечение файла
            self.extract_selected()
    
    def navigate_up(self):
        """Навигация на уровень выше"""
        current_item = self.currentItem()
        if current_item:
            parent = current_item.parent()
            if parent:
                # Получаем данные родительской папки
                parent_data = parent.data(0, Qt.UserRole)
                if parent_data and parent_data['type'] == 'folder':
                    # Нужно перестроить дерево для родительской папки
                    pass
    
    def show_context_menu(self, position):
        """Показать контекстное меню"""
        menu = QMenu()
        
        extract_action = QAction("Извлечь", self)
        extract_action.triggered.connect(self.extract_selected)
        menu.addAction(extract_action)
        
        extract_to_action = QAction("Извлечь в...", self)
        extract_to_action.triggered.connect(self.extract_to_folder)
        menu.addAction(extract_to_action)
        
        menu.addSeparator()
        
        select_all_action = QAction("Выделить все", self)
        select_all_action.triggered.connect(self.selectAll)
        menu.addAction(select_all_action)
        
        menu.exec_(self.viewport().mapToGlobal(position))
    
    def extract_selected(self):
        """Извлечь выбранные файлы"""
        selected_items = self.selectedItems()
        if not selected_items:
            return
        
        from main import ModernArchiver
        parent_window = self.parent().parent()
        
        # Запрашиваем папку для извлечения
        from PyQt5.QtWidgets import QFileDialog
        extract_dir = QFileDialog.getExistingDirectory(
            parent_window, "Выберите папку для извлечения"
        )
        
        if not extract_dir:
            return
        
        # Извлекаем файлы
        files_to_extract = []
        for item in selected_items:
            data = item.data(0, Qt.UserRole)
            if data and data['type'] == 'file':
                files_to_extract.append(data['full_path'])
        
        if files_to_extract:
            from zip_module import ZipArchiver
            success, results = ZipArchiver.extract_files(
                parent_window.current_archive, 
                files_to_extract, 
                extract_dir
            )
            
            if success:
                QMessageBox.information(parent_window, "Успех", 
                    f"Извлечено {len(files_to_extract)} файлов")
            else:
                QMessageBox.critical(parent_window, "Ошибка", 
                    "Ошибка при извлечении файлов")
    
    def extract_to_folder(self):
        """Извлечь в выбранную папку"""
        self.extract_selected()
    
    def mouseMoveEvent(self, event):
        """Обработка начала перетаскивания"""
        if event.buttons() & Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            
            # Получаем выбранные файлы
            selected_items = self.selectedItems()
            files_to_drag = []
            
            for item in selected_items:
                data = item.data(0, Qt.UserRole)
                if data and data['type'] == 'file':
                    files_to_drag.append(data['full_path'])
            
            if files_to_drag:
                # Создаем временные файлы для перетаскивания
                temp_files = []
                for file_path in files_to_drag:
                    # Здесь нужно создать временный файл на диске
                    # для возможности перетаскивания
                    pass
                
                # Формируем список URL для перетаскивания
                urls = [QUrl.fromLocalFile(f) for f in temp_files]
                mime_data.setUrls(urls)
                drag.setMimeData(mime_data)
                
                # Запускаем перетаскивание
                drag.exec_(Qt.CopyAction)
        
        super().mouseMoveEvent(event)