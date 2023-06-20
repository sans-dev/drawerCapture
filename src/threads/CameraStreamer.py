import logging
import logging.config

from PyQt6.QtCore import pyqtSignal, QProcess
from pathlib import Path

from threads import CameraThread, VideoCaptureDevice

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class CameraStreamer(CameraThread):
    streamRunning = pyqtSignal()
    buildingStream = pyqtSignal()
    streamStopped = pyqtSignal()

    def __init__(self, cameraData=None):
        logger.debug("initializing camera streamer")
        super().__init__(cameraData=cameraData)
        self.videoCapture = VideoCaptureDevice()
        self.config['--script'] = 'src/cmds/open_video_stream.bash'
        self.config['--dir'] = self._getVideoStreamDir().as_posix()
        self.videoCapture.deviceOpen.connect(self.streamRunning.emit)
        self.wasRunning = False

    def run(self):
        logger.info("running camera streamer thread")
        self.wasRunning = True
        super()._stopGphoto2Slaves()
        if self.proc is None:
            logger.debug("emitting building stream signal and  configuring process")
            self.buildingStream.emit()
            self.proc = QProcess()
            self.proc.finished.connect(self._procFinished)
            self.proc.readyReadStandardOutput.connect(self.printStdOut)
            self.proc.setCurrentReadChannel(1)
            self.proc.readyReadStandardError.connect(self.printStdErr)

            logger.debug("starting video stream process")
            self.proc.start('bash', self._buildKwargs())

            started = self.proc.waitForStarted()
            if not started:
                logger.error("failed to start video stream process")
                self.quit()
            self.proc.waitForReadyRead(-1)
            logger.info("Output stream ready")
            self.videoCapture.setVideoStreamDir(self.config['--dir'])
            self.videoCapture.start()

    def quit(self):
        logger.info("quitting camera streamer thread")
        self.wasRunning = False
        if self.proc:
            logger.info("stopping video stream process")
            self.proc.terminate()
            self.proc.waitForFinished()
            self.videoCapture.quit()
        super()._stopGphoto2Slaves()
        self.streamStopped.emit()
        super().quit()

    def getFrame(self):
        logger.debug("getting frame from videoCapture device")
        return self.videoCapture.device.read()

    def _getVideoStreamDir(self):
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