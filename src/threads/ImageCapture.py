from pathlib import Path
import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)

from PyQt6.QtCore import QProcess, pyqtSignal
from threads import CameraThread

logger = logging.getLogger(__name__)

class ImageCapture(CameraThread):
    IMG_FORMATS = {
        'Fuji' : '.raf',
    }
    WAIT_TIME_MS = 20_000

    imageCaptured = pyqtSignal(str)

    def __init__(self, cameraData=None):
        super().__init__(cameraData=cameraData)
        self.cmd = 'bash'
        self.config['--script'] = 'src/cmds/capture_image.bash'
        self.config['--image_dir'] = ''
        self.config['--image_name'] = ''
        self.config['--image_format'] = '.jpeg'

        self.finished.connect(self.quit)

    def run(self):
        logger.info("running image capture thread")
        super()._stopGphoto2Slaves()
        self._captureImage()

    def _captureImage(self):
        if self.proc is None:
            self.proc = QProcess()
            self.proc.readyReadStandardError.connect(self.printStdErr)
            self.proc.readyReadStandardOutput.connect(self.printStdOut)
            self.proc.finished.connect(self._procFinished)

            logger.debug("starting image capture process")
            self.proc.start(self.cmd, self._buildKwargs())
            started = self.proc.waitForStarted()

            if not started:
                logger.warining("failed to start image capture process")
                return
            self.proc.waitForFinished(ImageCapture.WAIT_TIME_MS)
        
    def quit(self):
        logger.info("quitting image capture thread")
        self.imageCaptured.emit(f"{self.config['--image_dir']}/{self.config['--image_name']}{self.config['--image_format']}")
        super()._stopGphoto2Slaves()
        super().quit()

    def setUpConfig(self, config: dict):
        for key, value in config.items():
            try:
                self.config[key] = value
            except KeyError:
                logger.error("key %s not found in config", key)