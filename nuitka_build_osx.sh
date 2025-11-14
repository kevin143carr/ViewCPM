#!/usr/bin/env bash
set -e

echo "************************ BUILDING MAC/LINUX COMPATIBLE VIEWCPM *******************************"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/staging"
EXE_NAME="viewcpm"
ZIP_NAME="viewcpm_osx.zip"

echo "Creating staging folder..."
mkdir -p "$BUILD_DIR"

echo "***************************** BUILDING EXECUTABLE WITH NUITKA ********************************"
# macOS users may need:  --clang  (if GCC is not present)
python3 -m nuitka \
    --onefile \
    --standalone \
    --enable-plugin=tk-inter \
    --output-dir="$BUILD_DIR" \
    --output-filename=viewcpm.app \
    viewcpm.py

cd "$BUILD_DIR"

echo "Copying prefs..."
# Your repo uses viewcpm_prefs.json.linux and viewcpm_prefs.json.mac presumably
# If you want a single file for both UNIX systems, adjust this.
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    cp ../viewcpm_prefs.json.linux viewcpm_prefs.json
else
    cp ../viewcpm_prefs.json.osx viewcpm_prefs.json
fi

echo "Copying support files..."
mkdir -p support/osx/libdskcpmtools
cp -R ../support/osx/libdskcpmtools/* support/osx/libdskcpmtools/

echo "***************************** CLEANING UP FOLDERS *************************************"
# rm -rf viewcpm.build
# rm -rf viewcpm.dist
# rm -rf viewcpm.onefile-build

echo "***************************** COMPRESSING DISTRIBUTION ********************************"
zip -r "$ZIP_NAME" .
echo "***************************** MOVING DISTRIBUTION **************************************"
mv "$ZIP_NAME" ../dist
cd ..
echo "Cleaning staging..."
## rm -rf staging

echo "Done!"

