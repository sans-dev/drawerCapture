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
    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

## Running the Application
To run the application, simply execute the following command in your terminal:

    ```
    python src/DrawerCapture.py
    ```
## Configure the Camera
1. Click the 'Add Camera' button.
2. Plug in your camera via USB.
3. Click 'Refresh'.
4. Select your camera from the list.

## Capturing Images 
1. Click the 'Capture' button.
2. Wait for a short while until the image is captured.
3. Preview the captured image.
4. Click 'Save' to save the image.

## Collection Information
After saving the image, a metadata mask opens to add metadata about the image.