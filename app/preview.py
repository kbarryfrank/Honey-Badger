import mistune
import tkinter as tk

class MarkdownRenderer:
    def __init__(self, text_widget: tk.Text):
        self.text = text_widget
        self.markdown_parser = mistune.create_markdown(renderer='ast')
        self._setup_tags()

    def _setup_tags(self):
        # Configure fonts and tags for clean minimal UI (2021 style, no emojis)
        self.text.tag_configure("h1", font=("TkDefaultFont", 18, "bold"), spacing1=10, spacing2=5)
        self.text.tag_configure("h2", font=("TkDefaultFont", 15, "bold"), spacing1=8, spacing2=4)
        self.text.tag_configure("h3", font=("TkDefaultFont", 13, "bold"), spacing1=6, spacing2=3)
        self.text.tag_configure("h4", font=("TkDefaultFont", 11, "bold"), spacing1=4, spacing2=2)
        self.text.tag_configure("h5", font=("TkDefaultFont", 10, "bold"), spacing1=4, spacing2=2)
        self.text.tag_configure("h6", font=("TkDefaultFont", 10, "bold"), spacing1=4, spacing2=2)

        self.text.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))
        self.text.tag_configure("italic", font=("TkDefaultFont", 10, "italic"))
        self.text.tag_configure("code", font=("Courier", 10), background="#f0f0f0")
        self.text.tag_configure("code_block", font=("Courier", 10), background="#f4f4f4", lmargin1=20, lmargin2=20, rmargin=20, spacing1=5, spacing2=5)
        self.text.tag_configure("paragraph", spacing1=4, spacing2=4)
        self.text.tag_configure("bullet", lmargin1=15, lmargin2=25, spacing1=2, spacing2=2)

    def render(self, md_content: str):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)

        try:
            ast = self.markdown_parser(md_content)
            if isinstance(ast, list):
                for block in ast:
                    self._render_block(block)
        except Exception as e:
            self.text.insert(tk.END, f"Error rendering markdown: {e}")

        self.text.config(state=tk.NORMAL)

    def _render_block(self, block, list_prefix=""):
        b_type = block.get("type")

        if b_type == "heading":
            level = block.get("attrs", {}).get("level", 1)
            tag = f"h{level}"
            children = block.get("children", [])
            self._render_inline(children, [tag])
            self.text.insert(tk.END, "\n")

        elif b_type == "paragraph":
            children = block.get("children", [])
            self._render_inline(children, ["paragraph"])
            self.text.insert(tk.END, "\n")

        elif b_type == "list":
            children = block.get("children", [])
            for item in children:
                self._render_block(item, list_prefix="•  ")

        elif b_type == "list_item":
            self.text.insert(tk.END, list_prefix, ("bullet",))
            children = block.get("children", [])
            for child in children:
                self._render_block(child)

        elif b_type in ("block_text", "block_code", "codespan"):
            # Handle text inside blocks
            raw = block.get("raw", "")
            if b_type == "block_code":
                self.text.insert(tk.END, raw + "\n", ("code_block",))
            else:
                children = block.get("children", [])
                if children:
                    for child in children:
                        self._render_block(child)
                elif raw:
                    self.text.insert(tk.END, raw)

        elif b_type == "blank_line":
            self.text.insert(tk.END, "\n")

        else:
            # Fallback for other block types
            children = block.get("children", [])
            if children:
                for child in children:
                    self._render_block(child)
            elif "raw" in block:
                self.text.insert(tk.END, block["raw"])

    def _render_inline(self, children, tags):
        for child in children:
            c_type = child.get("type")
            raw = child.get("raw", "")
            if c_type == "text":
                self.text.insert(tk.END, raw, tuple(tags))
            elif c_type == "strong":
                sub_children = child.get("children", [])
                self._render_inline(sub_children, tags + ["bold"])
            elif c_type == "emphasis":
                sub_children = child.get("children", [])
                self._render_inline(sub_children, tags + ["italic"])
            elif c_type == "codespan":
                self.text.insert(tk.END, raw, tuple(tags + ["code"]))
            else:
                if raw:
                    self.text.insert(tk.END, raw, tuple(tags))
                elif "children" in child:
                    self._render_inline(child["children"], tags)
