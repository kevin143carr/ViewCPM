#!/usr/bin/env bash
set -e

echo "************************ BUILDING MAC/LINUX COMPATIBLE VIEWCPM *******************************"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/staging"
EXE_NAME="viewcpm"
ZIP_NAME="viewcpm_osx.zip"
BASE_NAME="${ZIP_NAME%.zip}"

echo "Creating staging folder..."
rm -rf dist/$ZIP_NAME
rm -rf dist/$BASE_NAME
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo "***************************** BUILDING EXECUTABLE WITH NUITKA ********************************"
# macOS users may need:  --clang  (if GCC is not present)
# python3 -m nuitka --onefile --standalone --enable-plugin=tk-inter --output-dir="$BUILD_DIR" \
#    --output-filename=viewcpm.bin viewcpm.py

# TRYING TO MAKE AN MAC.APP BUT NO SUCCESS
python3 -m nuitka --standalone --enable-plugin=tk-inter --output-dir="$BUILD_DIR" \
    	--macos-create-app-bundle --macos-app-name="ViewCPM" \
	--macos-app-icon=viewcpmicon.png \
	--include-data-files=viewcpm_prefs.json.osx=viewcpm_prefs.json \
	--include-data-dir=support=support viewcpm.py

cd "$BUILD_DIR"

echo "Copying prefs..."
# Your repo uses viewcpm_prefs.json.linux and viewcpm_prefs.json.mac presumably
# If you want a single file for both UNIX systems, adjust this.
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    cp ../viewcpm_prefs.json.linux viewcpm_prefs.json
else
    cp ../viewcpm_prefs.json.osx viewcpm_prefs.json
fi

cp -R ../support .

# Define the name of the script you want to create
SCRIPT_NAME="runviewcpm.sh"
BINARY_NAME="viewcpm.bin"

# 1. Create the file using a heredoc with a quoted marker ('EOF')
# This ensures that "$0" is written literally into the new script
# and is interpreted only when viewcpm.sh is *executed*, not when created.
cat <<'EOF' > "$SCRIPT_NAME"
#!/usr/bin/env bash
set -e

# Change to the directory where the script is located to find the binary
cd "$(dirname "$0")"
pwd
./viewcpm.bin
EOF

# 2. Grant execute permissions to the new script
chmod +x "$SCRIPT_NAME"

# Note: Ensure viewcpm.bin also has execute permissions (chmod +x viewcpm.bin)
# before running the newly created script.

echo "Script '$SCRIPT_NAME' created and made executable."

echo "***************************** CLEANING UP FOLDERS *************************************"
rm -rf viewcpm.build
rm -rf viewcpm.dist
rm -rf viewcpm.onefile-build

echo "***************************** COMPRESSING DISTRIBUTION ********************************"
zip -r "$ZIP_NAME" .
echo "***************************** MOVING DISTRIBUTION **************************************"
mv "$ZIP_NAME" ../dist
cd ..
echo "Cleaning staging..."
rm -rf staging

echo "Done!"

