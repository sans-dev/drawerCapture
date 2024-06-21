import logging
import logging.config

from PyQt6.QtWidgets import QLabel, QGridLayout, QVBoxLayout
from PyQt6.QtCore import QTimer, pyqtSignal, Qt, QThreadPool
from PyQt6.QtGui import QImage, QPixmap
import cv2


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
    stop_stream_signal = pyqtSignal()

    def __init__(self, fs, panel_res):
        """
        Initializes the PreviewPanel widget.
        """
        logger.debug("initializing preview panel")
        super().__init__()
        self.label = QLabel("No camera selected")
        self.panel = Panel(panel_res)
        self.camera_streamer = CameraStreamer(fs=fs)
        self.image_capture = ImageCapture()
        self.video_device = VideoCaptureDevice(fs=fs)
        self.image_capture.set_image_dir('data/captures')
        self.camera_data = None
        self.frame = None
        self.panel_res = panel_res
        self.fs = fs
        self.is_streaming = False
        self.timer = QTimer()
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(2)
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
        spinner_layout.addWidget(self.panel, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
        spinner_layout.addWidget(self.loadingSpinner, 0, 0)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addLayout(spinner_layout)
        self.setLayout(layout)
        self.setMaximumHeight(self.panel_res[0])
    
    def connect_signals(self):
        """
        Connects the signals of the PreviewPanel widget.
        """
        logger.debug("connecting signals for preview panel")
        self.timer.timeout.connect(self.update_panel)
        self.video_device.signals.device_open.connect(self.update_panel)
        self.camera_streamer.signals.building_stream.connect(self.loadingSpinner.start)
        self.camera_streamer.signals.building_stream.connect(self.loadingSpinner.show)
        self.camera_streamer.signals.stream_enabled.connect(self.connect_video_device)
        self.video_device.signals.device_open.connect(self.start_timer)
        self.video_device.signals.device_open.connect(self.loadingSpinner.stop)
        self.video_device.signals.device_open.connect(self.loadingSpinner.hide)
        # self.image_capture.started.connect(self.loadingSpinner.start)
        # self.image_capture.started.connect(self.loadingSpinner.show)
        # self.image_capture.finished.connect(self.loadingSpinner.stop)
        # self.image_capture.finished.connect(self.loadingSpinner.hide)
        # self.image_capture.is_ready.connect(self.restart_stream)

        self.stop_stream_signal.connect(self.camera_streamer.stop_running)
        self.stop_stream_signal.connect(self.video_device.stop_device)

    def start_timer(self):
        logger.info(f"starting timer with {1000 // self.fs} msec interval")
        self.timer.start(1000 // self.fs)

    def set_text(self, text):
        self.label.setText(text)

    def connect_video_device(self, device_dir):
        self.video_device.set_device_dir(device_dir=device_dir)
        self.thread_pool.start(self.video_device)

    def start_stream(self):
        """
        Starts the camera stream preview.
        """
        
        logger.debug("starting preview")
        self.thread_pool.start(self.camera_streamer)

    def restart_stream(self, is_ready):
        if is_ready and self.is_streaming:
            self.thread_pool.start(self.camera_streamer)

    def stop_stream(self):   
        self.stop_stream_signal.emit()
        self.is_streaming = False

    def capture_image(self):
        """
        Captures an image from the camera stream.
        """
        self.camera_streamer.quit()
        self.thread_pool.start(self.image_capture)

    def set_camera_data(self, model, port):
        """
        Sets the camera data for the camera stream.
        """
        logger.info(f"setting camera data: {model=}, {port=}")
        self.model = model
        self.port = port
        self.camera_streamer.setCameraData(model, port)
        self.image_capture.setCameraData(model, port)

    def set_is_capture_ready(self, is_ready):
        self.is_capture_ready = is_ready

    def update_panel(self):
        """
        Updates the preview panel with the latest frame from the camera stream.
        """
        ret, self.frame = self.video_device.get_frame()
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
