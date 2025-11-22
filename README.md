# ViewCPM

**ViewCPM** is a graphical disk image manager for CP/M systems. It allows users to open, browse, modify, and export CP/M-compatible disk images. The tool supports several disk formats and integrates with `cpmtools` and `dskconv` to enable format conversion and editing operations.  Currently I am using this to work with my Kaypro II and Flash Floppy.  I also have other CP/M machines, TRS-80 Model 4P and a obscure 8"(er) called an EXO, which almost nobody knows about.  I will keep this updated about what is working and what is not.  Also check out FFMaker, which strictly converts image files, it can be found at https://github.com/kevin143carr/FF-Maker

---

## 🧩 Features

- **Open and View** `.TD0` (TeleDisk) disk images.
- **Automatic Conversion** from `.TD0` → `.IMD` for editable access.
- **Edit Disk Contents** — Add, delete, or extract files within the disk image.
- **Export to DSK** — Convert and save `.IMD` images as `.DSK` (EDSK) format for use with FlashFloppy, emulators, or other retro tools.
- **Integrated Tools** — Uses `cpmtools` and `dskconv` for cross-format conversions.
- **JSON Preferences** — Configure paths, diskdefs, and conversion parameters in a simple `viewcpm_prefs.json` file.

---

## ⚙️ How It Works

1. **Open a TD0 File**
   - When a `.TD0` disk image is selected, ViewCPM converts it into an intermediate `.IMD` file in a temporary directory.
   - This `.IMD` file becomes editable and viewable in the GUI.

2. **Edit Disk Contents**
   - ViewCPM uses `cpmtools` to allow adding, deleting, and extracting files inside the disk image.

3. **Export to DSK**
   - When you click the **Export** button, ViewCPM converts the `.IMD` file to `.DSK` using `dskconv`.
   - You can select a destination folder for the `.DSK` file via a standard file browser dialog.

---

## 🛠️ Preferences (`viewcpm_prefs.json`)

Example configuration:

```json
{
  "cpmtools_path": "support/libdskcpmtools",
  "last_host_folder": "/Users/whomever/projects/python/ViewCPM/input/KPIIFiles",
  "last_image_folder": "/Users/whomever/projects/python/ViewCPM/input/TD0",
  "diskdefs_path": "support/libdskcpmtools/diskdefs",
  "disk_format": "kpii",
  "last_disk_image": "/Users/whomever/projects/python/ViewCPM/input/TD0/kpii-149.td0",
  "tele.convparams": "dskconv -itype tele -otype imd {infile} {outfile}",
  "imd.convparams": "dskconv -itype imd -otype edsk {infile} {outfile}",
  "dsk.convparams": "dskconv -itype dsk -otype imd {infile} {outfile}",
  "imagedisk_command": "dskconv -itype imd -otype dsk {infile} {outfile}",
  "dsk_command": "dskconv -itype dsk -otype imd {infile} {outfile}"
}
```

---

## 🧮 Conversion Commands

| Conversion Type | Command Template |
|-----------------|------------------|
| TD0 → IMD | `dskconv -itype tele -otype imd {infile} {outfile}` |
| IMD → DSK | `dskconv -itype imd -otype edsk {infile} {outfile}` |
| DSK → IMD | `dskconv -itype dsk -otype imd {infile} {outfile}` |

---

## 🧱 Technical Overview

- **Language:** Python 3  
- **GUI Framework:** Tkinter  
- **Dependencies:** `cpmtools`, `dskconv`, `libdsk`  
- **Structure:**
  - `viewcpm.py` — main GUI
  - `viewcpm_logic.py` — conversion logic and file handling
  - `viewcpm_prefs.py` — preferences and configuration handling
  - `viewcpm_utils.py` — helper utilities

---

## 📦 Future Enhancements

- Native `.IMD` and `.DSK` editors
- Drag-and-drop file support
- Improved progress dialogs and status indicators
- Disk info and sector map visualization

---

## 🧰 Requirements

- Python 3.8+  
- `cpmtools` and `dskconv` available in the specified tools path  
- macOS, Linux, or Windows with proper path configuration

