import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)

import cv2
from PyQt6.QtCore import QRunnable, pyqtSignal, QObject
import time
logger = logging.getLogger(__name__)


class VideoDeviceSignals(QObject):
    device_open = pyqtSignal()
    send_frame = pyqtSignal(tuple)

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

    def __init__(self, fs, device_dir=None):
        super().__init__()
        self.device_dir = None
        self.fs = fs
        self.running = False
        self.device_dir = device_dir

    def run(self):
        """
        Runs the video capture device thread.

        If the video stream directory is not set, the function returns.
        If the device is not opened, it opens the video stream device at the specified directory and emits a signal.
        If the device is already open, it logs a message and returns.
        """
        time.sleep(2)
        self.signals.device_open.emit()
        if self.device_dir is None:
            logger.debug(f"video stream dir not set. Setting default device {0}")
            cap = cv2.VideoCapture(0, cv2.CAP_V4L)
        else:
            logger.debug(f"Opening device at {self.device_dir}")
            cap = cv2.VideoCapture(self.device_dir)
        if cap.isOpened():
            self.device_open = cap.isOpened()
            
            while self.device_open:
                out = cap.read()
                self.signals.send_frame.emit(out)
            logger.debug(f"releasing video device...")
            cap.release()
        else:
            logger.debug("Cannot open device...")

    def quit(self):
        self.device_open = False