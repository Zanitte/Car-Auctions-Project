from PySide6.QtWidgets import *
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QTimer, Qt
from pictures import ImageTextDelegate
from datetime import datetime, timedelta
from report_generator import ReportGenerator
from functools import partial
from my_account import AccountMenu

class CommentsDialog(QDialog):
    def __init__(self, cursor, connection, listing_id, logged_in_user, parent=None):
        super().__init__(parent)
        self.cursor = cursor
        self.connection = connection
        self.listing_id = listing_id
        self.logged_in_user = logged_in_user

        self.setWindowTitle(f"Comments for Listing #{listing_id}")
        self.setModal(True)

        layout = QVBoxLayout(self)

        self.comments_list = QListWidget()
        layout.addWidget(self.comments_list)

        comment_layout = QHBoxLayout()
        self.comment_edit = QLineEdit()
        comment_layout.addWidget(self.comment_edit)

        post_button = QPushButton("Post Comment")
        post_button.clicked.connect(self.post_comment)
        comment_layout.addWidget(post_button)

        layout.addLayout(comment_layout)

        self.populate_comments()

    def populate_comments(self):
        self.comments_list.clear()
        query = "SELECT username, comment_text, timestamp FROM comments WHERE listing_id = %s ORDER BY timestamp"
        self.cursor.execute(query, (self.listing_id,))
        comments = self.cursor.fetchall()

        for comment in comments:
            username, comment_text, timestamp = comment
            self.cursor.execute("SELECT username FROM accounts WHERE email = %s", (username,))
            user_result = self.cursor.fetchone()
            user_name = user_result[0] if user_result else username
            item = QListWidgetItem(f"{user_name} ({timestamp.strftime('%Y-%m-%d %H:%M:%S')}): {comment_text}")
            self.comments_list.addItem(item)

    def post_comment(self):
        comment_text = self.comment_edit.text().strip()
        if comment_text:
            username = self.logged_in_user
            query = "INSERT INTO comments (listing_id, username, email, comment_text) VALUES (%s, %s, %s, %s)"
            values = (self.listing_id, username, username, comment_text)
            self.cursor.execute(query, values)
            self.connection.commit()
            self.comment_edit.clear()
            self.populate_comments()

