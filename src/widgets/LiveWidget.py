from datetime import datetime

import logging
import logging.config

from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QVBoxLayout, QLabel, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal

from src.widgets.SelectCameraListWidget import SelectCameraListWidget
from src.widgets.PreviewPanel import PreviewPanel
from src.widgets.SpinnerWidget import LoadingSpinner 

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

    def __init__(self, imageWidget):
        logger.debug("initializing live widget")
        super().__init__()
        self.imagePanel = imageWidget
        self.initUI()
        self.connectSignals()

    def initUI(self):
        logger.debug("initializing live widget UI")

        self.setWindowTitle("Live Mode")

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

        # add camera selection list widget
        self.selectCameraListWidget = SelectCameraListWidget()
        self.selectCameraListWidget.hide()

        # add a loading spinner to the preview panel
        self.loadingSpinner = LoadingSpinner()

        # add preview panel
        self.previewPanel = PreviewPanel()
        self.previewPanelLabel = QLabel("Live Preview")
        self.previewPanelLabel.setStyleSheet('font-size: 20px;')
        self.panelLayout = QVBoxLayout()
        self.panelLayout.addWidget(self.previewPanelLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.panelLayout.addWidget(self.previewPanel)

        # add start live preview button and capture image button to a horizontal layout
        self.buttonLayout = QGridLayout()
        self.buttonLayout.addWidget(self.selectCameraButton,0,0,1,2)
        self.buttonLayout.addWidget(self.startLivePreviewButton,0,2,1,2)
        self.buttonLayout.addWidget(self.stopLivePreviewButton,0,4,1,2)
        self.buttonLayout.addWidget(self.captureImageButton,0,6,1,2)
        self.buttonLayout.addWidget(self.closeButton,0,8,1,2)
        
        # arange widgets in grid layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.selectCameraListWidget, 0, 0) 
        self.layout.addLayout(self.panelLayout, 0, 0)
        self.layout.addWidget(self.loadingSpinner, 0, 0, Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.buttonLayout, 1,0,1,1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(self.layout)

    def connectSignals(self):
        logger.debug("connecting signals for live widget")
        self.selectCameraListWidget.closed.connect(self._showPanelWidgets)
        self.selectCameraListWidget.cameraFetcher.started.connect(self.loadingSpinner.start)
        self.selectCameraListWidget.cameraFetcher.started.connect(self.loadingSpinner.show)
        self.selectCameraListWidget.cameraFetcher.finished.connect(self.loadingSpinner.stop)
        self.selectCameraListWidget.cameraFetcher.finished.connect(self.loadingSpinner.hide)
        self.selectCameraListWidget.confirmButton.clicked.connect(self._showPanelWidgets)
        self.selectCameraListWidget.confirmButton.clicked.connect(self._updatePreviewLabel)

        self.selectCameraListWidget.confirmButton.clicked.connect(self.enableSelectCameraButton)
        self.selectCameraListWidget.confirmButton.clicked.connect(self.enableStartLivePreviewButton)

        self.selectCameraButton.clicked.connect(self.selectCameraListWidget.show)

        self.previewPanel.cameraStreamer.buildingStream.connect(self.loadingSpinner.start)
        self.previewPanel.cameraStreamer.buildingStream.connect(self.loadingSpinner.show)
        self.previewPanel.cameraStreamer.streamRunning.connect(self.loadingSpinner.stop)
        self.previewPanel.cameraStreamer.streamRunning.connect(self.loadingSpinner.hide)

        self.selectCameraListWidget.selectedCameraChanged.connect(self.previewPanel.setCameraData)
        self.selectCameraListWidget.selectedCameraChanged.connect(self.enableCaptureImageButton)

        self.previewPanel.imageCapture.finished.connect(self._enableAllButtons)
        self.previewPanel.imageCapture.started.connect(self._disableAllButtons)
        self.previewPanel.imageCapture.started.connect(self.loadingSpinner.start)
        self.previewPanel.imageCapture.started.connect(self.loadingSpinner.show)
        self.previewPanel.imageCapture.finished.connect(self.loadingSpinner.stop)
        self.previewPanel.imageCapture.finished.connect(self.loadingSpinner.hide)
        self.previewPanel.previewStopped.connect(self.loadingSpinner.stop)
        self.previewPanel.previewStopped.connect(self.loadingSpinner.hide)

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
    
    def buildConfig(self, config={}):
        logger.debug("building config")
        config['--image_name'] = datetime.now().isoformat().replace(':','_').replace('.','-')
        config['--image_dir'] = 'data/captures' 
        return config
    
    def captureImage(self):
        logger.debug("capturing image")
        config = self.buildConfig()
        self.previewPanel.captureImage(config)

    def imageCaptured(self, imageName):
        logger.debug("image captured")
        self.changed.emit("image")
        self.imagePanel.setImage(imageName)

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
        self.previewPanel.close()
        self.selectCameraListWidget.close()
        self.selectCameraListWidget = None
        self.selectCameraListWidget = SelectCameraListWidget()
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
    from PyQt6.QtWidgets import QApplication
    from src.db.DB import DBAdapter, FileAgnosticDB
    from src.utils.searching import init_taxonomy
    from src.widgets.ImageWidget import ImageWidget
    app = QApplication(sys.argv)
    db = FileAgnosticDB()
    db_adapter = DBAdapter(db)
    taxonomy_dir = "tests/data/taxonomy_test.json"
    image_widget = ImageWidget(db_adapter, init_taxonomy(taxonomy_dir))
    window = LiveWidget(image_widget)
    window.show()
    sys.exit(app.exec())