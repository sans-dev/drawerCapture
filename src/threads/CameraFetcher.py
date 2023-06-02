from PyQt6.QtCore import pyqtSignal, QThread
import subprocess

class CameraFetcher(QThread):
    finished  = pyqtSignal(list)

    def run(self):
        cmd = ['gphoto2', '--auto-detect']
        output = subprocess.run(cmd, capture_output=True)
        lines = output.stdout.decode('utf-8').split('\n')
        cameras = []
        self.cameras_data = []
        for line in lines:
            if 'usb:' in line:
                cameras.append(line.split('usb:')[0])
                self.cameras_data.append(line)
        # check if any cameras were found
        if len(cameras) == 0:
            cameras.append('No cameras found')
        self.finished.emit(cameras)

    def getCameraData(self, camera):
        for camera_data in self.cameras_data:
            if camera in camera_data:
                return camera_data
        return None