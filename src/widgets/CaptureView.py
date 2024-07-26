import logging
import logging.config

from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy, QGridLayout
from PyQt6.QtCore import Qt, pyqtSignal
from src.widgets.PreviewPanel import PreviewPanel

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class PanelButton(QPushButton):
    def __init__(self, name, height, width_range, isEnable=False):
        super().__init__(name)
        self.setMaximumWidth(width_range[1])
        self.setMinimumWidth(width_range[0])
        self.setFixedHeight(height)
        self.setEnabled(isEnable)

class CaptureView(QWidget):
    def __init__(self, db_adapter, fs, panel_res):
        super().__init__()
        self.panel = PreviewPanel(fs, panel_res)
        self.model = None
        self.port = None
        self.db_apater = db_adapter
        self.init_ui()

    def init_ui(self):
        logger.debug("initializing live widget UI")
        self.setWindowTitle("Capture Mode")
        layout = QGridLayout()
        layout.addWidget(self.panel, 0, 0)

        button_layout = self.create_button_layout()
        layout.addLayout(button_layout,1,0)
        self.setLayout(layout)

    def create_button_layout(self):
        save_button = QPushButton("Save")
        close_button = QPushButton("Close")
        layout = QHBoxLayout()
        layout.addWidget(save_button)
        layout.addWidget(close_button)
        return layout

    def set_camera_data(self, camera_data): 
        self.model = camera_data.split('usb')[0].strip()
        self.port = f"usb{camera_data.split('usb')[-1].strip()}"
        self.panel.set_camera_data(self.model, self.port)


 
    def show_error_dialog(self, msg):
        QMessageBox.critical(self, "Error", msg)

if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser
    from PyQt6.QtWidgets import QApplication
    from src.db.DB import DBAdapter, DummyDB
    from src.utils.load_style_sheet import load_style_sheet

    parser = ArgumentParser()
    args = parser.parse_args()
    app = QApplication(sys.argv)
    app.setStyleSheet(load_style_sheet('PicPax'))
    db_adapter = DBAdapter(DummyDB())

    window = CaptureView(db_adapter, fs=5, panel_res=(1024,780))
    window.show()
    sys.exit(app.exec())