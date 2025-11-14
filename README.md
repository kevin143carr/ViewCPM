# ViewCPM

**ViewCPM** is a graphical disk image manager for CP/M systems. It allows users to open, browse, modify, and export CP/M-compatible disk images. The tool supports several disk formats and integrates with `cpmtools` and `dskconv` to enable format conversion and editing operations.  Currently I am using this to work with my Kaypro II and Flash Floppy.  I also have other CP/M machines, TRS-80 Model 4P and a obscure 8"(er) called an EXO, which almost nobody knows about.  I will keep this updated about what is working and what is not.  Also check out FFMaker, which strictly converts image files, it can be found at https://github.com/kevin143carr/FF-Maker

---

## ðŸ§© Features

- **Open and View** `.TD0` (TeleDisk) disk images.
- **Automatic Conversion** from `.TD0` â†’ `.IMD` for editable access.
- **Edit Disk Contents** â€” Add, delete, or extract files within the disk image.
- **Export to DSK** â€” Convert and save `.IMD` images as `.DSK` (EDSK) format for use with FlashFloppy, emulators, or other retro tools.
- **Integrated Tools** â€” Uses `cpmtools` and `dskconv` for cross-format conversions.
- **JSON Preferences** â€” Configure paths, diskdefs, and conversion parameters in a simple `viewcpm_prefs.json` file.

---

## âš™ï¸� How It Works

1. **Open a TD0 File**
   - When a `.TD0` disk image is selected, ViewCPM converts it into an intermediate `.IMD` file in a temporary directory.
   - This `.IMD` file becomes editable and viewable in the GUI.

2. **Edit Disk Contents**
   - ViewCPM uses `cpmtools` to allow adding, deleting, and extracting files inside the disk image.

3. **Export to DSK**
   - When you click the **Export** button, ViewCPM converts the `.IMD` file to `.DSK` using `dskconv`.
   - You can select a destination folder for the `.DSK` file via a standard file browser dialog.

---

## ðŸ› ï¸� Preferences (`viewcpm_prefs.json`)

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
  "imagedisk_command": "dskconv -itype imd -otype dsk {infile} {outfile}"
}
```

---

## ðŸ§® Conversion Commands

| Conversion Type | Command Template |
|-----------------|------------------|
| TD0 â†’ IMD | `dskconv -itype tele -otype imd {infile} {outfile}` |
| IMD â†’ DSK | `dskconv -itype imd -otype edsk {infile} {outfile}` |
| DSK â†’ IMD | `dskconv -itype dsk -otype imd {infile} {outfile}` |

---

## ðŸ§± Technical Overview

- **Language:** Python 3  
- **GUI Framework:** Tkinter  
- **Dependencies:** `cpmtools`, `dskconv`, `libdsk`  
- **Structure:**
  - `viewcpm.py` â€” main GUI
  - `viewcpm_logic.py` â€” conversion logic and file handling
  - `viewcpm_prefs.py` â€” preferences and configuration handling
  - `viewcpm_utils.py` â€” helper utilities

---

## ðŸ“¦ Future Enhancements

- Native `.IMD` and `.DSK` editors
- Drag-and-drop file support
- Improved progress dialogs and status indicators
- Disk info and sector map visualization

---

## ðŸ§° Requirements

- Python 3.8+  
- `cpmtools` and `dskconv` available in the specified tools path  
- macOS, Linux, or Windows with proper path configuration

---

## ðŸªª License

MIT License Â© 2025 Kevin Carr

---

## ðŸŒ� Binaries for OSX,Windows and Linux

## ðŸŒ� Repository

**GitHub:** [https://github.com/kevin143carr/ViewCPM](https://github.com/kevin143carr/ViewCPM)
