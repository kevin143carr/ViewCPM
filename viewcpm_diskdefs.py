# viewcpm_diskdefs.py
import re
import os

class DiskDefsManager:
    def __init__(self, diskdefs_path):
        self.diskdefs_path = diskdefs_path
        self.diskdefs = []
        if os.path.exists(diskdefs_path):
            self._parse_diskdefs()

    def _parse_diskdefs(self):
        with open(self.diskdefs_path, "r", encoding="utf-8") as f:
            content = f.read()

        pattern = r"diskdef\s+(\S+)(.*?)end"
        matches = re.findall(pattern, content, re.DOTALL)
        for name, body in matches:
            entry = {"name": name}
            for line in body.strip().splitlines():
                parts = line.strip().split()
                if len(parts) == 2:
                    key, value = parts
                    try:
                        entry[key] = int(value)
                    except ValueError:
                        entry[key] = value
            # Compute disk size if possible
            if all(k in entry for k in ("seclen", "tracks", "sectrk")):
                entry["disksize"] = entry["seclen"] * entry["tracks"] * entry["sectrk"]
            self.diskdefs.append(entry)

    def get_disk_names(self):
        return [d["name"] for d in self.diskdefs]

    def get_disk_info(self, name):
        for d in self.diskdefs:
            if d["name"] == name:
                return d
        return None
