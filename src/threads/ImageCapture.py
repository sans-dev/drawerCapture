import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)

from PyQt6.QtCore import QProcess
from threads import CameraThread

logger = logging.getLogger(__name__)

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
        self.config['--image_format'] = '.tiff'
        self.config['--image_quality'] = '0'

    def run(self):
        logger.info("running image capture thread")
        super()._stopGphoto2Slaves()
        self._captureImage()

    def _captureImage(self):
        if self.proc is None:
            self.proc = QProcess()
            if self.config['--debug'] == 'false':
                self.proc.readyReadStandardError.connect(self.printStdErr)
            self.proc.readyReadStandardOutput.connect(self.printStdOut)
            self.proc.finished.connect(self._procFinished)

            logger.debug("starting image capture process")
            self.proc.start(self.cmd, self._buildKwargs())
            started = self.proc.waitForStarted()

            if not started:
                logger.warining("failed to start image capture process")
                return
            self.proc.waitForFinished(-1)
        
    def quit(self):
        super()._stopGphoto2Slaves()
        super().quit()
        logger.info("quitting image capture thread")

    def setUpConfig(self, config: dict):
        for key, value in config.items():
            try:
                self.config[key] = value
            except KeyError:
                logger.error("key %s not found in config", key)