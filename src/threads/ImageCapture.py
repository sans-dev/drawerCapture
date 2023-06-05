from PyQt6.QtCore import QProcess
import shlex
from threads import CameraThread

class ImageCapture(CameraThread):
    IMG_FORMATS = {
        'Fuji' : '.raf',
    }
    WAIT_TIME_MS = 10_000

    def __init__(self, cameraData=None):
        super().__init__(cameraData=cameraData)
        self.cmd = 'bash'
        self.config = {
            '--script': 'src/cmds/capture_image.bash',
            '--image_dir': '',
            '--image_name': '',
            '--image_format': '.raf',
            '--image_quality': '0',
            '--camera_name': '' if self.cameraName is None else self.cameraName,
            '--port': '' if self.cameraPort is None else self.cameraPort,
            '--debug': 'false'
        }

        self.finished.connect(self.quit)

    def run(self):
        print("image capture started")
        super()._stopGphoto2Slaves()
        self._captureImage()

    def _captureImage(self):
        if self.proc is None:
            self.proc = QProcess()
            self.proc.finished.connect(self._procFinished)
            self.proc.start(self.cmd, self._buildConfig())
            started = self.proc.waitForStarted()
            if not started:
                print("image capture failed to start")
                error = self.proc.readAllStandardError().data().decode('utf-8')
                print(error)
            self.proc.waitForFinished(-1)
        
    def _procFinished(self):
        self.proc = None
        self.finished.emit()

    def quit(self):
        super()._stopGphoto2Slaves()
        super().quit()
        print("image capture closed")

    def setUpConfig(self, config: dict):
        for key, value in config.items():
            try:
                self.config[key] = value
            except KeyError:
                print(f"key {key} not found in config")

    def _buildConfig(self):
        config = []
        for key, value in self.config.items():
            if key == '--script':
                config.append(value)
                continue
            config.append(key)
            config.append(value)
        return shlex.split(' '.join(config))