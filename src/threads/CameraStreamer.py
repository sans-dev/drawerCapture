from PyQt6.QtCore import QThread, pyqtSignal
import cv2
import subprocess
import time
from pathlib import Path


class CameraStreamer(QThread):
    streamRunning = pyqtSignal()
    buildingStream = pyqtSignal()
    streamStopped = pyqtSignal()
    capturingImage = pyqtSignal()
    imageCaptured = pyqtSignal()

    def __init__(self, cameraData=None):
        super().__init__()
        if cameraData:
            self.setCameraData(cameraData)
        self.videoCapture = cv2.VideoCapture()
        self.videoStreamDir = Path('/dev/video2')
        self.startStreamCmd = ['bash', 'src/cmds/open_video_stream.bash']
        self.captureImgCmd = ['bash', 'src/cmds/capture_image.bash']

        self.capturingImage.connect(self.quit)
        self.imageCaptured.connect(self.start)

    def run(self):
        self._stopGphoto2Slaves()
        self.proc = subprocess.Popen(self.startStreamCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.buildingStream.emit()
        print("starting video stream with id {}".format(self.proc.pid))
        while not self.videoStreamDir.exists():
            print("waiting for video stream to open")
            time.sleep(1)
        self.videoCapture.open(self.videoStreamDir.as_posix())

        if self.videoCapture.isOpened():
            print("video stream opened")
            self.streamRunning.emit()
        else:
            print("video stream failed to open")
            self._stopGphoto2Slaves()
            return

    def quit(self):
        self.streamStopped.emit()
        self.proc.terminate()
        self.proc.wait()
        self.videoCapture.release()
        self._stopGphoto2Slaves()
        super().quit()
        print("video stream closed")

    def captureImage(self, captureDir, captureName):
        self.capturingImage.emit()
        self.captureImgCmd.append(captureDir)
        self.captureImgCmd.append(captureName)
        self.capProc = subprocess.Popen(self.captureImgCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while self.capProc.poll() is None:
            print("waiting for image capture to complete")
            self.sleep(1)
        self.imageCaptured.emit()

    def setCameraData(self, cameraData):
        self.cameraName = cameraData.split('usb')[0]
        self.cameraPort = f"usb{cameraData.split('usb')[-1]}"


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