# Basis-Image: Ubuntu
FROM ubuntu:latest

VOLUME /hostpipe
# Umgebungsvariablen setzen
ENV DEBIAN_FRONTEND=noninteractive

# Paketquellen aktualisieren und benötigte Pakete installieren
RUN apt-get update && apt-get install -y \
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


RUN curl -LO https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb

RUN xauth merge /root/.Xauthority
# Erstellen einer virtuellen Umgebung
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Arbeitsverzeichnis erstellen
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

#USER ssander
#RUN chown -R 1000:1000 /app
# Run drawer capture
CMD ["/opt/venv/bin/python", "-m", "src.drawerCapture", "--debug","--geo-data", "level-0", "--style", "Combinear"]