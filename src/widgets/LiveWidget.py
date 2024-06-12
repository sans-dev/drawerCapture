from datetime import datetime

import logging
import logging.config

from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QVBoxLayout, QLabel, QMessageBox, QStackedLayout, QHBoxLayout, QStackedWidget, QButtonGroup, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal

from src.widgets.SelectCameraListWidget import SelectCameraListWidget
from src.widgets.PreviewPanel import PreviewPanel
from src.widgets.ImageWidget import ImageWidget
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class PanelButton(QPushButton):
    def __init__(self, name, height, width_range, isEnable=False):
        super().__init__(name)
        self.setMaximumWidth(width_range[1])
        self.setMinimumWidth(width_range[0])
        self.setFixedHeight(height)
        self.setEnabled(isEnable)


class LivePanel(QWidget):
    def __init__(self, fs, panel_res):
        super().__init__()
        self.panel = PreviewPanel(fs, panel_res)
        self.model = None
        self.port = None
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        layout = QVBoxLayout()
        button_width_range = (300, 600)
        button_height = 32
        # add select camera button
        self.selectCameraButton = PanelButton("Select Camera", button_height, button_width_range, True)
        # add capture image button
        self.captureImageButton = PanelButton("Capture Image", button_height, button_width_range)
        # add a disabled button to start live preview
        self.startLivePreviewButton = PanelButton("Start Live Preview", button_height, button_width_range)
        # add a stop preview button at the bottom of the preview panel
        self.stopLivePreviewButton = PanelButton("Stop Live Preview", button_height, button_width_range)
        # add an close button
        self.closeButton = PanelButton("Close", button_height, button_width_range, True)

        # Arrange buttons in a vertical layout
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.selectCameraButton, alignment=Qt.AlignmentFlag.AlignHCenter)
        button_layout.addWidget(self.captureImageButton, alignment=Qt.AlignmentFlag.AlignHCenter)
        button_layout.addWidget(self.startLivePreviewButton, alignment=Qt.AlignmentFlag.AlignHCenter)
        button_layout.addWidget(self.stopLivePreviewButton, alignment=Qt.AlignmentFlag.AlignHCenter)
        button_layout.addWidget(self.closeButton, alignment=Qt.AlignmentFlag.AlignHCenter)
        button_layout.setSpacing(6)
        spacer = QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        layout.addWidget(self.panel)
        layout.addLayout(button_layout)
        layout.addItem(spacer)
        self.setLayout(layout)

    def connect_signals(self):
        self.startLivePreviewButton.clicked.connect(self.panel.startPreview)

    def enable_capture_buttons(self):
        self.captureImageButton.setEnabled(True)
        self.startLivePreviewButton.setEnabled(True)
        self.stopLivePreviewButton.setEnabled(True)

    def set_camera_data(self, camera_data):
        self.model = camera_data.split('usb')[0].strip()
        self.port = f"usb{camera_data.split('usb')[-1].strip()}"
        self.panel.setCameraData(self.model, self.port)

class LiveWidget(QWidget):
    changed = pyqtSignal(str)

    def __init__(self, db_adapter, taxonomomy, geo_data_dir, fs, panel_res):
        logger.debug("initializing live widget")
        super().__init__()
        self.db_apater = db_adapter
        self.image_widget = ImageWidget(
            db_adapter=db_adapter, taxonomy=taxonomomy, geo_data_dir=geo_data_dir)
        self.panel = LivePanel(fs, panel_res)
        self.camera_fetcher = SelectCameraListWidget()

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        logger.debug("initializing live widget UI")

        self.setWindowTitle("Capture Mode")

        self._layout = QStackedLayout()
        self._layout.addWidget(self.panel)
        self._layout.addWidget(self.camera_fetcher)
        self._layout.addWidget(self.image_widget)
        self.setLayout(self._layout)

    def connect_signals(self):
        logger.debug("connecting signals for live widget")
        self.panel.selectCameraButton.clicked.connect(self.show_camera_fetcher)
        self.camera_fetcher.exitButton.clicked.connect(self.show_panel)
        self.camera_fetcher.confirmButton.clicked.connect(self.show_panel)
        self.camera_fetcher.confirmButton.clicked.connect(self.panel.enable_capture_buttons)
        self.camera_fetcher.selectedCameraChanged.connect(self.panel.set_camera_data)
        self.camera_fetcher.selectedCameraChanged.connect(self.panel.panel.set_text)
 
    def show_panel(self):
        self._layout.setCurrentWidget(self.panel)

    def show_camera_fetcher(self):
        self._layout.setCurrentWidget(self.camera_fetcher)

    def show_image_widget(self):
        pass

    def show_error_dialog(self, msg):
        QMessageBox.critical(self, "Error", msg)

    def buildConfig(self, config={}): # TODO: move to config builder/own class/document holding the configuration
        logger.debug("building config")
        config['--image_name'] = datetime.now().isoformat().replace(':','_').replace('.','-')
        config['--image_dir'] = 'data/captures/' 
        return config
    
    def captureImage(self):
        logger.debug("capturing image")
        config = self.buildConfig()
        self.panel.captureImage(config)

    def imageCaptured(self, imageName):
        logger.debug("image captured")
        self.image_widget.setImage(imageName)

    def startPreview(self):
        logger.debug("starting preview")
        self.panel.startPreview()

    def stopPreview(self):
        logger.debug("stopping preview")
        self.panel.stopPreview()

    def closeLiveMode(self):
        logger.debug("closing live mode")
        self.close()
        self.image_widget.close()
        self.changed.emit("project")


if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser
    from PyQt6.QtWidgets import QApplication
    from src.db.DB import DBAdapter, DummyDB
    from src.utils.searching import init_taxonomy
    from src.widgets.ImageWidget import ImageWidget
    from src.configs.DataCollection import *

    parser = ArgumentParser()
    parser.add_argument('--taxonomy', choices=['test', 'prod'])
    parser.add_argument('--geo-data', choices=['level-0', 'level-1'])
    args = parser.parse_args()
    taxonomy = init_taxonomy(TAXONOMY[args.taxonomy])
    geo_data_dir = GEO[args.geo_data]
    app = QApplication(sys.argv)
    db_adapter = DBAdapter(DummyDB())

    window = LiveWidget(db_adapter, taxonomy, geo_data_dir, fs=1, panel_res=(1024,780))
    window.show()
    sys.exit(app.exec())