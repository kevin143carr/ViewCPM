# viewcpm_logic.py
import os
import subprocess
import shutil
import viewcpm_prefs as prefs

# ----------------------------
# Utilities
# ----------------------------

def run_command(cmd):
    """Run shell command and return (success, output)."""
    try:
        result = subprocess.run(cmd, shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def get_tmp_folder():
    """Return path to tmp folder, create if missing."""
    tmp_dir = os.path.join(os.getcwd(), "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    cleanup_tmp(tmp_dir)
    return tmp_dir

def cleanup_tmp(tmp_dir):
    """Delete oldest files if more than prefs['max_tmp_files'] exist."""
    max_files = prefs.get_pref("max_tmp_files", 20)
    files = [os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir) if os.path.isfile(os.path.join(tmp_dir, f))]
    if len(files) <= max_files:
        return
    # sort by modification time
    files.sort(key=os.path.getmtime)
    for f in files[:len(files)-max_files]:
        os.remove(f)

# ----------------------------
# Conversion
# ----------------------------

def convert_dsk_to_raw(samdisk_path, image_path):
    """
    Convert a .DSK/.IMD file to RAW in tmp folder.
    Returns path to RAW file.
    """
    if not samdisk_path or not os.path.isfile(samdisk_path):
        raise FileNotFoundError("SAMdisk executable not found.")

    tmp_dir = get_tmp_folder()
    raw_filename = os.path.splitext(os.path.basename(image_path))[0] + ".RAW"
    raw_path = os.path.join(tmp_dir, raw_filename)

    cmd = f'"{samdisk_path}" "{image_path}" "{raw_path}"'
    success, output = run_command(cmd)
    if not success:
        raise RuntimeError(f"SAMdisk conversion failed:\n{output}")
    return raw_path

# ----------------------------
# CP/M Image Operations
# ----------------------------

def list_image_files(cpmtools_path, raw_path, disk_format="kpii"):
    """
    Use cpmls -l -f disk_format to list files in RAW image.
    Returns list of (filename, size) tuples.
    """
    if not cpmtools_path or not os.path.isdir(cpmtools_path):
        raise FileNotFoundError("CP/M tools directory not found.")

    cpmls = os.path.join(cpmtools_path, "cpmls")
    if not os.path.isfile(cpmls):
        raise FileNotFoundError(f"cpmls not found in {cpmtools_path}")

    cmd = f'"{cpmls}" -f {disk_format} -l "{raw_path}"'
    success, output = run_command(cmd)
    files = []
    if success:
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            size = 0
            try:
                size = int(parts[1])
            except ValueError:
                pass
            filename = parts[-1]  # last column
            files.append((filename, f"{size:,}"))  # format with commas
    return files

def insert_file(cpmtools_path, raw_path, filename):
    """
    Insert file from host folder into RAW image using cpmtools.
    Assumes current directory contains the source file.
    """
    cpmcp = os.path.join(cpmtools_path, "cpmcp")
    if not os.path.isfile(cpmcp):
        raise FileNotFoundError(f"cpmcp not found in {cpmtools_path}")
    cmd = f'"{cpmcp}" "{filename}" "{raw_path}"'
    success, output = run_command(cmd)
    if not success:
        raise RuntimeError(f"Insert failed:\n{output}")

def extract_file(cpmtools_path, raw_path, filename, dest_folder):
    """
    Extract file from RAW image to dest_folder.
    """
    cpmcp = os.path.join(cpmtools_path, "cpmcp")
    if not os.path.isfile(cpmcp):
        raise FileNotFoundError(f"cpmcp not found in {cpmtools_path}")
    dest_path = os.path.join(dest_folder, filename)
    cmd = f'"{cpmcp}" "{raw_path}" "{dest_path}"'
    success, output = run_command(cmd)
    if not success:
        raise RuntimeError(f"Extract failed:\n{output}")

def delete_file(cpmtools_path, raw_path, filename):
    """
    Delete file from RAW image using cpmtools.
    """
    cpmrm = os.path.join(cpmtools_path, "cpmrm")
    if not os.path.isfile(cpmrm):
        raise FileNotFoundError(f"cpmrm not found in {cpmtools_path}")
    cmd = f'"{cpmrm}" "{raw_path}" "{filename}"'
    success, output = run_command(cmd)
    if not success:
        raise RuntimeError(f"Delete failed:\n{output}")
    
def get_disk_info(cpmtools_path, raw_path, disk_format="kpii"):
    """
    Returns (disk_size_bytes, free_bytes) of RAW image using cpmls -s or cpmtools.
    """
    if not cpmtools_path or not os.path.isdir(cpmtools_path):
        raise FileNotFoundError("CP/M tools directory not found.")

    cpmls = os.path.join(cpmtools_path, "cpmls")
    if not os.path.isfile(cpmls):
        raise FileNotFoundError(f"cpmls not found in {cpmtools_path}")

    # cpmls -f format -s image  returns size info
    cmd = f'"{cpmls}" -f {disk_format} -l "{raw_path}"'
    success, output = run_command(cmd)
    if not success:
        return 0, 0

    # Parse output like "size: 12288 free: 4096"
    import re
    disk_size = 0
    free_size = 0
    match = re.search(r'size:\s*(\d+)\s+free:\s*(\d+)', output)
    if match:
        disk_size = int(match.group(1))
        free_size = int(match.group(2))
    return disk_size, free_size

