import sys
from PySide6 import QtWidgets
from ui.main_window import MainWindow

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Устанавливаем стиль приложения
    app.setStyle("Fusion")
    
    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

