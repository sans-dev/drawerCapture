import logging
import logging.config

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
import cv2
import time

from threads.CameraStreamer import CameraStreamer
from threads.ImageCapture import ImageCapture

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class PreviewPanel(QLabel):
    """
    A widget that displays a live preview of the camera stream and allows capturing images.
    """
    previewStopped = pyqtSignal()
    capturedImage = pyqtSignal(str)

    def __init__(self):
        """
        Initializes the PreviewPanel widget.
        """
        logger.debug("initializing preview panel")
        super().__init__()
        self.cameraStreamer = CameraStreamer()
        self.imageCapture = ImageCapture()
        self.cameraData = None
        self.timer = QTimer()        
        self.frame = None
        self.initUI()
        self.connectSignals()
    
    def initUI(self):
        """
        Initializes the user interface of the PreviewPanel widget.
        """
        logger.debug("initializing preview panel UI")
        # set the size of the preview panel
        panel_size = (int(1024), int(780))
        self.setFixedSize(panel_size[0], panel_size[1])
        self.setFrameStyle(1)
        self.setLineWidth(1)
    
    def connectSignals(self):
        """
        Connects the signals of the PreviewPanel widget.
        """
        logger.debug("connecting signals for preview panel")
        self.timer.timeout.connect(self.updatePreview)
        self.cameraStreamer.streamStopped.connect(self.timer.stop)
        self.cameraStreamer.videoCapture.deviceOpen.connect(self.startTimer)

    def updatePreview(self):
        """
        Updates the preview panel with the latest frame from the camera stream.
        """
        try:
            ret, self.frame = self.cameraStreamer.getFrame()
        except Exception as e:
            logger.exception("failed to get frame from camera streamer: %s", e)
            self.cameraStreamer.quit()
        if ret:
            try:
                self._setPanelImage()
            except Exception as e:
                logger.exception("failed to update preview panel with new frame: %s", e)
        else:
            logger.error("failed to get frame from camera streamer")
        
    def startPreview(self):
        """
        Starts the camera stream preview.
        """
        logger.debug("starting preview")
        if self.cameraStreamer.wasRunning:
            self.startTimer()
        else:
            self.cameraStreamer.start()

    def startTimer(self):
        """
        Starts the timer for updating the preview panel.
        """
        logger.debug("starting timer")
        self.timer.start(100)

    def stopPreview(self):
        """
        Stops the camera stream preview.
        """
        logger.debug("stopping preview")
        self.timer.stop()
        self.freezePreview()
        self.previewStopped.emit()
    
    def emptyPreview(self):
        """
        Clears the preview panel.
        """
        logger.debug("emptying preview")
        self.setPixmap(QPixmap())

    def freezePreview(self):
        """
        Freezes the preview panel with a blurred image of the last frame.
        """
        if self.frame is not None:
            logger.debug("freezing preview")
            greyImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            blurImage = cv2.GaussianBlur(greyImage, (55, 55), 0)
            h, w = blurImage.shape
            bytesPerLine = w
            qt_image = QImage(blurImage.data, w, h, bytesPerLine, QImage.Format.Format_Grayscale8)
            pixmap = QPixmap.fromImage(qt_image)
            self.setPixmap(pixmap)
        else:
            self.emptyPreview()
        
    def setCameraData(self, cameraData):
        """
        Sets the camera data for the camera stream.
        """
        logger.info("setting camera data: %s", cameraData)
        self.cameraData = cameraData
        self.cameraStreamer.setCameraData(self.cameraData)
        self.imageCapture.setCameraData(self.cameraData)

    def captureImage(self, config):
        """
        Captures an image from the camera stream.
        """
        logger.debug("capturing image")
        if self.cameraStreamer.wasRunning:
            logger.debug("camera streamer was running, stopping it")
            self.imageCapture.finished.connect(self.startPreview)
            self.cameraStreamer.quit()
            self.freezePreview()
        self.imageCapture.setUpConfig(config)
        self.imageCapture.start()
        self.capturedImage.emit(config['--image_name'])

    def close(self):
        """
        Closes the PreviewPanel widget.
        """
        logger.debug("quitting preview panel")
        self.cameraStreamer.quit()
        self.timer.stop()
        self.emptyPreview()
        super().close()

    def _setPanelImage(self):
        """
        Sets the preview panel image with the latest frame from the camera stream.
        """
        logger.debug("updating preview panel with new frame")
        rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w            
        qt_image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.setPixmap(pixmap)

