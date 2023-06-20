import logging
import logging.config

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2

from threads import CameraStreamer, ImageCapture

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class PreviewPanel(QLabel):
    def __init__(self):
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
        logger.debug("initializing preview panel UI")
        # set the size of the preview panel
        panel_size = (int(1024), int(780))
        self.setFixedSize(panel_size[0], panel_size[1])
        self.setFrameStyle(1)
        self.setLineWidth(1)
    
    def connectSignals(self):
        logger.debug("connecting signals for preview panel")
        self.timer.timeout.connect(self.updatePreview)
        self.cameraStreamer.streamStopped.connect(self.timer.stop)
        self.cameraStreamer.videoCapture.deviceOpen.connect(self.startTimer)

    def updatePreview(self):
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
        logger.debug("starting preview")
        self.cameraStreamer.start()

    def startTimer(self):
        logger.debug("starting timer")
        self.timer.start(100)

    def stopPreview(self):
        logger.debug("stopping preview")
        self.cameraStreamer.quit()
        self.freezePreview()
    
    def emptyPreview(self):
        logger.debug("emptying preview")
        self.setPixmap(QPixmap())

    def freezePreview(self):
        if self.frame is not None:
            logger.debug("freezing preview")
            greyImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            blurImage = cv2.GaussianBlur(greyImage, (25, 25), 0)
            h, w = blurImage.shape
            bytesPerLine = w
            qt_image = QImage(blurImage.data, w, h, bytesPerLine, QImage.Format.Format_Grayscale8)
            pixmap = QPixmap.fromImage(qt_image)
            self.setPixmap(pixmap)
        else:
            self.emptyPreview()
        
    def setCameraData(self, cameraData):
        logger.info("setting camera data: %s", cameraData)
        self.cameraData = cameraData
        self.cameraStreamer.setCameraData(self.cameraData)
        self.imageCapture.setCameraData(self.cameraData)

    def captureImage(self, config):
        logger.debug("capturing image")
        if self.cameraStreamer.wasRunning:
            logger.debug("camera streamer was running, stopping it")
            self.imageCapture.finished.connect(self.startPreview)
            self.cameraStreamer.quit()
            self.freezePreview()
        self.imageCapture.setUpConfig(config)
        self.imageCapture.start()

    def _setPanelImage(self):
        logger.debug("updating preview panel with new frame")
        rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w            
        qt_image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.setPixmap(pixmap)

