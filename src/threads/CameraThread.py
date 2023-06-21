import subprocess
import logging
import logging.config
from PyQt6.QtCore import QThread

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class CameraThread(QThread):

    def __init__(self, cameraData=None):
        super().__init__()
        if cameraData:
            self.setCameraData(cameraData)
        self.model = None
        self.port = None
        self.config = dict()

        self.proc = None

    def setCameraData(self, cameraData):
        self.model = cameraData.split('usb')[0].strip()
        self.port = f"usb{cameraData.split('usb')[-1].strip()}"
        self.config['--model'] = self.model
        self.config['--port'] = self.port
        self.config['--debug'] = str(logger.getEffectiveLevel() == logging.DEBUG).lower()

    def getCameraDataAsString(self):
        return f"Camera Name: {self.model}, Port: {self.port}"

    def _stopGphoto2Slaves(self):
        logger.debug("stopping gphoto2 slave processes")
        # get the process id of the gphoto2 slave processes using pgrep -fla gphoto2
        # kill the processes using kill -9 <pid>
        cmd = ['pgrep', '-fla', 'gphoto2']
        
        output = subprocess.run(cmd, capture_output=True)
        output = output.stdout.decode('utf-8')
        # loop over output and filter processes that containing gphoto2
        # get the pid and kill the process
        for line in output.split('\n'):
            if 'gphoto2' in line:
                logger.debug("killing gphoto2 slave process %s", line)
                pid = line.split(' ')[0]
                cmd = [
                    'kill',
                    '-9',
                    pid
                ]
                subprocess.run(cmd)

    def _procFinished(self):
        self.proc = None

    def _buildKwargs(self):
        kwargs = []
        for key, value in self.config.items():
            if key == '--script':
                kwargs.append(value)
                continue
            kwargs.append(key)
            kwargs.append(value)
        logger.debug("kwargs: %s", kwargs)
        return kwargs

    def printStdOut(self):
            stdOut = self.proc.readAllStandardOutput().data().decode('utf-8')
            logger.info(stdOut)

    def printStdErr(self):
        stdErr = self.proc.readAllStandardError().data().decode('utf-8')
        logger.debug(stdErr)

    def quit(self):
        logger.debug("quitting camera thread")
        self._stopGphoto2Slaves()
        super().quit()