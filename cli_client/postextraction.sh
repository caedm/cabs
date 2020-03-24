#!/bin/sh

echo "postextraction"

# For MacOS
DESTINATION="/Applications/RGSConnect"

# Create destination folder
mkdir -p ${DESTINATION}

# Copy files to destination
cp rgsconnect.py "$DESTINATION"
cp cert.pem "$DESTINATION"
cp CABS_client.conf "$DESTINATION"

# For MacOS
cp rgs.sh /usr/local/bin/rgs
