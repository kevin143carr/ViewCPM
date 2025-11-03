# viewcpm_logic.py
import os
import subprocess
import shutil
import viewcpm_prefs as prefs
import shlex

# ----------------------------
# Utilities
# ----------------------------
def run_command(cmd, use_diskdefs=False, prefs=None):
    """
    Run shell command and return (success, output).

    Parameters:
        cmd (str): Command to run.
        cwd (str|None): Optional working directory.
        use_diskdefs (bool): If True, set CPMTOOLS to prefs['diskdefs_path'].
        prefs (dict|None): Preferences dict containing diskdefs_path.
    """
    try:
        env = os.environ.copy()
        if use_diskdefs and prefs:
            env['CPMTOOLS'] = prefs
            
        if use_diskdefs:
            cwd = os.path.dirname(prefs)  # get directory
        else:
            cwd = None

        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
            env=env
        )
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

# ----------------------------
# Export IMD to DSK
# ----------------------------

def convert_disk_image(cmd_template, tools_path, imd_path, out_path):
    """
    Convert an .IMD file to .DSK using the dskconv-style command defined in prefs.json.
    cmd_template: template like `"dskconv -otype dsk {infile} {outfile}"`
    tools_path: folder where dskconv resides
    imd_path: input IMD file
    out_path: final DSK output path chosen by user
    """

    if not cmd_template or not tools_path:
        raise ValueError("Missing 'dskconv_command' or 'cpmtools_path' in prefs")

    # Extract the executable name from the command template
    cmd_words = shlex.split(cmd_template)
    exe_name = cmd_words[0]
    converter_path = os.path.join(tools_path, exe_name)

    if not os.path.isfile(converter_path):
        raise FileNotFoundError(f"Converter executable not found: {converter_path}")

    # Fill template placeholders
    cmd_filled = cmd_template.format(infile=imd_path, outfile=out_path)

    # Replace exe name with full path
    cmd_parts = shlex.split(cmd_filled)
    cmd_parts[0] = converter_path

    # Quote parts safely for execution
    cmd = " ".join(f'"{part}"' for part in cmd_parts)

    # Run the command
    success, output = run_command(cmd)

    if not success:
        raise RuntimeError(f"DSK export failed:\n{output}")

    return out_path


def convert_dsk_to_imd(cmd_template, tools_path, image_path):
    """
    Convert a .DSK/.TD0 file to IMD using the converter defined in prefs.json.
    prefs: dict containing 'teledisk_command' and 'cpmtools_path'
    Returns path to converted IMD/RAW file in tmp folder.
    """

    if not cmd_template or not tools_path:
        raise ValueError("Missing 'teledisk_command' or 'cpmtools_path' in prefs")

    # Extract the converter executable name from the first word of the command
    cmd_words = shlex.split(cmd_template)
    exe_name = cmd_words[0]
    converter_path = os.path.join(tools_path, exe_name)

    if not os.path.isfile(converter_path):
        raise FileNotFoundError(f"Converter executable not found: {converter_path}")

    # Prepare output file path in temp folder
    tmp_dir = get_tmp_folder()
    imd_filename = os.path.splitext(os.path.basename(image_path))[0] + ".IMD"
    imd_path = os.path.join(tmp_dir, imd_filename)

    # Fill in infile/outfile placeholders
    cmd_filled = cmd_template.format(infile=image_path, outfile=imd_path)

    # Replace the bare exe name with the full path
    cmd_parts = shlex.split(cmd_filled)
    cmd_parts[0] = converter_path

    # Rebuild safely quoted command
    cmd = " ".join(f'"{part}"' for part in cmd_parts)

    # Run the command
    success, output = run_command(cmd)

    if not success:
        raise RuntimeError(f"Conversion failed:\n{output}")

    return imd_path

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
    success, output = run_command(cmd, True, prefs.get_pref("diskdefs_path"))
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

def insert_file(cpmtools_path, image_path, filename, disk_format="kpii"):
    """
    Insert file from host folder into RAW image using cpmtools.
    Assumes current directory contains the source file.
    """
    cpmcp = os.path.join(cpmtools_path, "cpmcp")
    if not os.path.isfile(cpmcp):
        raise FileNotFoundError(f"cpmcp not found in {cpmtools_path}")
    
    finalpath = os.path.basename(filename) 
    
    cmd = f'"{cpmcp}" -f {disk_format} "{image_path}" "{filename}" 0:{finalpath}'
    success, output = run_command(cmd)
    if not success:
        raise RuntimeError(f"Insert failed:\n{output}")

def extract_file(cpmtools_path, image_path, filename, dest_folder):
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

def delete_file(cpmtools_path, image_path, filename, disk_format="kpii"):
    """
    Delete file from RAW image using cpmtools.
    """
    cpmrm = os.path.join(cpmtools_path, "cpmrm")
    if not os.path.isfile(cpmrm):
        raise FileNotFoundError(f"cpmrm not found in {cpmtools_path}")
    cmd = f'"{cpmrm}" -f {disk_format} "{image_path}" 0:"{filename}"'
    success, output = run_command(cmd)
    if not success:
        raise RuntimeError(f"Delete failed:\n{output}")
    
def get_disk_info(cpmtools_path, image_path, disk_format="kpii"):
    """
    Returns (disk_size_bytes, free_bytes) of RAW image using cpmls -s or cpmtools.
    """
    if not cpmtools_path or not os.path.isdir(cpmtools_path):
        raise FileNotFoundError("CP/M tools directory not found.")

    cpmls = os.path.join(cpmtools_path, "cpmls")
    if not os.path.isfile(cpmls):
        raise FileNotFoundError(f"cpmls not found in {cpmtools_path}")

    # cpmls -f format -s image  returns size info
    cmd = f'"{cpmls}" -f {disk_format} -l "{image_path}"'
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

