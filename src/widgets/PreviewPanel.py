import logging
import logging.config

from PyQt6.QtWidgets import QSizePolicy, QFrame, QMessageBox
from PyQt6.QtWidgets import QLabel, QGridLayout, QVBoxLayout
from PyQt6.QtCore import QTimer, pyqtSignal, Qt, QThreadPool, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np

from src.threads.CameraStreamer import CameraStreamer
from src.threads.VideoCaptureDevice import VideoCaptureDevice
from src.threads.ImageCapture import ImageCapture
from src.widgets.SpinnerWidget import LoadingSpinner

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class Panel(QLabel):
    def __init__(self, resolution):
        super().__init__()
        self.resolution = resolution
        self.frame = None
        self.setMaximumSize(self.resolution[0], self.resolution[1])
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setFrameShape(QFrame.Shape.WinPanel)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # initilize with black image
        frame = np.zeros((resolution[1], resolution[0], 3)).astype(np.uint8)
        self.set_image(frame)

    def set_image(self, frame):
        """
        Sets the preview panel image with the latest frame from the camera stream.
        """
        logger.debug("updating preview panel with new frame")
        self.frame = cv2.resize(frame, self.resolution, interpolation=cv2.INTER_AREA)
        rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
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
    stop_stream_signal = pyqtSignal()
    image_captured = pyqtSignal(str)

    def __init__(self, fs, panel_res):
        """
        Initializes the PreviewPanel widget.
        """
        logger.debug("initializing preview panel")
        super().__init__()
        self.label = QLabel("No camera connected")
        self.panel = Panel(panel_res)
        self.camera_data = None
        self.frame = None
        self.panel_res = panel_res
        self.fs = fs
        self.is_streaming = False
        self.img_dir = ''
        self.thread_pool = QThreadPool()
        
        self.init_ui()
        self.connect_signals()
        

    def init_ui(self):
        """
        Initializes the user interface of the PreviewPanel widget.
        """
        logger.debug("initializing preview panel UI")
        self.loadingSpinner = LoadingSpinner()
        layout = QVBoxLayout()
        self.label.setMaximumHeight(20)
        spinner_layout = QGridLayout()
        spinner_layout.addWidget(self.panel, 0, 0)
        spinner_layout.addWidget(self.loadingSpinner, 0, 0)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addLayout(spinner_layout)
        self.setLayout(layout)
    
    def connect_signals(self):
        """
        Connects the signals of the PreviewPanel widget.
        """
        logger.debug("connecting signals for preview panel")
        # self.timer.timeout.connect(self.update_panel)

    def set_text(self, text):
        self.label.setText(text)

    def connect_video_device(self, device_dir):
        logger.info("connecting to video device dir")
        self.video_device = VideoCaptureDevice(self.fs, device_dir)
        self.video_device.signals.send_frame.connect(self.update_panel)
        self.video_device.signals.device_open.connect(self.loadingSpinner.stop)
        self.video_device.signals.device_open.connect(self.loadingSpinner.hide)
        self.stop_stream_signal.connect(self.video_device.quit)
        self.thread_pool.start(self.video_device)

    def start_stream(self):
        """
        Starts the camera stream preview.
        """
        logger.debug("starting preview")
        self.camera_streamer = CameraStreamer(self.fs)
        self.camera_streamer.set_camera_data(self.model, self.port)
        self.camera_streamer.signals.building_stream.connect(self.loadingSpinner.start)
        self.camera_streamer.signals.building_stream.connect(self.loadingSpinner.show)
        self.camera_streamer.signals.stream_enabled.connect(self.connect_video_device)
        self.stop_stream_signal.connect(self.camera_streamer.stop_running)
        self.thread_pool.start(self.camera_streamer)

    def restart_stream(self):
        if self.is_streaming:
            self.start_stream()
        
    def stop_stream(self):
        self.stop_stream_signal.emit()
        self.is_streaming = False
        self.panel.freeze()

    def capture_image(self):
        """
        Captures an image from the camera stream.
        """
        self.image_capture = ImageCapture()
        self.image_capture.set_camera_data(self.model, self.port)
        self.image_capture.set_image_dir(self.img_dir)
        self.image_capture.signals.started.connect(self.loadingSpinner.start)
        self.image_capture.signals.started.connect(self.loadingSpinner.show)
        self.image_capture.signals.finished.connect(self.loadingSpinner.stop)
        self.image_capture.signals.finished.connect(self.loadingSpinner.hide)
        self.image_capture.signals.finished.connect(self.restart_stream)
        self.image_capture.signals.img_captured.connect(self.on_image_captured)
        self.panel.freeze()
        print(self.thread_pool.activeThreadCount())
        while self.thread_pool.activeThreadCount() > 0:
            self.stop_stream_signal.emit()
        print(self.thread_pool.activeThreadCount())
        self.thread_pool.setMaxThreadCount(1)
        self.thread_pool.start(self.image_capture)

    def on_image_captured(self, img_dir):
        try:
            img = cv2.imread(img_dir)
            self.panel.set_image(img)
            self.image_captured.emit(img_dir)
        except FileNotFoundError as fne:
            QMessageBox.warning(self, "Could not load tmp image capture", f"{fne}")

    def set_image_dir(self, project_info):
        # when project is loaded, set this dir
        self.img_dir = project_info['Project Info']['project_dir'] + "/.project/.tmp_cap"

    def set_camera_data(self, model=None, port=None):
        """
        Sets the camera data for the camera stream.
        """
        # Log the setting of camera data
        logger.info(f"setting camera data: {model=}, {port=}")

        # Set instance attributes
        self.model = model
        self.port = port
        self.label.setText(f"{self.model} connected at port: {self.port}")

    def set_is_capture_ready(self, is_ready):
        self.is_capture_ready = is_ready

    @pyqtSlot(tuple)
    def update_panel(self, data):
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

    def close(self):
        """
        Closes the PreviewPanel widget.
        """
        logger.debug("quitting preview panel")
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
        window.set_camera_data('Sony Alpha-A5100 (Control)', 'usb:001,018')
        window.start_stream()
    app.processEvents()
    window.show()
    sys.exit(app.exec())
