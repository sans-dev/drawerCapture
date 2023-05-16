from PyQt6.QtCore import pyqtSignal
import cv2
import subprocess
import time
from pathlib import Path

from threads.CameraThread import CameraThread


class CameraStreamer(CameraThread):
    streamRunning = pyqtSignal()
    buildingStream = pyqtSignal()
    streamStopped = pyqtSignal()

    def __init__(self, cameraData=None):
        super().__init__(cameraData=cameraData)
        if cameraData:
            self.setCameraData(cameraData)
        self.videoCapture = cv2.VideoCapture()
        self.videoStreamDir = Path('/dev/video2')
        self.cmd = ['bash', 'src/cmds/open_video_stream.bash']

    def run(self):
        super()._stopGphoto2Slaves()
        # append camera name and port to the start stream command
        cmd = self.cmd.copy()
        cmd.append('--name')
        cmd.append(self.cameraName)
        cmd.append('--port')
        cmd.append(self.cameraPort)
        print(" ".join(self.cmd))
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.buildingStream.emit()
        print("starting video stream with id {}".format(self.proc.pid))
        while not self.videoStreamDir.exists():
            print("waiting for video stream to open")
            time.sleep(1)
        self.videoCapture.open(self.videoStreamDir.as_posix())
        print('start capturing video stream')

        if self.videoCapture.isOpened():
            print("video stream opened")
            self.streamRunning.emit()
        else:
            print("video stream failed to open")
            super()._stopGphoto2Slaves()
            return

    def quit(self):
        self.streamStopped.emit()
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
        self.videoCapture.release()
        super()._stopGphoto2Slaves()
        super().quit()
        print("video stream closed")
        self.finished.emit()