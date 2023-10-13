import logging
import logging.config

from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QImage, QPixmap
import cv2

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class ImagePanel(QLabel):

    def __init__(self):
        logger.debug("initializing preview panel")
        super().__init__()
        self.cameraData = None
        self.image = None
        self.initUI()
        self.connectSignals()
    
    def initUI(self):
        logger.debug("initializing preview panel UI")
        # set the size of the preview panel
        panel_size = (int(1280), int(960))
        self.setFixedSize(panel_size[0], panel_size[1])
        self.setFrameStyle(1)
        self.setLineWidth(1)
    
    def connectSignals(self):
        pass

    def emptyPreview(self):
        logger.debug("emptying preview")
        self.setPixmap(QPixmap())

    def close(self):
        logger.debug("quitting preview panel")
        self.emptyPreview()
        super().close()

    def setImage(self, image_dir):
        logger.info("updating image panel with new image: %s", image_dir)
        image = cv2.imread(image_dir)
        h, w, ch = image.shape
        # scale to fit the preview panel
        h_scale = h / self.height()
        w_scale = w / self.width()
        image = cv2.resize(image, (int(w / w_scale), int(h / h_scale)))
        h, w, ch = image.shape
        bytesPerLine = ch * w   
        qt_image = QImage(image.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.setPixmap(pixmap)