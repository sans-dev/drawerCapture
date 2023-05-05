import subprocess
from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QImage, QPixmap, QFont
import cv2
from widgets.SelectCameraListWidget import SelectCameraListWidget
from widgets.DataCollectionTextField import DataCollectionTextField
import time

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

        self.dataCollectionLabel = QLabel("Data Collection")
        self.dataCollectionLabel.setFont(QFont("Arial", 20))
        self.dataCollectionTextField = DataCollectionTextField()
        self.dataCollectionTextField.show()

        # Add the widgets to the layout
        self.layout.addWidget(self.selectCameraButton, 0, 0)
        self.layout.addLayout(self.livePreviewLayout, 1, 0)
        self.layout.addWidget(self.exitModeButton, 2, 0)
        self.layout.addWidget(self.dataCollectionTextField, 1, 1, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.dataCollectionLabel, 0, 1, alignment=Qt.AlignmentFlag.AlignHCenter)

    def selectCamera(self):
        self.selectCameraListWidget.show()

    def showLivePreviewOnCameraSelect(self, cameraName):
        self.livePreviewLabel.setText(cameraName)
        self.startLivePreviewButton.setEnabled(True)
    
    def exitLiveMode(self):
        self.hide()
        self.timer.stop()
        self.cameraStreamer.quit()
        self.cameraStreamer.streamRunningSignal.signal.disconnect(self.startTimer)
        self.liveModeClosedSignal.signal.emit()
    
    def startLivePreview(self):
        self.cameraStreamer = CameraStreamer(self.selectCameraListWidget.selectedCameraData)
        self.cameraStreamer.streamRunningSignal.signal.connect(self.startTimer)
        self.cameraStreamer.streamRunningSignal.signal.connect(self.livePreviewLabel.show)
        self.cameraStreamer.streamRunningSignal.signal.connect(self.startLivePreviewButton.hide)
        self.cameraStreamer.start()

    def startTimer(self):
        self.timer.start(1)

    def updateLivePreview(self):
        print("updating live preview")
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
        self._stopGphoto2Slaves()

        cmd = ['bash', 'src/cmds/open_video_stream.bash']
        print(cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"started process with id {proc.pid}")
        time.sleep(4)
        self.streamRunningSignal.signal.emit()
        self.videoCapture = cv2.VideoCapture('/dev/video2')

    def _stopGphoto2Slaves(self):
        # get the process id of the gphoto2 slave processes using pgrep -fla gphoto2
        # kill the processes using kill -9 <pid>
        cmd = ['pgrep', '-fla', 'gphoto2']
        
        output = subprocess.run(cmd, capture_output=True)
        output = output.stdout.decode('utf-8')
        # loop over output and filter processes that containing gphoto2
        # get the pid and kill the process
        for line in output.split('\n'):
            if 'gphoto2' in line:
                pid = line.split(' ')[0]
                print(pid)
                cmd = [
                    'kill',
                    '-9',
                    pid
                ]
                subprocess.run(cmd)


class StreamRunningSignal(QObject):
    signal = pyqtSignal()



        