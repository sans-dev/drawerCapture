import subprocess
from datetime import datetime
from argparse import ArgumentParser
def main(arg):
    cmd = ['bash', 'src/cmds/capture_image.bash']
    cmd.append(arg.capture_dir)
    cmd.append(arg.capture_name)
    subprocess.run(cmd)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--capture_dir', type=str, default='data/captures')
    parser.add_argument('--capture_name', type=str, default=datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + '.raf')
    args = parser.parse_args()
    main(args)