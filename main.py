import sys
import mysql.connector
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from login import ointerfata


def main():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        port="3306",
        database="database"
    )
    cursor = connection.cursor()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('zanittes-software-high-resolution-logo.png'))


    app_style = """
    QMainWindow, QDialog {
        background-color: #f0f0f0;
    }
    QPushButton {
        background-color: teal;
        color: white;
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #006060;
    }
    QPushButton:pressed {
        background-color: #004040;
    }
    QPushButton:disabled {
        background-color: grey;
        color: white;
    }
    QLineEdit, QTextEdit {
        background-color: white;
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 8px;
        font-size: 14px;
    }
    QLabel {
        font-weight: bold;
    }
    QListWidget {
        background-color: white;
        border: 1px solid #ccc;
        border-radius: 4px;
        outline: none;
    }
    QMenu {
        background-color: white;
        border: 1px solid #ccc;
        padding: 6px;
    }
    QMenu::item {
        padding: 8px 32px;
    }
    QMenu::item:selected {
        background-color: teal;
        color: white;
    }
    QCommandLinkButton, QPushButton#special_button {
        color: teal;
        background-color: transparent;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 12px;
        text-align: left;
    }
    QCommandLinkButton:hover, QPushButton#special_button:hover {
        border: 1px solid teal;
        background-color: #f0f8f8;
        box-shadow: 2px 2px 3px rgba(0, 128, 128, 0.2);
    }
    QCommandLinkButton:pressed, QPushButton#special_button:pressed {
        background-color: #e0f0f0;
        box-shadow: 1px 1px 2px rgba(0, 128, 128, 0.3) inset;
    }
    """

    app.setStyleSheet(app_style)

    window = ointerfata()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()