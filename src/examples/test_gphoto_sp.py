import subprocess


def main():
    cmd = ['gphoto2', '--auto-detect']
    output = subprocess.run(cmd, capture_output=True)
    lines = output.stdout.decode('utf-8').split('\n')
    cameras = []
    for line in lines:
        if 'usb:' in line:
            cameras.append(line.split('usb:')[0])
    print(cameras)

    # grep gphoto2 processes
    cmd = ['pgrep', '-fla', 'gphoto2']
    output = subprocess.run(cmd, capture_output=True)
    lines = output.stdout.decode('utf-8').split('\n')
    print("gphoto2 processes:")
    for line in lines:
        print(line)
    # open a video capture stream for each camera
    cmd = [
        'gphoto2',
        '--debug',
        '--capture-movie'
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        stout, sterr = proc.communicate()
        print(sterr.decode('utf-8'))
        # print(stout)
        if proc.poll() is not None:
            break



if __name__ == '__main__':
    main()