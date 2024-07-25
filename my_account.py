from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import *
from datetime import datetime, timedelta


class PaymentMethodDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Payment Method")

        layout = QFormLayout(self)

        self.bank_line_edit = QLineEdit(self)
        layout.addRow("Bank:", self.bank_line_edit)

        self.credit_card_number_line_edit = QLineEdit(self)
        layout.addRow("Credit Card Number:", self.credit_card_number_line_edit)

        self.date_line_edit = QLineEdit(self)
        layout.addRow("Expiry Date (MM/YY):", self.date_line_edit)

        self.cvv_line_edit = QLineEdit(self)
        self.cvv_line_edit.setValidator(QIntValidator(0, 999))
        layout.addRow("CVV:", self.cvv_line_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
class AccountMenu:
    def __init__(self, parent, cursor, connection, logged_in_user):
        self.parent = parent
        self.cursor = cursor
        self.connection = connection
        self.logged_in_user = logged_in_user

        self.account_menu = QMenu()

        settings_action = self.account_menu.addAction("Settings")
        settings_action.triggered.connect(self.show_settings_dialog)

        logout_action = self.account_menu.addAction("Logout")
        logout_action.triggered.connect(self.parent.logout)

    def show_settings_dialog(self):
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Settings")
        layout = QVBoxLayout(dialog)

        enter_address_button = QPushButton("Enter your address")
        enter_address_button.clicked.connect(self.enter_address)
        layout.addWidget(enter_address_button)

        enter_payment_method_button = QPushButton("Enter your payment method")
        enter_payment_method_button.clicked.connect(self.enter_payment_method)
        layout.addWidget(enter_payment_method_button)

        # Add a QPushButton for the "Change your username" option
        change_username_button = QPushButton("Change your username")
        change_username_button.clicked.connect(self.change_username)
        layout.addWidget(change_username_button)

        change_password_button = QPushButton("Change your password")
        change_password_button.clicked.connect(self.change_password)
        layout.addWidget(change_password_button)

        show_won_auctions_button = QPushButton("Show Won Auctions")
        show_won_auctions_button.clicked.connect(self.show_won_auctions)
        layout.addWidget(show_won_auctions_button)

        modify_car_listing_button = QPushButton("Modify Car Listing")
        modify_car_listing_button.clicked.connect(self.modify_car_listing)
        layout.addWidget(modify_car_listing_button)

        dialog.setLayout(layout)
        dialog.resize(460, 350)
        dialog.exec_()

    def enter_address(self):
        self.cursor.execute("SELECT id_user FROM accounts WHERE email = %s", (self.logged_in_user,))
        user_id = self.cursor.fetchone()
        if user_id:
            self.cursor.execute("SELECT * FROM user_address WHERE id_user = %s", (user_id[0],))
            address_exists = self.cursor.fetchone()

            if address_exists:
                QMessageBox.information(self.parent, "Information", "You have already entered your address.")
                return

            dialog = QDialog(self.parent)
            dialog.setWindowTitle("Enter Address")

            layout = QFormLayout(dialog)

            self.city_line_edit = QLineEdit(dialog)
            layout.addRow("City:", self.city_line_edit)

            self.street_line_edit = QLineEdit(dialog)
            layout.addRow("Street:", self.street_line_edit)

            self.number_h_line_edit = QLineEdit(dialog)
            self.number_h_line_edit.setValidator(QIntValidator(0, 9999))
            layout.addRow("House number:", self.number_h_line_edit)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)

            if dialog.exec() == QDialog.Accepted:
                city = self.city_line_edit.text()
                street = self.street_line_edit.text()
                number_h = self.number_h_line_edit.text()

                if city and street and number_h:
                    query = "INSERT INTO user_address (id_user, city, street, number_h) VALUES (%s, %s, %s, %s)"
                    self.cursor.execute(query, (user_id[0], city, street, number_h))
                    self.connection.commit()

                    QMessageBox.information(self.parent, "Success", "Address entered successfully.")
        else:
            QMessageBox.warning(self.parent, "Error", "User does not exist.")

    def enter_payment_method(self):
        self.cursor.execute("SELECT id_user FROM accounts WHERE email = %s", (self.logged_in_user,))
        user_id = self.cursor.fetchone()
        if user_id:
            self.cursor.execute("SELECT id_user FROM user_address WHERE id_user = %s", (user_id[0],))
            address_exists = self.cursor.fetchone()
            if not address_exists:
                QMessageBox.warning(self.parent, "Error", "Please enter your address first.")
                return

            dialog = PaymentMethodDialog(self.parent)
            if dialog.exec() == QDialog.Accepted:
                bank = dialog.bank_line_edit.text()
                credit_card_number = dialog.credit_card_number_line_edit.text()
                date = dialog.date_line_edit.text()
                try:
                    date = datetime.strptime(date, "%m/%y").strftime("%Y-%m-01")
                except ValueError:
                    QMessageBox.warning(self.parent, "Error",
                                        "Invalid date format. Please enter a valid date in the format MM/YY.")
                    return
                cvv = dialog.cvv_line_edit.text()

                if bank and credit_card_number and date and cvv:
                    query = "INSERT INTO payment_method (id_user, bank, credit_card_number, date, cvv) VALUES (%s, %s, %s, %s, %s)"
                    self.cursor.execute(query, (user_id[0], bank, credit_card_number, date, cvv))
                    self.connection.commit()

                    QMessageBox.information(self.parent, "Success", "Payment method entered successfully.")
        else:
            QMessageBox.warning(self.parent, "Error", "User does not exist.")

    def show_won_auctions(self):
        self.cursor.execute("SELECT * FROM bids WHERE bidder_email = %s", (self.logged_in_user,))
        won_auctions = self.cursor.fetchall()

        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Won Auctions")
        layout = QVBoxLayout(dialog)

        auctions_widget = QListWidget()

        for auction in won_auctions:
            id, make, model, year, bidder_email, bid_amount, bid_timestamp, listing_id, bidder_username = auction

            self.cursor.execute("SELECT start_date FROM car_listings WHERE listing_id = %s", (listing_id,))
            start_date = self.cursor.fetchone()[0]
            if isinstance(start_date, datetime):
                end_date = start_date + timedelta(minutes=360)
            else:
                end_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=360)

            if datetime.now() > end_date:
                item = QListWidgetItem(f"{make} {model} ({year}) - [${bid_amount}]\nBidder: {bidder_username}")
                auctions_widget.addItem(item)

        layout.addWidget(auctions_widget)
        dialog.setLayout(layout)
        dialog.exec_()

    def change_password(self):
        current_password, ok = QInputDialog.getText(self.parent, "Change Password", "Enter current password:", QLineEdit.Password)
        if ok and current_password:
            new_password, ok = QInputDialog.getText(self.parent, "Change Password", "Enter new password:", QLineEdit.Password)
            if ok and new_password:
                self.cursor.execute("SELECT password FROM accounts WHERE email = %s", (self.logged_in_user,))
                db_password = self.cursor.fetchone()[0]
                if db_password == current_password:
                    query = "UPDATE accounts SET password = %s WHERE email = %s"
                    self.cursor.execute(query, (new_password, self.logged_in_user))
                    self.connection.commit()

                    QMessageBox.information(self.parent, "Success", "Password updated successfully.")
                else:
                    QMessageBox.warning(self.parent, "Error", "Current password is incorrect.")

    def change_username(self):
        new_username, ok = QInputDialog.getText(self.parent, "Change Username", "Enter new username:")
        if ok and new_username:
            query = "UPDATE accounts SET username = %s WHERE email = %s"
            self.cursor.execute(query, (new_username, self.logged_in_user))
            self.connection.commit()

            QMessageBox.information(self.parent, "Success", "Username updated successfully.")

    def modify_car_listing(self):
        listing_id, ok = QInputDialog.getInt(self.parent, "Modify Car Listing", "Enter the listing ID of the car you want to modify:")
        if ok and listing_id:
            self.cursor.execute("SELECT make, model, year, price, description, image_path FROM car_listings WHERE listing_id = %s", (listing_id,))
            car_listing = self.cursor.fetchone()

            if car_listing:
                make, model, year, price, description, image_path = car_listing

                dialog = QDialog(self.parent)
                dialog.setWindowTitle("Modify Car Listing")
                layout = QVBoxLayout(dialog)

                self.make_lineedit = QLineEdit(make)
                layout.addWidget(QLabel("Make:"))
                layout.addWidget(self.make_lineedit)

                self.model_lineedit = QLineEdit(model)
                layout.addWidget(QLabel("Model:"))
                layout.addWidget(self.model_lineedit)

                self.year_lineedit = QLineEdit(str(year))
                layout.addWidget(QLabel("Year:"))
                layout.addWidget(self.year_lineedit)

                self.price_lineedit = QLineEdit(str(price))
                layout.addWidget(QLabel("Starting price:"))
                layout.addWidget(self.price_lineedit)

                self.description_textedit = QTextEdit(description)
                layout.addWidget(QLabel("Description:"))
                layout.addWidget(self.description_textedit)

                save_button = QPushButton("Save Changes")
                save_button.clicked.connect(lambda: self.save_car_listing_changes(listing_id))
                layout.addWidget(save_button)

                dialog.setLayout(layout)
                dialog.exec_()
            else:
                QMessageBox.warning(self.parent, "Error", "Car listing not found.")

    def save_car_listing_changes(self, listing_id):
        make = self.make_lineedit.text().strip()
        model = self.model_lineedit.text().strip()
        year = self.year_lineedit.text().strip()
        price = self.price_lineedit.text().strip()
        description = self.description_textedit.toPlainText().strip()

        query = "UPDATE car_listings SET make = %s, model = %s, year = %s, price = %s, description = %s WHERE listing_id = %s"
        self.cursor.execute(query, (make, model, year, price, description, listing_id))
        self.connection.commit()

        QMessageBox.information(self.parent, "Success", "Car listing modified successfully.")

    def logout(self):
        self.logged_in_user = None

        self.parent.close()

        from login import ointerfata
        ointerfata()

    def get_menu(self):
        return self.account_menu

