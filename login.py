import mysql.connector
from PySide6.QtWidgets import *
from PySide6.QtUiTools import QUiLoader
from auctions import SecondInterface

class ointerfata(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        self.ui = loader.load("interface.ui")
        self.ui.setWindowTitle("ZNT Auctions")
        self.ui.show()
        self.ui.email.setStyleSheet("""
                QLineEdit {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 14px;
                }
            """)

        self.ui.password.setStyleSheet("""
                QLineEdit {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 14px;
                }
            """)

        self.ui.pushButton.setStyleSheet("""
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
            """)

        self.ui.pushButton.clicked.connect(self.login)
        self.ui.actionClose.triggered.connect(QApplication.instance().quit)

        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            port="3306",
            database="database",
        )
        self.cursor = self.connection.cursor()

        self.ui.register_button.clicked.connect(self.open_registration_dialog)
        self.ui.forgot_password.clicked.connect(self.forgot_password_dialog)

    def open_registration_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Create New Account")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
            }
            QLabel {
                font-weight: bold;
            }
            QPushButton {
                background-color: teal;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }
        """)

        layout = QVBoxLayout(dialog)

        username_label = QLabel("Username:")
        self.username_lineedit = QLineEdit()
        username_layout = QHBoxLayout()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_lineedit)
        layout.addLayout(username_layout)

        email_label = QLabel("Email:")
        self.email_lineedit = QLineEdit()
        email_layout = QHBoxLayout()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_lineedit)
        layout.addLayout(email_layout)

        password_label = QLabel("Password:")
        self.password_lineedit = QLineEdit()
        self.password_lineedit.setEchoMode(QLineEdit.Password)
        password_layout = QHBoxLayout()
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_lineedit)
        layout.addLayout(password_layout)

        question_label = QLabel("Security Question: What's your neighbor's name?")
        self.question_lineedit = QLineEdit()
        question_layout = QHBoxLayout()
        question_layout.addWidget(question_label)
        question_layout.addWidget(self.question_lineedit)
        layout.addLayout(question_layout)

        create_button = QPushButton("Create Account")
        create_button.clicked.connect(lambda: self.register(dialog))
        layout.addWidget(create_button)

        dialog.exec_()

    def register(self, dialog):
        username = self.username_lineedit.text().strip()
        email = self.email_lineedit.text().strip()
        password = self.password_lineedit.text().strip()
        question = self.question_lineedit.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Email and password cannot be blank")
            return

        query = "SELECT * FROM accounts WHERE email = %s"
        self.cursor.execute(query, (email,))
        account = self.cursor.fetchone()

        if account:
            QMessageBox.warning(self, "Error", "The account already exists")
            return
        else:
            query = "INSERT INTO accounts (email, password, username, question) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (email, password, username, question))
            self.connection.commit()

            QMessageBox.information(self, "Success", "Account created successfully")
            dialog.accept()

    def forgot_password_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Forgot Password")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
            }
            QLabel {
                font-weight: bold;
            }
            QPushButton {
                background-color: teal;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }
        """)

        layout = QVBoxLayout(dialog)

        email_label = QLabel("Email:")
        self.forgot_password_email_lineedit = QLineEdit()
        email_layout = QHBoxLayout()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.forgot_password_email_lineedit)
        layout.addLayout(email_layout)

        question_label = QLabel("Security Question: What's your neighbor's name?")
        self.forgot_password_question_lineedit = QLineEdit()
        question_layout = QHBoxLayout()
        question_layout.addWidget(question_label)
        question_layout.addWidget(self.forgot_password_question_lineedit)
        layout.addLayout(question_layout)

        reset_button = QPushButton("Reset Password")
        reset_button.clicked.connect(lambda: self.reset_password(dialog))
        layout.addWidget(reset_button)

        dialog.exec_()

    def reset_password(self, dialog):
        email = self.forgot_password_email_lineedit.text().strip()
        answer = self.forgot_password_question_lineedit.text().strip()

        if not email or not answer:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        query = "SELECT * FROM accounts WHERE email = %s AND question = %s"
        self.cursor.execute(query, (email, answer))
        account = self.cursor.fetchone()

        if account:
            new_password, ok = QInputDialog.getText(self, "Reset Password", "Enter new password:", QLineEdit.Password)
            if ok and new_password:
                update_query = "UPDATE accounts SET password = %s WHERE email = %s"
                self.cursor.execute(update_query, (new_password, email))
                self.connection.commit()
                QMessageBox.information(self, "Success", "Your password has been reset successfully.")
                dialog.accept()
            else:
                QMessageBox.warning(self, "Error", "Password reset canceled.")
        else:
            QMessageBox.warning(self, "Error", "Wrong information provided.")

    def login(self):
        email = self.ui.email.text()
        password = self.ui.password.text()

        query = "SELECT * FROM accounts WHERE email = %s AND password = %s"
        self.cursor.execute(query, (email, password))
        account = self.cursor.fetchone()

        if account:
            self.ui.hide()
            self.second_interface = SecondInterface(self.cursor, self.connection, email)
        else:
            QMessageBox.warning(self, "Login Failed", "The account doesn't exist")




            