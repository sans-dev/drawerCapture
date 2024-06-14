import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)

from datetime import datetime
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

    WAIT_TIME_MS = 30_000

    imageCaptured = pyqtSignal(str)
    failed_signal = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, cameraData=None):
        super().__init__(cameraData=cameraData)
        self.cmd = 'bash'
        self.config['--script'] = 'src/cmds/capture_image.bash'
        self.config['--image_dir'] = ''
        self.config['--image_name'] = ''
        self.config['--image_format'] = '.jpg'

    def run(self):
        """
        Runs the image capture thread.
        """
        logger.info("running image capture thread")
        self._captureImage()

    def _captureImage(self):
        self.proc = QProcess()
        self.proc.readyReadStandardError.connect(self.printStdErr)
        self.proc.readyReadStandardOutput.connect(self.printStdOut)
        self.proc.finished.connect(self.quit)

        if self.proc.state() is not QProcess.ProcessState.NotRunning:
            logger.warning("image capture process already running")
            print(self.proc.state())
            return

        logger.debug("starting image capture process")
        self.proc.start(self.cmd, self._buildKwargs())

        if not self.proc.waitForStarted():
            self._handle_failure("failed to start image capture process")
            return

        if not self.proc.waitForFinished(ImageCapture.WAIT_TIME_MS):
            self._handle_failure(f"image capture process did not finish in {ImageCapture.WAIT_TIME_MS} ms")
            return

        if self.proc.exitCode() != 0 and not any("Saving file as " in err for err in self.get_std_err()):
            self._handle_failure(f"image capture process exited with code {self.proc.exitCode()}. {self.get_std_err()}")
            return

        logger.info("image capture process finished")
        self.imageCaptured.emit(f"{self.config['--image_dir']}/{self.config['--image_name']}{self.config['--image_format']}")

    def _handle_failure(self, message):
        logger.warning(message)
        self.failed_signal.emit(message)
        
    def set_image_name(self, name):
        self.config['--image_name'] = name

    def set_img_dir(self, dir):
        self.config['--image_dir'] = dir

    def quit(self):
        """
        Quits the image capture thread and emits the imageCaptured signal.
        """
        logger.info("quitting image capture worker")
        self.proc.terminate()
        self.finished.emit()

def handle_capture(response):
    print(response)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QThread

    app = QApplication(sys.argv)
    capture = ImageCapture()
    capture.setCameraData('Sony Alpha-A5100 (Control)', 'usb:001,015')
    capture.set_image_name(datetime.now().isoformat().replace(':','_').replace('.','-'))
    capture.set_img_dir('data/captures')
    thread = QThread()
    capture.moveToThread(thread)
    thread.finished.connect(capture.deleteLater)
    thread.started.connect(capture.run)
    thread.finished.connect(capture.quit)
    capture.imageCaptured.connect(handle_capture)
    thread.finished.connect(app.quit)
    thread.start()
    thread.quit()
    thread.wait()

    sys.exit(app.exec())