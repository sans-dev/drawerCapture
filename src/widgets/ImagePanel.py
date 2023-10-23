import logging
import logging.config
import rawpy
from PyQt6.QtWidgets import QLabel, QFileDialog
from PyQt6.QtGui import QImage, QPixmap
import cv2

from processors import AdaptiveHE

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class ImagePanel(QLabel):
    FORMATS = {
        4/3 : (int(1280),int(960)),
        16/9 : (int(1280),int(790)),
        3/2 : (int(1440),int(960))
    }

    def __init__(self, emitter):
        logger.debug("initializing preview panel")
        super().__init__()
        self.cameraData = None
        self.image = None
        self.emitter = emitter
        self.initUI()
        self.connectSignals()

    
    def initUI(self):
        logger.debug("initializing preview panel UI")
        # set the size of the preview panel
        self.panelSize = (int(1280), int(960))
        self.setFixedSize(self.panelSize[0], self.panelSize[1])
        self.setFrameStyle(1)
        self.setLineWidth(1)
    
    def connectSignals(self):
        logger.debug("connecting signals for preview panel")
        self.emitter.processed.connect(self._updatePanel)

    def emptyPreview(self):
        logger.debug("emptying preview")
        self.setPixmap(QPixmap())

    def close(self):
        logger.debug("quitting preview panel")
        self.emptyPreview()
        super().close()

    def loadImage(self, image_dir):
        logger.info("updating image panel with new image: %s", image_dir)
        self._loadImage(image_dir)
        h, w, ch = self.image.shape
        # scale to fit the preview panel
        self._setPanelFormat(w,h)
        h_scale = h / self.height()
        w_scale = w / self.width()
        self.image = cv2.resize(self.image, (int(w / w_scale), int(h / h_scale)))
        self._updatePanel()

    def processImage(self, processor : str):
        logger.info("processing image with: %s", processor)
        if processor == "adaptive_he":
            processor = AdaptiveHE(self.emitter)
        self.image = processor.process(self.image)
        self._updatePanel()

    def _setPanelFormat(self, img_width, img_height):
        img_format = img_width / img_height 
        self.panelSize = ImagePanel.FORMATS[img_format]
        self.setFixedSize(self.panelSize[0], self.panelSize[1])

    def _updatePanel(self):
        h, w, ch = self.image.shape
        bytesPerLine = ch * w   
        qt_image = QImage(self.image.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.setPixmap(pixmap)

    def _loadImage(self,image_dir):
        # check the format and choose the appropriate loading method
        # for raw images, use rawpy. For jpeg, use cv2
        logger.debug("loading image: %s", image_dir)
        if not image_dir.endswith(".jpeg"):
            with rawpy.imread(image_dir) as raw:
                self.image = raw.postprocess()
        else:
            self.image = cv2.imread(image_dir)

    def saveImage(self):
        logger.info("saving image")
        # open a file dialog to save the image
        options = QFileDialog.Options()
        options |= QFileDialog.Option.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self,"Save Image", "","JPEG (*.jpeg)", options=options)
        if file_name:
            cv2.imwrite(file_name, self.image)
            logger.debug("image saved to: %s", file_name)
        
        