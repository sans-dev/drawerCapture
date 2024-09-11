#!/bin/bash

# Setze den Installationspfad
INSTALL_DIR="$HOME/.local/share/drawerCapture"

# Erstelle das Installationsverzeichnis
mkdir -p "$INSTALL_DIR"

cp  DrawerCapture.sh "$INSTALL_DIR"
cp  assets/icons/app_icon.png "$INSTALL_DIR"

# Erstelle die .desktop-Datei
DESKTOP_FILE="$HOME/.local/share/applications/drawerCapture.desktop"
echo "[Desktop Entry]" > "$DESKTOP_FILE"
echo "Name=DrawerCapture" >> "$DESKTOP_FILE"
echo "Exec=$INSTALL_DIR/DrawerCapture.sh" >> "$DESKTOP_FILE"
echo "Icon=$INSTALL_DIR/app_icon.png" >> "$DESKTOP_FILE"
echo "Type=Application" >> "$DESKTOP_FILE"
echo "Categories=Graphics;" >> "$DESKTOP_FILE"
echo "StartupWMClass=DrawerCapture.py, DrawerCapture.py" >> "$DESKTOP_FILE"
# Setze die Berechtigungen für die .desktop-Datei
chmod +x "$DESKTOP_FILE"

# Setze die Berechtigungen für das EntryPoint-Skript
chmod +x "$INSTALL_DIR/DrawerCapture.sh"

# Erstelle einen symbolischen Link im ~/bin Verzeichnis
mkdir -p "$HOME/bin"
ln -sf "$INSTALL_DIR/DrawerCapture.sh" "$HOME/bin/drawer-capture"

# Füge ~/bin zum PATH hinzu, falls es noch nicht vorhanden ist
if ! echo "$PATH" | grep -q "$HOME/bin"; then
  echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.bashrc"
  source "$HOME/.bashrc"
fi

# Aktualisiere den Desktop-Datenbank-Cache
update-desktop-database "$HOME/.local/share/applications"

echo "Installation abgeschlossen. DrawerCapture ist jetzt im Launcher verfügbar und kann mit 'drawer-capture' von der Kommandozeile aus gestartet werden."