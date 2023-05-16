import subprocess
from unittest import TestCase
from pathlib import Path

class TestCaptureImage(TestCase):
        # setup
        def setUp(self):
            self.camera_name, self.camera_port = self._get_camera_and_port()
            self.test_dir = Path('/tmp')
            self.filename = 'test.raf'
            self.cmd = ['bash', 'src/cmds/capture_image.bash']
            self.cmd.append(self.test_dir.as_posix())
            self.cmd.append(self.filename)
            self.cmd.append(self.camera_name)
            self.cmd.append(self.camera_port)

        # teardown
        def tearDown(self):
            # remove test file
            self.test_dir.joinpath(self.filename).unlink()
    
        def test_capture_image_run(self):
            proc = subprocess.run(self.cmd)
            self.assertEqual(proc.returncode, 0)

        def test_capture_image_popen(self):
            proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stout, sterr = proc.communicate()
            print(stout.decode('utf-8'))
            print(sterr.decode('utf-8'))
            print(proc.returncode)
            self.assertEqual(proc.returncode, 0)

        def _get_camera_and_port(self):
            cmd = ['gphoto2', '--auto-detect']
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stout, sterr = proc.communicate()
            camera_name = stout.decode('utf-8').split('\n')[2].split()[0]
            camera_port = stout.decode('utf-8').split('\n')[2].split()[1]
            return camera_name, camera_port