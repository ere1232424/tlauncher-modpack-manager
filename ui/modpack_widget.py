from PySide6 import QtWidgets, QtCore, QtGui
import os
import json
import shutil
import zipfile
from typing import TYPE_CHECKING
from utils.resource_utils import resource_path
from ui.notification_widget import NotificationWidget
from utils.translator import Translator

if TYPE_CHECKING:
    from ui.main_window import MainWindow

# Константы для жанров (те же, что и в dialog_window.py)
GENRE_HARDCORE = "hardcore"
GENRE_HORROR = "horror"
GENRE_RPG = "rpg"
GENRE_VIBE = "vibe"

class DeleteConfirmDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подтверждение")
        self.setFixedSize(300, 150)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        layout = QtWidgets.QVBoxLayout(self)
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
        
        message = QtWidgets.QLabel("Вы уверены, что хотите удалить этот модпак?")
        message.setStyleSheet("color: white;")
        message.setAlignment(QtCore.Qt.AlignCenter)
        message.setWordWrap(True)
        
        buttons_layout = QtWidgets.QHBoxLayout()
        
        cancel_button = QtWidgets.QPushButton("Отмена")
        cancel_button.setStyleSheet("""
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
        cancel_button.clicked.connect(self.reject)
        
        delete_button = QtWidgets.QPushButton("Удалить")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #AA3333;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #CC4444;
            }
        """)
        delete_button.clicked.connect(self.accept)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(delete_button)
        
        container_layout.addWidget(message)
        container_layout.addLayout(buttons_layout)
        
        layout.addWidget(container)