---

# ViewCPM macOS Build Instructions

This section explains how to build ViewCPM for macOS using the provided `nuitka_build_osx.sh` script. The script supports multiple build types: standard binaries, macOS `.app` bundles, and PyInstaller executables with external support files.

---

## Running the Build Script

```bash
./nuitka_build_osx.sh
```

The script will prompt you to select a build type:

```
Select build type:
1) Standard binary application (Nuitka standalone onefile)
2) macOS .app bundle (Nuitka standalone)
3) mac executable with external support (PyInstaller executable)
4) Build all
```

Enter the number corresponding to your desired build.

---

## Build Options

### 1. Standard Binary (Nuitka Standalone Onefile)

- Produces a single `.bin` file using Nuitka.
- Includes the `support/` folder and `viewcpm_prefs.json` internally in the binary.
- Outputs are staged in `staging/`, and a zip file `viewcpm_osx_bin.zip` is created in `dist/`.
- A helper script `runviewcpm.sh` is generated to run the binary from its folder.

```bash
python3 -m nuitka --onefile --standalone \
    --enable-plugin=tk-inter --output-dir=staging \
    --include-data-files=viewcpm_prefs.json.osx=viewcpm_prefs.json \
    --include-data-dir=support=support \
    --output-filename=viewcpm.bin viewcpm.py
```

---

### 2. macOS `.app` Bundle (Nuitka Standalone)

- Creates a macOS `.app` bundle for ViewCPM.
- Includes the `support/` folder and `viewcpm_prefs.json` inside the `.app/Contents/Resources/`.
- Outputs are staged in `staging/`, and a zip file `viewcpm_osx_app.zip` is created in `dist/`.

```bash
python3 -m nuitka --standalone --enable-plugin=tk-inter --output-dir=staging \
    --macos-create-app-bundle --macos-app-name=ViewCPM \
    --macos-app-icon=viewcpmicon.png \
    --include-data-files=viewcpm_prefs.json.osx=viewcpm_prefs.json \
    --include-data-dir=support=support viewcpm.py
```

---

### 3. PyInstaller Executable with External Support

- Produces a single PyInstaller executable (`viewcpm`) placed in the `staging/` folder.
- **External resources** (`support/` folder and `viewcpm_prefs.json`) are kept next to the binary, not bundled internally.
- This allows users to modify configuration or support files without rebuilding the binary.
- A zip file `viewcpm_osx_exec.zip` is created in `dist/`.

```bash
pyinstaller --onefile --name viewcpm --distpath staging viewcpm.py
cp -R ../support staging/
cp ../viewcpm_prefs.json.osx staging/viewcpm_prefs.json
```

---

### 4. Build All

- Option `4` runs all three build types sequentially.
- Each build is staged in `staging/` temporarily, zipped, and then moved to `dist/`.

---

## Staging and Distribution

- `staging/` folder: temporary folder used during builds.
- `dist/` folder: contains the final zip files for distribution:

```
dist/
 ├─ viewcpm_osx_bin.zip
 ├─ viewcpm_osx_app.zip
 └─ viewcpm_osx_exec.zip
```

- After each build, `staging/` is cleaned and recreated for the next build.

---

## Notes

- **External resources**: Only the PyInstaller executable keeps resources external; Nuitka binaries bundle resources inside the binary or `.app`.
- **Run script**: For standard binaries, `runviewcpm.sh` is created inside `staging/` to simplify execution.

```
./runviewcpm.sh
```

- Make sure all required files (`support/` and `viewcpm_prefs.json`) exist in the expected locations before building.

---

## Cleanup

The script automatically removes intermediate build folders:

```bash
viewcpm.build
viewcpm.dist
viewcpm.onefile-build
staging/
```

Final distributions remain in `dist/`.

## 🪪 License

MIT License © 2025 Kevin Carr

---

## 🌐 Repository

**GitHub:** [https://github.com/kevin143carr/ViewCPM](https://github.com/kevin143carr/ViewCPM)
