from PySide6 import QtWidgets, QtCore, QtGui
import os
import json
import shutil
from utils.resource_utils import resource_path
from utils.translator import Translator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.main_window import MainWindow

# Константы для жанров
GENRE_HARDCORE = "hardcore"
GENRE_HORROR = "horror"
GENRE_RPG = "rpg"
GENRE_VIBE = "vibe"

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
        
        # Инициализируем переводчик
        self.translator = Translator()
        
        # Загружаем иконки жанров
        self.genre_icons = {
            GENRE_HARDCORE: QtGui.QIcon(resource_path('zhanar/hard.png')),
            GENRE_HORROR: QtGui.QIcon(resource_path('zhanar/horror.png')),
            GENRE_RPG: QtGui.QIcon(resource_path('zhanar/RPG.png')),
            GENRE_VIBE: QtGui.QIcon(resource_path('zhanar/vibe.png'))
        }
        
        self.setup_ui()
        
    def setup_ui(self):
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
        name_label = QtWidgets.QLabel(self.translator.translate("modpack_name") + ":")
        name_label.setStyleSheet("color: white;")
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText(self.translator.translate("modpack_name"))
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
        
        # Настройка жанров
        genre_label = QtWidgets.QLabel(self.translator.translate("genre") + ":")
        genre_label.setStyleSheet("color: white;")
        self.genre_combo = QtWidgets.QComboBox()
        self.genre_combo.setFixedHeight(20)
        self.genre_combo.setView(QtWidgets.QListView())
        
        # Настройка popup окна для жанров
        genre_popup = self.genre_combo.view()
        genre_popup.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        genre_popup.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        genre_popup.setSpacing(4)
        genre_popup.setContentsMargins(0, 4, 0, 4)
        
        # Добавляем жанры с иконками
        genres = [
            (GENRE_HARDCORE, self.translator.translate("genres.hardcore")),
            (GENRE_HORROR, self.translator.translate("genres.horror")),
            (GENRE_RPG, self.translator.translate("genres.rpg")),
            (GENRE_VIBE, self.translator.translate("genres.vibe"))
        ]
        
        for genre_key, genre_text in genres:
            self.genre_combo.addItem(self.genre_icons[genre_key], genre_text, genre_key)
        
        # Настраиваем отображение popup для жанров
        self.genre_combo.setMaxVisibleItems(len(genres))  # Показываем все жанры
        genre_popup.window().setWindowFlags(
            QtCore.Qt.Popup |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.NoDropShadowWindowHint
        )
        
        # Общий стиль для комбобоксов
        combo_style = """
            QComboBox {
                background-color: #2B2B2B;
                color: white;
                border: 1px solid #555555;
                border-radius: 2px;
                padding: 0px 2px;
                font-size: 11px;
                min-height: 18px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 14px;
            }
            
            QComboBox::down-arrow {
                image: url(zhanar/down-arrow.png);
                width: 8px;
                height: 8px;
            }
            
            QListView {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #383838;
                outline: none;
                padding: 0px;
                font-size: 11px;
            }
            
            QListView::item {
                height: 20px;
                padding: 2px 2px;
                border: none;
                background-color: #1e1e1e;
            }
            
            QListView::item:hover {
                background-color: #2d2d2d;
            }
            
            QListView::item:selected {
                background-color: #383838;
            }
            
            QScrollBar:vertical {
                border: none;
                background-color: #1e1e1e;
                width: 4px;
                margin: 0px;
                border-radius: 2px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #383838;
                min-height: 24px;
                border-radius: 2px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #424242;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
                border: none;
            }
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
                border: none;
            }
        """
        
        self.genre_combo.setStyleSheet(combo_style)
        
        # Настройка версий
        version_label = QtWidgets.QLabel(self.translator.translate("version") + ":")
        version_label.setStyleSheet("color: white;")
        
        # Создаем виджет для версий с прокруткой
        version_scroll = QtWidgets.QScrollArea()
        version_scroll.setWidgetResizable(True)
        version_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        version_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        version_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #383838;
                min-height: 24px;
                border-radius: 2px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
                border: none;
            }
        """)
        
        # Создаем контейнер для кнопок версий
        version_container = QtWidgets.QWidget()
        version_container.setStyleSheet("background-color: transparent;")
        version_grid = QtWidgets.QGridLayout(version_container)
        version_grid.setSpacing(8)  # Увеличиваем отступ между кнопками с 4 до 8
        version_grid.setContentsMargins(0, 0, 4, 0)
        
        # Список версий
        versions = ["1.20.4", "1.20.2", "1.20.1", "1.20", "1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19", 
                   "1.18.2", "1.18.1", "1.18", "1.17.1", "1.17", "1.16.5", "1.16.4", "1.16.3", "1.16.2", "1.16.1", "1.16"]
        
        # Создаем кнопки версий
        self.version_buttons = []
        self.selected_version = None
        
        # Стиль для кнопок версий
        button_style = """
            QPushButton {
                background-color: #2B2B2B;
                color: white;
                border: 1px solid #555555;
                border-radius: 2px;
                padding: 4px;
                font-size: 11px;
                min-height: 18px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #3B3B3B;
                border: 1px solid #666666;
            }
            QPushButton:checked {
                background-color: #383838;
                border: 1px solid #777777;
            }
        """
        
        # Размещаем кнопки в сетке (4 кнопки в ряд)
        for i, version in enumerate(versions):
            button = QtWidgets.QPushButton(version)
            button.setCheckable(True)
            button.setStyleSheet(button_style)
            button.clicked.connect(lambda checked, v=version: self.select_version(v))
            self.version_buttons.append(button)
            version_grid.addWidget(button, i // 4, i % 4)
            
            # Устанавливаем первую версию как выбранную по умолчанию
            if i == 0:
                button.setChecked(True)
                self.selected_version = version
        
        # Устанавливаем контейнер в область прокрутки
        version_scroll.setWidget(version_container)
        version_scroll.setFixedHeight(90)  # Показываем примерно 5-6 рядов кнопок
        
        # Добавляем виджеты в контейнер
        container_layout.addWidget(name_label)
        container_layout.addWidget(self.name_input)
        container_layout.addSpacing(10)
        container_layout.addWidget(genre_label)
        container_layout.addWidget(self.genre_combo)
        container_layout.addSpacing(10)
        container_layout.addWidget(version_label)
        container_layout.addWidget(version_scroll)
        container_layout.addSpacing(15)  # Добавляем отступ в 15 пикселей
        
        # Кнопки выбора
        self.icon_button = QtWidgets.QPushButton(self.translator.translate("choose_icon"))
        self.mods_button = QtWidgets.QPushButton(self.translator.translate("choose_mods"))
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
        
        # Кнопка сохранения
        self.save_button = QtWidgets.QPushButton(self.translator.translate("save"))
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
        container_layout.addWidget(self.icon_button)
        container_layout.addWidget(self.mods_button)
        container_layout.addWidget(self.save_button)
        
        # Добавляем основной контейнер в layout окна
        main_layout.addWidget(self.container)

    def handle_parent_state(self, state):
        if state & QtCore.Qt.WindowMinimized:
            self.hide()
        else:
            self.show()
            self.raise_()

    def eventFilter(self, obj, event):
        if obj == self.version_scroll.window():
            if event.type() == QtCore.QEvent.Type.Show:
                # Получаем popup и его размеры
                popup = self.version_scroll.widget()
                popup_window = popup.window()
                
                # Вычисляем позицию для popup
                scroll_rect = self.version_scroll.rect()
                global_point = self.version_scroll.mapToGlobal(scroll_rect.bottomLeft())
                
                # Устанавливаем позицию и размеры
                popup_window.move(global_point.x(), global_point.y())
                
                # Устанавливаем фиксированную ширину popup равной ширине scroll area
                popup.setFixedWidth(self.version_scroll.width())
                
                return True
        return super().eventFilter(obj, event)

    def choose_icon(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.window(),
            self.translator.translate("choose_icon"),
            "",
            "Изображения (*.png *.jpg *.jpeg *.ico);;Все файлы (*.*)"
        )
        if file_name:
            print(f"Выбрана иконка: {file_name}")
            self.selected_icon_path = file_name

    def choose_mods(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self.window(),
            self.translator.translate("choose_mods"),
            "",
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
        )
        if folder_path:
            print(f"Выбрана папка с модами: {folder_path}")
            self.selected_mods_path = folder_path

    def select_version(self, version):
        """Обработчик выбора версии"""
        # Снимаем выделение со всех кнопок
        for button in self.version_buttons:
            if button.text() != version:
                button.setChecked(False)
        self.selected_version = version

    def get_selected_version(self):
        """Возвращает выбранную версию"""
        return self.selected_version
        
    def save_modpack(self):
        # Проверка названия
        name = self.name_input.text().strip()
        if not name:
            QtWidgets.QMessageBox.critical(
                self,
                self.translator.translate("error"),
                self.translator.translate("error_messages.name_empty")
            )
            self.name_input.setFocus()
            return
            
        # Проверка выбора модов
        if not hasattr(self, 'selected_mods_path'):
            QtWidgets.QMessageBox.critical(
                self,
                self.translator.translate("error"),
                self.translator.translate("error_messages.mods_not_selected")
            )
            return
            
        # Проверка существования папки с модами
        if not os.path.exists(self.selected_mods_path):
            QtWidgets.QMessageBox.critical(
                self,
                self.translator.translate("error"),
                self.translator.translate("error_messages.mods_folder_not_exists")
            )
            return
            
        # Проверка наличия файлов в папке с модами
        if not os.listdir(self.selected_mods_path):
            QtWidgets.QMessageBox.critical(
                self,
                self.translator.translate("error"),
                self.translator.translate("error_messages.mods_folder_empty")
            )
            return

        # Получаем версию и создаем путь к папке версии
        version = self.get_selected_version()
        version_path = os.path.join("modpack", version)
        
        # Создаем папку версии, если её нет
        os.makedirs(version_path, exist_ok=True)
        
        # Создаем папку для модпака
        modpack_name = self.name_input.text().strip()
        modpack_path = os.path.join(version_path, modpack_name)
        
        if os.path.exists(modpack_path):
            QtWidgets.QMessageBox.warning(
                self,
                self.translator.translate("error"),
                self.translator.translate("error_messages.modpack_exists")
            )
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
            QtWidgets.QMessageBox.critical(
                self,
                self.translator.translate("error"),
                self.translator.translate("error_messages.copy_failed").format(str(e))
            )
            return
        
        # Создаем и сохраняем метаданные
        metadata = {
            'name': modpack_name,
            'version': version,
            'genre': self.genre_combo.currentData(),  # Сохраняем ключ жанра
            'genre_text': self.genre_combo.currentText(),  # Сохраняем текущий перевод для отображения
            'icon': icon_filename  # Будет None, если иконка не была выбрана
        }
        
        metadata_path = os.path.join(modpack_path, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        
        QtWidgets.QMessageBox.information(
            self,
            self.translator.translate("success"),
            self.translator.translate("modpack_saved")
        )
        
        # Обновляем список модпаков в главном окне
        main_window = self.parent().window()
        if main_window.__class__.__name__ == 'MainWindow':
            main_window.load_modpacks()
            
        self.accept() 