from PySide6.QtWidgets import *

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
            item = QListWidgetItem(f"{username} ({timestamp.strftime('%Y-%m-%d %H:%M:%S')}): {comment_text}")
            self.comments_list.addItem(item)

    def post_comment(self):
        comment_text = self.comment_edit.text().strip()
        if comment_text:
            self.cursor.execute("SELECT username FROM accounts WHERE email = %s", (self.logged_in_user,))
            user_result = self.cursor.fetchone()

            if user_result:
                username = user_result[0]
            else:
                QMessageBox.warning(self, "Error", "Username not found for the logged-in user.")
                return

            query = "INSERT INTO comments (listing_id, username, email, comment_text) VALUES (%s, %s, %s, %s)"
            values = (self.listing_id, username, self.logged_in_user, comment_text)
            self.cursor.execute(query, values)
            self.connection.commit()
            self.comment_edit.clear()
            self.populate_comments()
