import subprocess
import logging
import logging.config
from PyQt6.QtCore import QThread

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class CameraThread(QThread):
    """
    A QThread subclass for capturing images from a camera using gphoto2.

    Attributes:
    -----------
    model : str
        The camera model.
    port : str
        The camera port.
    config : dict
        A dictionary containing configuration options for gphoto2.
    proc : subprocess.Popen or None
        A subprocess object representing the gphoto2 process.

    Methods:
    --------
    setCameraData(cameraData: str) -> None:
        Sets the camera model and port based on the given cameraData string.
    getCameraDataAsString() -> str:
        Returns a string representation of the camera model and port.
    _stopGphoto2Slaves() -> None:
        Stops any running gphoto2 slave processes.
    _procFinished() -> None:
        Callback function to be called when the gphoto2 process finishes.
    _buildKwargs() -> list:
        Builds a list of command line arguments for gphoto2 based on the config dictionary.
    printStdOut() -> None:
        Prints the standard output of the gphoto2 process.
    printStdErr() -> None:
        Prints the standard error of the gphoto2 process.
    quit() -> None:
        Stops any running gphoto2 slave processes and quits the thread.
    """

    def __init__(self, cameraData=None):
        super().__init__()
        if cameraData:
            self.setCameraData(cameraData)
        self.model = None
        self.port = None
        self.config = dict()
        self.error_log = []

        self.proc = None

    def setCameraData(self, cameraData):
        """
        Sets the camera model and port based on the given cameraData string.

        Parameters:
        -----------
        cameraData : str
            A string containing the camera model and port in the format "MODEL usb:PORT".

        Returns:
        --------
        None
        """
        self.model = cameraData.split('usb')[0].strip()
        self.port = f"usb{cameraData.split('usb')[-1].strip()}"
        self.config['--model'] = self.model
        self.config['--port'] = self.port

    def getCameraDataAsString(self):
        """
        Returns a string representation of the camera model and port.

        Returns:
        --------
        str
            A string containing the camera model and port.
        """
        return f"Camera Name: {self.model}, Port: {self.port}"

    def _stopGphoto2Slaves(self):
        """
        Stops any running gphoto2 slave processes.

        Returns:
        --------
        None
        """
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
                cmd = [
                    'kill',
                    '-9',
                    pid
                ]
                subprocess.run(cmd)

    def _procFinished(self):
        """
        Callback function to be called when the gphoto2 process finishes.

        Returns:
        --------
        None
        """
        print("In Camera Thread proc_finished")
        self.proc = None

    def _buildKwargs(self):
        """
        Builds a list of command line arguments for gphoto2 based on the config dictionary.

        Returns:
        --------
        list
            A list of command line arguments for gphoto2.
        """
        kwargs = []
        for key, value in self.config.items():
            if key == '--script':
                kwargs.append(value)
                continue
            kwargs.append(key)
            kwargs.append(value)
        return kwargs

    def printStdOut(self):
        """
        Prints the standard output of the gphoto2 process.

        Returns:
        --------
        None
        """
        self.error_log.append(self.proc.readAllStandardOutput().data().decode('utf-8'))
        print(self.error_log[-1])

    def printStdErr(self):
        """
        Prints the standard error of the gphoto2 process.

        Returns:
        --------
        None
        """
        self.error_log.append(self.proc.readAllStandardError().data().decode('utf-8'))
        print(self.error_log[-1])

    def get_std_err(self):
        """
        Returns the standard error of the gphoto2 process.
        """
        return self.error_log
    
    def quit(self):
        """
        Stops any running gphoto2 slave processes and quits the thread.

        Returns:
        --------
        None
        """
        self._stopGphoto2Slaves()
        super().quit()