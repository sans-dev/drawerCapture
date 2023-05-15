import subprocess
from threads.CameraThread import CameraThread

class ImageCapture(CameraThread):

    def __init__(self, cameraData=None):
        super().__init__(cameraData=cameraData)
        if cameraData:
            self.setCameraData(cameraData)
        self.captureImgCmd = ['bash', 'src/cmds/capture_image.bash']

    def run(self):
        print("starting image capture")
        self.proc = subprocess.Popen(self.captureImgCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while self.proc.poll() is None:
            print("waiting for image capture to complete")
            self.sleep(1)
        # check of proc terminated with exit code 0
        if self.proc.returncode == 0:
            print("image capture completed")
        else:
            print("image capture failed")
            stout, sterr = self.proc.communicate()
            print(stout.decode('utf-8'))
            print(sterr.decode('utf-8'))
        self.proc = None
        
    def quit(self):
        super()._stopGphoto2Slaves()
        super().quit()
        print("image capture stopped")

    def captureImage(self, captureDir, captureName):
        super()._stopGphoto2Slaves()
        self.captureImgCmd.append(captureDir)
        self.captureImgCmd.append(captureName)
        print(" ".join(self.captureImgCmd))
        self.start()
        self.quit()