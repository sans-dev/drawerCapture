import subprocess
import time
from pathlib import Path
import cv2
from datetime import datetime

from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QImage, QPixmap, QFont

from widgets.SelectCameraListWidget import SelectCameraListWidget
from widgets.DataCollectionTextField import DataCollectionTextField
from widgets.SpinnerWidget import LoadingSpinner 

from signals.WidgetSignal import WidgetSignal

class LiveWidget(QWidget):
    changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # setup grid layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # add an close button
        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self.closeLiveMode)
        self.layout.addWidget(self.closeButton, 0, 0, Qt.AlignmentFlag.AlignRight)

    def closeLiveMode(self):
        self.changed.emit("main")
'''
class LivePreviewWidget(QWidget):
    def __init__(self):
        # Set the calling window as the parent
        super().__init__()
        self.liveModeClosedSignal = LiveModeClosedSignal()
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateLivePreview)
        self.cameraStreamer = None

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
        self.livePreviewLabel.setFixedSize(int(1920/2), int(1080/2))
        self.livePreviewLabel.setFrameStyle(1)
        self.livePreviewLabel.setLineWidth(1)
        self.livePreviewLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # disable and hide the label
        self.livePreviewLabel.setEnabled(False)
        # self.livePreviewLabel.hide()

        # create a waiting spinner
        self.spinner = LoadingSpinner()
        self.spinner.hide()

        # add a button to start the live preview
        self.startLivePreviewButton = QPushButton("Start Live Preview")
        self.startLivePreviewButton.clicked.connect(self.startLivePreview)
        self.startLivePreviewButton.setEnabled(False)

        self.stopLivePreviewButton = QPushButton("Stop Live Preview")
        self.stopLivePreviewButton.clicked.connect(self.stopLivePreview)
        self.stopLivePreviewButton.setEnabled(False)

        # add the preview and the button into a grid layout in the same cell
        self.livePreviewLayout = QGridLayout()
        # self.livePreviewLayout.addWidget(self.livePreviewLabel, 0, 0)
        self.livePreviewLayout.addWidget(self.startLivePreviewButton, 1, 0, Qt.AlignmentFlag.AlignCenter)
        self.livePreviewLayout.addWidget(self.spinner, 0, 0, Qt.AlignmentFlag.AlignCenter)
        self.livePreviewLayout.addWidget(self.stopLivePreviewButton, 2, 0, Qt.AlignmentFlag.AlignCenter)

        # create a list widget to select the camera
        self.selectCameraListWidget = SelectCameraListWidget()
        self.selectCameraListWidget.selectedCameraChanged.signal.connect(self.showLivePreviewOnCameraSelect)
        self.selectCameraListWidget.hide()

        self.dataCollectionLabel = QLabel("Data Collection")
        self.dataCollectionLabel.setFont(QFont("Arial", 20))
        self.dataCollectionTextField = DataCollectionTextField()
        self.dataCollectionTextField.show()

        # add button to capture an image 
        self.captureImageButton = QPushButton("Capture Image")
        self.captureImageButton.clicked.connect(self.captureImage)

        # Add the widgets to the layout
        self.layout.addWidget(self.selectCameraButton, 0, 0)
        self.layout.addWidget(self.livePreviewLabel, 1, 0)
        self.layout.addLayout(self.livePreviewLayout, 2, 0)
        self.layout.addWidget(self.exitModeButton, 3, 0)
        self.layout.addWidget(self.dataCollectionTextField, 1, 2, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.dataCollectionLabel, 0, 2, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.captureImageButton, 3, 2, alignment=Qt.AlignmentFlag.AlignBottom)

    def captureImage(self):
        if self.cameraStreamer is not None:
            captureDir = 'data/captures'
            Path(captureDir).mkdir(parents=True, exist_ok=True)
            imageName = f'{datetime.now().date().isoformat()}.raf'
            self.cameraStreamer.captureImage(captureDir, imageName)
    
    def selectCamera(self):
        self.selectCameraListWidget.show()

    def showLivePreviewOnCameraSelect(self, cameraName):
        self.cameraStreamer = CameraStreamer(self.selectCameraListWidget.selectedCameraData)
        self.livePreviewLabel.setText(cameraName)
        self.startLivePreviewButton.setEnabled(True)
    
    def stopLivePreview(self):
        self.cameraStreamer.quit()
        self.cameraStreamer.streamRunningSignal.signal.disconnect(self.startTimer)
        self.cameraStreamer.buildingStreamSignal.signal.disconnect(self.spinner.show)
        self.cameraStreamer.buildingStreamSignal.signal.disconnect(self.spinner.start)
        self.cameraStreamer.buildingStreamSignal.signal.disconnect(self.livePreviewLabel.show)
        self.cameraStreamer.buildingStreamSignal.signal.disconnect(self.startLivePreviewButton.hide)
        self.cameraStreamer.streamRunningSignal.signal.disconnect(self.spinner.stop)
        self.cameraStreamer.streamRunningSignal.signal.disconnect(self.spinner.hide)
        self.livePreviewLabel.hide()
        self.startLivePreviewButton.show()
        self.stopLivePreviewButton.setEnabled(False)
        self.spinner.stop()
        self.spinner.hide()
        self.timer.stop()

    def exitLiveMode(self):
        self.hide()
        self.timer.stop()
        if self.cameraStreamer:
            self.stopLivePreview()
        self.liveModeClosedSignal.signal.emit()
    
    def startLivePreview(self):
        self.cameraStreamer.streamRunningSignal.signal.connect(self.startTimer)
        self.cameraStreamer.buildingStreamSignal.signal.connect(self.spinner.show)
        self.cameraStreamer.buildingStreamSignal.signal.connect(self.spinner.start)
        self.cameraStreamer.buildingStreamSignal.signal.connect(self.livePreviewLabel.show)
        self.cameraStreamer.buildingStreamSignal.signal.connect(self.startLivePreviewButton.hide)
        self.cameraStreamer.streamRunningSignal.signal.connect(self.spinner.hide)
        self.cameraStreamer.streamRunningSignal.signal.connect(self.spinner.stop)
        self.stopLivePreviewButton.setEnabled(True)
        self.cameraStreamer.start()

    def startTimer(self):
        self.timer.start(1)

    def updateLivePreview(self):
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
            self.livePreviewLabel.setPixmap(pixmap)

class CameraStreamer(QThread):
    def __init__(self, cameraData):
        super().__init__()
        self.cameraName = cameraData.split('usb')[0]
        self.cameraPort = f"usb{cameraData.split('usb')[-1]}"
        self.videoCapture = cv2.VideoCapture()
        self.streamRunningSignal = StreamRunningSignal()
        self.buildingStreamSignal = BuildingStreamSignal()
        self.videoStreamDir = Path('/dev/video2')
        self.startStreamCmd = ['bash', 'src/cmds/open_video_stream.bash']
        self.captureImgCmd = ['bash', 'src/cmds/capture_image.bash']

    def run(self):
        self._stopGphoto2Slaves()
        self.proc = subprocess.Popen(self.startStreamCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.buildingStreamSignal.signal.emit()
        print("starting video stream with id {}".format(self.proc.pid))
        while not self.videoStreamDir.exists():
            print("waiting for video stream to open")
            time.sleep(1)
        self.videoCapture.open(self.videoStreamDir.as_posix())

        if self.videoCapture.isOpened():
            print("video stream opened")
            self.streamRunningSignal.signal.emit()
        else:
            print("video stream failed to open")
            self._stopGphoto2Slaves()
            return

    def quit(self):
        self.proc.terminate()
        self.proc.wait()
        self.videoCapture.release()
        self._stopGphoto2Slaves()

    def captureImage(self, captureDir, captureName):
        self._stopGphoto2Slaves()
        self.captureImgCmd.append(captureDir)
        self.captureImgCmd.append(captureName)
        subprocess.run(self.captureImgCmd)
        self._stopGphoto2Slaves()

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

class BuildingStreamSignal(QObject):
    signal = pyqtSignal()

''' 