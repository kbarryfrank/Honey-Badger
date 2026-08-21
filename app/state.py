import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".honey_badger_config.json"

class AppState:
    def __init__(self):
        self.current_folder: Path | None = None
        self.current_file: Path | None = None
        self.buffer: str = ""
        self.is_modified: bool = False
        self.load_config()

    def load_config(self):
        try:
            if CONFIG_FILE.exists():
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                folder_path = data.get("last_folder")
                if folder_path and Path(folder_path).is_dir():
                    self.current_folder = Path(folder_path)
        except Exception:
            pass

    def save_config(self):
        try:
            data = {}
            if self.current_folder:
                data["last_folder"] = str(self.current_folder.resolve())
            CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass
