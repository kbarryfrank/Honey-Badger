import time
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from app.state import AppState
from app.sidebar import Sidebar
from app.editor import EditorPanel

class AppWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Honey Badger")
        self.root.geometry("900x600")
        self.root.minsize(600, 400)

        self.state = AppState()

        # Top Bar
        top_bar = tk.Frame(self.root, bg="#e0e0e0", height=40)
        top_bar.pack(side=tk.TOP, fill=tk.X)
        top_bar.pack_propagate(False)

        title_label = tk.Label(top_bar, text="Honey Badger", font=("TkDefaultFont", 11, "bold"), bg="#e0e0e0", fg="#333333")
        title_label.pack(side=tk.LEFT, padx=12)

        open_btn = tk.Button(top_bar, text="Open Folder", command=self.open_folder_dialog, relief=tk.FLAT, bg="#ffffff", padx=10, pady=2)
        open_btn.pack(side=tk.RIGHT, padx=12, pady=6)

        # Status Bar
        self.status_bar = tk.Label(self.root, text="Ready", font=("TkDefaultFont", 9), bg="#f0f0f0", fg="#555555", anchor="w", padx=10, pady=4)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Main Layout
        main_frame = tk.Frame(self.root, bg="#ffffff")
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Editor Panel
        self.editor = EditorPanel(main_frame, self.state, self.on_text_changed)
        self.editor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Sidebar Panel
        self.sidebar = Sidebar(
            main_frame,
            self.state,
            on_file_select=self.load_file,
            on_file_create=self.on_file_created,
            on_file_delete=self.on_file_deleted,
            on_file_rename=self.on_file_renamed
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Key Bindings
        self.root.bind("<Control-n>", lambda e: self.sidebar._on_new_note_click())
        self.root.bind("<Control-f>", lambda e: self.focus_search())
        self.root.bind("<Control-s>", lambda e: self.save_current_file())

        # Load initial folder files if config exists
        if self.state.current_folder:
            self.sidebar.refresh_files()
            self.update_status(f"Loaded folder: {self.state.current_folder.name}")

    def update_status(self, text: str):
        self.status_bar.config(text=text)

    def focus_search(self):
        self.sidebar.search_entry.focus_set()
        self.sidebar.search_entry.select_range(0, tk.END)

    def open_folder_dialog(self):
        if self.state.is_modified and self.state.current_file:
            if messagebox.askyesno("Unsaved Changes", f"Save changes to {self.state.current_file.name} before opening a new folder?"):
                self.save_current_file()

        folder = filedialog.askdirectory()
        if folder:
            self.state.current_folder = Path(folder)
            self.state.current_file = None
            self.state.is_modified = False
            self.state.save_config()
            self.sidebar.refresh_files()
            self.editor.clear()
            self.update_status(f"Opened folder: {self.state.current_folder.name}")

    def load_file(self, file_path: Path):
        if self.state.current_file == file_path:
            return

        if self.state.is_modified and self.state.current_file:
            if messagebox.askyesno("Unsaved Changes", f"Save changes to {self.state.current_file.name} before switching?"):
                self.save_current_file()

        self.state.current_file = file_path
        self.state.is_modified = False
        try:
            content = file_path.read_text(encoding="utf-8")
            self.editor.load_file_content(content)
            self.update_status(str(file_path))
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")

    def save_current_file(self):
        if not self.state.current_file:
            return
        content = self.editor.get_content()
        try:
            self.state.current_file.write_text(content, encoding="utf-8")
            self.state.is_modified = False
            t_str = time.strftime("%H:%M:%S")
            self.update_status(f"Saved [{t_str}] - {self.state.current_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not write file: {e}")

    def on_text_changed(self):
        if self.state.current_file and not self.state.is_modified:
            self.state.is_modified = True
            self.update_status(f"Unsaved* - {self.state.current_file}")

    def on_file_created(self, file_path: Path):
        self.sidebar.refresh_files()
        self.load_file(file_path)

    def on_file_deleted(self, file_path: Path):
        if self.state.current_file == file_path:
            self.state.current_file = None
            self.state.is_modified = False
            self.editor.clear()
        self.sidebar.refresh_files()
        self.update_status("File deleted")

    def on_file_renamed(self, old_path: Path, new_path: Path):
        if self.state.current_file == old_path:
            self.state.current_file = new_path
            self.update_status(str(new_path))
        self.sidebar.refresh_files()
