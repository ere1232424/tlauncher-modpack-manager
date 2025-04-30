from PySide6 import QtWidgets, QtCore

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