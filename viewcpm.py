# viewcpm.py
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import viewcpm_logic as logic
import viewcpm_prefs as prefs
import viewcpm_utils as utils
from viewcpm_diskops import DiskImageManager
from viewcpm_diskdefs import DiskDefsManager


# ----------------------------
# Tooltip Helper
# ----------------------------
# ----------------------------
# Tooltip Helper (cross-platform safe)
# ----------------------------
def create_tooltip(widget, text):
    tooltip = tk.Toplevel(widget)
    tooltip.withdraw()
    tooltip.overrideredirect(True)

    label = tk.Label(
        tooltip,
        text=text,
        background="#ffffe0",   # light yellow background
        foreground="#000000",   # black text
        relief="solid",
        borderwidth=1,
        justify="left",
        wraplength=200,
        padx=4,
        pady=2
    )
    label.pack(ipadx=1)

    def show_tooltip(event):
        tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        tooltip.deiconify()

    def hide_tooltip(event):
        tooltip.withdraw()

    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)


class ViewCPMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ViewCPM - CP/M Disk Image Manager")         
        self.geometry("1000x600")
        self.minsize(800, 500)
    
        # Temporarily withdraw window until fully configured
        self.withdraw()
    
        # Preferences
        self.samdisk_path = prefs.get_pref("samdisk_path", "")
        self.cpmtools_path = prefs.get_pref("cpmtools_path", "")
        self.diskdefs_path = prefs.get_pref("diskdefs_path", "")
        
        # Make prefs available on self
        self.prefs = prefs  # <-- Add this line        
        
        # Diskdefs Manager
        self.diskdefs_manager = None
        if self.diskdefs_path and os.path.exists(self.diskdefs_path):
            self.diskdefs_manager = DiskDefsManager(self.diskdefs_path)        
    
        # Disk manager
        self.disk_manager = DiskImageManager(self.cpmtools_path, status_callback=self.status_callback)
    
        # UI
        self.create_toolbar()
        self.create_main_panes()
        self.create_statusbar()
        self.bind_events()
    
        # Schedule final window setup after idle
        self.after_idle(self.finish_setup)
        
    # -------------------------------------------------------------------------
    # Diskdefs loader
    # -------------------------------------------------------------------------
    def _load_diskdefs(self):
        """Load diskdefs from path in preferences if available."""
        diskdefs_path = self.prefs.get("diskdefs_path")
        if diskdefs_path and os.path.exists(diskdefs_path):
            self.diskdefs_manager = DiskDefsManager(diskdefs_path)
        else:
            self.diskdefs_manager = None    
        
    def finish_setup(self):
        # Center window
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
    
        # Deiconify and bring to front
        self.deiconify()
        self.lift()
        self.focus_force()        

    # ----------------------------
    # Toolbar
    # ----------------------------
    def create_toolbar(self):
        toolbar = ttk.Frame(self, padding=4)
        ttk.Button(toolbar, text="Open Folder", command=self.open_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Open Image", command=self.open_disk_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Insert", command=self.insert_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Extract", command=self.extract_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete", command=self.delete_file).pack(side=tk.LEFT, padx=2)
    
        # Get saved disk format from prefs
        saved_format = self.prefs.get_pref("disk_format", "")
        
        # --- Disk Format Dropdown ---
        disk_formats = []
        if self.diskdefs_manager:
            disk_formats = sorted(self.diskdefs_manager.get_disk_names(), key=str.lower)

    
        self.disk_format_var = tk.StringVar()
        self.disk_format_combo = ttk.Combobox(
            toolbar,
            textvariable=self.disk_format_var,
            values=disk_formats,
            state="readonly",
            width=20
        )
        
        if saved_format and saved_format in disk_formats:
            self.disk_format_combo.set(saved_format)
        else:
            self.disk_format_combo.set("Choose Disk Format")        
        
        self.disk_format_combo.pack(side=tk.LEFT, padx=6)
        create_tooltip(self.disk_format_combo, "Select a disk format from diskdefs")
    
        self.disk_format_combo.bind("<<ComboboxSelected>>", self.on_disk_format_selected)
        # ----------------------------
    
        settings_btn = ttk.Button(toolbar, text="Preferences", command=self.open_prefs_dialog)
        settings_btn.pack(side=tk.RIGHT, padx=2)
        create_tooltip(settings_btn, "Preferences for paths and other things")
    
        toolbar.pack(side=tk.TOP, fill=tk.X)

    # ----------------------------
    # Main Panes
    # ----------------------------
    def create_main_panes(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.paned = ttk.Panedwindow(main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Left: Host Folder
        left_frame = ttk.Frame(self.paned, padding=2)
        ttk.Label(left_frame, text="Host Folder", font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
        self.folder_tree = self.create_treeview(left_frame)
        self.folder_tree.pack(fill=tk.BOTH, expand=True)
        self.paned.add(left_frame, weight=1)

        # Right: Disk Image
        right_frame = ttk.Frame(self.paned, padding=2)
        ttk.Label(right_frame, text="Disk Image", font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
        self.image_tree = self.create_treeview(right_frame)
        self.image_tree.pack(fill=tk.BOTH, expand=True)
        # Disk info labels
        self.disk_info_var = tk.StringVar(value="Disk Size: N/A   Free Space: N/A")
        ttk.Label(right_frame, textvariable=self.disk_info_var).pack(anchor="w", pady=(2,0))       
        
        self.paned.add(right_frame, weight=1)        

    def create_treeview(self, parent):
        tree = ttk.Treeview(parent, columns=("name", "size"), show="headings")
        tree.heading("name", text="Filename")
        tree.heading("size", text="Size")
        tree.column("name", width=300, anchor="w")
        tree.column("size", width=100, anchor="e")

        yscroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    # ----------------------------
    # Status Bar
    # ----------------------------
    def create_statusbar(self):
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X)

    def status_callback(self, msg):
        self.status_var.set(msg)

    # ----------------------------
    # Event Bindings
    # ----------------------------
    def bind_events(self):
        # Drag-and-drop can be implemented later
        pass
    
    # ----------------------------
    # Disk Format Selection
    # ----------------------------
    def on_disk_format_selected(self, event):
        selected = self.disk_format_var.get()
        if not selected or not self.diskdefs_manager:
            return
    
        # Save to prefs
        self.prefs.set_pref("disk_format", selected)
    
        # Optional info popup
        info = self.diskdefs_manager.get_disk_info(selected)
        if info:
            disksize = info.get("disksize", 0)
            size_kb = disksize / 1024
            messagebox.showinfo(
                "Disk Format Selected",
                f"Selected: {selected}\nCalculated Size: {size_kb:.1f} KB"
            )

    # ----------------------------
    # Preferences
    # ----------------------------
    def open_prefs_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Preferences")         
    
        # SAMdisk
        tk.Label(dialog, text="SAMdisk Path:").pack(padx=10, pady=(10,0))
        entry_samdisk = tk.Entry(dialog, width=60)
        entry_samdisk.pack(padx=10, pady=2)
        entry_samdisk.insert(0, self.samdisk_path)
    
        def browse_samdisk():
            path = filedialog.askopenfilename(title="Select SAMdisk executable")
            if path:
                entry_samdisk.delete(0, tk.END)
                entry_samdisk.insert(0, path)
                self.samdisk_path = path
                prefs.set_pref("samdisk_path", path)
    
        tk.Button(dialog, text="Browse...", command=browse_samdisk).pack(padx=10, pady=2)
    
        # cpmtools
        tk.Label(dialog, text="cpmtools Path:").pack(padx=10, pady=(10,0))
        entry_cpmtools = tk.Entry(dialog, width=60)
        entry_cpmtools.pack(padx=10, pady=2)
        entry_cpmtools.insert(0, self.cpmtools_path)
    
        def browse_cpmtools():
            path = filedialog.askdirectory(title="Select cpmtools directory")
            if path:
                entry_cpmtools.delete(0, tk.END)
                entry_cpmtools.insert(0, path)
                self.cpmtools_path = path
                prefs.set_pref("cpmtools_path", path)
                self.disk_manager.cpmtools_path = path
    
        tk.Button(dialog, text="Browse...", command=browse_cpmtools).pack(padx=10, pady=2)
    
        # Diskdefs
        tk.Label(dialog, text="Diskdefs File:").pack(padx=10, pady=(10,0))
        entry_diskdefs = tk.Entry(dialog, width=60)
        entry_diskdefs.pack(padx=10, pady=2)
        entry_diskdefs.insert(0, prefs.get_pref("diskdefs_path", ""))
    
        def browse_diskdefs():
            path = filedialog.askopenfilename(
                title="Select diskdefs file",
                filetypes=[("All files", "*.*")]
            )
            if path:
                entry_diskdefs.delete(0, tk.END)
                entry_diskdefs.insert(0, path)
                prefs.set_pref("diskdefs_path", path)
                # Refresh dropdown if diskdefs changed
                self.diskdefs_path = path
                if os.path.exists(path):
                    self.diskdefs_manager = DiskDefsManager(path)
                    self.disk_format_combo["values"] = self.diskdefs_manager.get_disk_names()                
    
        tk.Button(dialog, text="Browse...", command=browse_diskdefs).pack(padx=10, pady=2)
    
        # Final actions
        tk.Button(dialog, text="Check Paths", command=self.check_paths_button).pack(padx=10, pady=10)
    
        # Center the dialog on parent
        dialog.update_idletasks()
        w = dialog.winfo_width()
        h = dialog.winfo_height()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        dialog.deiconify()
             

    def check_paths_button(self):
        ok, messages = utils.check_paths(self.samdisk_path, self.cpmtools_path)
        utils.show_path_check_result(ok, messages)

    # ----------------------------
    # Host Folder
    # ----------------------------
    def open_folder(self):
        last_folder = prefs.get_pref("last_host_folder", os.path.expanduser("~"))
        folder = filedialog.askdirectory(title="Select Host Folder", initialdir=last_folder)
        if folder:
            prefs.set_pref("last_host_folder", folder)
            for item in self.folder_tree.get_children():
                self.folder_tree.delete(item)
            files = utils.list_host_files(folder)
            for f, size in files:
                self.folder_tree.insert("", "end", values=(f, size))
            self.status_var.set(f"Loaded folder: {folder}")

    # ----------------------------
    # Disk Image
    # ----------------------------
    def open_disk_image(self):
        last_folder = prefs.get_pref("last_image_folder", os.path.expanduser("~"))
        filetypes = [("Disk Images", "*.dsk *.img *.imd"), ("All files", "*.*")]
        image_path = filedialog.askopenfilename(title="Select Disk Image", filetypes=filetypes, initialdir=last_folder)
        if image_path:
            prefs.set_pref("last_image_folder", os.path.dirname(image_path))
            self._current_image_path = image_path
            threading.Thread(target=self.convert_and_list_image, args=(image_path,), daemon=True).start()

    def convert_and_list_image(self, image_path):
        self.status_var.set(f"Converting {image_path} → tmp RAW")
        try:
            # Convert to RAW via SAMdisk
            raw_path = logic.convert_dsk_to_raw(self.samdisk_path, image_path)
            self._current_raw_path = raw_path
            self.disk_manager.set_current_raw(raw_path)
    
            # Determine selected disk format
            disk_format = "kpii"  # default
            if self.disk_format_var.get() and self.diskdefs_manager:
                disk_format = self.disk_format_var.get()
            self._current_disk_format = disk_format
    
            # List files from image
            files = logic.list_image_files(self.cpmtools_path, raw_path, disk_format=disk_format)
            # Populate tree AND refresh disk info
            self.image_tree.after(0, self.refresh_image_tree)
    
            # Compute disk size from diskdefs
            disk_size = 0
            if self.diskdefs_manager:
                disk_info = self.diskdefs_manager.get_disk_info(disk_format)
                if disk_info:
                    disk_size = disk_info.get("disksize", 0)
    
            # Sum file sizes to calculate remaining space
            used_size = sum(size for _, size in files)
            free_size = max(disk_size - used_size, 0) if disk_size else 0
    
            # Update GUI
            self.disk_info_var.set(
                f"Disk Size: {disk_size:,} bytes   Free Space: {free_size:,} bytes"
                if disk_size else "Disk Size: N/A   Free Space: N/A"
            )
            self.status_var.set(f"Loaded disk image: {image_path}")
    
        except Exception as e:
            self.status_var.set(str(e))

    def populate_image_tree(self, files):
        for item in self.image_tree.get_children():
            self.image_tree.delete(item)
        for f, size in files:
            self.image_tree.insert("", "end", values=(f, size))
            
    def update_title(self, filename=None):
        base_title = "ViewCPM - CP/M Disk Image Manager"
        if filename:
            # ShaZam! — show the filename in brackets in the title
            self.title(f"{base_title} - [{os.path.basename(filename)}]")
        else:
            self.title(base_title)

    # ----------------------------
    # Insert / Extract / Delete
    # ----------------------------
    def insert_file(self):
        selection = self.folder_tree.selection()
        if not selection:
            messagebox.showwarning("Insert", "No files selected in folder.")
            return
        files = [self.folder_tree.item(i)['values'][0] for i in selection]
        host_folder = prefs.get_pref("last_host_folder", "")
        self.disk_manager.insert_files(host_folder, files, callback=self.refresh_image_tree)

    def extract_file(self):
        selection = self.image_tree.selection()
        if not selection:
            messagebox.showwarning("Extract", "No files selected in disk image.")
            return
        files = [self.image_tree.item(i)['values'][0] for i in selection]
        dest_folder = filedialog.askdirectory(title="Select Destination Folder")
        if not dest_folder:
            return
        self.disk_manager.extract_files(files, dest_folder, callback=None)

    def delete_file(self):
        selection = self.image_tree.selection()
        if not selection:
            messagebox.showwarning("Delete", "No files selected in disk image.")
            return
        files = [self.image_tree.item(i)['values'][0] for i in selection]
        if messagebox.askyesno("Delete", f"Delete {len(files)} file(s) from image?"):
            self.disk_manager.delete_files(files, callback=self.refresh_image_tree)

    def refresh_image_tree(self):
        if getattr(self, "_current_raw_path", None):
            # Determine selected disk format
            disk_format = getattr(self, "_current_disk_format", "kpii")
            if self.disk_format_var.get() and self.diskdefs_manager:
                disk_format = self.disk_format_var.get()
                self._current_disk_format = disk_format
    
            # List files
            files = logic.list_image_files(self.cpmtools_path, self._current_raw_path, disk_format=disk_format)
            self.image_tree.after(0, self.populate_image_tree, files)
            
            disk_size = 0
            if self.diskdefs_manager:
                disk_info = self.diskdefs_manager.get_disk_info(disk_format)
                if disk_info:
                    disk_size = disk_info.get("disksize", 0)
            
            # Sum file sizes safely (remove commas)
            used_size = sum(int(str(size).replace(',', '')) for _, size in files)
            free_size = max(disk_size - used_size, 0) if disk_size else 0
            
            self.disk_info_var.set(
                f"Disk Size: {disk_size:,} bytes   Free Space: {free_size:,} bytes"
                if disk_size else "Disk Size: N/A   Free Space: N/A"
            )

# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    app = ViewCPMApp()
    app.mainloop()
