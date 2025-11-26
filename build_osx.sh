#!/usr/bin/env bash
set -e
clear

echo "********************** PREPARING MAC OS BUILD *********************"
echo "Select build type:"
echo "1) Standard binary application (Nuitka with external resources)"
echo "2) MacOS .app bundle (Nuitka with internal resources)"
echo "3) Mac executable (Pyinstaller with exteranl resources)"
echo "4) Build all"
echo "x) To Exit"
read -p "Enter choice [1, 2, 3 or 4]: " choice

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/staging"

mkdir -p "$BUILD_DIR"
mkdir -p "$SCRIPT_DIR/dist"

# Function to create run script for .bin
build_runscript() {
    local script_name="runviewcpm.sh"
    cat <<'EOF' > "$script_name"
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
pwd
./viewcpm.bin
EOF
    chmod +x "$script_name"
    echo "Script '$script_name' created and made executable."
}

# Function to build either binary or app
build_viewcpm() {
    local build_type=$1  # "bin" or "app"
    
    if [[ "$build_type" == "bin" ]]; then
	ZIP_NAME="viewcpm_osx_bin.zip"
	echo "=== Building Standard Binary ==="
	
	# Clean old files safely
	[[ -f dist/$ZIP_NAME ]] && rm dist/$ZIP_NAME
	[[ -d dist/${ZIP_NAME%.zip} ]] && rm -rf dist/${ZIP_NAME%.zip}
	
	python3 -m nuitka --onefile --standalone \
	    --enable-plugin=tk-inter --output-dir="$BUILD_DIR" \
	    --include-data-files=viewcpm_prefs.json.osx=viewcpm_prefs.json \
	    --include-data-dir=support=support \
	    --output-filename=viewcpm.bin viewcpm.py
	
	cd "$BUILD_DIR"
	build_runscript
	
	cp -R ../support .
	cp ../viewcpm_prefs.json.osx viewcpm_prefs.json	

    elif [[ "$build_type" == "app" ]]; then
	ZIP_NAME="viewcpm_osx_app.zip"
	echo "=== Building macOS .app Bundle ==="
	
	# Clean old files safely
	[[ -f dist/$ZIP_NAME ]] && rm dist/$ZIP_NAME
	[[ -d dist/${ZIP_NAME%.zip} ]] && rm -rf dist/${ZIP_NAME%.zip}
	
	python3 -m nuitka --standalone --enable-plugin=tk-inter --output-dir="$BUILD_DIR" \
	    --macos-create-app-bundle --macos-app-name="ViewCPM" \
	    --macos-app-icon=viewcpmicon.png \
	    --include-data-files=viewcpm_prefs.json.osx=viewcpm_prefs.json \
	    --include-data-dir=support=support viewcpm.py
	
	cd "$BUILD_DIR"
    elif [[ "$build_type" == "exec" ]]; then
	ZIP_NAME="viewcpm_osx_exec.zip"
	echo "=== Building Pyinstaller Executable ==="
	pyinstaller --onefile --name viewcpm --distpath staging viewcpm.py
	rm -rf build
		
	# Clean old files safely
	[[ -f dist/$ZIP_NAME ]] && rm dist/$ZIP_NAME
	[[ -d dist/${ZIP_NAME%.zip} ]] && rm -rf dist/${ZIP_NAME%.zip}	
	cd $BUILD_DIR
	cp -R ../support .
	cp ../viewcpm_prefs.json.osx viewcpm_prefs.json
    else
	echo "Unknown build type: $build_type"
	exit 1
    fi

    rm -rf viewcpm.dist
    rm -rf viewcpm.build
    rm -rf viewcpm.onefile-build

    # Compress and move distribution
    zip -r "$ZIP_NAME" .
    mv "$ZIP_NAME" "$SCRIPT_DIR/dist/"
    cd "$SCRIPT_DIR"

    # Clean staging for next build
    rm -rf "$BUILD_DIR"
    mkdir -p "$BUILD_DIR"
}

# Handle user choice
case "$choice" in
    1) build_viewcpm "bin" ;;
    2) build_viewcpm "app" ;;
    3) build_viewcpm "exec" ;;
    4) 
	build_viewcpm "bin"
	build_viewcpm "app"
	build_viewcpm "exec"
	;;
    *)
	echo "Invalid choice. Exiting ..."
	exit 1
	;;
esac

# Final cleanup
rm -rf viewcpm.build viewcpm.dist viewcpm.onefile-build
rm -rf "$BUILD_DIR"

echo "Done! Distribution zip(s) are in dist/"
