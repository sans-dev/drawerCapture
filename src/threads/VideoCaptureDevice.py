import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)

import cv2

from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)

class VideoCaptureDevice(QThread):
    """
    A class representing a video capture device.

    Attributes:
    - deviceOpen (pyqtSignal): A signal emitted when the device is opened.
    - device (cv2.VideoCapture): The video capture device.
    - videoStreamDir (str): The directory of the video stream.

    Methods:
    - run(): Opens the video stream device.
    - setVideoStreamDir(videoStreamDir): Sets the directory of the video stream.
    - quit(): Quits the video capture device thread and releases the video stream device.
    """
    deviceOpen = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.device = cv2.VideoCapture()
        self.videoStreamDir = None

    def run(self):
        """
        Runs the video capture device thread.

        If the video stream directory is not set, the function returns.
        If the device is not opened, it opens the video stream device at the specified directory and emits a signal.
        If the device is already open, it logs a message and returns.
        """
        
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
        """
        Sets the directory for the video stream.

        Args:
            videoStreamDir (str): The directory for the video stream.
        """
        logger.debug("setting video stream dir to %s", videoStreamDir)
        self.videoStreamDir = videoStreamDir

    def quit(self):
        """
        Quits the video capture device thread and releases the video stream device if it is open.
        """
        logger.info("quitting video capture device thread")
        if self.device.isOpened():
            logger.info("closing video stream device")
            self.device.release()
        super().quit()