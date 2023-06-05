import subprocess
from PyQt6.QtCore import QThread

class CameraThread(QThread):

    def __init__(self, cameraData=None):
        super().__init__()
        if cameraData:
            self.setCameraData(cameraData)
        self.cameraName = None
        self.cameraPort = None
        self.proc = None
        self.config = dict()

        self.proc = None

    def setCameraData(self, cameraData):
        self.cameraName = cameraData.split('usb')[0].strip()
        self.cameraPort = f"usb{cameraData.split('usb')[-1].strip()}"
        self.config['--camera_name'] = self.cameraName
        self.config['--port'] = self.cameraPort

    def getCameraDataAsString(self):
        return f"Camera Name: {self.cameraName}, Port: {self.cameraPort}"

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
        self.proc = QProcess()