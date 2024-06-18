import logging
import logging.config

from PyQt6.QtWidgets import QLabel, QGridLayout, QVBoxLayout
from PyQt6.QtCore import QTimer, pyqtSignal, Qt, QThread
from PyQt6.QtGui import QImage, QPixmap
import cv2


from src.threads.CameraStreamer import CameraStreamer
from src.threads.ImageCapture import ImageCapture
from src.widgets.SpinnerWidget import LoadingSpinner

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class Panel(QLabel):
    def __init__(self, resolution):
        super().__init__()
        self.resolution = resolution
        self.frame = None
        self.setFixedSize(self.resolution[0], self.resolution[1])
        self.setFrameStyle(1)
        self.setLineWidth(1)

    def set_image(self, frame):
        """
        Sets the preview panel image with the latest frame from the camera stream.
        """
        logger.debug("updating preview panel with new frame")
        self.frame = frame
        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w            
        qt_image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.setPixmap(pixmap)

    def clear_image(self):
        """
        Clears the preview panel.
        """
        logger.debug("emptying preview")
        self.setPixmap(QPixmap())

    def freeze(self):
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
            self.clear_image()

class PreviewPanel(QLabel):
    """
    A widget that displays a live preview of the camera stream and allows capturing images.
    """
    previewStopped = pyqtSignal()

    def __init__(self, fs, panel_res):
        """
        Initializes the PreviewPanel widget.
        """
        logger.debug("initializing preview panel")
        super().__init__()
        self.label = QLabel("No camera selected")
        self.panel = Panel(panel_res)
        self.cameraStreamer = CameraStreamer(fs=fs)
        self.imageCapture = ImageCapture()
        self.cameraData = None
        self.frame = None
        self.panel_res = panel_res
        self.fs = fs
        self.capture_thread = QThread() 
        self.stream_thread = QThread()
        self.imageCapture.moveToThread(self.capture_thread)
        self.capture_thread.started.connect(self.imageCapture.run)
        self.capture_thread.finished.connect(self.imageCapture.quit)
        self.cameraStreamer.moveToThread(self.stream_thread)
        self.stream_thread.started.connect(self.cameraStreamer.run)
        # self.stream_thread.finished.connect(self.cameraStreamer.deleteLater)
        self.stream_thread.finished.connect(self.cameraStreamer.quit)
        self.initUI()
        self.connectSignals()


    def initUI(self):
        """
        Initializes the user interface of the PreviewPanel widget.
        """
        logger.debug("initializing preview panel UI")
        self.loadingSpinner = LoadingSpinner()
        layout = QVBoxLayout()
        self.label.setMaximumHeight(20)
        spinner_layout = QGridLayout()
        spinner_layout.addWidget(self.panel, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
        spinner_layout.addWidget(self.loadingSpinner, 0, 0)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addLayout(spinner_layout)
        self.setLayout(layout)
        self.setMaximumHeight(self.panel_res[0])
    
    def connectSignals(self):
        """
        Connects the signals of the PreviewPanel widget.
        """
        logger.debug("connecting signals for preview panel")
        
        self.cameraStreamer.buildingStream.connect(self.loadingSpinner.start)
        self.cameraStreamer.buildingStream.connect(self.loadingSpinner.show)
        self.cameraStreamer.streamRunning.connect(self.loadingSpinner.stop)
        self.cameraStreamer.streamRunning.connect(self.loadingSpinner.hide)

        self.capture_thread.started.connect(self.loadingSpinner.start)
        self.capture_thread.started.connect(self.loadingSpinner.show)
        self.capture_thread.finished.connect(self.loadingSpinner.stop)
        self.capture_thread.finished.connect(self.loadingSpinner.hide)

        self.previewStopped.connect(self.loadingSpinner.stop)
        self.previewStopped.connect(self.loadingSpinner.hide)

    def set_text(self, text):
        self.label.setText(text)

    def updatePreview(self, data):
        """
        Updates the preview panel with the latest frame from the camera stream.
        """
        ret, self.frame = data
        if ret:
            try:
                self.panel.set_image(self.frame)
            except Exception as e:
                logger.exception("failed to update preview panel with new frame: %s", e)
        else:
            logger.error("failed to get frame from camera streamer")
        
    def startPreview(self):
        """
        Starts the camera stream preview.
        """
        self.cameraStreamer.frame_ready.connect(self.updatePreview)
        logger.debug("starting preview")
        self.stream_thread.start()

    def stop_preview(self):   
        if self.stream_thread.isRunning():
            self.cameraStreamer.frame_ready.disconnect(self.updatePreview)
            self.stream_thread.quit()
        self.panel.clear_image()
    
    def pause_preview(self):
        """
        Stops the camera stream preview.
        """
        logger.debug("stopping preview")
        self.cameraStreamer.frame_ready.disconnect(self.updatePreview)
        self.panel.freeze()
        self.previewStopped.emit()
        
    def setCameraData(self, model, port):
        """
        Sets the camera data for the camera stream.
        """
        logger.info(f"setting camera data: {model=}, {port=}")
        self.model = model
        self.port = port
        self.cameraStreamer.setCameraData(model, port)
        self.imageCapture.setCameraData(model, port)

    def captureImage(self):
        """
        Captures an image from the camera stream.
        """
        logger.debug("capturing image")
        self.capture_thread.start()
        if self.stream_thread.isRunning():
            self.pause_preview()

    def close(self):
        """
        Closes the PreviewPanel widget.
        """
        logger.debug("quitting preview panel")
        self.stream_thread.quit()
        self.capture_thread.quit()
        self.panel.clear_image()
        super().close()



if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--preview', action='store_true')
    args = parser.parse_args()
    app = QApplication(sys.argv)
    window = PreviewPanel(fs=10, panel_res= (1024, 780))
    if args.preview:
        window.setCameraData('Sony Alpha-A5100 (Control)', 'usb:001,018')
        window.startPreview()
    app.processEvents()
    window.show()
    sys.exit(app.exec())
