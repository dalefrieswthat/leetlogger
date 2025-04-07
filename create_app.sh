#!/bin/bash

# Create necessary directories
mkdir -p LeetLogger.app/Contents/MacOS
mkdir -p LeetLogger.app/Contents/Resources

# First convert SVG to PNG using ImageMagick
convert -background none -resize 1024x1024 icon.svg icon.png

# Convert PNG to ICNS
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset
rm -R icon.iconset

# Move icon to Resources
mv icon.icns LeetLogger.app/Contents/Resources/

# Create Info.plist
cat > LeetLogger.app/Contents/Info.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>LeetLogger</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.leet.logger</string>
    <key>CFBundleName</key>
    <string>LeetLogger</string>
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
cat > LeetLogger.app/Contents/MacOS/LeetLogger << 'EOF'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/../.."
python3 main.py
EOF

# Make the launcher executable
chmod +x LeetLogger.app/Contents/MacOS/LeetLogger

echo "Application bundle created successfully!"
echo "You can now move LeetLogger.app to your Applications folder" 