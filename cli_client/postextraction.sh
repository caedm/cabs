#!/bin/sh

echo "Files extracted; beginning setup"

# For MacOS
DESTINATION="/Applications/RGSConnect"

# Create destination folder
mkdir -p "$DESTINATION"
chmod +rx "$DESTINATION"

# Copy files to destination
cp rgsconnect.py "$DESTINATION"
chmod +rx "$DESTINATION/rgsconnect.py"
cp cert.pem "$DESTINATION"
chmod +r "$DESTINATION/cert.pem"
cp CABS_client.conf "$DESTINATION"
chmod +r "$DESTINATION/CABS_client.conf"

# For MacOS
cp rgs.sh /usr/local/bin/rgs
chmod +rx /usr/local/bin/rgs
