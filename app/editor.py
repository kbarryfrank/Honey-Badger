import tkinter as tk
from app.preview import MarkdownRenderer

class EditorPanel(tk.Frame):
    def __init__(self, parent, state, on_text_changed):
        super().__init__(parent, bg="#ffffff")
        self.state = state
        self.on_text_changed = on_text_changed
        self.render_timer_id = None

        # Content container
        content_frame = tk.Frame(self, bg="#ffffff")
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Unified live editable markdown view
        self.text_widget = tk.Text(content_frame, wrap=tk.WORD, font=("TkDefaultFont", 11), bg="#ffffff", fg="#222222", bd=0, highlightthickness=0, relief=tk.FLAT, state=tk.NORMAL)
        self.text_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=12)
        self.text_widget.bind("<<Modified>>", self._on_text_modified)
        self.text_widget.bind("<KeyRelease>", self._on_key_release)

        self.renderer = MarkdownRenderer(self.text_widget)

    def load_file_content(self, content: str):
        self.text_widget.edit_modified(False)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", content)
        self.state.buffer = content
        self.renderer.render(content)

    def get_content(self) -> str:
        return self.text_widget.get("1.0", tk.END).rstrip("\n")

    def _on_text_modified(self, event=None):
        if self.text_widget.edit_modified():
            content = self.text_widget.get("1.0", tk.END)
            self.state.buffer = content
            self.on_text_changed()
            self.text_widget.edit_modified(False)

    def _on_key_release(self, event):
        if self.render_timer_id is not None:
            self.after_cancel(self.render_timer_id)
        self.render_timer_id = self.after(500, self._apply_live_formatting)

    def _apply_live_formatting(self):
        self.render_timer_id = None
        content = self.text_widget.get("1.0", tk.END)
        try:
            pos = self.text_widget.index(tk.INSERT)
            self.renderer.render(content)
            self.text_widget.mark_set(tk.INSERT, pos)
        except Exception:
            pass

    def clear(self):
        self.text_widget.delete("1.0", tk.END)
        self.state.buffer = ""
        self.state.current_file = None
