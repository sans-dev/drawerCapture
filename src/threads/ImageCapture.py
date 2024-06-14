from pathlib import Path
import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)

from PyQt6.QtCore import pyqtSignal, QProcess
from src.threads.CameraThread import CameraThread

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
    WAIT_TIME_MS = 30_000

    imageCaptured = pyqtSignal(str)
    failed_signal = pyqtSignal(str)

    def __init__(self, cameraData=None):
        super().__init__(cameraData=cameraData)
        self.cmd = 'bash'
        self.config['--script'] = 'src/cmds/capture_image.bash'
        self.config['--image_dir'] = ''
        self.config['--image_name'] = ''
        self.config['--image_format'] = '.jpg'
        self.proc = QProcess()
        self.proc.readyReadStandardError.connect(self.printStdErr)
        self.proc.readyReadStandardOutput.connect(self.printStdOut)
        self.proc.finished.connect(self.quit)

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
        if self.proc.state() is QProcess.ProcessState.NotRunning:

            logger.debug("starting image capture process")
            self.proc.start(self.cmd, self._buildKwargs())
            started = self.proc.waitForStarted()
            if not started:
                logger.warining("failed to start image capture process")
                self.failed_signal.emit("failed to start image capture process")
                return
            finished = self.proc.waitForFinished(ImageCapture.WAIT_TIME_MS)
            if not finished:
                logger.warning("image capture process did not finish in {} ms".format(ImageCapture.WAIT_TIME_MS))
                self.failed_signal.emit("image capture process did not finish in {} ms".format(ImageCapture.WAIT_TIME_MS))
                return
            if self.proc.exitCode()!= 0 and not "Saving file as " in " ".join(self.get_std_err()):
                logger.warning("image capture process exited with code {}. {}".format(self.proc.exitCode(), self.get_std_err()))
                self.failed_signal.emit("image capture process exited with code {}. {}".format(self.proc.exitCode(), self.get_std_err()))
                return
            logger.info("image capture process finished")
            self.imageCaptured.emit(self.config['--image_dir'] + self.config['--image_name'] + self.config['--image_format'])
        else:
            logger.warning("image capture process already running")
            print(self.proc.state())
        
    def quit(self):
        """
        Quits the image capture thread and emits the imageCaptured signal.
        """
        logger.info("quitting image capture thread")
        #super()._stopGphoto2Slaves()
        #self.proc.kill()

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



if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QThread
    app = QApplication(sys.argv)

    capture = ImageCapture()
    capture.setCameraData('Sony Alpha-A5100 (Control)', 'usb:001,004')
    thread = QThread()
    capture.moveToThread(thread)
    thread.started.connect(capture.run)
    thread.finished.connect(capture.quit)
    thread.start()
    sys.exit(app.exec())