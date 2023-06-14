from PyQt6.QtCore import QProcess
from threads import CameraThread

class ImageCapture(CameraThread):
    IMG_FORMATS = {
        'Fuji' : '.raf',
    }
    WAIT_TIME_MS = 10_000

    def __init__(self, cameraData=None):
        super().__init__(cameraData=cameraData)
        self.cmd = 'bash'
        self.config['--script'] = 'src/cmds/capture_image.bash'
        self.config['--image_dir'] = ''
        self.config['--image_name'] = ''
        self.config['--image_format'] = '.raf'
        self.config['--image_quality'] = '0'
        self.config['--debug'] = 'true'

        self.finished.connect(self.quit)

    def run(self):
        print("image capture started")
        super()._stopGphoto2Slaves()
        self._captureImage()

    def _captureImage(self):
        if self.proc is None:
            self.proc = QProcess()
            self.proc.finished.connect(self._procFinished)
            self.proc.start(self.cmd, self._buildKwargs())
            self.proc.readyReadStandardOutput.connect(self.printStdOut)
            started = self.proc.waitForStarted()
            if not started:
                print("image capture failed to start")
                stdOut = self.proc.readAllStandardOutput().data().decode('utf-8')
                stdErr = self.proc.readAllStandardError().data().decode('utf-8')
                print('ImageCapture Output:\n', stdOut)
                print('ImageCapture Error:\n', stdErr)

            self.proc.waitForFinished(-1)
        
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