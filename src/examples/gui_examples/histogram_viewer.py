import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class HistogramWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()

        self.image_path = image_path
        self.initUI()

    def initUI(self):
        # Create Matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.plot_histogram()

    def plot_histogram(self):
        # Load the image
        img = cv2.imread(self.image_path)

        if img is None:
            print("Error loading image.")
            return

        # Calculate RGB histograms
        hist_r = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([img], [1], None, [256], [0, 256])
        hist_b = cv2.calcHist([img], [2], None, [256], [0, 256])

        # Flatten the histogram arrays to 1D
        hist_r = hist_r.flatten()
        hist_g = hist_g.flatten()
        hist_b = hist_b.flatten()

        # Plot the histogram on the Matplotlib canvas
        ax = self.figure.add_subplot(111)
        ax.plot(hist_r, color='red', label='Red')
        ax.plot(hist_g, color='green', label='Green')
        ax.plot(hist_b, color='blue', label='Blue')
        # Fill the area under each histogram curve
        ax.fill_between(range(len(hist_r)), hist_r, alpha=0.3, color='red') 
        ax.fill_between(range(len(hist_g)), hist_g, alpha=0.3, color='green')
        ax.fill_between(range(len(hist_b)), hist_b, alpha=0.3, color='blue')
        ax.set_title('RGB Histogram')
        ax.set_xlabel('Pixel Intensity')
        ax.set_ylabel('Frequency')
        self.canvas.draw()



class MainWindow(QWidget): 
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Histogram App") # Add a window title

        layout = QVBoxLayout()  
        self.button = QPushButton("Show Histogram")
        self.button.clicked.connect(self.show_histogram)
        layout.addWidget(self.button) 

        self.setLayout(layout) 
    def show_histogram(self):
      image_path = "tests/data/test_img.jpg" # Replace with actual path
      self.histogram_window = HistogramWidget(image_path)
      self.histogram_window.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())