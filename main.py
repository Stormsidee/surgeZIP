import sys
import os
import zipfile
import tarfile
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTreeWidget, 
                             QTreeWidgetItem, QFileDialog, QMessageBox, 
                             QHeaderView, QMenu, QAction, QRubberBand)
from PyQt5.QtCore import Qt, QPoint, QSize, QMimeData, QUrl, QTimer, QRect
from PyQt5.QtGui import (QFont, QPalette, QColor, QIcon, QDrag, QCursor, 
                         QPainter, QBrush, QPen)

# Опциональные импорты
try:
    import py7zr
    HAS_PY7ZR = True
except ImportError:
    HAS_PY7ZR = False

try:
    import rarfile
    HAS_RARFILE = True
except ImportError:
    HAS_RARFILE = False

try:
    import pycdlib
    HAS_PYCDLIB = True
except ImportError:
    HAS_PYCDLIB = False

class ModernArchiver(QMainWindow):
    def __init__(self, initial_archive=None):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.current_archive = initial_archive
        self.current_archive_path = ""
        self.navigation_history = []
        
        # Проверяем доступность библиотек
        self.check_dependencies()
        self.initUI()
        
        if self.current_archive:
            self.load_archive(self.current_archive)
    
    def check_dependencies(self):
        """Проверяем наличие необходимых библиотек"""
        missing = []
        try:
            import zipfile
        except:
            missing.append("zipfile (встроен)")
        try:
            import tarfile
        except:
            missing.append("tarfile (встроен)")
        try:
            import py7zr
        except:
            missing.append("py7zr - установите: pip install py7zr")
        try:
            import rarfile
        except:
            missing.append("rarfile - установите: pip install rarfile")
        try:
            import pycdlib
        except:
            missing.append("pycdlib - установите: pip install pycdlib")
        
        if missing:
            print("ВНИМАНИЕ: Отсутствуют библиотеки:")
            for lib in missing:
                print(f"  - {lib}")
    
    def initUI(self):
        # Основной виджет
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        
        # Главный layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Кастомный заголовок
        title_bar = QWidget()
        title_bar.setFixedHeight(32)
        title_bar.setObjectName("TitleBar")
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)
        
        # Иконка и название
        title_label = QLabel("surgeZIP")
        title_label.setStyleSheet("color: #CCCCCC; font-weight: 600; font-size: 11px;")
        
        # Кнопки управления окном
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)
        
        self.btn_minimize = self.create_title_button("─", "#666666")
        self.btn_minimize.clicked.connect(self.showMinimized)
        
        self.btn_maximize = self.create_title_button("□", "#666666")
        self.btn_maximize.clicked.connect(self.toggle_maximize)
        
        self.btn_close = self.create_title_button("✕", "#FF5555")
        self.btn_close.clicked.connect(self.close)
        
        btn_layout.addWidget(self.btn_minimize)
        btn_layout.addWidget(self.btn_maximize)
        btn_layout.addWidget(self.btn_close)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addLayout(btn_layout)
        
        layout.addWidget(title_bar)
        
        # Минималистичная панель инструментов
        toolbar = QWidget()
        toolbar.setFixedHeight(40)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 5, 8, 5)
        toolbar_layout.setSpacing(5)
        
        self.btn_back = self.create_tool_button("←", "Назад")
        self.btn_back.setEnabled(False)
        self.btn_back.clicked.connect(self.navigate_back)
        
        self.btn_up = self.create_tool_button("↑", "Вверх")
        self.btn_up.clicked.connect(self.navigate_up)
        
        self.btn_home = self.create_tool_button("🏠", "Корень")
        self.btn_home.clicked.connect(self.navigate_home)
        
        self.btn_extract = self.create_tool_button("📤", "Извлечь")
        self.btn_extract.clicked.connect(self.extract_selected)
        
        toolbar_layout.addWidget(self.btn_back)
        toolbar_layout.addWidget(self.btn_up)
        toolbar_layout.addWidget(self.btn_home)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_extract)
        
        layout.addWidget(toolbar)
        
        # Дерево файлов - максимально большое
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Имя", "Размер", "Дата"])
        self.tree_widget.setColumnWidth(0, 400)
        self.tree_widget.setColumnWidth(1, 80)
        self.tree_widget.setColumnWidth(2, 120)
        self.tree_widget.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.tree_widget.setSelectionBehavior(QTreeWidget.SelectRows)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Настраиваем заголовки таблицы
        header = self.tree_widget.header()
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignLeft)
        
        layout.addWidget(self.tree_widget)
        
        # Применяем стили
        self.setStyleSheet("""
            #CentralWidget {
                background: #1A1A2E;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
            #TitleBar {
                background-color: #252540;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            }
            QTreeWidget {
                background-color: #161625;
                color: #E0E0E0;
                border: none;
                font-size: 12px;
                outline: none;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QTreeWidget::item {
                padding: 5px 3px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.02);
            }
            QTreeWidget::item:selected {
                background-color: rgba(100, 149, 237, 0.25);
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QHeaderView::section {
                background-color: #252540;
                color: #AAAAAA;
                padding: 6px;
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 0.05);
                font-weight: 600;
                font-size: 11px;
            }
        """)
        
        # Размер окна
        self.setGeometry(100, 100, 900, 800)
        self.setWindowOpacity(0.9)
        
        # Настраиваем drag-and-drop
        self.setup_drag_and_drop()
        
        # Контекстное меню
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        # Для перемещения окна
        self.drag_pos = None
    
    def create_title_button(self, text, color):
        btn = QPushButton(text)
        btn.setFixedSize(20, 20)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.05);
                color: {color};
                border: none;
                border-radius: 3px;
                font-size: 9px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
        """)
        return btn
    
    def create_tool_button(self, icon, tooltip):
        btn = QPushButton(icon)
        btn.setToolTip(tooltip)
        btn.setFixedSize(30, 26)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 149, 237, 0.15);
                color: #6495ED;
                border: 1px solid rgba(100, 149, 237, 0.2);
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(100, 149, 237, 0.25);
                border: 1px solid rgba(100, 149, 237, 0.4);
            }
            QPushButton:disabled {
                background-color: rgba(100, 100, 100, 0.1);
                color: #666666;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
        return btn
    
    def setup_drag_and_drop(self):
        """Настройка drag-and-drop"""
        self.tree_widget.setDragEnabled(False)
        self.tree_widget.mousePressEvent = self.tree_mouse_press
        self.tree_widget.mouseMoveEvent = self.tree_mouse_move
        self.tree_widget.mouseReleaseEvent = self.tree_mouse_release
        
        self.rubber_band = None
        self.rubber_band_start = None
        self.drag_start_pos = None
        self.saved_selection = None
    
    def tree_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()
            item = self.tree_widget.itemAt(event.pos())
            selected = self.tree_widget.selectedItems()
            
            # Если выделено несколько и нажали на выделенный - сохраняем выделение
            if item and item in selected and len(selected) > 1:
                self.saved_selection = list(selected)
                event.accept()
                return
            
            if not item or self.tree_widget.indexAt(event.pos()).column() == -1:
                self.rubber_band_start = event.pos()
                self.rubber_band = QRubberBand(QRubberBand.Rectangle, self.tree_widget.viewport())
                self.rubber_band.setGeometry(QRect(self.rubber_band_start, QPoint()))
                self.rubber_band.show()
                self.tree_widget.clearSelection()
            else:
                QTreeWidget.mousePressEvent(self.tree_widget, event)
        else:
            QTreeWidget.mousePressEvent(self.tree_widget, event)
    
    def tree_mouse_move(self, event):
        # Восстанавливаем сохраненное выделение перед началом drag
        if self.saved_selection and not (event.buttons() & Qt.LeftButton):
            self.saved_selection = None
        
        if self.rubber_band and self.rubber_band_start:
            rect = QRect(self.rubber_band_start, event.pos()).normalized()
            self.rubber_band.setGeometry(rect)
            
            for i in range(self.tree_widget.topLevelItemCount()):
                item = self.tree_widget.topLevelItem(i)
                item_rect = self.tree_widget.visualItemRect(item)
                if rect.intersects(item_rect):
                    item.setSelected(True)
                else:
                    item.setSelected(False)
        
        elif self.drag_start_pos and (event.pos() - self.drag_start_pos).manhattanLength() > 15:
            selected_items = self.tree_widget.selectedItems()
            if selected_items and self.current_archive:
                # Восстанавливаем сохраненное выделение перед drag
                if self.saved_selection:
                    self.tree_widget.clearSelection()
                    for item in self.saved_selection:
                        item.setSelected(True)
                    self.saved_selection = None
                
                self.start_drag()
                self.drag_start_pos = None
                return
        
        QTreeWidget.mouseMoveEvent(self.tree_widget, event)
    
    def tree_mouse_release(self, event):
        if self.rubber_band:
            self.rubber_band.hide()
            self.rubber_band = None
            self.rubber_band_start = None
        
        if self.drag_start_pos:
            self.drag_start_pos = None
        
        if self.saved_selection:
            self.saved_selection = None
        
        QTreeWidget.mouseReleaseEvent(self.tree_widget, event)
    
    def start_drag(self):
        """Начать перетаскивание выбранных файлов"""
        selected_items = self.tree_widget.selectedItems()
        if not selected_items or not self.current_archive:
            return
        
        # Получаем список файлов для перетаскивания
        files_to_drag = []
        for item in selected_items:
            data = item.data(0, Qt.UserRole)
            if not data:
                continue
            
            if data.get('type') == 'file':
                files_to_drag.append(data)
            elif data.get('type') == 'folder':
                files_to_drag.append(data)
        
        if not files_to_drag:
            return
        
        # Создаем временные файлы
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp(prefix="drag_")
        
        try:
            # Определяем тип архива
            archive_ext = os.path.splitext(self.current_archive)[1].lower()
            
            if archive_ext == '.zip':
                self.extract_zip_to_temp(files_to_drag, temp_dir)
            elif archive_ext == '.rar':
                self.extract_rar_to_temp(files_to_drag, temp_dir)
            elif archive_ext in ['.7z', '.7zip']:
                self.extract_7z_to_temp(files_to_drag, temp_dir)
            elif archive_ext == '.tar':
                self.extract_tar_to_temp(files_to_drag, temp_dir)
            elif archive_ext == '.gz':
                self.extract_gz_to_temp(files_to_drag, temp_dir)
            elif archive_ext == '.bz2':
                self.extract_bz2_to_temp(files_to_drag, temp_dir)
            elif archive_ext == '.iso':
                self.extract_iso_to_temp(files_to_drag, temp_dir)
            else:
                # Пробуем извлечь как обычный файл
                self.extract_generic_to_temp(files_to_drag, temp_dir)
            
            # Собираем все файлы из временной директории
            temp_files = []
            for item in files_to_drag:
                if item.get('type') == 'file':
                    # Для файлов - путь к извлеченному файлу
                    extracted_path = os.path.join(temp_dir, item['full_path'])
                    if os.path.exists(extracted_path):
                        temp_files.append(extracted_path)
                elif item.get('type') == 'folder':
                    # Для папок - путь к извлеченной папке
                    folder_name = item['name']
                    folder_path = os.path.join(temp_dir, folder_name)
                    os.makedirs(folder_path, exist_ok=True)
                    temp_files.append(folder_path)
            
            if temp_files:
                # Создаем MIME данные
                mime_data = QMimeData()
                urls = [QUrl.fromLocalFile(f) for f in temp_files]
                mime_data.setUrls(urls)
                
                # Создаем и запускаем перетаскивание
                drag = QDrag(self.tree_widget)
                drag.setMimeData(mime_data)
                drag.exec_(Qt.CopyAction)
                self.tree_widget.clearSelection()
            else:
                print("No temp files extracted")
            
            # Удаляем временную директорию через 60 секунд
            QTimer.singleShot(60000, lambda: shutil.rmtree(temp_dir, ignore_errors=True))
            
        except Exception as e:
            print(f"Ошибка при создании временных файлов: {e}")
            import traceback
            traceback.print_exc()
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def extract_zip_to_temp(self, items, temp_dir):
        """Извлечение файлов из ZIP во временную директорию"""
        with zipfile.ZipFile(self.current_archive, 'r') as zipf:
            for item in items:
                if item.get('type') == 'file':
                    try:
                        zipf.extract(item['full_path'], temp_dir)
                    except:
                        pass
                elif item.get('type') == 'folder':
                    folder_path = item['path'].rstrip('/') + '/'
                    for file_info in zipf.infolist():
                        if file_info.filename.startswith(folder_path):
                            try:
                                zipf.extract(file_info.filename, temp_dir)
                            except:
                                pass
    
    def extract_rar_to_temp(self, items, temp_dir):
        """Извлечение файлов из RAR во временную директорию"""
        try:
            import rarfile
            with rarfile.RarFile(self.current_archive, 'r') as rarf:
                for item in items:
                    if item.get('type') == 'file':
                        try:
                            rarf.extract(item['full_path'], temp_dir)
                        except:
                            pass
                    elif item.get('type') == 'folder':
                        folder_path = item['path'].rstrip('/') + '/'
                        for file_info in rarf.infolist():
                            if file_info.filename.startswith(folder_path):
                                try:
                                    rarf.extract(file_info.filename, temp_dir)
                                except:
                                    pass
        except Exception as e:
            print(f"Ошибка при извлечении RAR: {e}")
    
    def extract_7z_to_temp(self, items, temp_dir):
        """Извлечение файлов из 7z во временную директорию"""
        try:
            with py7zr.SevenZipFile(self.current_archive, 'r') as archive:
                # Собираем список файлов для извлечения
                files_to_extract = []
                for item in items:
                    if item.get('type') == 'file':
                        files_to_extract.append(item['full_path'])
                    elif item.get('type') == 'folder':
                        # Извлекаем все файлы в папке
                        folder_path = item['path'].rstrip('/') + '/'
                        for file_info in archive.list():
                            if file_info.filename.startswith(folder_path):
                                files_to_extract.append(file_info.filename)
                
                if files_to_extract:
                    archive.extract(targets=files_to_extract, path=temp_dir)
        except Exception as e:
            print(f"Ошибка при извлечении 7z: {e}")
    
    def extract_tar_to_temp(self, items, temp_dir):
        """Извлечение файлов из TAR во временную директорию"""
        with tarfile.open(self.current_archive, 'r') as tarf:
            for item in items:
                if item.get('type') == 'file':
                    try:
                        tarf.extract(item['full_path'], temp_dir)
                    except:
                        pass
                elif item.get('type') == 'folder':
                    folder_path = item['path'].rstrip('/') + '/'
                    for member in tarf.getmembers():
                        if member.name.startswith(folder_path):
                            try:
                                tarf.extract(member, temp_dir)
                            except:
                                pass
    
    def extract_gz_to_temp(self, items, temp_dir):
        """Извлечение файлов из GZ во временную директорию"""
        with tarfile.open(self.current_archive, 'r:gz') as tarf:
            for item in items:
                if item.get('type') == 'file':
                    try:
                        tarf.extract(item['full_path'], temp_dir)
                    except:
                        pass
                elif item.get('type') == 'folder':
                    folder_path = item['path'].rstrip('/') + '/'
                    for member in tarf.getmembers():
                        if member.name.startswith(folder_path):
                            try:
                                tarf.extract(member, temp_dir)
                            except:
                                pass
    
    def extract_bz2_to_temp(self, items, temp_dir):
        """Извлечение файлов из BZ2 во временную директорию"""
        with tarfile.open(self.current_archive, 'r:bz2') as tarf:
            for item in items:
                if item.get('type') == 'file':
                    try:
                        tarf.extract(item['full_path'], temp_dir)
                    except:
                        pass
                elif item.get('type') == 'folder':
                    folder_path = item['path'].rstrip('/') + '/'
                    for member in tarf.getmembers():
                        if member.name.startswith(folder_path):
                            try:
                                tarf.extract(member, temp_dir)
                            except:
                                pass
    
    def extract_iso_to_temp(self, items, temp_dir):
        """Извлечение файлов из ISO во временную директорию"""
        try:
            import pycdlib
            iso = pycdlib.PyCdlib()
            iso.open(self.current_archive)
            
            for item in items:
                if item.get('type') == 'file':
                    iso_path = item['full_path'].replace('/', '\\')
                    output_path = os.path.join(temp_dir, item['name'])
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    try:
                        iso.get_file_from_iso(output_path, iso_path=iso_path)
                    except:
                        pass
                elif item.get('type') == 'folder':
                    # Извлекаем все файлы в папке
                    folder_path = item['path'].rstrip('/') + '/'
                    for dirname, dirlist, filelist in iso.walk(iso_path='/' + folder_path):
                        for filename in filelist:
                            filepath = os.path.join(dirname, filename)
                            iso_path = filepath.replace('/', '\\')
                            output_path = os.path.join(temp_dir, filepath)
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            try:
                                iso.get_file_from_iso(output_path, iso_path=iso_path)
                            except:
                                pass
            
            iso.close()
        except Exception as e:
            print(f"Ошибка при извлечении ISO: {e}")
    
    def extract_generic_to_temp(self, items, temp_dir):
        """Извлечение файлов из неизвестного формата"""
        # Просто копируем сам архив как файл
        import shutil
        for item in items:
            if item.get('type') == 'file':
                shutil.copy2(self.current_archive, temp_dir)
                break
    
    def show_context_menu(self, position):
        """Показать контекстное меню"""
        menu = QMenu()
        
        extract_action = QAction("📤 Извлечь", self)
        extract_action.triggered.connect(self.extract_selected)
        menu.addAction(extract_action)
        
        extract_to_action = QAction("📁 Извлечь в папку...", self)
        extract_to_action.triggered.connect(self.extract_to_folder)
        menu.addAction(extract_to_action)
        
        menu.exec_(self.tree_widget.viewport().mapToGlobal(position))
    
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.btn_maximize.setText("□")
        else:
            self.showMaximized()
            self.btn_maximize.setText("❐")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_pos'):
            self.move(event.globalPos() - self.drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if hasattr(self, 'drag_pos'):
            del self.drag_pos
    
    def load_archive(self, archive_path):
        """Загрузить архив"""
        try:
            self.current_archive = archive_path
            self.navigation_history = []
            self.display_archive_contents("")
            
            # Обновляем заголовок окна
            self.setWindowTitle(f"surgeZIP - {os.path.basename(archive_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть архив:\n{str(e)}")
    
    def display_archive_contents(self, path=""):
        """Отобразить содержимое архива"""
        if not self.current_archive:
            return
        
        self.tree_widget.clear()
        self.current_archive_path = path
        
        try:
            # Определяем формат архива
            archive_ext = os.path.splitext(self.current_archive)[1].lower()
            
            if archive_ext == '.zip':
                self.display_zip_contents(path)
            elif archive_ext == '.rar':
                self.display_rar_contents(path)
            elif archive_ext in ['.7z', '.7zip']:
                self.display_7z_contents(path)
            elif archive_ext == '.tar':
                self.display_tar_contents(path)
            elif archive_ext == '.gz':
                self.display_gz_contents(path)
            elif archive_ext == '.bz2':
                self.display_bz2_contents(path)
            elif archive_ext == '.iso':
                self.display_iso_contents(path)
            else:
                QMessageBox.warning(self, "Внимание", 
                    f"Формат {archive_ext} не поддерживается.")
        
        except Exception as e:
            print(f"Ошибка при отображении содержимого: {e}")
            import traceback
            traceback.print_exc()
    
    def display_zip_contents(self, path=""):
        """Отобразить содержимое ZIP архива"""
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
                        elif len(parts) > 1:
                            # Добавляем первую папку в пути
                            first_folder = parts[0]
                            if first_folder:
                                folders.add(first_folder)
                else:
                    if '/' in filepath:
                        parts = filepath.split('/')
                        first_part = parts[0]
                        if first_part:
                            folders.add(first_part)
                    else:
                        if not filepath.endswith('/'):
                            files.append({
                                'name': filepath,
                                'info': file_info
                            })
            
            # Добавляем ".." если не в корне
            if path:
                up_item = QTreeWidgetItem(self.tree_widget)
                up_item.setText(0, "..")
                up_item.setText(1, "")
                up_item.setText(2, "")
                up_item.setData(0, Qt.UserRole, {'type': 'up'})
            
            # Добавляем папки
            for folder in sorted(folders):
                item = QTreeWidgetItem(self.tree_widget)
                item.setText(0, f"📁 {folder}")
                item.setText(1, "")
                item.setText(2, "")
                item.setData(0, Qt.UserRole, {
                    'type': 'folder',
                    'name': folder,
                    'path': (path + folder + '/') if path else (folder + '/')
                })
            
            # Добавляем файлы
            for file_data in sorted(files, key=lambda x: x['name']):
                file_info = file_data['info']
                item = QTreeWidgetItem(self.tree_widget)
                item.setText(0, f"📄 {file_data['name']}")
                item.setText(1, self.format_size(file_info.file_size))
                
                date_time = datetime(*file_info.date_time)
                item.setText(2, date_time.strftime("%d.%m.%y %H:%M"))
                
                item.setData(0, Qt.UserRole, {
                    'type': 'file',
                    'name': file_data['name'],
                    'full_path': file_info.filename,
                    'size': file_info.file_size
                })
    
    def display_rar_contents(self, path=""):
        """Отобразить содержимое RAR архива"""
        try:
            import rarfile
            with rarfile.RarFile(self.current_archive, 'r') as rarf:
                folders = set()
                files = []
                
                for file_info in rarf.infolist():
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
                
                # Добавляем ".." если не в корне
                if path:
                    up_item = QTreeWidgetItem(self.tree_widget)
                    up_item.setText(0, "..")
                    up_item.setText(1, "")
                    up_item.setText(2, "")
                    up_item.setData(0, Qt.UserRole, {'type': 'up'})
                
                # Добавляем папки
                for folder in sorted(folders):
                    item = QTreeWidgetItem(self.tree_widget)
                    item.setText(0, f"📁 {folder}")
                    item.setText(1, "")
                    item.setText(2, "")
                    item.setData(0, Qt.UserRole, {
                        'type': 'folder',
                        'name': folder,
                        'path': (path + folder + '/') if path else (folder + '/')
                    })
                
                # Добавляем файлы
                for file_data in sorted(files, key=lambda x: x['name']):
                    file_info = file_data['info']
                    item = QTreeWidgetItem(self.tree_widget)
                    item.setText(0, f"📄 {file_data['name']}")
                    item.setText(1, self.format_size(file_info.file_size))
                    
                    # RAR не хранит дату в том же формате
                    item.setText(2, "")
                    
                    item.setData(0, Qt.UserRole, {
                        'type': 'file',
                        'name': file_data['name'],
                        'full_path': file_info.filename,
                        'size': file_info.file_size
                    })
        except Exception as e:
            print(f"Ошибка при чтении RAR: {e}")
    
    def display_7z_contents(self, path=""):
        """Отобразить содержимое 7z архива"""
        try:
            with py7zr.SevenZipFile(self.current_archive, 'r') as archive:
                folders = set()
                files = []
                
                for file_info in archive.list():
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
                
                # Добавляем ".." если не в корне
                if path:
                    up_item = QTreeWidgetItem(self.tree_widget)
                    up_item.setText(0, "..")
                    up_item.setText(1, "")
                    up_item.setText(2, "")
                    up_item.setData(0, Qt.UserRole, {'type': 'up'})
                
                # Добавляем папки
                for folder in sorted(folders):
                    item = QTreeWidgetItem(self.tree_widget)
                    item.setText(0, f"📁 {folder}")
                    item.setText(1, "")
                    item.setText(2, "")
                    item.setData(0, Qt.UserRole, {
                        'type': 'folder',
                        'name': folder,
                        'path': (path + folder + '/') if path else (folder + '/')
                    })
                
                # Добавляем файлы
                for file_data in sorted(files, key=lambda x: x['name']):
                    file_info = file_data['info']
                    item = QTreeWidgetItem(self.tree_widget)
                    item.setText(0, f"📄 {file_data['name']}")
                    item.setText(1, self.format_size(file_info.uncompressed))
                    item.setText(2, "")
                    
                    item.setData(0, Qt.UserRole, {
                        'type': 'file',
                        'name': file_info.filename,
                        'full_path': file_info.filename,
                        'size': file_info.uncompressed
                    })
        except Exception as e:
            print(f"Ошибка при чтении 7z: {e}")
    
    def display_tar_contents(self, path=""):
        """Отобразить содержимое TAR архива"""
        with tarfile.open(self.current_archive, 'r') as tarf:
            folders = set()
            files = []
            
            for member in tarf.getmembers():
                filepath = member.name
                
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
                            
                            if member.isdir():
                                folders.add(name)
                            else:
                                files.append({
                                    'name': name,
                                    'member': member
                                })
                else:
                    if '/' in filepath:
                        first_part = filepath.split('/')[0]
                        if member.isdir():
                            folders.add(first_part)
                    else:
                        if member.isfile():
                            files.append({
                                'name': filepath,
                                'member': member
                            })
            
            # Добавляем ".." если не в корне
            if path:
                up_item = QTreeWidgetItem(self.tree_widget)
                up_item.setText(0, "..")
                up_item.setText(1, "")
                up_item.setText(2, "")
                up_item.setData(0, Qt.UserRole, {'type': 'up'})
            
            # Добавляем папки
            for folder in sorted(folders):
                item = QTreeWidgetItem(self.tree_widget)
                item.setText(0, f"📁 {folder}")
                item.setText(1, "")
                item.setText(2, "")
                item.setData(0, Qt.UserRole, {
                    'type': 'folder',
                    'name': folder,
                    'path': (path + folder + '/') if path else (folder + '/')
                })
            
            # Добавляем файлы
            for file_data in sorted(files, key=lambda x: x['name']):
                member = file_data['member']
                item = QTreeWidgetItem(self.tree_widget)
                item.setText(0, f"📄 {file_data['name']}")
                item.setText(1, self.format_size(member.size))
                
                date_time = datetime.fromtimestamp(member.mtime)
                item.setText(2, date_time.strftime("%d.%m.%y %H:%M"))
                
                item.setData(0, Qt.UserRole, {
                    'type': 'file',
                    'name': member.name,
                    'full_path': member.name,
                    'size': member.size
                })
    
    def display_gz_contents(self, path=""):
        """Отобразить содержимое GZ архива"""
        self.display_tar_contents(path)
    
    def display_bz2_contents(self, path=""):
        """Отобразить содержимое BZ2 архива"""
        self.display_tar_contents(path)
    
    def display_iso_contents(self, path=""):
        """Отобразить содержимое ISO образа"""
        try:
            import pycdlib
            iso = pycdlib.PyCdlib()
            iso.open(self.current_archive)
            
            folders = set()
            files = []
            
            for dirname, dirlist, filelist in iso.walk(iso_path='/' + path if path else '/'):
                # Убираем начальный слэш
                dirname = dirname.lstrip('/')
                
                if dirname == path:
                    for filename in filelist:
                        files.append({
                            'name': filename,
                            'full_path': os.path.join(dirname, filename).replace('\\', '/')
                        })
                    for dirname in dirlist:
                        if dirname not in ['.', '..']:
                            folders.add(dirname)
                elif dirname.startswith(path + '/') if path else True:
                    relative = dirname[len(path) + 1:] if path else dirname
                    parts = relative.split('/')
                    if len(parts) == 1:
                        folders.add(parts[0])
            
            # Добавляем ".." если не в корне
            if path:
                up_item = QTreeWidgetItem(self.tree_widget)
                up_item.setText(0, "..")
                up_item.setText(1, "")
                up_item.setText(2, "")
                up_item.setData(0, Qt.UserRole, {'type': 'up'})
            
            # Добавляем папки
            for folder in sorted(folders):
                item = QTreeWidgetItem(self.tree_widget)
                item.setText(0, f"📁 {folder}")
                item.setText(1, "")
                item.setText(2, "")
                item.setData(0, Qt.UserRole, {
                    'type': 'folder',
                    'name': folder,
                    'path': (path + '/' + folder) if path else folder
                })
            
            # Добавляем файлы
            for file_data in sorted(files, key=lambda x: x['name']):
                item = QTreeWidgetItem(self.tree_widget)
                item.setText(0, f"📄 {file_data['name']}")
                item.setText(1, "?")
                item.setText(2, "")
                
                item.setData(0, Qt.UserRole, {
                    'type': 'file',
                    'name': file_data['name'],
                    'full_path': file_data['full_path'],
                    'size': 0
                })
            
            iso.close()
        except Exception as e:
            print(f"Ошибка при чтении ISO: {e}")
    
    def on_item_double_clicked(self, item, column):
        """Обработка двойного клика"""
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        
        if data.get('type') == 'folder':
            new_path = data['path']
            self.navigation_history.append(self.current_archive_path)
            self.display_archive_contents(new_path)
            self.btn_back.setEnabled(True)
            self.tree_widget.clearSelection()
            
        elif data.get('type') == 'up':
            if self.navigation_history:
                prev_path = self.navigation_history.pop()
                self.display_archive_contents(prev_path)
                self.tree_widget.clearSelection()
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
            QMessageBox.warning(self, "Внимание", "Выберите файлы или папки для извлечения")
            return
        
        files_to_extract = []
        for item in selected_items:
            data = item.data(0, Qt.UserRole)
            if data:
                if data.get('type') == 'file':
                    files_to_extract.append(data['full_path'])
                elif data.get('type') == 'folder':
                    # Для папок добавляем все файлы в ней
                    folder_path = data['path']
                    self._collect_files_in_folder(folder_path, files_to_extract)
        
        if files_to_extract:
            self.extract_files(files_to_extract)
        else:
            QMessageBox.warning(self, "Внимание", "Выберите файлы или папки для извлечения")
    
    def extract_files(self, file_paths):
        if not file_paths:
            return
        
        extract_dir = QFileDialog.getExistingDirectory(
            self, "Выберите папку для извлечения",
            os.path.join(os.path.expanduser("~"), "Desktop")
        )
        
        if not extract_dir:
            return
        
        try:
            # Определяем формат архива
            archive_ext = os.path.splitext(self.current_archive)[1].lower()
            
            if archive_ext == '.zip':
                self.extract_zip_files(file_paths, extract_dir)
            elif archive_ext == '.rar':
                self.extract_rar_files(file_paths, extract_dir)
            elif archive_ext in ['.7z', '.7zip']:
                self.extract_7z_files(file_paths, extract_dir)
            elif archive_ext == '.tar':
                self.extract_tar_files(file_paths, extract_dir)
            elif archive_ext == '.gz':
                self.extract_gz_files(file_paths, extract_dir)
            elif archive_ext == '.bz2':
                self.extract_bz2_files(file_paths, extract_dir)
            elif archive_ext == '.iso':
                self.extract_iso_files(file_paths, extract_dir)
            else:
                QMessageBox.warning(self, "Внимание", 
                    f"Формат {archive_ext} не поддерживается для извлечения.")
                return
            
            QMessageBox.information(self, "Успех", "Файлы успешно извлечены")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось извлечь файлы:\n{str(e)}")
    
    def extract_zip_files(self, file_paths, extract_dir):
        with zipfile.ZipFile(self.current_archive, 'r') as zipf:
            for file_path in file_paths:
                try:
                    zipf.extract(file_path, extract_dir)
                except:
                    pass
    
    def extract_rar_files(self, file_paths, extract_dir):
        try:
            import rarfile
            with rarfile.RarFile(self.current_archive, 'r') as rarf:
                for file_path in file_paths:
                    try:
                        rarf.extract(file_path, extract_dir)
                    except:
                        pass
        except Exception as e:
            print(f"Ошибка при извлечении RAR: {e}")
    
    def extract_7z_files(self, file_paths, extract_dir):
        try:
            with py7zr.SevenZipFile(self.current_archive, 'r') as archive:
                archive.extract(targets=file_paths, path=extract_dir)
        except Exception as e:
            print(f"Ошибка при извлечении 7z: {e}")
    
    def extract_tar_files(self, file_paths, extract_dir):
        with tarfile.open(self.current_archive, 'r') as tarf:
            for file_path in file_paths:
                try:
                    tarf.extract(file_path, extract_dir)
                except:
                    pass
    
    def extract_gz_files(self, file_paths, extract_dir):
        with tarfile.open(self.current_archive, 'r:gz') as tarf:
            for file_path in file_paths:
                try:
                    tarf.extract(file_path, extract_dir)
                except:
                    pass
    
    def extract_bz2_files(self, file_paths, extract_dir):
        with tarfile.open(self.current_archive, 'r:bz2') as tarf:
            for file_path in file_paths:
                try:
                    tarf.extract(file_path, extract_dir)
                except:
                    pass
    
    def extract_iso_files(self, file_paths, extract_dir):
        try:
            import pycdlib
            iso = pycdlib.PyCdlib()
            iso.open(self.current_archive)
            
            for file_path in file_paths:
                iso_path = file_path.replace('/', '\\')
                output_path = os.path.join(extract_dir, os.path.basename(file_path))
                try:
                    iso.get_file_from_iso(output_path, iso_path=iso_path)
                except:
                    pass
            
            iso.close()
        except Exception as e:
            print(f"Ошибка при извлечении ISO: {e}")
    
    def extract_to_folder(self):
        self.extract_selected()
    
    def _collect_files_in_folder(self, folder_path, files_list):
        """Собирает все файлы в папке для текущего архива"""
        if not self.current_archive:
            return
        
        archive_ext = os.path.splitext(self.current_archive)[1].lower()
        
        try:
            if archive_ext == '.zip':
                with zipfile.ZipFile(self.current_archive, 'r') as zipf:
                    for file_info in zipf.infolist():
                        if file_info.filename.startswith(folder_path):
                            files_list.append(file_info.filename)
            elif archive_ext == '.rar':
                import rarfile
                with rarfile.RarFile(self.current_archive, 'r') as rarf:
                    for file_info in rarf.infolist():
                        if file_info.filename.startswith(folder_path):
                            files_list.append(file_info.filename)
            elif archive_ext in ['.7z', '.7zip']:
                with py7zr.SevenZipFile(self.current_archive, 'r') as archive:
                    for file_info in archive.list():
                        if file_info.filename.startswith(folder_path):
                            files_list.append(file_info.filename)
            elif archive_ext in ['.tar', '.gz', '.bz2']:
                mode = 'r'
                if archive_ext == '.gz':
                    mode = 'r:gz'
                elif archive_ext == '.bz2':
                    mode = 'r:bz2'
                with tarfile.open(self.current_archive, mode) as tarf:
                    for member in tarf.getmembers():
                        if member.name.startswith(folder_path):
                            files_list.append(member.name)
            elif archive_ext == '.iso':
                import pycdlib
                iso = pycdlib.PyCdlib()
                iso.open(self.current_archive)
                for dirname, dirlist, filelist in iso.walk(iso_path='/' + folder_path):
                    for filename in filelist:
                        filepath = os.path.join(dirname, filename).replace('\\', '/')
                        files_list.append(filepath)
                iso.close()
        except Exception as e:
            print(f"Ошибка при сборе файлов в папке: {e}")

    def format_size(self, size):
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} ТБ"

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Темная палитра
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(26, 26, 46))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(22, 22, 37))
    palette.setColor(QPalette.AlternateBase, QColor(30, 30, 50))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(37, 37, 64))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Highlight, QColor(100, 149, 237))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    # Обработка аргументов командной строки
    initial_archive = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '--extract-to' and len(sys.argv) > 2:
            archive_path = sys.argv[2]
            if os.path.exists(archive_path):
                # Извлечь в выбранную папку
                extract_dir = QFileDialog.getExistingDirectory(
                    None, "Выберите папку для извлечения",
                    os.path.join(os.path.expanduser("~"), "Desktop")
                )
                if extract_dir:
                    try:
                        # Определяем формат и извлекаем все
                        archive_ext = os.path.splitext(archive_path)[1].lower()
                        if archive_ext == '.zip':
                            with zipfile.ZipFile(archive_path, 'r') as zipf:
                                zipf.extractall(extract_dir)
                        elif archive_ext == '.rar' and HAS_RARFILE:
                            import rarfile
                            with rarfile.RarFile(archive_path, 'r') as rarf:
                                rarf.extractall(extract_dir)
                        elif archive_ext in ['.7z', '.7zip'] and HAS_PY7ZR:
                            with py7zr.SevenZipFile(archive_path, 'r') as archive:
                                archive.extractall(path=extract_dir)
                        elif archive_ext == '.tar':
                            with tarfile.open(archive_path, 'r') as tarf:
                                tarf.extractall(extract_dir)
                        elif archive_ext == '.gz':
                            with tarfile.open(archive_path, 'r:gz') as tarf:
                                tarf.extractall(extract_dir)
                        elif archive_ext == '.bz2':
                            with tarfile.open(archive_path, 'r:bz2') as tarf:
                                tarf.extractall(extract_dir)
                        elif archive_ext == '.iso' and HAS_PYCDLIB:
                            import pycdlib
                            iso = pycdlib.PyCdlib()
                            iso.open(archive_path)
                            for dirname, dirlist, filelist in iso.walk(iso_path='/'):
                                for filename in filelist:
                                    filepath = os.path.join(dirname, filename)
                                    iso_path = filepath.replace('/', '\\')
                                    output_path = os.path.join(extract_dir, filepath)
                                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                                    iso.get_file_from_iso(output_path, iso_path=iso_path)
                            iso.close()
                        QMessageBox.information(None, "Успех", "Файлы успешно извлечены")
                    except Exception as e:
                        QMessageBox.critical(None, "Ошибка", f"Не удалось извлечь файлы:\n{str(e)}")
                return  # Выход после извлечения
        elif sys.argv[1] == '--compress' and len(sys.argv) > 2:
            # Сжать файлы
            paths = sys.argv[2:]
            files_to_compress = []
            for path in paths:
                if os.path.exists(path):
                    files_to_compress.append(path)
            
            if files_to_compress:
                # Диалог выбора формата и имени архива
                from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton
                dialog = QDialog()
                dialog.setWindowTitle("Создать архив")
                layout = QVBoxLayout(dialog)
                
                # Выбор формата
                format_layout = QHBoxLayout()
                format_layout.addWidget(QLabel("Формат:"))
                format_combo = QComboBox()
                format_combo.addItems(['zip', 'tar', 'gz', 'bz2'])
                if HAS_PY7ZR:
                    format_combo.addItem('7z')
                format_layout.addWidget(format_combo)
                layout.addLayout(format_layout)
                
                # Имя архива
                name_layout = QHBoxLayout()
                name_layout.addWidget(QLabel("Имя архива:"))
                name_edit = QLineEdit("archive")
                name_layout.addWidget(name_edit)
                layout.addLayout(name_layout)
                
                # Кнопки
                btn_layout = QHBoxLayout()
                ok_btn = QPushButton("OK")
                ok_btn.clicked.connect(dialog.accept)
                cancel_btn = QPushButton("Отмена")
                cancel_btn.clicked.connect(dialog.reject)
                btn_layout.addWidget(ok_btn)
                btn_layout.addWidget(cancel_btn)
                layout.addLayout(btn_layout)
                
                if dialog.exec_() == QDialog.Accepted:
                    format_selected = format_combo.currentText()
                    name = name_edit.text()
                    if not name:
                        name = "archive"
                    output_path = os.path.join(os.path.dirname(files_to_compress[0]), f"{name}.{format_selected}")
                    
                    try:
                        if format_selected == 'zip':
                            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                for file_path in files_to_compress:
                                    if os.path.isfile(file_path):
                                        zipf.write(file_path, os.path.basename(file_path))
                                    elif os.path.isdir(file_path):
                                        for root, dirs, files in os.walk(file_path):
                                            for file in files:
                                                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.dirname(file_path)))
                        elif format_selected in ['tar', 'gz', 'bz2']:
                            mode = 'w'
                            if format_selected == 'gz':
                                mode = 'w:gz'
                            elif format_selected == 'bz2':
                                mode = 'w:bz2'
                            with tarfile.open(output_path, mode) as tarf:
                                for file_path in files_to_compress:
                                    tarf.add(file_path, arcname=os.path.basename(file_path))
                        elif format_selected == '7z' and HAS_PY7ZR:
                            with py7zr.SevenZipFile(output_path, 'w') as archive:
                                for file_path in files_to_compress:
                                    archive.write(file_path, os.path.basename(file_path))
                        QMessageBox.information(None, "Успех", "Архив успешно создан")
                    except Exception as e:
                        QMessageBox.critical(None, "Ошибка", f"Не удалось создать архив:\n{str(e)}")
                return  # Выход после сжатия
        else:
            # Обычный файл архива
            archive_path = sys.argv[1]
            if os.path.exists(archive_path):
                initial_archive = archive_path
    
    window = ModernArchiver(initial_archive)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()