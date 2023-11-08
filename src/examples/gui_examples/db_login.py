import sys
sys.path.append('src')
import mysql.connector
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget
# add project root to the path

from widgets.DataCollectionTextField import DataCollectionTextField
from utils.Emitter import TextEditEmitter
from db.drawerCaptureOrm import Engine
class DatabaseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.connection = None
        self.emitter = TextEditEmitter()
        self.engine = None

        self.setWindowTitle("Database Application")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()

    def init_ui(self):
        self.data_collection_text_field = DataCollectionTextField(emitter=self.emitter)
        self.emitter.textChanged.connect(self.insert)
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

        self.layout.addWidget(self.lbl_username)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.lbl_password)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username == "" or password == "":
            username = "root"
            password = "p2h3g1legosteine"
        
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user=username,
                password=password,
                database='drawerCaptureDB'
            )
            self.engine = Engine(self.connection, emitter=self.emitter)
            self.setCentralWidget(self.data_collection_text_field)
        except mysql.connector.Error as err:
            print("Error: ", err)
            self.username_input.clear()
            self.password_input.clear()

    def insert(self, data):
        if self.connection:
            try:
                self.engine.insertMuseum(data['General Information']['Museum / Facility'])
                self.engine.insertCollection(data['General Information']['Collection Name'], self.engine.museums[-1].id)
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
