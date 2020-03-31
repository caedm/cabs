#!/bin/sh

echo "Files extracted; beginning setup"

# For MacOS
DESTINATION="/Applications/RGSConnect"

# Create destination folder
mkdir -p "$DESTINATION"
chmod a+rx "$DESTINATION"

# Copy files to destination
cp rgsconnect.py "$DESTINATION"
chmod a+rx "$DESTINATION/rgsconnect.py"
cp rgsconnect_legacy.py "$DESTINATION"
chmod a+rx "$DESTINATION/rgsconnect_legacy.py"
cp cert.pem "$DESTINATION"
chmod a+r "$DESTINATION/cert.pem"
cp CABS_client.conf "$DESTINATION"
chmod a+r "$DESTINATION/CABS_client.conf"

# For MacOS
cp rgs.sh /usr/local/bin/rgs
chmod a+rx /usr/local/bin/rgs

echo "Installation Complete!"
