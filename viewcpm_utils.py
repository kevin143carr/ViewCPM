import os
import sys
import platform
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_resource_path(relative_path):
    """
    Returns an absolute path to a resource inside the macOS .app bundle,
    or inside the working directory when running from source.
    """
    # Running inside Nuitka macOS .app
    if getattr(sys, "frozen", False):
        # Go from MacOS/ → Contents/Resources/
        base_path = os.path.join(os.path.dirname(sys.executable), "..", "Resources")
        base_path = os.path.abspath(base_path)
    else:
        # Running from source tree
        base_path = os.path.dirname(os.path.abspath(__file__))

    final_path = os.path.join(base_path, relative_path)
    logger.debug(f"Requested: {relative_path}\n"
                f"    Base Path:  {base_path}\n"
                f"    Final Path: {final_path}\n\n")

    return os.path.join(base_path, relative_path)

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
    """Check cpmtools paths. Returns (ok: bool, messages: list)."""
    messages = []

    if not cpmtools_path or not is_directory(cpmtools_path):
        messages.append("cpmtools path is missing or not a directory.")
    else:
        # On Windows, executables end with .exe
        is_windows = platform.system().lower().startswith("win")
        suffix = ".exe" if is_windows else ""

        for exe in ["cpmls", "cpmcp"]:
            exe_path = os.path.join(cpmtools_path, exe + suffix)
            if not is_executable_file(exe_path):
                messages.append(f"{exe + suffix} not found or not executable in cpmtools directory.")

    return len(messages) == 0, messages

def show_path_check_result(iparent, ok, messages):
    """Display results in a messagebox."""
    if ok:
        messagebox.showinfo("Success", "cpmtools paths are valid!", parent=iparent)
    else:
        messagebox.showerror("Path Check Failed", "\n".join(messages), parent=iparent)
        
def parse_size(value):
    try:
        return int(str(value).replace(',', '').strip())
    except (ValueError, TypeError):
        return 0
