import logging
import logging.config
import time

from PyQt6.QtCore import pyqtSignal, QProcess, QThread, QTimer
from pathlib import Path

from src.threads.CameraThread import CameraThread
from src.threads.VideoCaptureDevice import VideoCaptureDevice

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class CameraStreamer(CameraThread):
    """
    A thread that streams video from a camera device.

    Attributes:
        streamRunning (pyqtSignal): A signal emitted when the video stream is running.
        buildingStream (pyqtSignal): A signal emitted when the video stream is being built.
        streamStopped (pyqtSignal): A signal emitted when the video stream has stopped.

    Args:
        cameraData (dict): A dictionary containing information about the camera device.

    """
    streamRunning = pyqtSignal()
    buildingStream = pyqtSignal()
    streamStopped = pyqtSignal()
    frame_ready = pyqtSignal(tuple)

    def __init__(self, fs, cameraData=None):
        """
        Initializes the CameraStreamer object.

        Args:
            cameraData (dict): A dictionary containing information about the camera device.

        """
        logger.debug("initializing camera streamer")
        super().__init__(cameraData=cameraData)
        self.fs = fs # sampling fqequency in milliseconds
        self.videoCapture = VideoCaptureDevice()
        self.config['--script'] = 'src/cmds/open_video_stream.bash'
        self.config['--dir'] = self._getVideoStreamDir().as_posix()
        self.config['--fs'] = str(fs)
        self.videoCapture.deviceOpen.connect(self.streamRunning.emit)
        self.wasRunning = False

    def run(self):
        """
        Starts the video stream.

        """
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_frame)
        logger.info("running camera streamer thread")
        self.wasRunning = True
        super()._stopGphoto2Slaves()
        if not self.proc:
            logger.debug("emitting building stream signal and  configuring process")
            self.buildingStream.emit()
            self.proc = QProcess()
            self.proc.readyReadStandardOutput.connect(self.printStdOut)
            self.proc.setCurrentReadChannel(1)
            self.proc.readyReadStandardError.connect(self.printStdErr)

            logger.debug("starting video stream process")
            print("================ RUN CMD IN SUBPROC =================")
            print(" ".join(self._buildKwargs()))
            self.proc.start('bash', self._buildKwargs())

            started = self.proc.waitForStarted()
            if not started:
                logger.error("failed to start video stream process")
                self.quit()
            self.proc.waitForReadyRead(-1)
            logger.info("Output stream ready")
            if 'error' in "".join(self.error_log).lower():
                print("baaaad")
            self.videoCapture.setVideoStreamDir(self.config['--dir'])
            logger.debug("Starting Timer")
            self.timer.start(1000//self.fs)
            self.videoCapture.start()
    
    def quit(self):
        """
        Stops the video stream.

        """
        logger.info("quitting camera streamer thread")
        self.wasRunning = False
        self.timer.stop()
        if self.proc:
            logger.info("stopping video stream process")
            self.proc.terminate()
            self.proc.waitForFinished(1000)
            self.videoCapture.quit()
        self.streamStopped.emit()
        self.proc = None
        super().quit()

    def send_frame(self):
        """
        Gets a frame from the video stream.

        Returns:
            numpy.ndarray: A frame from the video stream.

        """
        logger.debug("getting frame from videoCapture device")
        return self.frame_ready.emit(self.videoCapture.device.read())

    def _getVideoStreamDir(self):
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
    
    def reset_camera(self):
        proc = QProcess()
        proc.start('gphoto2', ['--set-config','movie=0'])
        logger.info("resetting camera movie mode")
        if proc.waitForFinished():
            proc.terminate()

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    fs = 1
    stream = CameraStreamer(fs=fs)
    stream.setCameraData('Sony Alpha-A5100 (Control)', 'usb:001,028')
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