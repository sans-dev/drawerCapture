from pathlib import Path
import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)

from PyQt6.QtCore import QProcess, pyqtSignal
from threads import CameraThread

logger = logging.getLogger(__name__)

class ImageCapture(CameraThread):
    """
    A thread for capturing images from a camera.

    Attributes:
    IMG_FORMATS (dict): A dictionary of image formats and their corresponding file extensions.
    WAIT_TIME_MS (int): The maximum time to wait for the image capture process to finish, in milliseconds.
    imageCaptured (pyqtSignal): A signal emitted when an image is captured.
    """

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
        self.config['--image_format'] = '.jpg'

        self.finished.connect(self.quit)

    def run(self):
        """
        Runs the image capture thread.
        """
        logger.info("running image capture thread")
        super()._stopGphoto2Slaves()
        self._captureImage()

    def _captureImage(self):
        """
        Starts the image capture process.
        """
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
        """
        Quits the image capture thread and emits the imageCaptured signal.
        """
        logger.info("quitting image capture thread")
        self.imageCaptured.emit(f"{self.config['--image_dir']}/{self.config['--image_name']}{self.config['--image_format']}")
        super()._stopGphoto2Slaves()

    def setUpConfig(self, config: dict):
        """
        Sets up the configuration for the image capture thread.

        Args:
        config (dict): A dictionary of configuration options.
        """
        for key, value in config.items():
            try:
                self.config[key] = value
            except KeyError:
                logger.error("key %s not found in config", key)