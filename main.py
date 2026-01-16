import sys
import os
import zipfile
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QProgressBar, 
                             QFileDialog, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

# Импортируем наш улучшенный виджет
from module.drag_tree_widget import DragDropTreeWidget

class ModernArchiver(QMainWindow):
    def __init__(self, initial_archive=None):
        super().__init__()
        self.selected_files = []
        self.current_archive = initial_archive
        self.current_archive_path = ""
        self.navigation_history = []
        
        # Загрузка иконок
        self.load_icons()
        self.initUI()
        
    def load_icons(self):
        """Загружаем иконки"""
        self.icon_provider = {
            'folder': None,
            'file': None,
            'archive': None,
            'up': None
        }
        
        # Пробуем загрузить из папки icons
        icon_paths = {
            'folder': 'icons/folder.ico',
            'file': 'icons/file.ico',
            'archive': 'icons/archive.ico',
            'up': None  # Используем системную
        }
        
        for key, path in icon_paths.items():
            if path and os.path.exists(path):
                self.icon_provider[key] = QIcon(path)
        
        # Если не загрузили, используем системные
        if not self.icon_provider['folder']:
            self.icon_provider['folder'] = QApplication.style().standardIcon(
                QApplication.style().SP_DirIcon
            )
        if not self.icon_provider['file']:
            self.icon_provider['file'] = QApplication.style().standardIcon(
                QApplication.style().SP_FileIcon
            )
        if not self.icon_provider['archive']:
            self.icon_provider['archive'] = QApplication.style().standardIcon(
                QApplication.style().SP_FileIcon
            )
        if not self.icon_provider['up']:
            self.icon_provider['up'] = QApplication.style().standardIcon(
                QApplication.style().SP_ArrowUp
            )
    
    def initUI(self):
        # Настройка главного окна
        if self.current_archive:
            self.setWindowTitle(f'ModernArchiver - {os.path.basename(self.current_archive)}')
        else:
            self.setWindowTitle('ModernArchiver v1.1')
            
        self.setGeometry(300, 300, 900, 600)
        self.setWindowOpacity(0.95)
        
        # Установка иконки приложения
        if os.path.exists('icons/icon.ico'):
            self.setWindowIcon(QIcon('icons/icon.ico'))
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        central_widget.setLayout(main_layout)
        
        # Панель инструментов
        toolbar_layout = QHBoxLayout()
        
        self.btn_back = QPushButton("← Назад")
        self.btn_back.setEnabled(False)
        self.btn_back.clicked.connect(self.navigate_back)
        toolbar_layout.addWidget(self.btn_back)
        
        self.btn_up = QPushButton("↑ Вверх")
        self.btn_up.clicked.connect(self.navigate_up)
        toolbar_layout.addWidget(self.btn_up)
        
        self.btn_home = QPushButton("🏠 Корень")
        self.btn_home.clicked.connect(self.navigate_home)
        toolbar_layout.addWidget(self.btn_home)
        
        toolbar_layout.addStretch()
        
        # Путь навигации
        self.path_label = QLabel("")
        self.path_label.setStyleSheet("color: #aaa; padding: 5px;")
        toolbar_layout.addWidget(self.path_label)
        
        main_layout.addLayout(toolbar_layout)
        
        # Разделитель
        splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель - НАШ УЛУЧШЕННЫЙ ВИДЖЕТ С DRAG-AND-DROP И ВЫДЕЛЕНИЕМ ОБЛАСТИ
        self.tree_widget = DragDropTreeWidget()
        self.tree_widget.setHeaderLabels(["Имя", "Размер", "Дата"])
        self.tree_widget.setColumnWidth(0, 300)
        self.tree_widget.itemDoubleClicked.connect(self.on_tree_item_double_clicked)
        
        # Если есть архив, устанавливаем путь для drag-and-drop
        if self.current_archive:
            self.tree_widget.set_archive_path(self.current_archive)
        
        # Правая панель - предпросмотр/информация
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        self.info_label = QLabel("Выберите файл или папку")
        self.info_label.setStyleSheet("color: #888; padding: 10px;")
        right_layout.addWidget(self.info_label)
        
        # Кнопки действий
        action_layout = QHBoxLayout()
        
        self.btn_extract = QPushButton("📤 Извлечь")
        self.btn_extract.clicked.connect(self.extract_selected)
        action_layout.addWidget(self.btn_extract)
        
        self.btn_extract_to = QPushButton("📁 Извлечь в...")
        self.btn_extract_to.clicked.connect(self.extract_to_folder)
        action_layout.addWidget(self.btn_extract_to)
        
        right_layout.addLayout(action_layout)
        right_layout.addStretch()
        
        right_panel.setLayout(right_layout)
        
        splitter.addWidget(self.tree_widget)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 300])
        
        main_layout.addWidget(splitter)
        
        # Статусная строка
        self.status_label = QLabel("Готов")
        self.status_label.setStyleSheet("color: #aaa; padding: 5px; border-top: 1px solid #444;")
        main_layout.addWidget(self.status_label)
        
        # Применяем стиль
        self.apply_styles()
        
        # Если передан архив, загружаем его
        if self.current_archive:
            self.load_archive(self.current_archive)
    
    def apply_styles(self):
        """Применение стилей к интерфейсу"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e
                );
            }
            QTreeWidget {
                background-color: rgba(30, 30, 40, 0.8);
                color: white;
                border: 1px solid #444;
                border-radius: 5px;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: rgba(100, 149, 237, 0.5);
            }
            QTreeWidget::item:hover {
                background-color: rgba(100, 149, 237, 0.3);
            }
            QPushButton {
                background-color: #4169E1;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6495ED;
                border: 1px solid #87CEEB;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
            QLabel {
                color: white;
            }
        """)
    
    def load_archive(self, archive_path):
        """Загрузить архив и отобразить его содержимое"""
        try:
            self.current_archive = archive_path
            self.tree_widget.set_archive_path(archive_path)
            self.navigation_history = []
            self.display_archive_contents("")
            self.status_label.setText(f"Архив загружен: {os.path.basename(archive_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить архив: {str(e)}")
    
    def display_archive_contents(self, path=""):
        """Отобразить содержимое архива по указанному пути с иконками"""
        if not self.current_archive:
            return
        
        self.tree_widget.clear()
        self.current_archive_path = path
        
        # Обновляем путь навигации
        nav_text = f"Архив: {os.path.basename(self.current_archive)}"
        if path:
            nav_text += f" / {path}"
        self.path_label.setText(nav_text)
        
        try:
            with zipfile.ZipFile(self.current_archive, 'r') as zipf:
                folders = set()
                files = []
                
                for file_info in zipf.infolist():
                    filepath = file_info.filename
                    
                    if path:
                        if filepath.startswith(path):
                            relative = filepath[len(path):]
                            if not relative:
                                continue
                                
                            parts = relative.split('/')
                            
                            if len(parts) == 1:
                                name = parts[0]
                                if not name:
                                    continue
                                    
                                if filepath.endswith('/'):
                                    folders.add(name)
                                else:
                                    files.append({
                                        'name': name,
                                        'info': file_info
                                    })
                    else:
                        if '/' in filepath:
                            first_part = filepath.split('/')[0]
                            if filepath.endswith('/'):
                                folders.add(first_part)
                        else:
                            if not filepath.endswith('/'):
                                files.append({
                                    'name': filepath,
                                    'info': file_info
                                })
                
                # ВАЖНО: Добавляем ".." если не в корне - с иконкой
                if path:
                    from PyQt5.QtWidgets import QTreeWidgetItem
                    up_item = QTreeWidgetItem(self.tree_widget)
                    up_item.setText(0, "..")
                    up_item.setText(1, "")
                    up_item.setText(2, "На уровень выше")
                    up_item.setIcon(0, self.icon_provider['up'])
                    up_item.setData(0, Qt.UserRole, {'type': 'up'})
                
                # ВАЖНО: Папки отображаем как [папка] - с иконкой папки
                for folder in sorted(folders):
                    from PyQt5.QtWidgets import QTreeWidgetItem
                    item = QTreeWidgetItem(self.tree_widget)
                    item.setText(0, f"[{folder}]")
                    item.setText(1, "Папка")
                    item.setText(2, "")
                    item.setIcon(0, self.icon_provider['folder'])
                    item.setData(0, Qt.UserRole, {
                        'type': 'folder',
                        'name': folder,
                        'path': (path + folder + '/') if path else (folder + '/')
                    })
                
                # ВАЖНО: Файлы отображаем с их реальными именами - с иконкой файла
                for file_data in sorted(files, key=lambda x: x['name']):
                    from PyQt5.QtWidgets import QTreeWidgetItem
                    file_info = file_data['info']
                    item = QTreeWidgetItem(self.tree_widget)
                    item.setText(0, file_data['name'])
                    item.setText(1, self.format_size(file_info.file_size))
                    
                    date_time = datetime(*file_info.date_time)
                    item.setText(2, date_time.strftime("%Y-%m-%d %H:%M"))
                    
                    # Устанавливаем иконку файла
                    item.setIcon(0, self.icon_provider['file'])
                    
                    item.setData(0, Qt.UserRole, {
                        'type': 'file',
                        'name': file_data['name'],
                        'full_path': file_info.filename,
                        'size': file_info.file_size
                    })
                
                # Сортируем: сначала "..", потом папки, потом файлы
                self.tree_widget.sortItems(0, Qt.AscendingOrder)
                
                # Обновляем статус
                self.status_label.setText(f"Папок: {len(folders)}, Файлов: {len(files)}")
                
        except Exception as e:
            self.status_label.setText(f"Ошибка: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать архив: {str(e)}")
    
    def on_tree_item_double_clicked(self, item, column):
        """Обработка двойного клика"""
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        
        if data.get('type') == 'folder':
            new_path = data['path']
            self.navigation_history.append(self.current_archive_path)
            self.display_archive_contents(new_path)
            self.btn_back.setEnabled(True)
            
        elif data.get('type') == 'up':
            if self.navigation_history:
                prev_path = self.navigation_history.pop()
                self.display_archive_contents(prev_path)
            else:
                if self.current_archive_path:
                    parts = self.current_archive_path.rstrip('/').split('/')
                    if len(parts) > 1:
                        new_path = '/'.join(parts[:-1]) + '/'
                    else:
                        new_path = ""
                    self.display_archive_contents(new_path)
            
            self.btn_back.setEnabled(len(self.navigation_history) > 0)
            
        elif data.get('type') == 'file':
            self.extract_files([data['full_path']])
    
    def navigate_back(self):
        if self.navigation_history:
            prev_path = self.navigation_history.pop()
            self.display_archive_contents(prev_path)
            self.btn_back.setEnabled(len(self.navigation_history) > 0)
    
    def navigate_up(self):
        if self.current_archive_path:
            parts = self.current_archive_path.rstrip('/').split('/')
            if parts:
                new_path = '/'.join(parts[:-1]) + '/' if len(parts) > 1 else ""
                self.display_archive_contents(new_path)
                if self.navigation_history and self.navigation_history[-1] == self.current_archive_path:
                    self.navigation_history.pop()
    
    def navigate_home(self):
        self.navigation_history = []
        self.display_archive_contents("")
        self.btn_back.setEnabled(False)
    
    def extract_selected(self):
        selected_items = self.tree_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Внимание", "Выберите файлы для извлечения")
            return
        
        files_to_extract = []
        for item in selected_items:
            data = item.data(0, Qt.UserRole)
            if data and data.get('type') == 'file':
                files_to_extract.append(data['full_path'])
        
        if files_to_extract:
            self.extract_files(files_to_extract)
        else:
            QMessageBox.warning(self, "Внимание", "Выберите файлы для извлечения")
    
    def extract_files(self, file_paths):
        if not file_paths:
            return
        
        extract_dir = QFileDialog.getExistingDirectory(
            self, "Выберите папку для извлечения",
            os.path.join(os.path.expanduser("~"), "Desktop")
        )
        
        if not extract_dir:
            return
        
        self.status_label.setText("Извлечение файлов...")
        QApplication.processEvents()
        
        try:
            with zipfile.ZipFile(self.current_archive, 'r') as zipf:
                extracted_count = 0
                for file_path in file_paths:
                    try:
                        output_path = os.path.join(extract_dir, os.path.basename(file_path))
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        
                        with zipf.open(file_path) as source, open(output_path, 'wb') as target:
                            target.write(source.read())
                        
                        extracted_count += 1
                    except Exception as e:
                        print(f"Ошибка при извлечении {file_path}: {e}")
                
                self.status_label.setText(f"Извлечено {extracted_count} файлов")
                QMessageBox.information(self, "Успех", 
                    f"Успешно извлечено {extracted_count} файлов в:\n{extract_dir}")
                
        except Exception as e:
            self.status_label.setText("Ошибка при извлечении")
            QMessageBox.critical(self, "Ошибка", f"Не удалось извлечь файлов: {str(e)}")
    
    def extract_to_folder(self):
        self.extract_selected()
    
    def format_size(self, size):
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} ТБ"

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)
    
    initial_archive = None
    if len(sys.argv) > 1:
        archive_path = sys.argv[1]
        if os.path.exists(archive_path):
            initial_archive = archive_path
    
    window = ModernArchiver(initial_archive=initial_archive)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()