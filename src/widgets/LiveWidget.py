from datetime import datetime

import logging
import logging.config

from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QVBoxLayout, QLabel, QMessageBox, QStackedLayout, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt, pyqtSignal

from src.widgets.SelectCameraListWidget import SelectCameraListWidget
from src.widgets.PreviewPanel import PreviewPanel
from src.widgets.SpinnerWidget import LoadingSpinner 
from src.widgets.ImageWidget import ImageWidget
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class LiveWidget(QWidget):
    """
    A widget for live camera preview and image capture.

    Signals:
    changed(str): emitted when the selected camera is changed.

    Methods:
    __init__(self, imagePanel): initializes the widget.
    initUI(self): initializes the user interface.
    connectSignals(self): connects signals to slots.
    enableStartLivePreviewButton(self): enables the start live preview button.
    """
class LiveWidget(QWidget):
    changed = pyqtSignal(str)

    def __init__(self, db_adapter, taxonomomy, geo_data_dir, fs):
        logger.debug("initializing live widget")
        super().__init__()
        self.db_apater = db_adapter
        self.fs = fs
        self.imageWidget = ImageWidget(
            db_adapter=db_adapter, taxonomy=taxonomomy, geo_data_dir=geo_data_dir)
        self.initUI()
        self.connectSignals()

    def initUI(self):
        logger.debug("initializing live widget UI")

        self.setWindowTitle("Live Mode")

        layout = QStackedWidget()
        live_layout = QGridLayout()
        button_layout = QHBoxLayout()
        
        # add select camera button
        self.selectCameraButton = QPushButton("Select Camera")
        self.selectCameraButton.clicked.connect(self.selectCamera)

        # add capture image button
        self.captureImageButton = QPushButton("Capture Image")
        self.captureImageButton.clicked.connect(self.captureImage)
        self.captureImageButton.setEnabled(False)

        # add a disabled button to start live preview
        self.startLivePreviewButton = QPushButton("Start Live Preview")
        self.startLivePreviewButton.setEnabled(False)
        self.startLivePreviewButton.clicked.connect(self.startPreview)
        self.startLivePreviewButton.show()

        # add a stop preview button at the bottom of the preview panel
        self.stopLivePreviewButton = QPushButton("Stop Live Preview")
        self.stopLivePreviewButton.clicked.connect(self.stopPreview)
        self.stopLivePreviewButton.setEnabled(False)
        
        # add an close button
        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self.closeLiveMode)

        button_layout.addWidget(self.selectCameraButton)
        button_layout.addWidget(self.captureImageButton)
        button_layout.addWidget(self.startLivePreviewButton)
        button_layout.addWidget(self.stopLivePreviewButton)
        button_layout.addWidget(self.closeButton)

        # add camera selection list widget
        self.selectCameraListWidget = SelectCameraListWidget()
        self.selectCameraListWidget.hide()

        # add preview panel
        self.previewPanel = PreviewPanel(fs=self.fs)
        self.previewPanelLabel = QLabel("Live Preview")
        self.previewPanelLabel.setStyleSheet('font-size: 20px;')
        self.panelLayout = QVBoxLayout()
        self.panelLayout.addWidget(self.previewPanelLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.panelLayout.addWidget(self.previewPanel)
        
        # arange widgets in grid layout
        live_layout.addWidget(self.selectCameraListWidget, 0, 0) 
        live_layout.addLayout(self.panelLayout, 0, 0)
        live_layout.addLayout(button_layout, 1,0,1,1, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.imageWidget)
        layout.addWidget(self.selectCameraListWidget)
        self.setLayout(layout)

    def connectSignals(self):
        logger.debug("connecting signals for live widget")
        # self.selectCameraListWidget.closed.connect(self._showPanelWidgets)
        self.selectCameraListWidget.confirmButton.clicked.connect(self._showPanelWidgets)
        self.selectCameraListWidget.confirmButton.clicked.connect(self._updatePreviewLabel)

        self.selectCameraListWidget.confirmButton.clicked.connect(self.enableSelectCameraButton)
        self.selectCameraListWidget.confirmButton.clicked.connect(self.enableStartLivePreviewButton)

        self.selectCameraButton.clicked.connect(self.selectCameraListWidget.show)

        self.selectCameraListWidget.selectedCameraChanged.connect(self.previewPanel.setCameraData)
        self.selectCameraListWidget.selectedCameraChanged.connect(self.enableCaptureImageButton)

        self.previewPanel.imageCapture.finished.connect(self._enableAllButtons)
        self.previewPanel.imageCapture.started.connect(self._disableAllButtons)

        self.previewPanel.imageCapture.imageCaptured.connect(self.imageCaptured)
        self.previewPanel.imageCapture.failed_signal.connect(self.show_error_dialog)

    def show_error_dialog(self, msg):
        QMessageBox.critical(self, "Error", msg)

    def enableStartLivePreviewButton(self):
        logger.debug("enabling start live preview button")
        self.startLivePreviewButton.setEnabled(True)

    def enableSelectCameraButton(self):
        logger.debug("enabling select camera button")
        self.selectCameraButton.setEnabled(True)

    def enableCaptureImageButton(self):
        logger.debug("enabling capture image button")
        self.captureImageButton.setEnabled(True)

    def selectCamera(self):
        logger.debug("selecting camera")
        self._hidePanelWidgets()
        if not self.selectCameraListWidget.isRefreshed:
            logger.debug("refreshing camera list")
            self.selectCameraListWidget.refreshButtonClicked()
    
    def buildConfig(self, config={}): # TODO: move to config builder/own class/document holding the configuration
        logger.debug("building config")
        config['--image_name'] = datetime.now().isoformat().replace(':','_').replace('.','-')
        config['--image_dir'] = 'data/captures/' 
        return config
    
    def captureImage(self):
        logger.debug("capturing image")
        config = self.buildConfig()
        self.previewPanel.captureImage(config)

    def imageCaptured(self, imageName):
        logger.debug("image captured")
        self.imageWidget.setImage(imageName)

    def startPreview(self):
        logger.debug("starting preview")
        self.selectCameraListWidget.setEnabled(False)
        self.startLivePreviewButton.setEnabled(False)
        self.stopLivePreviewButton.setEnabled(True)
        self.previewPanel.startPreview()

    def stopPreview(self):
        logger.debug("stopping preview")
        self.selectCameraButton.setEnabled(True)
        self.selectCameraListWidget.setEnabled(True)
        self.startLivePreviewButton.setEnabled(True)
        self.stopLivePreviewButton.setEnabled(False)
        self.previewPanel.stopPreview()

    def closeLiveMode(self):
        logger.debug("closing live mode")
        self.close()
        self.imageWidget.close()
        self.changed.emit("project")

    def _hidePanelWidgets(self):
        logger.debug("hiding panel widgets")
        self.previewPanel.hide()
        self.previewPanelLabel.hide()
        self.selectCameraButton.hide()
        self.startLivePreviewButton.hide()
        self.stopLivePreviewButton.hide()
        self.captureImageButton.hide()
        self.closeButton.hide()
    
    def _showPanelWidgets(self):
        logger.debug("showing panel widgets")
        self.previewPanel.show()
        self.previewPanelLabel.show()
        self.selectCameraButton.show()
        self.startLivePreviewButton.show()
        self.captureImageButton.show()
        self.closeButton.show()

    def _updatePreviewLabel(self):
        logger.debug("updating preview label")
        self.previewPanelLabel.setText(f"Live Preview ({self.previewPanel.cameraStreamer.getCameraDataAsString()})")

    def _disableAllButtons(self):
        self.selectCameraButton.setEnabled(False)
        self.startLivePreviewButton.setEnabled(False)
        self.captureImageButton.setEnabled(False)
        self.closeButton.setEnabled(False)
        self.stopLivePreviewButton.setEnabled(False)

    def _enableAllButtons(self):
        self.selectCameraButton.setEnabled(True)
        self.startLivePreviewButton.setEnabled(True)
        self.captureImageButton.setEnabled(True)
        self.closeButton.setEnabled(True)
        self.stopLivePreviewButton.setEnabled(True)
        
        
        
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

    window = LiveWidget(db_adapter, taxonomy, geo_data_dir, fs=1)
    window.show()
    sys.exit(app.exec())