class CarListingItem(QListWidgetItem):
    def __init__(self, make, model, year, price, description, image_paths, start_date, car_widget):
        super().__init__(f"{make} {model} ({year}) - ${price} - {description}")
        self.make = make
        self.model = model
        self.year = year
        self.price = price
        self.description = description
        self.image_path = image_paths
        if isinstance(start_date, str):
            try:
                self.start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                self.start_date = datetime.now()
        else:
            self.start_date = start_date or datetime.now()
        self.bids = {}
        self.listing_id = None
        self.car_widget = car_widget

        self.bid_button = QPushButton("Bid")
        self.bid_button.setStyleSheet("""
            QPushButton {
                background-color: teal; 
                color: white;
            }
            QPushButton:disabled {
                background-color: grey; 
                color: white;
            }

        """)
        self.bid_button.setFixedSize(100, 50)
        self.bid_button.clicked.connect(self.initiate_bid)

        self.image_paths = []
        for image_path in image_paths.split(','):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(190, pixmap.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_paths.append(pixmap)

    def __lt__(self, other):
        return self.remaining_time() < other.remaining_time()

    def remaining_time(self):
        now = datetime.now()
        if self.start_date is not None:
            remaining = self.start_date + timedelta(minutes=360) - now
            return remaining.total_seconds()
        else:
            return 0

    def initiate_bid(self):
        if not self.car_widget.logged_in_user:
            QMessageBox.warning(self.car_widget, "Not Logged In", "You need to log in to place a bid.")
            return

        if self.car_widget.logged_in_user == self.email:
            QMessageBox.warning(self.car_widget, "Invalid Bid", "You cannot bid on your own car.")
            return

        cursor = self.car_widget.cursor
        connection = self.car_widget.connection
        logged_in_user = self.car_widget.logged_in_user

        cursor.execute("SELECT id_user FROM accounts WHERE email = %s", (logged_in_user,))
        user_id = cursor.fetchone()

        if user_id:
            cursor.execute("SELECT * FROM user_address WHERE id_user = %s", (user_id[0],))
            address_exists = cursor.fetchone()

            cursor.execute("SELECT * FROM payment_method WHERE id_user = %s", (user_id[0],))
            payment_method_exists = cursor.fetchone()

            if not address_exists or not payment_method_exists:
                QMessageBox.warning(self.car_widget, "Incomplete Profile",
                                    "You need to enter your address and payment method before placing a bid.")
                return

        bid, ok = QInputDialog.getInt(self.car_widget, "Place Bid", "Enter your bid amount:")
        if ok:
            username = self.car_widget.logged_in_user
            if bid < self.price:
                QMessageBox.warning(self.car_widget, "Invalid Bid",
                                    f"Your bid must be higher than the current price of ${self.price}.")
                return

            if username in self.bids:
                current_bid = self.bids[username][0]
                if bid <= current_bid:
                    QMessageBox.warning(self.car_widget, "Invalid Bid",
                                        f"Your bid must be higher than your current bid of ${current_bid}.")
                    return

            self.bids[username] = (bid, datetime.now())
            self.price = max(self.price, bid)
            self.update_remaining_time()

            self.car_widget.process_bid(self, bid)

            QMessageBox.information(self.car_widget, "Bid Placed", f"Your bid of ${bid} has been placed.")

    def update_remaining_time(self):
        remaining_time = self.remaining_time()
        if remaining_time <= 0:
            self.timer.stop()
            self.bid_button.setDisabled(True)  # bid button disable
        highest_bid = max(self.bids.values(), key=lambda x: x[0], default=(self.price, None))[0]
        self.setText(
            f"{self.make} {self.model} ({self.year}) - [${highest_bid}] - {self.description} (Remaining time: {str(timedelta(seconds=remaining_time)) if remaining_time > 0 else 'Expired'})"
        )

    def get_remaining_time_secs(self):
        remaining_time = self.remaining_time()
        if remaining_time > 0:
            return int(remaining_time)
        else:
            return 0


class SecondInterface(QMainWindow):
    def __init__(self, cursor, connection, logged_in_user):
        super().__init__()
        self.cursor = cursor
        self.connection = connection
        self.logged_in_user = logged_in_user
        loader = QUiLoader()
        self.ui = loader.load("actualolx.ui")
        self.ui.setWindowTitle("ZNT Auctions")
        self.ui.show()
        self.ui.actionClose.triggered.connect(QApplication.instance().quit)
        self.ui.sellcar.clicked.connect(self.sell_car)

        self.image_paths = ""
        self.document_paths= ""

        self.car_widget = self.ui.findChild(QListWidget, "ListWidget")

        self.listing_items_map = {}
        self.populate_car_listings()

        delegate = ImageTextDelegate(self.car_widget)
        self.car_widget.setItemDelegate(delegate)

        self.ui.lineEdit.textChanged.connect(self.searchbox)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_listings)
        self.update_timer.start(1000)

        self.reports_button = self.ui.findChild(QPushButton, "Reports")
        self.reports_button.clicked.connect(self.show_reports)


        self.report_browser = QTextBrowser()



        self.account_menu = AccountMenu(self, cursor, connection, logged_in_user)
        my_account_button = self.ui.findChild(QPushButton, "My_Account")
        my_account_button.setMenu(self.account_menu.get_menu())

    def logout(self):
        self.logged_in_user = None

        from login import ointerfata
        self.ui.hide()
        self.ointerfata = ointerfata()

    def update_listings(self):
        for i in range(self.car_widget.count()):
            item = self.car_widget.item(i)
            if item is not None:
                listing_id = item.data(Qt.UserRole + 1)
                car_item = self.listing_items_map.get(listing_id)

                if car_item is not None:
                    self.update_listing_item(item, car_item)

        self.car_widget.sortItems()

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_listings)
        self.update_timer.start(1000)

    def update_listing_item(self, item, car_item):
        remaining_time = car_item.remaining_time()
        if remaining_time <= 0:
            highest_bid_tuple = max(car_item.bids.values(), key=lambda x: x[0], default=(0, None))
            highest_bid = highest_bid_tuple[0]
            highest_bidder = car_item.highest_bidder
            if highest_bidder:
                if highest_bid_tuple[1]:
                    bid_timestamp_str = highest_bid_tuple[1].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    bid_timestamp_str = "N/A"

                item_text = f"{car_item.make} {car_item.model} ({car_item.year}) - [${highest_bid}]\n{car_item.description}\n(Auction Ended. The highest bidder is {highest_bidder} with a bid of ${highest_bid} at {bid_timestamp_str})"
            else:
                item_text = f"{car_item.make} {car_item.model} ({car_item.year}) - [${highest_bid}]\n{car_item.description}\n(Auction Ended with no bids.)"
            item.setText(item_text)
            car_item.bid_button.setDisabled(True)  # bid button disable
        else:
            highest_bid = max(car_item.bids.values(), key=lambda x: x[0], default=(car_item.price, None))[0]
            remaining_time_str = str(timedelta(seconds=remaining_time))
            item_text = f"{car_item.make} {car_item.model} ({car_item.year}) - [${highest_bid}]\n{car_item.description} (Remaining Time: {remaining_time_str})"
            item.setText(item_text)
            car_item.bid_button.setEnabled(True)

    def searchbox(self, text):
        text = text.lower()

        if text:
            query = "SELECT * FROM car_listings WHERE LOWER(CONCAT(make, ' ', model, ' (', year, ') - $', price, ' - ', description)) LIKE %s"
            search_pattern = f"%{text}%"
            self.cursor.execute(query, (search_pattern,))
            car_listings = self.cursor.fetchall()
        else:
            self.cursor.execute("SELECT * FROM car_listings")
            car_listings = self.cursor.fetchall()

        self.car_widget.clear()

        self.populate_car_listings(car_listings)

    def upload_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        file_paths, _ = file_dialog.getOpenFileNames(self, "Upload Image", "", "Images (*.png *.jpg *.jpeg)",
                                                     options=options)
        if file_paths:
            self.image_paths = ','.join(file_paths)

    def add_car_to_database(self, dialog):
        make = self.make_lineedit.text().strip()
        model = self.model_lineedit.text().strip()
        year = self.year_lineedit.text().strip()
        price = self.price_lineedit.text().strip()
        description = self.description_textedit.toPlainText().strip()
        image_paths = self.image_paths if self.image_paths else None
        document_paths = self.document_paths if self.document_paths else None

        if not all([make, model, year, price, description, image_paths, document_paths]):
            QMessageBox.warning(self, "Missing Information", "All fields must be filled in.")
            return

        try:
            year = int(year)
            price = float(price)
            if price > 2147483647:
                QMessageBox.warning(self, "Invalid Input", "Your price must be lower.")
                return
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Year and price must be numbers.")
            return

        start_date = datetime.now().isoformat()

        self.cursor.execute("SELECT id_user, email FROM accounts WHERE email = %s", (self.logged_in_user,))
        user_id, email = self.cursor.fetchone()

        query = "INSERT INTO car_listings (make, model, year, price, description, image_path, start_date, id_user, email, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (make, model, year, price, description, image_paths, start_date, user_id, email, user_id)
        self.cursor.execute(query, values)
        self.connection.commit()
        listing_id = self.cursor.lastrowid

        if self.document_paths:
            query = "INSERT INTO documents (images, listing_id) VALUES (%s, %s)"
            values = (self.document_paths, listing_id)
            self.cursor.execute(query, values)
            self.connection.commit()

        QMessageBox.information(self, "Listing ID", f"Your listing ID is {listing_id}.")

        dialog.close()

        car_item = CarListingItem(make, model, year, price, description, image_paths, start_date, self)
        car_item.listing_id = listing_id
        self.listing_items_map[listing_id] = car_item

        self.populate_car_listings()

    def populate_car_listings(self, car_listings=None):
        if car_listings is None:

            self.cursor.execute(
                "SELECT make, model, year, price, description, image_path, start_date, listing_id, highest_bidder, email, id_user, user_id FROM car_listings")
            car_listings = self.cursor.fetchall()

        self.car_widget.clear()

        for listing in car_listings:
            make, model, year, price, description, image_path, start_date, listing_id, highest_bidder, email, id_user, user_id = listing

            car_item = CarListingItem(make, model, year, price, description, image_path, start_date, self)
            car_item.listing_id = listing_id
            car_item.highest_bidder = highest_bidder
            car_item.email = email
            car_item.id_user = id_user
            car_item.user_id = user_id

            self.cursor.execute(
                "SELECT bidder_email, bid_amount, bid_timestamp FROM bids WHERE listing_id = %s", (listing_id,))
            bids = self.cursor.fetchall()

            for bid in bids:
                bidder_email, bid_amount, bid_timestamp = bid
                if isinstance(bid_timestamp, str):
                    bid_timestamp = datetime.fromisoformat(bid_timestamp)
                car_item.bids[bidder_email] = (bid_amount, bid_timestamp)

            self.listing_items_map[listing_id] = car_item

            self.car_widget.sortItems()

            remaining_time_str = str(
                timedelta(seconds=car_item.remaining_time())) if car_item.remaining_time() > 0 else "Expired"
            list_item = QListWidgetItem(
                f"{make} {model} ({year}) - [${price}]\n{description} (Remaining Time: {remaining_time_str})")
            list_item.setData(Qt.UserRole, car_item.get_remaining_time_secs())
            list_item.setData(Qt.UserRole + 1, listing_id)
            list_item.setData(Qt.DecorationRole, car_item.image_paths)

            self.car_widget.addItem(list_item)

            item_widget = QWidget()
            item_widget_layout = QHBoxLayout(item_widget)
            item_widget_layout.setContentsMargins(0, 0, 0, 0)

            button_layout = QHBoxLayout()
            button_layout.addStretch()

            comments_button = QPushButton("Comments")
            show_comments_dialog = partial(self.show_comments_dialog, car_item)
            comments_button.clicked.connect(show_comments_dialog)
            button_layout.addWidget(comments_button)

            button_layout.addWidget(car_item.bid_button)

            item_widget_layout.addLayout(button_layout, Qt.AlignTop)

            self.car_widget.setItemWidget(list_item, item_widget)

        self.car_widget.sortItems()

    def show_comments_dialog(self, car_item):
        comments_dialog = CommentsDialog(self.cursor, self.connection, car_item.listing_id, self.logged_in_user, self)
        comments_dialog.exec_()

    def process_bid(self, car_item, bid):
        email = self.logged_in_user

        self.cursor.execute("SELECT username FROM accounts WHERE email = %s", (email,))
        username_result = self.cursor.fetchone()
        username = username_result[0] if username_result else "Unknown User"

        bid_timestamp = datetime.now().isoformat()

        query = "INSERT INTO bids (make, model, year, bidder_email, bid_amount, bid_timestamp, listing_id, bidder_username) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
        car_item.make, car_item.model, car_item.year, email, bid, bid_timestamp, car_item.listing_id, username)
        self.cursor.execute(query, values)
        self.connection.commit()

        query = "SELECT MAX(bid_amount) AS highest_bid FROM bids WHERE listing_id = %s"
        self.cursor.execute(query, (car_item.listing_id,))
        highest_bid = self.cursor.fetchone()[0]

        query = "UPDATE car_listings SET price = %s, highest_bidder = %s WHERE listing_id = %s"
        values = (highest_bid, username, car_item.listing_id)
        self.cursor.execute(query, values)
        self.connection.commit()

        car_item.price = highest_bid
        car_item.highest_bidder = username
        car_item.update_remaining_time()

    def sell_car(self):
        self.cursor.execute("SELECT id_user FROM accounts WHERE email = %s", (self.logged_in_user,))
        user_id = self.cursor.fetchone()
        if user_id:
            self.cursor.execute("SELECT * FROM user_address WHERE id_user = %s", (user_id[0],))
            address_exists = self.cursor.fetchone()

            self.cursor.execute("SELECT * FROM payment_method WHERE id_user = %s", (user_id[0],))
            payment_method_exists = self.cursor.fetchone()

            if not address_exists or not payment_method_exists:
                QMessageBox.warning(self, "Error",
                                    "You need to enter your address and payment method before selling a car.")
                return
        dialog = QDialog(self)
        dialog.setWindowTitle("Sell a car")


        layout = QVBoxLayout(dialog)

        make_label = QLabel("Make:")
        self.make_lineedit = QLineEdit()
        make_layout = QHBoxLayout()
        make_layout.addWidget(make_label)
        make_layout.addWidget(self.make_lineedit)
        layout.addLayout(make_layout)

        model_label = QLabel("Model:")
        self.model_lineedit = QLineEdit()
        model_layout = QHBoxLayout()
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_lineedit)
        layout.addLayout(model_layout)

        year_label = QLabel("Year:")
        self.year_lineedit = QLineEdit()
        year_layout = QHBoxLayout()
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_lineedit)
        layout.addLayout(year_layout)

        price_label = QLabel("Starting price:")
        self.price_lineedit = QLineEdit()
        price_layout = QHBoxLayout()
        price_layout.addWidget(price_label)
        price_layout.addWidget(self.price_lineedit)
        layout.addLayout(price_layout)

        description_label = QLabel("Description:")
        self.description_textedit = QTextEdit()
        layout.addWidget(description_label)
        layout.addWidget(self.description_textedit)

        self.upload_image_button = QPushButton("Upload Images")
        self.upload_image_button.clicked.connect(self.upload_image)
        layout.addWidget(self.upload_image_button)

        self.upload_document_button = QPushButton("Upload Documents")
        self.upload_document_button.clicked.connect(self.upload_documents)
        layout.addWidget(self.upload_document_button)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_car_to_database(dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.exec_()

    def upload_documents(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        file_paths, _ = file_dialog.getOpenFileNames(self, "Upload Document Images", "", "Images (*.png *.jpg *.jpeg)",
                                                     options=options)
        if file_paths:
            self.document_paths = ','.join(file_paths)

    def show_reports(self):
        report_dialog = QDialog(self)
        report_dialog.setWindowTitle("ZNT Auctions - Reports")
        report_dialog.setModal(False)

        layout = QVBoxLayout(report_dialog)
        self.report_browser = QTextBrowser()
        layout.addWidget(self.report_browser)

        report_dialog.resize(800, 600)

        report_generator = ReportGenerator(self.cursor, self.connection, self.listing_items_map, self.report_browser)
        report_generator.generate_reports()

        report_dialog.show()




