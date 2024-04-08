# DrawerCapture

Drawer Capture is a work in progress project aiming to build an open-source GUI-based application to streamline the process of digitizing museum drawers. It uses gphoto2 in the backend to configure and control a set of different cameras to take images remotely. A mask provided helps to gather important metadata about species and the museum.

## Installation
To run Drawer Capture, you need to install some prerequisites. These instructions have been tested on Ubuntu only.

1. Install usblib by running the following command in your terminal:
    ```
    sudo apt-get install libusb
    ```
2. Clone the libgphoto repository from GitHub:
    ```
    git clone https://github.com/gphoto/libgphoto2.git
    ```
3. Navigate to the cloned libgphoto repository and follow the installation instructions in the INSTALL file. You will need to compile and install it with the Fuji camlib.

4. Install gphoto2 for terminal:
    ```
    sudo apt-get install gphoto2
    ```
6. Install ffmpeg:
    ```
    sudo apt-get install ffmpeg
    
    ```
7. Install the kernel mod 4l2loopback:
    ```
    sudo apt-get install v4l2loopback-dkms
    ```
8. Create a Python environment, activate it, and install the requirements:
    ```
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

## Running the Application
Just run the command python drawerCapture.py

## Configure the Camera
Click add camera button
plug in your camera via usb
click refresh 
select your camera

## Capturing Images 
click capture button
wait a short while
image is previewed 
click save 

## Collection Information
after save meta info mask opens to add metainformation

