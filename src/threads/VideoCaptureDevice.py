from PyQt6.QtCore import QThread, pyqtSignal
import cv2

class VideoCaptureDevice(QThread):
    deviceOpen = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.device = cv2.VideoCapture()
        self.videoStreamDir = None

    def run(self):
        if self.videoStreamDir is None:
            print('No video stream dir set')
            return
        if not self.device.isOpened():
            print('Start capturing video stream on {}'.format(self.videoStreamDir))
            self.device.open(self.videoStreamDir)
            self.deviceOpen.emit()
        else:
            print('Device already opened')

    def setVideoStreamDir(self, videoStreamDir):
        self.videoStreamDir = videoStreamDir