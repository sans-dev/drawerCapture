import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)

from PyQt6.QtCore import pyqtSignal, QThread, QProcess

logger = logging.getLogger(__name__)
class CameraFetcher(QThread):
    """
    A QThread subclass that fetches connected cameras using gphoto2.

    Signals:
        finished: A signal that is emitted when the camera fetching process is finished.
                  The signal carries a list of connected cameras.

    Attributes:
        WAIT_TIME_MS (int): The maximum time to wait for the camera fetching process to finish.
        proc (QProcess): The QProcess instance that runs the camera fetching process.
        cameras_data (list): A list of strings containing information about connected cameras.
    """

    finished  = pyqtSignal(list)
    WAIT_TIME_MS = 10_000

    def __init__(self):
        super().__init__()
        self.proc = None
        self.cameras_data = []

    def run(self):
        """
        Starts the camera fetching process and emits the 'finished' signal when the process is done.
        """
        if self.proc is None:
            logger.info("fetching cameras")
            self.proc = QProcess()
            self.proc.finished.connect(self.procFinished)

            self.proc.start('gphoto2', ['--auto-detect'])
            finished = self.proc.waitForFinished(self.WAIT_TIME_MS)
            logger.debug("finished: %s", finished)
            if not finished:
                self.finished.emit(['No cameras found'])
                logger.debug("Fetching cameras timed out")
                return
            
            output = self.proc.readAllStandardOutput()
            lines = output.data().decode('utf-8').split('\n')
            cameras = []
            self.cameras_data = []

            for line in lines:
                if 'usb:' in line:
                    logger.debug("found camera: %s", line)
                    cameras.append(line.split('usb:')[0])
                    self.cameras_data.append(line)

            if len(cameras) == 0:
                cameras.append('No cameras found')
            self.finished.emit(cameras)

    def procFinished(self):
        """
        Resets the 'proc' attribute to None when the camera fetching process is finished.
        """
        self.proc = None
        
    def getCameraData(self, camera):
        """
        Returns the camera data for the specified camera.

        Args:
            camera (str): The name of the camera.

        Returns:
            str: The camera data, or None if the camera is not found.
        """
        logger.debug("getting camera data for %s", camera)
        for camera_data in self.cameras_data:
            if camera in camera_data:
                return camera_data
        return None

    def quit(self):
        """
        Stops the camera fetching process and emits the 'finished' signal with a 'No cameras found' message.
        """
        logger.debug("quitting camera fetcher")
        if self.proc is not None:
            self.proc.kill()
            self.finished.emit(['No cameras found'])
        super().quit()