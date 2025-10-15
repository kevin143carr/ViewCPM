# viewcpm_diskops.py
import os
import threading
import viewcpm_logic as logic

class DiskImageManager:
    def __init__(self, cpmtools_path, status_callback=None):
        """
        cpmtools_path: Path to CP/M tools directory
        status_callback: function(str) to update status bar
        """
        self.cpmtools_path = cpmtools_path
        self._current_raw_path = None
        self.status_callback = status_callback or (lambda msg: None)

    def set_current_raw(self, raw_path):
        self._current_raw_path = raw_path

    # --- Insert ---
    def insert_files(self, host_folder, files, callback=None):
        if not self._current_raw_path:
            raise RuntimeError("No disk image loaded.")
        def task():
            try:
                for f in files:
                    host_file = os.path.join(host_folder, f)
                    logic.insert_file(self.cpmtools_path, self._current_raw_path, host_file)
                self.status_callback("Insert complete.")
            except Exception as e:
                self.status_callback(f"Insert failed: {e}")
            if callback:
                callback()
        threading.Thread(target=task, daemon=True).start()

    # --- Extract ---
    def extract_files(self, files, dest_folder, callback=None):
        if not self._current_raw_path:
            raise RuntimeError("No disk image loaded.")
        def task():
            try:
                for f in files:
                    logic.extract_file(self.cpmtools_path, self._current_raw_path, f, dest_folder)
                self.status_callback("Extract complete.")
            except Exception as e:
                self.status_callback(f"Extract failed: {e}")
            if callback:
                callback()
        threading.Thread(target=task, daemon=True).start()

    # --- Delete ---
    def delete_files(self, files, callback=None):
        if not self._current_raw_path:
            raise RuntimeError("No disk image loaded.")
        def task():
            try:
                for f in files:
                    logic.delete_file(self.cpmtools_path, self._current_raw_path, f)
                self.status_callback("Delete complete.")
            except Exception as e:
                self.status_callback(f"Delete failed: {e}")
            if callback:
                callback()
        threading.Thread(target=task, daemon=True).start()
