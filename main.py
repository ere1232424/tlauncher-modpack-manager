from PySide6 import QtWidgets, QtCore, QtGui
import os
import json
import shutil
import zipfile
import tempfile
import webbrowser
import sys
from PySide6.QtWidgets import QScroller, QScrollerProperties

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DialogWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(350, 450)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        if parent:
            self.setWindowModality(QtCore.Qt.WindowModal)
            parent.window().windowHandle().windowStateChanged.connect(self.handle_parent_state)
        
        # Загружаем иконки жанров
        self.genre_icons = {
            'Хардкорная сборка': QtGui.QIcon(resource_path('zhanar/hard.png')),
            'Хоррор сборка': QtGui.QIcon(resource_path('zhanar/horror.png')),
            'RPG сборка': QtGui.QIcon(resource_path('zhanar/RPG.png')),
            'Вайбовая сборка': QtGui.QIcon(resource_path('zhanar/vibe.png'))
        }
        
        # Основной layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Основной контейнер
        self.container = QtWidgets.QWidget()
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            QWidget#container {
                background-color: #2B2B2B;
                border: 2px solid #555555;
                border-radius: 10px;
            }
        """)
        
        # Layout для контейнера
        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(10)
        
        # Анимация прозрачности
        self.opacity_animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(200)
        
        # Кнопка закрытия
        close_button = QtWidgets.QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888888;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                color: red;
            }
        """)
        
        # Добавляем кнопку закрытия в отдельный layout для выравнивания справа
        close_layout = QtWidgets.QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_button)
        container_layout.addLayout(close_layout)
        
        # Поле ввода названия
        name_label = QtWidgets.QLabel("Название:")
        name_label.setStyleSheet("color: white;")
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Введите название мод-пака")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #3B3B3B;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #666666;
                background-color: #404040;
            }
        """)
        
        # Выбор жанра
        genre_label = QtWidgets.QLabel("Жанр:")
        genre_label.setStyleSheet("color: white;")
        self.genre_combo = QtWidgets.QComboBox()
        
        # Добавляем жанры с иконками
        for genre_name, icon in self.genre_icons.items():
            self.genre_combo.addItem(icon, genre_name)
            
        self.genre_combo.setStyleSheet("""
            QComboBox {
                background-color: #3B3B3B;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                padding-left: 35px;  /* Место для иконки */
            }
            QComboBox:hover {
                background-color: #4B4B4B;
            }
            QComboBox::drop-down {
                border: none;
                width: 35px;
            }
            QComboBox::down-arrow {
                image: url(zhanar/down-arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #2B2B2B;
                color: white;
                border: 1px solid #555555;
                selection-background-color: #4B4B4B;
            }
            QComboBox::item {
                padding: 8px;
                padding-left: 35px;  /* Место для иконки */
            }
        """)
        
        # Кнопки выбора
        self.icon_button = QtWidgets.QPushButton("Выбрать иконку")
        self.mods_button = QtWidgets.QPushButton("Выбрать моды")
        button_style = """
            QPushButton {
                background-color: #3B3B3B;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #4B4B4B;
                border: 1px solid #666666;
            }
        """
        self.icon_button.setStyleSheet(button_style)
        self.mods_button.setStyleSheet(button_style)
        self.icon_button.clicked.connect(self.choose_icon)
        self.mods_button.clicked.connect(self.choose_mods)
        
        # Выбор версии
        version_label = QtWidgets.QLabel("Версия:")
        version_label.setStyleSheet("color: white;")
        self.version_combo = QtWidgets.QComboBox()
        versions = ["1.20.4", "1.20.2", "1.20.1", "1.20", "1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19", 
                   "1.18.2", "1.18.1", "1.18", "1.17.1", "1.17", "1.16.5", "1.16.4", "1.16.3", "1.16.2", "1.16.1", "1.16"]
        self.version_combo.addItems(versions)
        self.version_combo.setStyleSheet("""
            QComboBox {
                background-color: #3B3B3B;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
            }
            QComboBox:hover {
                background-color: #4B4B4B;
            }
            QComboBox::drop-down {
                border: none;
                width: 0px;
            }
            QComboBox::down-arrow {
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #2B2B2B;
                color: white;
                border: 1px solid #555555;
                selection-background-color: #4B4B4B;
            }
        """)
        
        # Кнопка сохранения
        self.save_button = QtWidgets.QPushButton("Сохранить")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #3B3B3B;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #4B4B4B;
                border: 1px solid #666666;
            }
            QPushButton:pressed {
                background-color: #2B2B2B;
                border: 1px solid #777777;
            }
        """)
        self.save_button.clicked.connect(self.save_modpack)
        
        # Добавляем все элементы в контейнер
        container_layout.addWidget(name_label)
        container_layout.addWidget(self.name_input)
        container_layout.addSpacing(10)
        container_layout.addWidget(genre_label)
        container_layout.addWidget(self.genre_combo)
        container_layout.addSpacing(10)
        container_layout.addWidget(self.icon_button)
        container_layout.addWidget(self.mods_button)
        container_layout.addSpacing(10)
        container_layout.addWidget(version_label)
        container_layout.addWidget(self.version_combo)
        container_layout.addStretch()
        container_layout.addWidget(self.save_button)
        
        # Добавляем основной контейнер в layout окна
        main_layout.addWidget(self.container)

    def handle_parent_state(self, state):
        if state & QtCore.Qt.WindowMinimized:
            self.hide()
        else:
            self.show()
            self.raise_()

    def choose_icon(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.window(),
            "Выберите иконку",
            "",
            "Изображения (*.png *.jpg *.jpeg *.ico);;Все файлы (*.*)"
        )
        if file_name:
            print(f"Выбрана иконка: {file_name}")
            self.selected_icon_path = file_name

    def choose_mods(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self.window(),
            "Выберите папку с модами",
            "",
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
        )
        if folder_path:
            print(f"Выбрана папка с модами: {folder_path}")
            self.selected_mods_path = folder_path

    def save_modpack(self):
        # Проверка названия
        name = self.name_input.text().strip()
        if not name:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                "Название модпака не может быть пустым!\nПожалуйста, введите название модпака."
            )
            self.name_input.setFocus()
            return
            
        # Проверка выбора модов
        if not hasattr(self, 'selected_mods_path'):
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                "Папка с модами не выбрана!\nПожалуйста, выберите папку с модами."
            )
            return
            
        # Проверка существования папки с модами
        if not os.path.exists(self.selected_mods_path):
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                "Выбранная папка с модами не существует!\nПожалуйста, выберите существующую папку с модами."
            )
            return
            
        # Проверка наличия файлов в папке с модами
        if not os.listdir(self.selected_mods_path):
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                "Выбранная папка с модами пуста!\nПожалуйста, выберите папку, содержащую моды."
            )
            return

        # Получаем версию и создаем путь к папке версии
        version = self.version_combo.currentText()
        version_path = os.path.join("modpack", version)
        
        # Создаем папку версии, если её нет
        os.makedirs(version_path, exist_ok=True)
        
        # Создаем папку для модпака
        modpack_name = self.name_input.text().strip()
        modpack_path = os.path.join(version_path, modpack_name)
        
        if os.path.exists(modpack_path):
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Модпак с таким названием уже существует!")
            return
            
        os.makedirs(modpack_path)
        
        # Копируем иконку в папку модпака, если она была выбрана
        icon_filename = None
        if hasattr(self, 'selected_icon_path'):
            icon_extension = os.path.splitext(self.selected_icon_path)[1]
            icon_filename = "icon" + icon_extension
            icon_destination = os.path.join(modpack_path, icon_filename)
            shutil.copy2(self.selected_icon_path, icon_destination)
        
        # Перемещаем моды в папку модпака
        mods_destination = os.path.join(modpack_path, "mods")
        try:
            # Если папка mods уже существует, удаляем её
            if os.path.exists(mods_destination):
                shutil.rmtree(mods_destination)
            # Копируем папку с модами вместо перемещения
            shutil.copytree(self.selected_mods_path, mods_destination)
        except Exception as e:
            # Если произошла ошибка при копировании, удаляем созданную папку модпака
            shutil.rmtree(modpack_path)
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось скопировать моды: {str(e)}")
            return
        
        # Создаем и сохраняем метаданные
        metadata = {
            'name': modpack_name,
            'version': version,
            'genre': self.genre_combo.currentText(),
            'icon': icon_filename  # Будет None, если иконка не была выбрана
        }
        
        metadata_path = os.path.join(modpack_path, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        
        QtWidgets.QMessageBox.information(self, "Успех", "Модпак успешно сохранен!")
        
        # Обновляем список модпаков в главном окне
        main_window = self.parent().window()
        if isinstance(main_window, MainWindow):
            main_window.load_modpacks()
            
        self.accept()

class DeleteConfirmDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подтверждение удаления")
        self.setFixedSize(300, 150)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Основной layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Основной контейнер
        container = QtWidgets.QWidget()
        container.setObjectName("container")
        container.setStyleSheet("""
            QWidget#container {
                background-color: #2B2B2B;
                border: 2px solid #555555;
                border-radius: 10px;
            }
        """)
        
        # Layout для контейнера
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)
        
        # Текст предупреждения
        warning_label = QtWidgets.QLabel("Вы уверены, что хотите удалить модпак?\nЭто действие нельзя отменить.")
        warning_label.setStyleSheet("color: white;")
        warning_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Контейнер для кнопок
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Кнопки
        yes_button = QtWidgets.QPushButton("Удалить")
        no_button = QtWidgets.QPushButton("Отмена")
        
        button_style = """
            QPushButton {
                background-color: #3B3B3B;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #4B4B4B;
            }
        """
        
        yes_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #AA3333;
            }
            QPushButton:hover {
                background-color: #CC4444;
            }
        """)
        no_button.setStyleSheet(button_style)
        
        yes_button.clicked.connect(self.accept)
        no_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(no_button)
        buttons_layout.addWidget(yes_button)
        
        container_layout.addWidget(warning_label)
        container_layout.addLayout(buttons_layout)
        
        layout.addWidget(container)

class NotificationWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, text=""):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        
        # Настройка размеров
        self.setFixedSize(300, 50)
        
        # Основной layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Контейнер уведомления
        self.container = QtWidgets.QWidget()
        self.container.setObjectName("notificationContainer")
        self.container.setStyleSheet("""
            QWidget#notificationContainer {
                background-color: #2B2B2B;
                border: 1px solid #555555;
                border-radius: 5px;
            }
        """)
        
        # Layout контейнера
        container_layout = QtWidgets.QHBoxLayout(self.container)
        container_layout.setContentsMargins(15, 10, 15, 10)
        
        # Иконка успеха
        icon_label = QtWidgets.QLabel("✓")
        icon_label.setStyleSheet("""
            QLabel {
                color: #00FF00;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        # Текст уведомления
        text_label = QtWidgets.QLabel(text)
        text_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 13px;
            }
        """)
        
        container_layout.addWidget(icon_label)
        container_layout.addWidget(text_label)
        layout.addWidget(self.container)
        
        # Анимация появления
        self.animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.finished.connect(self.on_animation_finished)
        
        # Таймер для автоматического скрытия
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.start_fade_out)
        
        self.is_fading_out = False
        
        # Устанавливаем начальную прозрачность
        self.setWindowOpacity(0.0)
    
    def show_notification(self):
        if self.parent():
            # Получаем главное окно
            parent = self.parent()
            
            # Получаем абсолютные координаты главного окна
            parent_pos = parent.mapToGlobal(QtCore.QPoint(0, 0))
            
            # Вычисляем позицию уведомления
            x = parent_pos.x() + (parent.width() - self.width()) // 2
            y = parent_pos.y() + 10
            
            # Устанавливаем позицию
            self.move(x, y)
        
        # Показываем с анимацией
        self.show()
        self.raise_()
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        
        # Запускаем таймер
        self.timer.start(2000)
    
    def start_fade_out(self):
        if not self.is_fading_out:
            self.is_fading_out = True
            self.animation.setStartValue(1.0)
            self.animation.setEndValue(0.0)
            self.animation.start()
    
    def on_animation_finished(self):
        if self.is_fading_out:
            self.hide()
            self.is_fading_out = False
            self.deleteLater()  # Удаляем виджет после скрытия

class ModpackWidget(QtWidgets.QWidget):
    def __init__(self, name, genre, icon_path=None, parent=None, modpack_path=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.modpack_path = modpack_path
        self.is_enabled = False
        self.name = name
        
        # Создаем layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Контейнер для виджета
        container = QtWidgets.QWidget()
        container.setObjectName("modpackContainer")
        container.setStyleSheet("""
            QWidget#modpackContainer {
                background-color: #2B2B2B;
                border-radius: 6px;
            }
        """)
        
        container_layout = QtWidgets.QHBoxLayout(container)
        container_layout.setContentsMargins(6, 6, 6, 6)
        container_layout.setSpacing(6)
        
        # Иконка модпака
        icon_label = QtWidgets.QLabel()
        icon_label.setFixedSize(45, 45)
        if icon_path and os.path.exists(icon_path):
            pixmap = QtGui.QPixmap(icon_path)
        else:
            pixmap = QtGui.QPixmap("icon-auto.jpg")
        icon_label.setPixmap(pixmap.scaled(45, 45, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        container_layout.addWidget(icon_label)
        
        # Информация о модпаке
        info_layout = QtWidgets.QVBoxLayout()
        info_layout.setSpacing(0)
        
        # Название модпака
        name_label = QtWidgets.QLabel(name)
        name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        info_layout.addWidget(name_label)
        
        # Контейнер для жанра и версии
        details_container = QtWidgets.QHBoxLayout()
        details_container.setSpacing(8)
        
        # Контейнер для жанра с иконкой
        genre_container = QtWidgets.QHBoxLayout()
        genre_container.setSpacing(4)
        
        # Иконка жанра
        genre_icon = QtWidgets.QLabel()
        genre_icon.setFixedSize(12, 12)
        
        # Определяем иконку жанра
        genre_icons = {
            'Хардкорная сборка': 'zhanar/hard.png',
            'Хоррор сборка': 'zhanar/horror.png',
            'RPG сборка': 'zhanar/RPG.png',
            'Вайбовая сборка': 'zhanar/vibe.png'
        }
        
        if genre in genre_icons and os.path.exists(genre_icons[genre]):
            pixmap = QtGui.QPixmap(genre_icons[genre])
            genre_icon.setPixmap(pixmap.scaled(12, 12, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        
        # Текст жанра
        genre_label = QtWidgets.QLabel(genre)
        genre_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
            }
        """)
        
        genre_container.addWidget(genre_icon)
        genre_container.addWidget(genre_label)
        
        # Добавляем версию
        version = os.path.basename(os.path.dirname(modpack_path)) if modpack_path else ""
        version_label = QtWidgets.QLabel(version)
        version_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
            }
        """)
        
        details_container.addLayout(genre_container)
        details_container.addWidget(version_label)
        details_container.addStretch()
        
        info_layout.addLayout(details_container)
        
        container_layout.addLayout(info_layout)
        container_layout.addStretch()
        
        # Кнопки
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(0)
        
        # Общий стиль для иконок-кнопок
        icon_button_style = """
            QPushButton {
                background-color: #3B3B3B;
                color: #888888;
                border: none;
                border-radius: 3px;
                font-size: 14px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #4B4B4B;
                color: white;
            }
            QPushButton:checked {
                color: #FFD700;
            }
        """
        
        # Кнопка "В избранное"
        self.favorite_button = QtWidgets.QPushButton("★")
        self.favorite_button.setFixedSize(25, 25)
        self.favorite_button.setStyleSheet(icon_button_style)
        self.favorite_button.setCheckable(True)
        self.favorite_button.clicked.connect(self.toggle_favorite)
        
        # Загружаем состояние избранного из метаданных
        if self.modpack_path:
            metadata_path = os.path.join(self.modpack_path, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    self.favorite_button.setChecked(metadata.get('favorite', False))

        # Кнопка "Импорт"
        self.import_button = QtWidgets.QPushButton("⬇")
        self.import_button.setFixedSize(25, 25)
        self.import_button.setStyleSheet(icon_button_style)
        self.import_button.clicked.connect(self.export_modpack)
        
        # Кнопка "Удалить" (корзина)
        self.delete_button = QtWidgets.QPushButton("🗑")
        self.delete_button.setFixedSize(25, 25)
        self.delete_button.setStyleSheet(icon_button_style + """
            QPushButton:hover {
                color: #FF4444;
            }
        """)
        self.delete_button.clicked.connect(self.delete_modpack)
        
        # Кнопка "Включить"
        self.enable_button = QtWidgets.QPushButton("Включить")
        self.enable_button.setFixedSize(80, 25)
        self.enable_button.setStyleSheet("""
            QPushButton {
                background-color: #3B3B3B;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4B4B4B;
            }
        """)
        self.enable_button.clicked.connect(self.toggle_modpack)
        
        # Создаем контейнер для всех кнопок с фиксированной шириной
        buttons_container = QtWidgets.QWidget()
        buttons_container.setFixedWidth(190)
        buttons_container_layout = QtWidgets.QHBoxLayout(buttons_container)
        buttons_container_layout.setContentsMargins(0, 0, 0, 0)
        buttons_container_layout.setSpacing(8)
        
        # Добавляем кнопки в контейнер
        buttons_container_layout.addWidget(self.favorite_button)
        buttons_container_layout.addWidget(self.import_button)
        buttons_container_layout.addWidget(self.delete_button)
        buttons_container_layout.addWidget(self.enable_button)
        
        # Добавляем контейнер с кнопками в основной layout
        buttons_layout.addWidget(buttons_container)
        container_layout.addLayout(buttons_layout)
        
        layout.addWidget(container)

    def toggle_favorite(self):
        if not self.modpack_path:
            return
            
        # Получаем текущее состояние
        is_favorite = self.favorite_button.isChecked()
        
        # Обновляем метаданные
        metadata_path = os.path.join(self.modpack_path, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            metadata['favorite'] = is_favorite
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=4)
        
        # Обновляем список модпаков в главном окне
        main_window = self.window()
        if isinstance(main_window, MainWindow):
            main_window.load_modpacks()

    def export_modpack(self):
        if not self.modpack_path:
            return
            
        # Получаем имя модпака
        modpack_name = os.path.basename(self.modpack_path)
        
        # Открываем диалог сохранения файла
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Сохранить модпак",
            f"{modpack_name}.zip",
            "ZIP Archive (*.zip)"
        )
        
        if not file_path:
            return
            
        try:
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.modpack_path):
                    for file in files:
                        file_path_src = os.path.join(root, file)
                        arcname = os.path.relpath(file_path_src, self.modpack_path)
                        zipf.write(file_path_src, arcname)
            
            # Показываем уведомление об успехе
            notification = NotificationWidget(self.window(), "Модпак успешно сохранен!")
            notification.show_notification()
            
        except Exception as e:
            error_dialog = QtWidgets.QDialog(self.window())
            error_dialog.setWindowTitle("Ошибка")
            error_dialog.setFixedSize(300, 150)
            error_dialog.setWindowFlag(QtCore.Qt.FramelessWindowHint)
            error_dialog.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            
            layout = QtWidgets.QVBoxLayout(error_dialog)
            layout.setContentsMargins(0, 0, 0, 0)
            
            container = QtWidgets.QWidget()
            container.setObjectName("container")
            container.setStyleSheet("""
                QWidget#container {
                    background-color: #2B2B2B;
                    border: 2px solid #555555;
                    border-radius: 10px;
                }
            """)
            
            container_layout = QtWidgets.QVBoxLayout(container)
            container_layout.setContentsMargins(20, 20, 20, 20)
            
            error_label = QtWidgets.QLabel(f"Не удалось создать архив: {str(e)}")
            error_label.setStyleSheet("color: white;")
            error_label.setAlignment(QtCore.Qt.AlignCenter)
            error_label.setWordWrap(True)
            
            ok_button = QtWidgets.QPushButton("OK")
            ok_button.setStyleSheet("""
                QPushButton {
                    background-color: #3B3B3B;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    padding: 8px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #4B4B4B;
                }
            """)
            ok_button.clicked.connect(error_dialog.accept)
            
            container_layout.addWidget(error_label)
            container_layout.addWidget(ok_button, alignment=QtCore.Qt.AlignCenter)
            
            layout.addWidget(container)
            
            if self.window():
                center_point = self.window().geometry().center()
                dialog_geometry = error_dialog.geometry()
                dialog_geometry.moveCenter(center_point)
                error_dialog.setGeometry(dialog_geometry)
            
            error_dialog.exec()

    def delete_modpack(self):
        dialog = DeleteConfirmDialog(self.window())
        
        # Центрируем диалог относительно главного окна
        if self.window():
            center_point = self.window().geometry().center()
            dialog_geometry = dialog.geometry()
            dialog_geometry.moveCenter(center_point)
            dialog.setGeometry(dialog_geometry)
        
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            try:
                # Удаляем папку модпака
                shutil.rmtree(self.modpack_path)
                
                # Обновляем список модпаков в главном окне
                main_window = self.window()
                if isinstance(main_window, MainWindow):
                    main_window.load_modpacks()
                    
            except Exception as e:
                error_dialog = QtWidgets.QDialog(self.window())
                error_dialog.setWindowTitle("Ошибка")
                error_dialog.setFixedSize(300, 150)
                error_dialog.setWindowFlag(QtCore.Qt.FramelessWindowHint)
                error_dialog.setAttribute(QtCore.Qt.WA_TranslucentBackground)
                
                layout = QtWidgets.QVBoxLayout(error_dialog)
                layout.setContentsMargins(0, 0, 0, 0)
                
                container = QtWidgets.QWidget()
                container.setObjectName("container")
                container.setStyleSheet("""
                    QWidget#container {
                        background-color: #2B2B2B;
                        border: 2px solid #555555;
                        border-radius: 10px;
                    }
                """)
                
                container_layout = QtWidgets.QVBoxLayout(container)
                container_layout.setContentsMargins(20, 20, 20, 20)
                
                error_label = QtWidgets.QLabel(f"Не удалось удалить модпак:\n{str(e)}")
                error_label.setStyleSheet("color: white;")
                error_label.setAlignment(QtCore.Qt.AlignCenter)
                error_label.setWordWrap(True)
                
                ok_button = QtWidgets.QPushButton("OK")
                ok_button.setStyleSheet("""
                    QPushButton {
                        background-color: #3B3B3B;
                        color: white;
                        border: 1px solid #555555;
                        border-radius: 5px;
                        padding: 8px;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #4B4B4B;
                    }
                """)
                ok_button.clicked.connect(error_dialog.accept)
                
                container_layout.addWidget(error_label)
                container_layout.addWidget(ok_button, alignment=QtCore.Qt.AlignCenter)
                
                layout.addWidget(container)
                
                if self.window():
                    center_point = self.window().geometry().center()
                    dialog_geometry = error_dialog.geometry()
                    dialog_geometry.moveCenter(center_point)
                    error_dialog.setGeometry(dialog_geometry)
                
                error_dialog.exec()

    def toggle_modpack(self):
        # Получаем путь к папке .minecraft
        minecraft_path = os.path.join(os.getenv('APPDATA'), '.minecraft')
        if not os.path.exists(minecraft_path):
            QtWidgets.QMessageBox.critical(
                self.window(),
                "Ошибка",
                "Папка .minecraft не найдена!\nУбедитесь, что Minecraft установлен."
            )
            return

        # Папки, которые нужно обработать
        folders = ['config', 'journeymap', 'resourcepacks', 'shaderpacks']
        
        # Путь к папке mods в модпаке
        modpack_mods_path = os.path.join(self.modpack_path, 'mods')
        
        # Проверяем содержимое папки mods
        has_jar_files = False
        has_folders = False
        if os.path.exists(modpack_mods_path):
            for item in os.listdir(modpack_mods_path):
                item_path = os.path.join(modpack_mods_path, item)
                if os.path.isfile(item_path) and item.lower().endswith('.jar'):
                    has_jar_files = True
                elif os.path.isdir(item_path) and item in folders:
                    has_folders = True
        
        # Путь к папке для резервных копий в нашем модпаке
        backup_path = os.path.join(self.modpack_path, '_backup')
        
        if self.is_enabled:
            # Выключаем модпак
            try:
                # Обрабатываем папку mods
                mc_mods_path = os.path.join(minecraft_path, 'mods')
                if os.path.exists(mc_mods_path):
                    # Очищаем текущую папку mods
                    for item in os.listdir(mc_mods_path):
                        item_path = os.path.join(mc_mods_path, item)
                        try:
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                        except Exception as e:
                            print(f"Не удалось удалить {item_path}: {e}")
                    
                    # Восстанавливаем моды из бэкапа, если они есть
                    backup_mods = os.path.join(backup_path, 'mods')
                    if os.path.exists(backup_mods):
                        for item in os.listdir(backup_mods):
                            src_path = os.path.join(backup_mods, item)
                            dst_path = os.path.join(mc_mods_path, item)
                            if os.path.isfile(src_path):
                                shutil.copy2(src_path, dst_path)
                
                # Обрабатываем остальные папки
                if has_folders:
                    for folder in folders:
                        mc_folder = os.path.join(minecraft_path, folder)
                        backup_folder = os.path.join(backup_path, folder)
                        modpack_folder = os.path.join(modpack_mods_path, folder)
                        
                        # Если папка существует в модпаке
                        if os.path.exists(modpack_folder):
                            # Удаляем текущую папку из .minecraft
                            if os.path.exists(mc_folder):
                                shutil.rmtree(mc_folder)
                            
                            # Восстанавливаем из бэкапа, если он есть
                            if os.path.exists(backup_folder):
                                shutil.copytree(backup_folder, mc_folder)
                
                # Удаляем папку с резервными копиями
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
                
                self.is_enabled = False
                MainWindow.active_modpack = None
                self.enable_button.setText("Включить")
                self.enable_button.setStyleSheet("""
                    QPushButton {
                        background-color: #3B3B3B;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #4B4B4B;
                    }
                """)
                
                # Обновляем состояние всех кнопок
                main_window = self.window()
                if isinstance(main_window, MainWindow):
                    main_window.update_enable_buttons()
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self.window(),
                    "Ошибка",
                    f"Не удалось отключить модпак: {str(e)}"
                )
                return
                
        else:
            # Включаем модпак
            try:
                # Создаем папку для резервных копий
                os.makedirs(backup_path, exist_ok=True)
                
                # Обрабатываем папку mods
                if has_jar_files:
                    mc_mods_path = os.path.join(minecraft_path, 'mods')
                    backup_mods = os.path.join(backup_path, 'mods')
                    
                    # Создаем папку mods если её нет
                    os.makedirs(mc_mods_path, exist_ok=True)
                    
                    # Делаем бэкап существующих модов
                    if os.path.exists(mc_mods_path) and os.listdir(mc_mods_path):
                        os.makedirs(backup_mods, exist_ok=True)
                        for item in os.listdir(mc_mods_path):
                            src_path = os.path.join(mc_mods_path, item)
                            dst_path = os.path.join(backup_mods, item)
                            if os.path.isfile(src_path):
                                shutil.copy2(src_path, dst_path)
                    
                    # Очищаем папку mods
                    for item in os.listdir(mc_mods_path):
                        item_path = os.path.join(mc_mods_path, item)
                        try:
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                        except Exception as e:
                            print(f"Не удалось удалить {item_path}: {e}")
                    
                    # Копируем JAR файлы
                    for item in os.listdir(modpack_mods_path):
                        if item.lower().endswith('.jar'):
                            src_path = os.path.join(modpack_mods_path, item)
                            dst_path = os.path.join(mc_mods_path, item)
                            shutil.copy2(src_path, dst_path)
                
                # Обрабатываем остальные папки
                if has_folders:
                    for folder in folders:
                        mc_folder = os.path.join(minecraft_path, folder)
                        backup_folder = os.path.join(backup_path, folder)
                        modpack_folder = os.path.join(modpack_mods_path, folder)
                        
                        # Если папка существует в модпаке
                        if os.path.exists(modpack_folder):
                            # Делаем бэкап если папка существует в .minecraft
                            if os.path.exists(mc_folder):
                                shutil.copytree(mc_folder, backup_folder)
                                shutil.rmtree(mc_folder)
                            
                            # Копируем папку из модпака
                            shutil.copytree(modpack_folder, mc_folder)
                
                self.is_enabled = True
                MainWindow.active_modpack = self
                self.enable_button.setText("Выключить")
                self.enable_button.setStyleSheet("""
                    QPushButton {
                        background-color: #AA3333;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #CC4444;
                    }
                """)
                
                # Обновляем состояние всех кнопок
                main_window = self.window()
                if isinstance(main_window, MainWindow):
                    main_window.update_enable_buttons()
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self.window(),
                    "Ошибка",
                    f"Не удалось включить модпак: {str(e)}"
                )
                return

class MainWindow(QtWidgets.QMainWindow):
    active_modpack = None  # Статическая переменная для отслеживания активного модпака
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mincragt Menedger")
        self.setFixedSize(500, 600)  # Фиксируем размер окна
        
        # Устанавливаем иконку приложения
        app_icon = QtGui.QIcon(resource_path("icon.ico"))
        self.setWindowIcon(app_icon)
        app = QtWidgets.QApplication.instance()
        app.setWindowIcon(app_icon)
        
        # Инициализируем атрибуты для диалога и анимаций
        self.dialog = None
        self.animation_group = None
        self.blur_animation = None
        
        # Создаем оверлей
        self.overlay = QtWidgets.QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.5);")
        self.overlay.hide()
        
        # Создаем эффект размытия
        self.blur_effect = QtWidgets.QGraphicsBlurEffect(self)
        self.blur_effect.setBlurRadius(0)
        self.overlay.setGraphicsEffect(self.blur_effect)
        
        # Создаем папку modpack, если её нет
        os.makedirs("modpack", exist_ok=True)
        
        # Создаем центральный виджет
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Создаем главный layout
        layout = QtWidgets.QVBoxLayout(self.central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Верхняя панель
        top_panel = QtWidgets.QHBoxLayout()
        
        # Заголовок "Мои сборки"
        title_label = QtWidgets.QLabel("Мои сборки")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        top_panel.addWidget(title_label)
        
        # Кнопка добавления
        self.button = QtWidgets.QPushButton("+")
        self.button.setFixedSize(60, 60)
        self.button.clicked.connect(self.show_dialog)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #2B2B2B;
                color: white;
                font-size: 24px;
                border: 2px solid white;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #3B3B3B;
            }
            QPushButton:disabled {
                background-color: #1B1B1B;
                color: #808080;
                border-color: #808080;
            }
        """)
        
        top_panel.addStretch()
        top_panel.addWidget(self.button)
        
        layout.addLayout(top_panel)
        
        # Создаем QScrollArea
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        # Настраиваем плавную прокрутку
        QScroller.grabGesture(scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        scroller = QScroller.scroller(scroll_area.viewport())
        scroll_properties = scroller.scrollerProperties()
        
        # Настройка параметров плавности
        scroll_properties.setScrollMetric(QScrollerProperties.VerticalOvershootPolicy, QScrollerProperties.OvershootAlwaysOff)
        scroll_properties.setScrollMetric(QScrollerProperties.ScrollingCurve, QtCore.QEasingCurve.OutCubic)
        scroll_properties.setScrollMetric(QScrollerProperties.DragStartDistance, 0.002)
        scroll_properties.setScrollMetric(QScrollerProperties.MinimumVelocity, 0.05)
        scroll_properties.setScrollMetric(QScrollerProperties.MaximumVelocity, 0.5)
        scroll_properties.setScrollMetric(QScrollerProperties.MaximumClickThroughVelocity, 0.5)
        scroll_properties.setScrollMetric(QScrollerProperties.DragVelocitySmoothingFactor, 0.15)
        scroll_properties.setScrollMetric(QScrollerProperties.AcceleratingFlickMaximumTime, 0.4)
        scroll_properties.setScrollMetric(QScrollerProperties.AcceleratingFlickSpeedupFactor, 1.2)
        scroll_properties.setScrollMetric(QScrollerProperties.SnapPositionRatio, 0.2)
        scroll_properties.setScrollMetric(QScrollerProperties.DecelerationFactor, 0.15)
        
        scroller.setScrollerProperties(scroll_properties)
        
        # Улучшенный стиль скроллбара
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2B2B2B;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 24px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #666666;
            }
            QScrollBar::handle:vertical:pressed {
                background: #777777;
            }
            QScrollBar::add-line:vertical {
                height: 0px;
            }
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
                border-radius: 4px;
            }
        """)
        
        # Создаем контейнер для модпаков
        modpacks_container = QtWidgets.QWidget()
        modpacks_container.setStyleSheet("background-color: transparent;")
        modpacks_container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.modpacks_layout = QtWidgets.QVBoxLayout(modpacks_container)
        self.modpacks_layout.setContentsMargins(0, 0, 0, 0)
        self.modpacks_layout.setSpacing(8)
        self.modpacks_layout.setAlignment(QtCore.Qt.AlignTop)
        
        # Устанавливаем контейнер в QScrollArea
        scroll_area.setWidget(modpacks_container)
        
        # Добавляем QScrollArea в главный layout
        layout.addWidget(scroll_area, 1)  # Устанавливаем stretch factor в 1
        
        # Загружаем существующие модпаки
        self.load_modpacks()
        
    def load_modpacks(self):
        # Очищаем существующие модпаки
        for i in reversed(range(self.modpacks_layout.count())): 
            widget = self.modpacks_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
            
        # Список для хранения модпаков
        modpacks = []
            
        # Проходим по всем версиям
        for version in os.listdir("modpack"):
            version_path = os.path.join("modpack", version)
            if os.path.isdir(version_path):
                # Проходим по всем модпакам версии
                for modpack in os.listdir(version_path):
                    modpack_path = os.path.join(version_path, modpack)
                    if os.path.isdir(modpack_path):
                        # Загружаем метаданные
                        metadata_path = os.path.join(modpack_path, "metadata.json")
                        if os.path.exists(metadata_path):
                            with open(metadata_path, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                                
                            # Получаем путь к иконке
                            icon_path = None
                            if metadata.get('icon'):
                                icon_path = os.path.join(modpack_path, metadata['icon'])
                                
                            # Добавляем модпак в список
                            modpacks.append({
                                'name': metadata['name'],
                                'genre': metadata['genre'],
                                'icon_path': icon_path,
                                'path': modpack_path,
                                'favorite': metadata.get('favorite', False)
                            })
        
        # Сортируем модпаки: сначала избранные, потом остальные
        modpacks.sort(key=lambda x: (not x['favorite'], x['name']))
        
        # Создаем виджеты для каждого модпака
        for modpack in modpacks:
            modpack_widget = ModpackWidget(
                name=modpack['name'],
                genre=modpack['genre'],
                icon_path=modpack['icon_path'],
                parent=self,
                modpack_path=modpack['path']
            )
            self.modpacks_layout.addWidget(modpack_widget)
        
    def show_dialog(self):
        if self.dialog is not None and self.dialog.isVisible():
            return
            
        # Отключаем кнопку на время показа диалога
        self.button.setEnabled(False)
        
        # Показываем оверлей на всё окно
        self.overlay.setGeometry(self.rect())
        self.overlay.show()
        self.overlay.raise_()
            
        # Создаем новые анимации
        self.create_animations()
            
        # Создаем новый диалог
        self.dialog = DialogWindow(self)
        self.dialog.finished.connect(self.dialog_closed)
        
        # Позиционируем диалог по центру главного окна
        dialog_geometry = self.dialog.geometry()
        center_point = self.geometry().center()
        dialog_geometry.moveCenter(center_point)
        self.dialog.setGeometry(dialog_geometry)
        
        # Устанавливаем начальную прозрачность и показываем диалог
        self.dialog.setWindowOpacity(0.0)
        self.dialog.show()
        self.dialog.raise_()  # Поднимаем диалог над оверлеем
        
        # Запускаем анимации
        self.dialog.opacity_animation.setStartValue(0.0)
        self.dialog.opacity_animation.setEndValue(1.0)
        
        # Создаем параллельную группу анимаций
        self.animation_group = QtCore.QParallelAnimationGroup(self)
        self.animation_group.addAnimation(self.dialog.opacity_animation)
        
        # Добавляем анимацию размытия
        self.blur_animation.setStartValue(0)
        self.blur_animation.setEndValue(10)
        self.animation_group.addAnimation(self.blur_animation)
        
        # Запускаем все анимации одновременно
        self.animation_group.start()
        
    def dialog_closed(self):
        if self.dialog and self.blur_animation:
            # Создаем параллельную группу для закрытия
            close_group = QtCore.QParallelAnimationGroup(self)
            
            # Анимация исчезновения размытия
            close_animation = QtCore.QPropertyAnimation(self.blur_effect, b"blurRadius", self)
            close_animation.setDuration(200)
            close_animation.setStartValue(10)
            close_animation.setEndValue(0)
            close_group.addAnimation(close_animation)
            
            # Запускаем анимации
            close_group.start()
            
            # Подключаем очистку после завершения
            close_group.finished.connect(lambda: self.cleanup_animations(close_group))
        
        # Скрываем оверлей
        self.overlay.hide()
        
        # Включаем кнопку обратно
        self.button.setEnabled(True)
        
        # Очищаем ссылку на диалог
        self.dialog = None
        
    def cleanup_animations(self, animation_group):
        # Очищаем все анимации
        if animation_group:
            animation_group.deleteLater()
        if self.animation_group:
            self.animation_group.deleteLater()
        if self.blur_animation:
            self.blur_animation.deleteLater()
        self.blur_animation = None
        self.animation_group = None

    def create_animations(self):
        # Создаем анимацию размытия
        self.blur_animation = QtCore.QPropertyAnimation(self.blur_effect, b"blurRadius", self)
        self.blur_animation.setDuration(200)
        
        # Создаем группу анимаций
        self.animation_group = QtCore.QParallelAnimationGroup(self)
        self.animation_group.addAnimation(self.blur_animation)

    def import_modpack(self):
        # Открываем диалог выбора файла
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Выберите файл модпака",
            "",
            "Файлы модпаков (*.zip);;Все файлы (*.*)"
        )
        
        if file_path:
            # TODO: Добавить логику импорта модпака
            print(f"Импорт модпака: {file_path}")

    def update_enable_buttons(self):
        # Проходим по всем виджетам модпаков и обновляем состояние кнопок
        for i in range(self.modpacks_layout.count()):
            widget = self.modpacks_layout.itemAt(i).widget()
            if isinstance(widget, ModpackWidget):
                if MainWindow.active_modpack is None:
                    # Если нет активного модпака, включаем все кнопки
                    widget.enable_button.setEnabled(True)
                    widget.enable_button.setToolTip("")
                    widget.favorite_button.setEnabled(True)
                    widget.import_button.setEnabled(True)
                    widget.delete_button.setEnabled(True)
                    widget.favorite_button.setToolTip("")
                    widget.import_button.setToolTip("")
                    widget.delete_button.setToolTip("")
                else:
                    if widget != MainWindow.active_modpack:
                        # Если есть активный модпак, отключаем все кнопки у неактивных модпаков
                        widget.enable_button.setEnabled(False)
                        widget.favorite_button.setEnabled(False)
                        widget.import_button.setEnabled(False)
                        widget.delete_button.setEnabled(False)
                        tooltip = "Сначала отключите активный модпак"
                        widget.enable_button.setToolTip(tooltip)
                        widget.favorite_button.setToolTip(tooltip)
                        widget.import_button.setToolTip(tooltip)
                        widget.delete_button.setToolTip(tooltip)
                    else:
                        # Для активного модпака оставляем только кнопку выключения
                        widget.favorite_button.setEnabled(False)
                        widget.import_button.setEnabled(False)
                        widget.delete_button.setEnabled(False)
                        tooltip = "Сначала отключите модпак"
                        widget.favorite_button.setToolTip(tooltip)
                        widget.import_button.setToolTip(tooltip)
                        widget.delete_button.setToolTip(tooltip)

app = QtWidgets.QApplication([])
window = MainWindow()
window.show()
app.exec()

