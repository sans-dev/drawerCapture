import logging
import logging.config
import rawpy
from PyQt6.QtWidgets import QLabel, QFileDialog
from PyQt6.QtGui import QImage, QPixmap
import cv2

from processors import AdaptiveHE

logging.config.fileConfig('configs/logging.conf',
                          disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class ImagePanel(QLabel):
    """
    A widget that displays an image and allows for image processing and saving.
    """
    FORMATS = {
        1.3: (int(1280), int(960)),
        1.7: (int(1280), int(790)),
        1.5: (int(1440), int(960))
    }

    def __init__(self, emitter):
        """
        Initializes the ImagePanel widget.

        Args:
            emitter: An object that emits signals.
        """
        logger.debug("initializing preview panel")
        super().__init__()
        self.cameraData = None
        self.image = None
        self.emitter = emitter
        self.initUI()
        self.connectSignals()

    def initUI(self):
        """
        Initializes the user interface for the ImagePanel widget.
        """
        logger.debug("initializing preview panel UI")
        # set the size of the preview panel
        self.panelSize = (int(1280), int(960))
        self.setFixedSize(self.panelSize[0], self.panelSize[1])
        self.setFrameStyle(1)
        self.setLineWidth(1)

    def connectSignals(self):
        """
        Connects signals for the ImagePanel widget.
        """
        logger.debug("connecting signals for preview panel")
        self.emitter.processed.connect(self._updatePanel)

    def emptyPreview(self):
        """
        Clears the preview panel.
        """
        logger.debug("emptying preview")
        self.setPixmap(QPixmap())

    def close(self):
        """
        Closes the ImagePanel widget.
        """
        logger.debug("quitting preview panel")
        self.emptyPreview()
        super().close()

    def loadImage(self, image_dir):
        """
        Loads an image from a file and displays it in the ImagePanel widget.

        Args:
            image_dir: The path to the image file.
        """
        logger.info("updating image panel with new image: %s", image_dir)
        self._loadImage(image_dir)
        h, w, ch = self.image.shape
        # scale to fit the preview panel
        self._setPanelFormat(w, h)
        h_scale = h / self.height()
        w_scale = w / self.width()
        self.image = cv2.resize(
            self.image, (int(w / w_scale), int(h / h_scale)))
        self._updatePanel()

    def processImage(self, processor: str):
        """
        Processes the current image using the specified image processing algorithm.

        Args:
            processor: The name of the image processing algorithm to use.
        """
        logger.info("processing image with: %s", processor)
        if processor == "adaptive_he":
            processor = AdaptiveHE(self.emitter)
        self.image = processor.process(self.image)
        self._updatePanel()

    def _setPanelFormat(self, img_width, img_height):
        """
        Sets the size of the ImagePanel widget based on the aspect ratio of the current image.

        Args:
            img_width: The width of the current image.
            img_height: The height of the current image.
        """
        img_format = img_width / img_height
        img_format = int(img_format) + int(10*(img_format - int(img_format)))/10
        self.panelSize = ImagePanel.FORMATS[img_format]
        self.setFixedSize(self.panelSize[0], self.panelSize[1])

    def _updatePanel(self):
        """
        Updates the ImagePanel widget with the current image.
        """
        h, w, ch = self.image.shape
        bytesPerLine = ch * w
        qt_image = QImage(self.image.data, w, h, bytesPerLine,
                          QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.setPixmap(pixmap)

    def _loadImage(self, image_dir):
        """
        Loads an image from a file.

        Args:
            image_dir: The path to the image file.
        """
        # check the format and choose the appropriate loading method
        # for raw images, use rawpy. For jpeg, use cv2
        logger.debug("loading image: %s", image_dir)
        if not image_dir.endswith(".jpeg"):
            with rawpy.imread(image_dir) as raw:
                self.image = raw.postprocess()
        else:
            self.image = cv2.imread(image_dir)
            print(self.image)

    def saveImage(self):
        """
        Saves the current image to a file.
        """
        logger.info("saving image")
        # open a file dialog to save the image
        options = QFileDialog.Options()
        options |= QFileDialog.Option.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "JPEG (*.jpeg)", options=options)
        if file_name:
            cv2.imwrite(file_name, self.image)
            logger.debug("image saved to: %s", file_name)
