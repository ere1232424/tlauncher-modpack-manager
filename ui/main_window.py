from PySide6 import QtWidgets, QtCore, QtGui
import os
import json
from PySide6.QtWidgets import QScroller, QScrollerProperties
from utils.resource_utils import resource_path
from utils.translator import Translator
from ui.dialog_window import DialogWindow
from ui.modpack_widget import ModpackWidget

# Константы для жанров (те же, что и в dialog_window.py)
GENRE_HARDCORE = "hardcore"
GENRE_HORROR = "horror"
GENRE_RPG = "rpg"
GENRE_VIBE = "vibe"

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Инициализируем переводчик
        self.translator = Translator()
        
        self.setWindowTitle(self.translator.translate("window_title"))
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
        
        # Сначала настраиваем UI
        self.setup_ui()
        
        # После настройки UI устанавливаем сохраненный язык
        saved_language = self.translator.current_language
        index = self.language_combo.findData(saved_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
    def setup_ui(self):
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
        title_label = QtWidgets.QLabel(self.translator.translate("my_modpacks"))
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        top_panel.addWidget(title_label)
        
        # Добавляем выпадающий список для выбора языка
        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItem("🇷🇺 Русский", "ru")
        self.language_combo.addItem("🇬🇧 English", "en")
        self.language_combo.setFixedWidth(120)
        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: #2B2B2B;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox:hover {
                background-color: #3B3B3B;
            }
            QComboBox::drop-down {
                border: none;
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
                selection-background-color: #3B3B3B;
            }
        """)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        
        top_panel.addWidget(self.language_combo)
        top_panel.addStretch()
        
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
        
        print("Начинаю загрузку модпаков...")
        
        # Проходим по всем версиям
        if not os.path.exists("modpack"):
            print("Директория modpack не существует")
            os.makedirs("modpack", exist_ok=True)
            return
            
        for version in os.listdir("modpack"):
            version_path = os.path.join("modpack", version)
            print(f"Обрабатываю версию: {version}")
            if os.path.isdir(version_path):
                # Проходим по всем модпакам версии
                for modpack in os.listdir(version_path):
                    modpack_path = os.path.join(version_path, modpack)
                    print(f"Найден модпак: {modpack} в {modpack_path}")
                    if os.path.isdir(modpack_path):
                        # Загружаем метаданные
                        metadata_path = os.path.join(modpack_path, "metadata.json")
                        try:
                            if not os.path.exists(metadata_path):
                                print(f"Создаю метаданные по умолчанию для: {modpack}")
                                # Создаем метаданные по умолчанию
                                default_metadata = {
                                    'name': modpack,
                                    'version': version,
                                    'genre': GENRE_HARDCORE,  # По умолчанию используем ключ жанра
                                    'icon': None,
                                    'favorite': False
                                }
                                # Сохраняем метаданные
                                with open(metadata_path, 'w', encoding='utf-8') as f:
                                    json.dump(default_metadata, f, ensure_ascii=False, indent=4)
                                metadata = default_metadata
                            else:
                                with open(metadata_path, 'r', encoding='utf-8') as f:
                                    metadata = json.load(f)
                                    print(f"Загружены метаданные: {metadata}")
                                
                            # Получаем путь к иконке
                            icon_path = None
                            if metadata.get('icon'):
                                icon_path = os.path.join(modpack_path, metadata['icon'])
                                print(f"Путь к иконке: {icon_path}")
                                
                            # Добавляем модпак в список
                            modpacks.append({
                                'name': metadata['name'],
                                'genre': metadata['genre'],
                                'icon_path': icon_path,
                                'path': modpack_path,
                                'favorite': metadata.get('favorite', False)
                            })
                            print(f"Модпак добавлен в список: {metadata['name']}")
                        except Exception as e:
                            print(f"Ошибка при работе с метаданными {metadata_path}: {str(e)}")
        
        print(f"Всего найдено модпаков: {len(modpacks)}")
        
        # Сортируем модпаки: сначала избранные, потом остальные
        modpacks.sort(key=lambda x: (not x['favorite'], x['name']))
        
        # Создаем виджеты для каждого модпака
        for modpack in modpacks:
            print(f"Создаю виджет для модпака: {modpack['name']}")
            modpack_widget = ModpackWidget(
                name=modpack['name'],
                genre=modpack['genre'],
                icon_path=modpack['icon_path'],
                parent=self,
                modpack_path=modpack['path']
            )
            self.modpacks_layout.addWidget(modpack_widget)
        
        print("Загрузка модпаков завершена")
        
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
                active_modpack = ModpackWidget.get_active_modpack()
                if active_modpack is None:
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
                    if widget != active_modpack:
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

    def change_language(self, index):
        language = self.language_combo.currentData()
        self.translator.set_language(language)
        self.update_translations()
        
    def update_translations(self):
        # Обновляем все тексты в интерфейсе
        self.setWindowTitle(self.translator.translate("window_title"))
        
        # Обновляем заголовок
        title_label = self.findChild(QtWidgets.QLabel)
        if title_label:
            title_label.setText(self.translator.translate("my_modpacks"))
            
        # Перезагружаем список модпаков для обновления их текстов
        self.load_modpacks() 