class ModpackWidget(QtWidgets.QWidget):
    _active_modpack = None  # Статическая переменная для отслеживания активного модпака
    
    @classmethod
    def get_active_modpack(cls):
        return cls._active_modpack
    
    @classmethod
    def set_active_modpack(cls, modpack):
        cls._active_modpack = modpack

    def __init__(self, name, genre, icon_path=None, parent=None, modpack_path=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.modpack_path = modpack_path
        self.is_enabled = False
        self.name = name
        self.translator = Translator()
        
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
            GENRE_HARDCORE: 'zhanar/hard.png',
            GENRE_HORROR: 'zhanar/horror.png',
            GENRE_RPG: 'zhanar/RPG.png',
            GENRE_VIBE: 'zhanar/vibe.png'
        }
        
        if genre in genre_icons and os.path.exists(genre_icons[genre]):
            pixmap = QtGui.QPixmap(genre_icons[genre])
            genre_icon.setPixmap(pixmap.scaled(12, 12, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        
        # Текст жанра
        genre_text = self.translator.translate(f"genres.{genre}")
        genre_label = QtWidgets.QLabel(genre_text)
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
        if main_window.__class__.__name__ == 'MainWindow':
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
                # Сначала пробуем отключить модпак, если он активен
                if self.is_enabled:
                    self.toggle_modpack()
                
                # Даем системе время на освобождение файлов
                QtCore.QThread.msleep(500)
                
                try:
                    # Сначала пробуем обычное удаление
                    shutil.rmtree(self.modpack_path)
                except Exception:
                    # Если не получилось, используем командную строку Windows
                    import subprocess
                    
                    # Преобразуем путь в правильный формат для cmd
                    path = self.modpack_path.replace('/', '\\')
                    
                    # Пробуем принудительное удаление через cmd
                    try:
                        subprocess.run(['cmd', '/c', f'rd /s /q "{path}"'], 
                                    check=True, 
                                    capture_output=True,
                                    text=True,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
                    except subprocess.CalledProcessError as e:
                        # Если и это не помогло, пробуем через PowerShell с повышенными правами
                        try:
                            ps_command = f'Remove-Item -Path "{path}" -Recurse -Force'
                            subprocess.run(['powershell', '-Command', ps_command],
                                        check=True,
                                        capture_output=True,
                                        text=True,
                                        creationflags=subprocess.CREATE_NO_WINDOW)
                        except subprocess.CalledProcessError as ps_error:
                            raise Exception(f"Не удалось удалить файлы даже с повышенными правами: {ps_error.stderr}")
                
                # Проверяем, действительно ли папка удалена
                if os.path.exists(self.modpack_path):
                    raise Exception("Не удалось удалить папку модпака")
                
                # Обновляем список модпаков в главном окне
                main_window = self.window()
                if main_window.__class__.__name__ == 'MainWindow':
                    main_window.load_modpacks()
                    
            except Exception as e:
                error_msg = str(e)
                if "WinError 5" in error_msg:
                    error_msg = "Отказано в доступе. Убедитесь, что файлы не используются другими программами и у вас есть права администратора."
                elif "WinError 32" in error_msg:
                    error_msg = "Файл используется другим процессом. Закройте Minecraft и другие программы, которые могут использовать файлы модпака."
                
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
                
                error_label = QtWidgets.QLabel(f"Не удалось удалить модпак:\n{error_msg}")
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
        print(f"Путь к .minecraft: {minecraft_path}")
        
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
        print(f"Путь к папке модов в модпаке: {modpack_mods_path}")
        
        # Проверяем содержимое папки mods
        has_jar_files = False
        has_folders = False
        inner_mods_path = None

        if os.path.exists(modpack_mods_path):
            print("Содержимое папки модов:")
            for item in os.listdir(modpack_mods_path):
                item_path = os.path.join(modpack_mods_path, item)
                print(f"- {item}")
                if os.path.isfile(item_path) and item.lower().endswith('.jar'):
                    has_jar_files = True
                elif os.path.isdir(item_path):
                    if item == 'mods':
                        inner_mods_path = item_path
                    elif item in folders:
                        has_folders = True

            # Если jar-файлы не найдены в основной папке, проверяем вложенную папку mods
            if not has_jar_files and inner_mods_path and os.path.exists(inner_mods_path):
                print("Проверяем вложенную папку mods:")
                for item in os.listdir(inner_mods_path):
                    print(f"- {item}")
                    if item.lower().endswith('.jar'):
                        has_jar_files = True
                        # Используем вложенную папку mods как основную
                        modpack_mods_path = inner_mods_path
                        print(f"Найдены моды во вложенной папке: {modpack_mods_path}")
                        break
        else:
            print("Папка модов не найдена в модпаке!")
            QtWidgets.QMessageBox.critical(
                self.window(),
                "Ошибка",
                "Папка mods не найдена в модпаке!"
            )
            return
            
        print(f"Найдены JAR файлы: {has_jar_files}")
        print(f"Найдены дополнительные папки: {has_folders}")
        
        if not has_jar_files:
            print("В модпаке не найдены .jar файлы!")
            QtWidgets.QMessageBox.critical(
                self.window(),
                "Ошибка",
                "В модпаке не найдены .jar файлы модов!"
            )
            return

        # Путь к папке для резервных копий в нашем модпаке
        backup_path = os.path.join(self.modpack_path, '_backup')
        
        if self.is_enabled:
            # Выключаем модпак
            try:
                # Обрабатываем папку mods
                mc_mods_path = os.path.join(minecraft_path, 'mods')
                print(f"Выключение модпака - очистка папки: {mc_mods_path}")
                
                if os.path.exists(mc_mods_path):
                    # Очищаем текущую папку mods
                    for item in os.listdir(mc_mods_path):
                        item_path = os.path.join(mc_mods_path, item)
                        try:
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                                print(f"Удален файл: {item}")
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                                print(f"Удалена папка: {item}")
                        except Exception as e:
                            print(f"Не удалось удалить {item_path}: {e}")
                    
                    # Восстанавливаем моды из бэкапа, если они есть
                    backup_mods = os.path.join(backup_path, 'mods')
                    if os.path.exists(backup_mods):
                        print("Восстановление модов из бэкапа")
                        for item in os.listdir(backup_mods):
                            src_path = os.path.join(backup_mods, item)
                            dst_path = os.path.join(mc_mods_path, item)
                            if os.path.isfile(src_path):
                                shutil.copy2(src_path, dst_path)
                                print(f"Восстановлен файл: {item}")
                
                # Обрабатываем остальные папки
                if has_folders:
                    print("Обработка дополнительных папок")
                    for folder in folders:
                        mc_folder = os.path.join(minecraft_path, folder)
                        backup_folder = os.path.join(backup_path, folder)
                        modpack_folder = os.path.join(modpack_mods_path, folder)
                        
                        # Если папка существует в модпаке
                        if os.path.exists(modpack_folder):
                            # Удаляем текущую папку из .minecraft
                            if os.path.exists(mc_folder):
                                shutil.rmtree(mc_folder)
                                print(f"Удалена папка: {folder}")
                            
                            # Восстанавливаем из бэкапа, если он есть
                            if os.path.exists(backup_folder):
                                shutil.copytree(backup_folder, mc_folder)
                                print(f"Восстановлена папка из бэкапа: {folder}")
                
                # Удаляем папку с резервными копиями
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
                    print("Удалена папка с резервными копиями")
                
                self.is_enabled = False
                ModpackWidget.set_active_modpack(None)
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
                if main_window.__class__.__name__ == 'MainWindow':
                    main_window.update_enable_buttons()
                
                print("Модпак успешно выключен")
                
            except Exception as e:
                print(f"Ошибка при выключении модпака: {str(e)}")
                QtWidgets.QMessageBox.critical(
                    self.window(),
                    "Ошибка",
                    f"Не удалось отключить модпак: {str(e)}"
                )
                return
                
        else:
            # Включаем модпак
            try:
                print("Начинаем включение модпака")
                # Создаем папку для резервных копий
                os.makedirs(backup_path, exist_ok=True)
                print(f"Создана папка для бэкапа: {backup_path}")
                
                # Обрабатываем папку mods
                if has_jar_files:
                    mc_mods_path = os.path.join(minecraft_path, 'mods')
                    backup_mods = os.path.join(backup_path, 'mods')
                    
                    # Создаем папку mods если её нет
                    os.makedirs(mc_mods_path, exist_ok=True)
                    print(f"Создана/проверена папка: {mc_mods_path}")
                    
                    # Делаем бэкап существующих модов
                    if os.path.exists(mc_mods_path) and os.listdir(mc_mods_path):
                        os.makedirs(backup_mods, exist_ok=True)
                        print("Создание бэкапа существующих модов")
                        for item in os.listdir(mc_mods_path):
                            src_path = os.path.join(mc_mods_path, item)
                            dst_path = os.path.join(backup_mods, item)
                            if os.path.isfile(src_path):
                                shutil.copy2(src_path, dst_path)
                                print(f"Сохранен в бэкап: {item}")
                    
                    # Очищаем папку mods
                    print("Очистка папки mods")
                    for item in os.listdir(mc_mods_path):
                        item_path = os.path.join(mc_mods_path, item)
                        try:
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                                print(f"Удален файл: {item}")
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                                print(f"Удалена папка: {item}")
                        except Exception as e:
                            print(f"Не удалось удалить {item_path}: {e}")
                    
                    # Копируем JAR файлы
                    print("Копирование модов из модпака")
                    for item in os.listdir(modpack_mods_path):
                        if item.lower().endswith('.jar'):
                            src_path = os.path.join(modpack_mods_path, item)
                            dst_path = os.path.join(mc_mods_path, item)
                            try:
                                shutil.copy2(src_path, dst_path)
                                print(f"Скопирован мод: {item}")
                            except Exception as e:
                                print(f"Ошибка при копировании {item}: {e}")
                
                # Обрабатываем остальные папки
                if has_folders:
                    print("Обработка дополнительных папок")
                    for folder in folders:
                        mc_folder = os.path.join(minecraft_path, folder)
                        backup_folder = os.path.join(backup_path, folder)
                        modpack_folder = os.path.join(modpack_mods_path, folder)
                        
                        # Если папка существует в модпаке
                        if os.path.exists(modpack_folder):
                            # Делаем бэкап если папка существует в .minecraft
                            if os.path.exists(mc_folder):
                                shutil.copytree(mc_folder, backup_folder)
                                print(f"Создан бэкап папки: {folder}")
                                shutil.rmtree(mc_folder)
                                print(f"Удалена существующая папка: {folder}")
                            
                            # Копируем папку из модпака
                            shutil.copytree(modpack_folder, mc_folder)
                            print(f"Скопирована папка из модпака: {folder}")
                
                self.is_enabled = True
                ModpackWidget.set_active_modpack(self)
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
                if main_window.__class__.__name__ == 'MainWindow':
                    main_window.update_enable_buttons()
                
                print("Модпак успешно включен")
                
            except Exception as e:
                print(f"Ошибка при включении модпака: {str(e)}")
                QtWidgets.QMessageBox.critical(
                    self.window(),
                    "Ошибка",
                    f"Не удалось включить модпак: {str(e)}"
                )
                return 