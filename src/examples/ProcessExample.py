from PyQt6.QtCore import QProcess

class ExampleProc(QProcess):
    def __init__(self):
        super().__init__()
        self.finished.connect(self._procFinished)

    def _procFinished(self):
        print("process finished")

    def run(self):
        self.start('bash', ['src/cmds/example.bash', '--camera_name', 'test', '--port', '0000'])
        started = self.waitForStarted()
        if not started:
            print("process failed to start")
            error = self.readAllStandardError().data().decode('utf-8')
            print(error)
            return
        print("process started")
        self.waitForFinished(-1)
        output = self.readAllStandardOutput().data().decode('utf-8')
        print(output)

def main():
    proc = ExampleProc()
    proc.run()

if __name__ == '__main__':
    main()