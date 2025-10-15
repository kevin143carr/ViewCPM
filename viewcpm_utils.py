import os
from tkinter import messagebox

def list_host_files(folder_path):
    """
    Returns a list of files in the host folder with their sizes.
    Output: [(filename, size), ...]
    """
    file_list = []
    try:
        for f in os.listdir(folder_path):
            full_path = os.path.join(folder_path, f)
            if os.path.isfile(full_path):
                size = os.path.getsize(full_path)
                file_list.append((f, size))
    except Exception as e:
        print(f"Error listing host files: {e}")
    return file_list

def is_executable_file(path):
    """Check if path exists and is executable."""
    return os.path.isfile(path) and os.access(path, os.X_OK)

def is_directory(path):
    """Check if path exists and is a directory."""
    return os.path.isdir(path)

def check_paths(samdisk_path, cpmtools_path):
    """Check SAMdisk and cpmtools paths. Returns (ok: bool, messages: list)."""
    messages = []

    if not samdisk_path or not is_executable_file(samdisk_path):
        messages.append("SAMdisk path is missing or not executable.")

    if not cpmtools_path or not is_directory(cpmtools_path):
        messages.append("cpmtools path is missing or not a directory.")
    else:
        # check required binaries
        for exe in ["cpmls", "cpmcp"]:
            exe_path = os.path.join(cpmtools_path, exe)
            if not is_executable_file(exe_path):
                messages.append(f"{exe} not found or not executable in cpmtools directory.")

    return len(messages) == 0, messages

def show_path_check_result(ok, messages):
    """Display results in a messagebox."""
    if ok:
        messagebox.showinfo("Success", "SAMdisk and cpmtools paths are valid!")
    else:
        messagebox.showerror("Path Check Failed", "\n".join(messages))
