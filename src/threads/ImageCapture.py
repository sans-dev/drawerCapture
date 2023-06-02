import subprocess
import shlex
from threads import CameraThread

class ImageCapture(CameraThread):
    IMG_FORMATS = {
        'Fuji' : '.raf',
    }

    def __init__(self, cameraData=None):
        super().__init__(cameraData=cameraData)
        self.cmd = ['bash', 'src/cmds/capture_image.bash']
        self.config = {
            '--image_dir': '',
            '--image_name': '',
            '--image_format': '.raf',
            '--image_quality': '0',
            '--camera_name': '' if self.cameraName is None else self.cameraName,
            '--port': '' if self.cameraPort is None else self.cameraPort,
            '--debug': 'false'
        }

        self.finished.connect(self.quit)

    def run(self):
        try:
            self.proc = subprocess.Popen(
                self._buildCmd(), 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                )

            while self.proc.poll() is None:
                stout, _ = self.proc.communicate()
                print(stout.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            print("Process failed because it did not return a sucessful return code")
            print("Return cfode={e.returncode} \n {e}")
        except FileNotFoundError as e:
            print("Process failed because the executable was not found")
            print(e)
            print(self._buildCmd())
        finally:
            self.proc = None
        
    def quit(self):
        super()._stopGphoto2Slaves()
        super().quit()
        print("image capture closed")

    def captureImage(self):
        super()._stopGphoto2Slaves()
        print('starting image capture')
        self.start()

    def setUpConfig(self, config: dict):
        for key, value in config.items():
            try:
                self.config[key] = value
            except KeyError:
                print(f"key {key} not found in config")

    def _resetCmd(self):
        self.cmd = ['bash', 'src/cmds/capture_image.bash']

    def _buildCmd(self):
        cmd = self.cmd.copy()
        for key, value in self.config.items():
            cmd.append(key)
            cmd.append(value)
        return shlex.split(' '.join(cmd))