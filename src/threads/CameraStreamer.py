from PyQt6.QtCore import pyqtSignal, QProcess
from pathlib import Path

from threads import CameraThread, VideoCaptureDevice


class CameraStreamer(CameraThread):
    streamRunning = pyqtSignal()
    buildingStream = pyqtSignal()
    streamStopped = pyqtSignal()

    def __init__(self, cameraData=None):
        super().__init__(cameraData=cameraData)
        self.videoCapture = VideoCaptureDevice()
        self.config['--script'] = 'src/cmds/open_video_stream.bash'
        self.config['--dir'] = self._getVideoStreamDir().as_posix()
        self.videoCapture.deviceOpen.connect(self.streamRunning.emit)
        self.wasRunning = False

    def run(self):
        self.wasRunning = True
        print('Building video stream')
        super()._stopGphoto2Slaves()
        if self.proc is None:
            self.buildingStream.emit()
            self.proc = QProcess()
            self.proc.finished.connect(self._procFinished)
            self.proc.readyReadStandardOutput.connect(self.printStdOut)

            self.proc.start('bash', self._buildKwargs())

            started = self.proc.waitForStarted()
            if not started:
                print('Failed to start video stream')
                return
            print('Video stream running')
            self.proc.waitForReadyRead(-1)
            self.videoCapture.setVideoStreamDir(self.config['--dir'])
            self.videoCapture.start()

    def quit(self):
        self.streamStopped.emit()
        self.wasRunning = False
        if self.proc:
            print('Terminate streaming process')
            self.videoCapture.device.release()
            self.proc.kill()
        super()._stopGphoto2Slaves()
        super().quit()

    def _getVideoStreamDir(self):
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
                    return Path(lines[idx + 1].strip())
        return None