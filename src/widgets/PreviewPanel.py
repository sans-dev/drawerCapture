from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
import cv2
import time
from threads.CameraStreamer import CameraStreamer
from threads.ImageCapture import ImageCapture

class PreviewPanel(QLabel):
    def __init__(self):
        super().__init__()
        self.cameraStreamer = CameraStreamer()
        self.imageCapture = ImageCapture()
        self.cameraData = None
        self.timer = QTimer()        
        self.wasStreaming = False
        
        self.initUI()
        self.connectSignals()
    
    def initUI(self):
        # set the size of the preview panel
        panel_size = (int(1024), int(780))
        self.setFixedSize(panel_size[0], panel_size[1])
        self.setFrameStyle(1)
        self.setLineWidth(1)
    
    def connectSignals(self):
        self.timer.timeout.connect(self.updatePreview)
        self.cameraStreamer.streamRunning.connect(self.startTimer)
        self.cameraStreamer.streamStopped.connect(self.timer.stop)

        self.imageCapture.started.connect(self.stopPreview)
        self.imageCapture.finished.connect(self.startPreview)

    def updatePreview(self):
        while self.cameraStreamer.videoCapture.isOpened() == False:
            print("waiting for video capture")
            time.sleep(1)
        ret, frame = self.cameraStreamer.videoCapture.read()
        if ret:
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w            
            qt_image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.setPixmap(pixmap)
        
    def startPreview(self):
        if self.wasStreaming:
            self.cameraStreamer.start()

    def startTimer(self):
        self.timer.start(100)

    def stopPreview(self):
        self.cameraStreamer.quit()
        self.emptyPreview()

    def emptyPreview(self):
        self.setPixmap(QPixmap())
        
    def setCameraData(self, cameraData):
        self.cameraData = cameraData
        self.cameraStreamer.setCameraData(self.cameraData)
        self.imageCapture.setCameraData(self.cameraData)

    def captureImage(self, captureDir, captureName):
        self.imageCapture.captureImage(captureDir, captureName)
