import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)

from PyQt6.QtCore import pyqtSignal, QThread, QProcess

logger = logging.getLogger(__name__)
class CameraFetcher(QThread):
    finished  = pyqtSignal(list)
    WAIT_TIME_MS = 10_000

    def __init__(self):
        super().__init__()
        self.proc = None
        self.cameras_data = []

    def run(self):
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
        self.proc = None
        
    def getCameraData(self, camera):
        logger.debug("getting camera data for %s", camera)
        for camera_data in self.cameras_data:
            if camera in camera_data:
                return camera_data
        return None

    def quit(self):
        logger.debug("quitting camera fetcher")
        if self.proc is not None:
            self.proc.kill()
            self.finished.emit(['No cameras found'])
        super().quit()