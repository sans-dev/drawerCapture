import subprocess
from PyQt6.QtCore import QThread

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

    def getCameraDataAsString(self):
        return f"Camera Name: {self.model}, Port: {self.port}"

    def _stopGphoto2Slaves(self):
        # get the process id of the gphoto2 slave processes using pgrep -fla gphoto2
        # kill the processes using kill -9 <pid>
        cmd = ['pgrep', '-fla', 'gphoto2']
        
        output = subprocess.run(cmd, capture_output=True)
        output = output.stdout.decode('utf-8')
        # loop over output and filter processes that containing gphoto2
        # get the pid and kill the process
        for line in output.split('\n'):
            if 'gphoto2' in line:
                pid = line.split(' ')[0]
                print(pid)
                cmd = [
                    'kill',
                    '-9',
                    pid
                ]
                subprocess.run(cmd)

    def _procFinished(self):
        self.proc = None
        self.finished.emit()

    def _buildKwargs(self):
        kwargs = []
        for key, value in self.config.items():
            if key == '--script':
                kwargs.append(value)
                continue
            kwargs.append(key)
            kwargs.append(value)
        print(kwargs)
        return kwargs