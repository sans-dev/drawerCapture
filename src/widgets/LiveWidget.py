from datetime import datetime

from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QStackedLayout
from PyQt6.QtCore import Qt, pyqtSignal

from widgets.SelectCameraListWidget import SelectCameraListWidget
from widgets.DataCollectionTextField import DataCollectionTextField
from widgets.SpinnerWidget import LoadingSpinner 
from widgets.PreviewPanel import PreviewPanel

class LiveWidget(QWidget):
    changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.initUI()
        self.connectSignals()

    def initUI(self):
        self.setWindowTitle("Live Mode")
        # setup grid layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

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
        self.stopLivePreviewButton.hide()

        # stack start and stop preview buttons
        self.startStopStackLayout = QStackedLayout()
        self.startStopStackLayout.addWidget(self.startLivePreviewButton)
        self.startStopStackLayout.addWidget(self.stopLivePreviewButton)
        
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
        
        # add data collection text field
        self.dataCollectionTextField = DataCollectionTextField()
        self.dataCollectionLabel = QLabel("Data Collection")
        self.dataCollectionLabel.setStyleSheet('font-size: 20px;')
        self.dataCollectionLayout = QVBoxLayout()
        self.dataCollectionLayout.addWidget(self.dataCollectionLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.dataCollectionLayout.addWidget(self.dataCollectionTextField)

        # add start live preview button and capture image button to a horizontal layout
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.selectCameraButton)
        self.buttonLayout.addLayout(self.startStopStackLayout, Qt.AlignmentFlag.AlignLeft)
        self.buttonLayout.addWidget(self.captureImageButton)
        
        # arange widgets in grid layout
        self.layout.addWidget(self.selectCameraListWidget, 0, 0, Qt.AlignmentFlag.AlignTop)
        self.layout.addLayout(self.panelLayout, 0, 0, Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.loadingSpinner, 0, 0, Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.dataCollectionLayout, 0, 1, Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.closeButton, 1, 1, Qt.AlignmentFlag.AlignBottom)
        self.layout.addLayout(self.buttonLayout, 1, 0, Qt.AlignmentFlag.AlignLeft)

    def connectSignals(self):
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

        self.stopLivePreviewButton.clicked.connect(self.loadingSpinner.stop)
        self.stopLivePreviewButton.clicked.connect(self.loadingSpinner.hide)

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

    def enableStartLivePreviewButton(self):
        self.startLivePreviewButton.setEnabled(True)

    def enableSelectCameraButton(self):
        self.selectCameraButton.setEnabled(True)

    def enableCaptureImageButton(self):
        self.captureImageButton.setEnabled(True)

    def selectCamera(self):
        self._hidePanelWidgets()
        if not self.selectCameraListWidget.isRefreshed:
            self.selectCameraListWidget.refreshButtonClicked()
    
    def captureImage(self):
        isoTimeStamp = datetime.now().isoformat().replace(':','_').replace('.','-')
        self.previewPanel.captureImage('data/captures',f'{isoTimeStamp}_test.raf')

    def startPreview(self):
        self.selectCameraListWidget.setEnabled(False)
        self.startStopStackLayout.setCurrentIndex(1)
        self.previewPanel.wasStreaming = True
        self.previewPanel.startPreview()

    def stopPreview(self):
        self.previewPanel.wasStreaming = False
        self.captureImageButton.setEnabled(False)
        self.selectCameraButton.setEnabled(True)
        self.selectCameraListWidget.setEnabled(True)
        self.startStopStackLayout.setCurrentIndex(0)
        self.previewPanel.stopPreview()

    def closeLiveMode(self):
        self.previewPanel.stopPreview()
        self.changed.emit("main")

    def _hidePanelWidgets(self):
        self.previewPanel.hide()
        self.previewPanelLabel.hide()
        self.selectCameraButton.hide()
        self.startLivePreviewButton.hide()
        self.captureImageButton.hide()
    
    def _showPanelWidgets(self):
        self.previewPanel.show()
        self.previewPanelLabel.show()
        self.selectCameraButton.show()
        self.startLivePreviewButton.show()
        self.captureImageButton.show()

    def _updatePreviewLabel(self):
        self.previewPanelLabel.setText(f"Live Preview ({self.previewPanel.cameraStreamer.getCameraDataAsString()})")

    def _disableAllButtons(self):
        self.selectCameraButton.setEnabled(False)
        self.startLivePreviewButton.setEnabled(False)
        self.captureImageButton.setEnabled(False)
        self.closeButton.setEnabled(False)

    def _enableAllButtons(self):
        self.selectCameraButton.setEnabled(True)
        self.startLivePreviewButton.setEnabled(True)
        self.captureImageButton.setEnabled(True)
        self.closeButton.setEnabled(True)