# DrawerCapture
Drawer Capture is an GUI based application for remote photo capturing and and acquisition of the most relevant collection metadata (taxonomy, location and time of collection). The aim is to provide an inferace that combines the capturing of images in the museum collection digitization process with the aquisition of relevant meta data. 

## Installation
### Prerequisites 
- Docker:
    - To install docker follow this link (https://docs.docker.com/engine/install/ubuntu/)

### Via install.sh - run - (Docker required, tested on Ubuntu only)
Clone this repo, open a terminal in its directory and run the following:

```sh
chmod +x install.sh
./install.sh
```

The application should be findable in launcher under DrawerCapture. It runs the latest build from docker hub

### Local Docker build - dev - (Docker required, tested on Ubuntu only)
Clone this repo, open a terminal in its directory and run the following:

```.sh
docker compose build
chmod +x drawerCapture.sh
./drawerCapture.sh --local # start application from local build. By ommit --local the latest build on docker hub is used
```

### From source -dev - (local) 
To install from source clone this repo an install the following dependencies.
1. Install pkg dependencies:

```sh
apt-get update && apt-get install -y \
    python3 \
    python3.12-venv \
    python3-pip \
    libgphoto2-dev \
    libusb-1.0-0-dev \
    gphoto2 \
    libxcb-cursor0 \
    libqt6gui6 \
    libqt6widgets6 \
    libqt6core6 \
    libqt6dbus6 \
    libqt6network6 \
    libxcb-xinerama0 \
    libnss3 \
    libasound2t64 \
    libxkbfile-dev \
    xauth \
    curl \
    fonts-liberation \
    libu2f-udev \
    wget \
    xdg-utils \
    nautilus \
    && rm -rf /var/lib/apt/lists/*
```

2. Create a Python environment, activate it, and install the requirements:

```sh
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Run with:

```sh
python3 -m src.drawerCapture
```