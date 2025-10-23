import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import viewcpm_prefs as prefs  # safe self-import for get/set_pref
import viewcpm_utils as utils

PREF_FILE = "viewcpm_prefs.json"

def load_prefs():
    """Load preferences from JSON file."""
    if os.path.exists(PREF_FILE):
        with open(PREF_FILE, "r") as f:
            return json.load(f)
    return {}

def save_prefs(prefs):
    """Save preferences to JSON file."""
    with open(PREF_FILE, "w") as f:
        json.dump(prefs, f, indent=2)

def get_pref(key, default=None):
    prefs = load_prefs()
    return prefs.get(key, default)

def set_pref(key, value):
    prefs = load_prefs()
    prefs[key] = value
    save_prefs(prefs)
    
    
def check_paths_button(parent):
    ok, messages = utils.check_paths(parent.teledisk_command, parent.cpmtools_path)
    utils.show_path_check_result(ok, messages)
      
    # ----------------------------
    # Preferences
    # ----------------------------
def open_prefs_dialog(parent):
    """Show the Preferences dialog window."""
    dialog = tk.Toplevel(parent)
    dialog.title("Preferences")
    dialog.transient(parent)
    dialog.grab_set()  # make modal

    # Load current prefs
    teledisk_cmd = prefs.get_pref("teledisk_command", "")
    imagedisk_cmd = prefs.get_pref("imagedisk_command", "")
    dsk_cmd = prefs.get_pref("dsk_command", "")
    cpmtools_path = prefs.get_pref("cpmtools_path", "")
    diskdefs_path = prefs.get_pref("diskdefs_path", "")

    # Teledisk
    tk.Label(dialog, text="Teledisk (.td0) command:").pack(padx=10, pady=(10,0), anchor="w")
    entry_teledisk = tk.Entry(dialog, width=60)
    entry_teledisk.pack(padx=10, pady=2)
    entry_teledisk.insert(0, teledisk_cmd)

    # ImageDisk
    tk.Label(dialog, text="ImageDisk (.imd) command:").pack(padx=10, pady=(10,0), anchor="w")
    entry_imagedisk = tk.Entry(dialog, width=60)
    entry_imagedisk.pack(padx=10, pady=2)
    entry_imagedisk.insert(0, imagedisk_cmd)

    # DSK
    tk.Label(dialog, text="DSK (.dsk) command:").pack(padx=10, pady=(10,0), anchor="w")
    entry_dskdisk = tk.Entry(dialog, width=60)
    entry_dskdisk.pack(padx=10, pady=2)
    entry_dskdisk.insert(0, dsk_cmd)

    # cpmtools
    tk.Label(dialog, text="cpmtools Path:").pack(padx=10, pady=(10,0), anchor="w")
    entry_cpmtools = tk.Entry(dialog, width=60)
    entry_cpmtools.pack(padx=10, pady=2)
    entry_cpmtools.insert(0, cpmtools_path)

    def browse_cpmtools():
        path = filedialog.askdirectory(title="Select cpmtools directory")
        if path:
            entry_cpmtools.delete(0, tk.END)
            entry_cpmtools.insert(0, path)

    tk.Button(dialog, text="Browse...", command=browse_cpmtools).pack(padx=10, pady=2, anchor="w")

    # Diskdefs
    tk.Label(dialog, text="Diskdefs File:").pack(padx=10, pady=(10,0), anchor="w")
    entry_diskdefs = tk.Entry(dialog, width=60)
    entry_diskdefs.pack(padx=10, pady=2)
    entry_diskdefs.insert(0, diskdefs_path)

    def browse_diskdefs():
        path = filedialog.askopenfilename(
            title="Select diskdefs file",
            filetypes=[("All files", "*.*")]
        )
        if path:
            entry_diskdefs.delete(0, tk.END)
            entry_diskdefs.insert(0, path)

    tk.Button(dialog, text="Browse...", command=browse_diskdefs).pack(padx=10, pady=2, anchor="w")

    # --- Save & Close / Check Paths ---
    def save_all_prefs():
        prefs.set_pref("teledisk_command", entry_teledisk.get())
        prefs.set_pref("imagedisk_command", entry_imagedisk.get())
        prefs.set_pref("dsk_command", entry_dskdisk.get())
        prefs.set_pref("cpmtools_path", entry_cpmtools.get())
        prefs.set_pref("diskdefs_path", entry_diskdefs.get())
        dialog.destroy()

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=10, pady=10, fill="x")

    tk.Label(button_frame).pack(side="left", expand=True)

    # parent is the main app, so we can call its check_paths_button
    tk.Button(button_frame, text="Check Paths",
              command=lambda: check_paths_button(parent)).pack(side=tk.RIGHT, padx=5)

    tk.Button(button_frame, text="Save & Close", command=save_all_prefs).pack(side=tk.RIGHT, padx=5)

    # Center the dialog on parent
    dialog.update_idletasks()
    w = dialog.winfo_width()
    h = dialog.winfo_height()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
    dialog.geometry(f"{w}x{h}+{x}+{y}")
    dialog.deiconify()

    dialog.wait_window()

