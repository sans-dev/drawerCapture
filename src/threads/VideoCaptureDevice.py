import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)

import cv2

from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)

class VideoCaptureDevice(QThread):
    deviceOpen = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.device = cv2.VideoCapture()
        self.videoStreamDir = None

    def run(self):
        if self.videoStreamDir is None:
            logger.debug("video stream dir not set")
            return
        if not self.device.isOpened():
            logger.info("opening video stream device at %s", self.videoStreamDir)
            self.device.open(self.videoStreamDir)
            self.deviceOpen.emit()
        else:
            logger.info("video stream device already open")

    def setVideoStreamDir(self, videoStreamDir):
        logger.debug("setting video stream dir to %s", videoStreamDir)
        self.videoStreamDir = videoStreamDir

    def quit(self):
        logger.info("quitting video capture device thread")
        if self.device.isOpened():
            logger.info("closing video stream device")
            self.device.release()
        super().quit()