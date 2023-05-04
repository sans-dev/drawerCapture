import sys
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsProxyWidget, QPushButton, QWidget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Create a QGraphicsView and set its size policy
        view = QGraphicsView(self)
        view.setFixedSize(400, 300)

        # Create a QGraphicsScene and set its background color
        scene = QGraphicsScene(self)
        scene.setBackgroundBrush(self.palette().window())

        # Set the QGraphicsScene for the QGraphicsView
        view.setScene(scene)

        # Create a QPushButton widget and add it to the QGraphicsScene
        button = QPushButton("Click me")
        proxy = QGraphicsProxyWidget()
        proxy.setWidget(button)
        scene.addItem(proxy)

        # Set the position of the button in the QGraphicsScene
        proxy.setPos(100, 100)

        # Show the window
        self.setWindowTitle("Free-Move Field Example")
        self.setGeometry(100, 100, 400, 300)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
