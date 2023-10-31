import sys
import mysql.connector
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

class DatabaseApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Database Application")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()
        self.connection = None

    def init_ui(self):
        self.login_widget = QWidget()
        self.setCentralWidget(self.login_widget)

        self.layout = QVBoxLayout()
        self.login_widget.setLayout(self.layout)

        self.lbl_username = QLabel("Username:")
        self.username_input = QLineEdit()

        self.lbl_password = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)

        self.query_text = QTextEdit()
        self.query_text.setPlaceholderText("Enter your SQL query here")

        self.execute_button = QPushButton("Execute Query")
        self.execute_button.clicked.connect(self.execute_query)

        self.layout.addWidget(self.lbl_username)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.lbl_password)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user=username,
                password=password,
                database='drawerCaptureDB'
            )
            self.show_query_ui()
        except mysql.connector.Error as err:
            print("Error: ", err)
            self.username_input.clear()
            self.password_input.clear()

    def show_query_ui(self):
        self.layout.removeWidget(self.username_input)
        self.layout.removeWidget(self.password_input)
        self.layout.removeWidget(self.login_button)
        
        self.layout.addWidget(self.query_text)
        self.layout.addWidget(self.execute_button)

    def execute_query(self):
        if self.connection:
            query = self.query_text.toPlainText()
            try:
                cursor = self.connection.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                for result in results:
                    print(result)
            except mysql.connector.Error as err:
                print("Error: ", err)
        else:
            print("Not connected to the database.")

def main():
    app = QApplication(sys.argv)
    window = DatabaseApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
