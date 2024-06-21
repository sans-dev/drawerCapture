import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)

import cv2
from PyQt6.QtCore import QRunnable, pyqtSignal, QObject, QTimer

logger = logging.getLogger(__name__)


class VideoDeviceSignals(QObject):
    device_open = pyqtSignal()

class VideoCaptureDevice(QRunnable):
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
    signals = VideoDeviceSignals()

    def __init__(self, fs):
        super().__init__()
        self.device = cv2.VideoCapture()
        self.device_dir = None
        self.fs = fs
        self.running = False

    def run(self):
        """
        Runs the video capture device thread.

        If the video stream directory is not set, the function returns.
        If the device is not opened, it opens the video stream device at the specified directory and emits a signal.
        If the device is already open, it logs a message and returns.
        """
        
        if self.device_dir is None:
            logger.debug("video stream dir not set")
            return
        if not self.device.isOpened():
            logger.info("opening video stream device at %s", self.device_dir)
            self.signals.device_open.emit()
            self.device.open(self.device_dir)
            logger.info("Connected to device")
            self.running = True
            while self.running:
                continue
            self.quit()
        else:
            logger.info("video stream device already open")

    def stop_device(self):
        self.running = False

    def set_device_dir(self, device_dir):
        """
        Sets the directory for the video stream.

        Args:
            videoStreamDir (str): The directory for the video stream.
        """
        logger.debug("setting video stream dir to %s", device_dir)
        self.device_dir = device_dir

    def get_frame(self):
        """
        Gets a frame from the video stream.

        Returns:
            numpy.ndarray: A frame from the video stream.

        """
        logger.debug("getting frame from videoCapture device")
        return self.device.read()
    
    def quit(self):
        """
        Quits the video capture device thread and releases the video stream device if it is open.
        """
        logger.info("quitting video capture device thread")
        if self.device.isOpened():
            logger.info("closing video stream device")
            self.device.release()