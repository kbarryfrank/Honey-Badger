import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from pathlib import Path

class Sidebar(tk.Frame):
    def __init__(self, parent, state, on_file_select, on_file_create, on_file_delete, on_file_rename):
        super().__init__(parent, bg="#f0f0f0", width=220)
        self.pack_propagate(False)
        self.state = state
        self.on_file_select = on_file_select
        self.on_file_create = on_file_create
        self.on_file_delete = on_file_delete
        self.on_file_rename = on_file_rename

        self.all_files = [] # list of all Path objects for search
        self.current_view_dir = None # current folder being browsed
        self.item_mapping = [] # list mapping listbox index to Path or "UP"

        # Search box frame
        search_frame = tk.Frame(self, bg="#f0f0f0")
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("TkDefaultFont", 10), bd=1, relief=tk.SOLID)
        self.search_entry.pack(side=tk.TOP, fill=tk.X)
        self.search_entry.insert(0, "Search...")
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)

        # Folder label / header
        self.folder_label = tk.Label(self, text="No folder open", font=("TkDefaultFont", 9, "bold"), bg="#f0f0f0", fg="#666666", anchor="w")
        self.folder_label.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(0, 4))

        # File listbox with scrollbar
        list_container = tk.Frame(self, bg="#f0f0f0")
        list_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)

        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set, font=("TkDefaultFont", 10), bg="#ffffff", bd=0, highlightthickness=0, selectbackground="#0078d7", selectforeground="#ffffff")
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self.listbox.bind("<Button-3>", self._show_context_menu) # Right click on Linux/Windows
        self.listbox.bind("<Button-2>", self._show_context_menu) # Right click on macOS

        # New Note button at bottom
        new_btn = tk.Button(self, text="New Note", command=self._on_new_note_click, relief=tk.FLAT, bg="#e5e5e5", fg="#000000", pady=6)
        new_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=8)

        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Rename", command=self._context_rename)
        self.context_menu.add_command(label="Delete", command=self._context_delete)

        self.selected_index = None

    def _on_search_focus_in(self, event):
        if self.search_entry.get() == "Search...":
            self.search_entry.delete(0, tk.END)

    def _on_search_focus_out(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search...")

    def _on_search_change(self, *args):
        query = self.search_var.get()
        if not self.state.current_folder:
            return
        if query == "Search..." or not query:
            self._populate_list([], mode="browse")
        else:
            filtered = [f for f in self.all_files if query.lower() in str(f.relative_to(self.state.current_folder)).lower()]
            self._populate_list(filtered, mode="search")

    def refresh_files(self):
        self.all_files = []
        if self.state.current_folder and self.state.current_folder.is_dir():
            if not self.current_view_dir or not str(self.current_view_dir).startswith(str(self.state.current_folder)):
                self.current_view_dir = self.state.current_folder

            try:
                rel = self.current_view_dir.relative_to(self.state.current_folder)
                display_name = f"{self.state.current_folder.name}" if str(rel) == "." else f"{self.state.current_folder.name}/{rel}"
            except Exception:
                display_name = self.state.current_folder.name
            self.folder_label.config(text=display_name)

            try:
                self.all_files = sorted([p for p in self.state.current_folder.rglob("*") if p.is_file() and p.suffix.lower() in ('.md', '.txt')])
            except Exception:
                self.all_files = []
        else:
            self.current_view_dir = None
            self.folder_label.config(text="No folder open")
            self._populate_list([], mode="browse")
            return

        query = self.search_var.get()
        if query and query != "Search...":
            filtered = [f for f in self.all_files if query.lower() in str(f.relative_to(self.state.current_folder)).lower()]
            self._populate_list(filtered, mode="search")
        else:
            self._populate_list([], mode="browse")

    def _populate_list(self, files, mode="browse"):
        self.listbox.delete(0, tk.END)
        self.item_mapping = []

        if mode == "search":
            for f in files:
                try:
                    rel_path = str(f.relative_to(self.state.current_folder))
                except ValueError:
                    rel_path = f.name
                self.listbox.insert(tk.END, rel_path)
                self.item_mapping.append(f)
        else:
            if not self.current_view_dir or not self.state.current_folder:
                return

            if self.current_view_dir != self.state.current_folder:
                self.listbox.insert(tk.END, ".. (parent folder)")
                self.item_mapping.append("UP")

            try:
                subdirs = sorted([p for p in self.current_view_dir.iterdir() if p.is_dir() and not p.name.startswith('.')])
                text_files = sorted([p for p in self.current_view_dir.iterdir() if p.is_file() and p.suffix.lower() in ('.md', '.txt')])
            except Exception:
                subdirs, text_files = [], []

            for d in subdirs:
                self.listbox.insert(tk.END, f"{d.name}/")
                self.item_mapping.append(d)

            for f in text_files:
                self.listbox.insert(tk.END, f.name)
                self.item_mapping.append(f)

        if self.state.current_file in self.item_mapping:
            idx = self.item_mapping.index(self.state.current_file)
            self.listbox.selection_set(idx)

    def _on_select(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        if idx < len(self.item_mapping):
            target = self.item_mapping[idx]
            if target == "UP":
                if self.current_view_dir and self.current_view_dir != self.state.current_folder:
                    self.current_view_dir = self.current_view_dir.parent
                    self.refresh_files()
            elif isinstance(target, Path):
                if target.is_dir():
                    self.current_view_dir = target
                    self.refresh_files()
                elif target.is_file():
                    self.on_file_select(target)

    def _on_new_note_click(self):
        if not self.state.current_folder:
            messagebox.showwarning("Warning", "Please open a folder first.")
            return
        
        # Default path prefix to current view dir if inside a subfolder
        default_prefix = ""
        if self.current_view_dir and self.current_view_dir != self.state.current_folder:
            try:
                rel = self.current_view_dir.relative_to(self.state.current_folder)
                default_prefix = f"{rel}/"
            except Exception:
                pass

        name = simpledialog.askstring("New Note", "Enter note filename or path (e.g. note.md or note.txt):", initialvalue=default_prefix)
        if name:
            if not name.endswith((".md", ".txt")):
                name += ".md"
            file_path = self.state.current_folder / name
            if file_path.exists():
                messagebox.showerror("Error", "File already exists.")
                return
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text("", encoding="utf-8")
                # Navigate view dir to parent of new file if needed
                self.current_view_dir = file_path.parent
                self.on_file_create(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create file: {e}")

    def _show_context_menu(self, event):
        try:
            index = self.listbox.nearest(event.y)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)
            self.listbox.see(index)
            self.selected_index = index
            target = self.item_mapping[index] if index < len(self.item_mapping) else None
            if isinstance(target, Path) and target.is_file():
                self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _context_rename(self):
        if self.selected_index is None or self.selected_index >= len(self.item_mapping) or not self.state.current_folder:
            return
        target = self.item_mapping[self.selected_index]
        if not isinstance(target, Path) or not target.is_file():
            return
        old_path = target
        try:
            rel_old = str(old_path.relative_to(self.state.current_folder))
        except ValueError:
            rel_old = old_path.name
        new_name = simpledialog.askstring("Rename Note", "Enter new path/filename:", initialvalue=rel_old)
        if new_name:
            if not new_name.endswith((".md", ".txt")):
                new_name += ".md"
            new_path = self.state.current_folder / new_name
            if new_path.exists():
                messagebox.showerror("Error", "File with that name already exists.")
                return
            try:
                new_path.parent.mkdir(parents=True, exist_ok=True)
                old_path.rename(new_path)
                self.current_view_dir = new_path.parent
                self.on_file_rename(old_path, new_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename file: {e}")

    def _context_delete(self):
        if self.selected_index is None or self.selected_index >= len(self.item_mapping):
            return
        target = self.item_mapping[self.selected_index]
        if not isinstance(target, Path) or not target.is_file():
            return
        file_path = target
        if messagebox.askyesno("Delete Note", f"Are you sure you want to delete {file_path.name}?"):
            try:
                file_path.unlink()
                self.on_file_delete(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete file: {e}")
