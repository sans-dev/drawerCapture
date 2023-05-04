import subprocess
from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2
from widgets.SelectCameraListWidget import SelectCameraListWidget

class LiveModeClosedSignal(QObject):
    signal = pyqtSignal()

class LiveModeWindow(QWidget):
    def __init__(self):
        # Set the calling window as the parent
        super().__init__()
        self.liveModeClosedSignal = LiveModeClosedSignal()
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateLivePreview)

        self.initUI()

    def initUI(self):
        # Set the window title and size
        self.setWindowTitle("Live Mode")
        self.setGeometry(100, 100, 800, 800)

        # Create the layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Create the widgets
        self.exitModeButton = QPushButton("Exit")
        self.exitModeButton.clicked.connect(self.exitLiveMode)

        self.selectCameraButton = QPushButton("Select Camera")
        self.selectCameraButton.clicked.connect(self.selectCamera)

        # create a live preview for a video stream using label 
        self.livePreviewLabel = QLabel("Live Preview")
        self.livePreviewLabel.setFixedSize(400, 300)
        self.livePreviewLabel.setFrameStyle(1)
        self.livePreviewLabel.setLineWidth(1)
        self.livePreviewLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # disable and hide the label
        self.livePreviewLabel.setEnabled(False)
        self.livePreviewLabel.hide()

        # add a button to start the live preview
        self.startLivePreviewButton = QPushButton("Start Live Preview")
        self.startLivePreviewButton.clicked.connect(self.startLivePreview)
        self.startLivePreviewButton.setEnabled(False)

        # add the preview and the button into a grid layout in the same cell
        self.livePreviewLayout = QGridLayout()
        self.livePreviewLayout.addWidget(self.livePreviewLabel, 0, 0)
        self.livePreviewLayout.addWidget(self.startLivePreviewButton, 0, 0, Qt.AlignmentFlag.AlignCenter)

        # create a list widget to select the camera
        self.selectCameraListWidget = SelectCameraListWidget()
        self.selectCameraListWidget.selectedCameraChanged.signal.connect(self.showLivePreviewOnCameraSelect)
        self.selectCameraListWidget.hide()

        # Add the widgets to the layout
        self.layout.addWidget(self.selectCameraButton, 0, 0)
        self.layout.addLayout(self.livePreviewLayout, 1, 0)
        self.layout.addWidget(self.exitModeButton, 2, 0)

    def selectCamera(self):
        self.selectCameraListWidget.show()

    def showLivePreviewOnCameraSelect(self, cameraName):
        self.livePreviewLabel.setText(cameraName)
        self.startLivePreviewButton.setEnabled(True)
    
    def exitLiveMode(self):
        self.hide()
        self.liveModeClosedSignal.signal.emit()
    
    def startLivePreview(self):
        self.cameraStreamer = CameraStreamer(self.selectCameraListWidget.selectedCameraData)
        self.cameraStreamer.streamRunningSignal.signal.connect(self.startTimer)
        self.cameraStreamer.start()

    def startTimer(self):
        self.timer.start(1)

    def updateLivePreview(self):
        ret, frame = self.cameraStreamer.videoCapture.read()
        if ret:
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w            
            qt_image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.livePreviewLabel.setPixmap(pixmap)


class CameraStreamer(QThread):
    def __init__(self, cameraData):
        super().__init__()
        self.cameraName = cameraData.split('usb')[0]
        self.cameraPort = f"usb{cameraData.split('usb')[-1]}"
        self.videoCapture = None
        self.streamRunningSignal = StreamRunningSignal()

    def run(self):
        print(self.cameraName)
        print(self.cameraPort)

        cmd = [
            'gphoto2', 
            '--capture-movie', 
            '--stdout', 
            f'--port={self.cameraPort}', 
            '|',
            'ffmpeg', 
            '-i', 
            '-', 
            '-vcodec', 
            'rawvideo', 
            '-pix_fmt', 
            'yuv720p', 
            '-threads',
            '0',
            '-f',
            'v4l2',
            f'/dev/{self.cameraName[0]}'
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            output = proc.stdout.readline()
            if proc.poll() is not None:
                print("Process ended")
                print(output.strip())
                break
            if output:
                print(output.strip())
            else:
                print("Stream running")
                break
        self.videoCapture = cv2.VideoCapture(f'/dev/{self.cameraName}')
        print(self.videoCapture.isOpened())
        self.streamRunningSignal.signal.emit()

class StreamRunningSignal(QObject):
    signal = pyqtSignal()



        