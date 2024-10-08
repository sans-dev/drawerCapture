"""
Module: CameraStreamer
Author: Sebastian Sander
This module contains the CameraStreamer class, which is a thread that streams video from a camera device.
"""


import logging
import logging.config
import time

from PyQt6.QtCore import pyqtSignal, QProcess, QThread, QObject
from pathlib import Path

from src.threads.CameraThread import CameraWorker

logging.config.fileConfig('configs/logging/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class CameraStreamerSignals(QObject):
    building_stream = pyqtSignal()
    stream_enabled = pyqtSignal(str)

class CameraStreamer(CameraWorker):
    """
    A thread that streams video from a camera device.

    Attributes:
        streamRunning (pyqtSignal): A signal emitted when the video stream is running.
        buildingStream (pyqtSignal): A signal emitted when the video stream is being built.
        streamStopped (pyqtSignal): A signal emitted when the video stream has stopped.

    Args:
        cameraData (dict): A dictionary containing information about the camera device.

    """
    signals = CameraStreamerSignals()

    def __init__(self, fs, cameraData=None):
        """
        Initializes the CameraStreamer object.

        Args:
            cameraData (dict): A dictionary containing information about the camera device.

        """
        logger.debug("initializing camera streamer")
        super().__init__(cameraData=cameraData)
        self.fs = fs # sampling fqequency in milliseconds
        self.config['--script'] = 'src/cmds/open_video_stream.bash'
        self.config['--dir'] = self._get_device_dir().as_posix()
        self.config['--fs'] = str(fs)
        self.running = False

    def run(self):
        """
        Enable connection to camera

        """
        logger.info("running camera streamer thread")
        if not self.proc:
            logger.debug("emitting building stream signal and configuring process")
            self.signals.building_stream.emit()
            self.proc = QProcess()
            self.proc.readyReadStandardOutput.connect(self.printStdOut)
            self.proc.setCurrentReadChannel(1)
            self.proc.readyReadStandardError.connect(self.printStdErr)

            logger.debug("starting video stream process")
            logger.info("================ RUN CMD IN SUBPROC =================")
            logger.info(" ".join(self._buildKwargs()))
            self.proc.start('bash', self._buildKwargs())

            started = self.proc.waitForStarted()
            if not started:
                logger.error("failed to start video stream process")
                self.quit()

            self.proc.waitForReadyRead(-1)
            time.sleep(6)
            if 'error' in "".join(self.error_log).lower():
                logger.warning(f"Error trying to connect to camera. {self.error_log}")
                self.quit()

            logger.info("Camera connected")
            self.signals.stream_enabled.emit(self.config['--dir'])
            self.running = True
            while self.running:
                continue
            self.quit()

    def stop_running(self):
        self.running = False

    def quit(self):
        """
        Stops the video stream.

        """
        logger.info("quitting camera streamer thread")
        self.wasRunning = False
        logger.info("stopping video stream process")
        self.proc.terminate()
        self.proc.waitForFinished(1000)
        self.proc = None
        self.reset_camera()
        super().quit()

    def reset_camera(self):
        proc = QProcess()
        proc.start('gphoto2', ['--set-config','movie=0'])
        logger.info("resetting camera movie mode")
        if proc.waitForFinished():
            proc.terminate()

    def _get_device_dir(self):
        """
        Gets the directory of the video stream.

        Returns:
            pathlib.Path: The directory of the video stream.

        """
        logger.debug("getting video4linux device directory")
        proc = QProcess()
        proc.start('v4l2-ctl', ['-d', self.port, '--list-devices'])
        started = proc.waitForStarted()
        if started:
            proc.waitForFinished()
            output = proc.readAllStandardOutput()
            output = output.data().decode('utf-8')
            lines = output.split('\n')
            for idx, line in enumerate(lines):
                if 'Dummy' in line:
                    logger.info("found dummy device at %s", lines[idx + 1].strip())
                    return Path(lines[idx + 1].strip())
        return None
    


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    fs = 1
    stream = CameraStreamer(fs=fs)
    stream.set_camera_data('Sony Alpha-A5100 (Control)', 'usb:001,028')
    thread = QThread()
    stream.moveToThread(thread)
    thread.started.connect(stream.run)
    thread.finished.connect(stream.quit)
    thread.finished.connect(stream.deleteLater)
    thread.start()


    while thread.isRunning():
        ret, frame = stream.getFrame()
        time.sleep(1/fs)
        print(type(frame))
    stream.reset_camera()
    sys.exit(app.exec())