#!/bin/bash

# Create necessary directories
mkdir -p DSAProblemTracker.app/Contents/MacOS
mkdir -p DSAProblemTracker.app/Contents/Resources

# Create Info.plist
cat > DSAProblemTracker.app/Contents/Info.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>DSAProblemTracker</string>
    <key>CFBundleIdentifier</key>
    <string>com.dsa.problemtracker</string>
    <key>CFBundleName</key>
    <string>DSA Problem Tracker</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Create the launcher script
cat > DSAProblemTracker.app/Contents/MacOS/DSAProblemTracker << 'EOF'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/../.."
python3 main.py
EOF

# Make the launcher executable
chmod +x DSAProblemTracker.app/Contents/MacOS/DSAProblemTracker

echo "Application bundle created successfully!"
echo "You can now move DSAProblemTracker.app to your Applications folder" 