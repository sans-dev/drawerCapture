# DrawerCapture

Drawer Capture is a work in progress project aiming to build an open-source GUI-based application to streamline the process of digitizing museum drawers. It uses gphoto2 in the backend to configure and control a set of different cameras to take images remotely. A mask provided helps to gather important metadata about species and the museum.

## Installation
### Manual
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
### Docker (Ubuntu Only)
To install Drawer Capture using Docker, follow these steps:

1. Install Docker on your system by following the official Docker installation guide for your operating system.

2. Once Docker is installed, open a terminal and run the following command to pull the Docker image for Drawer Capture:
    ```
    docker pull username/drawer-capture:latest
    ```
    Replace `username` with your Docker username.

### Docker Compose Installation (recommended)
To install Docker Compose, follow these steps:

1. Make sure you have Docker installed on your system. If not, refer to the official Docker installation guide for your operating system.

2. Open a terminal and run the following command to download the latest version of Docker Compose:
    ```
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    ```

3. Once the download is complete, apply executable permissions to the Docker Compose binary:
    ```
    sudo chmod +x /usr/local/bin/docker-compose
    ```

4. Verify that Docker Compose is installed correctly by running the following command:
    ```
    docker-compose --version
    ```

    You should see the version information for Docker Compose printed in the terminal.

#### Building and Running the Application with Docker Compose

To build and run the application using Docker Compose, follow these steps:

1. Pull the repository from GitHub by running the following command in your terminal:
    ```
    git clone https://github.com/sans-dev/drawerCapture
    ```

2. Navigate into the repository's top level directory, where the `docker-compose.yml` file lies:

3. Build the Docker images by running the following command:
    ```
    docker-compose build
    ```

4. Once the build is complete, start the application by running the following command:
    ```
    docker-compose up
    ```

   This will start all the services defined in the `docker-compose.yml` file and you should see the applications GUI.


## Running the Application
To run the application, simply execute the following command in your terminal:

    ```
    python -m src.DrawerCapture
    ```