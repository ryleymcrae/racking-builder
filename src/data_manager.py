import os
import sys
from json import load, dump

class DataManager:
    _instance = None
    _file_name = "data.json"  # Only the file name here, not the full path

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.file_path = self.get_file_path(self._file_name)
            self.data = self.load_data()
            self._initialized = True

    def get_file_path(self, file_name):
        """Determine the correct file path for data.json."""
        if getattr(sys, '_MEIPASS', False):
            # PyInstaller bundle (extracted temp directory)
            return os.path.join(sys._MEIPASS, file_name)
        else:
            # Normal script execution (development mode)
            return os.path.join(os.path.dirname(__file__), file_name)

    def load_data(self):
        """Load data from JSON."""
        with open(self.file_path) as f:
            return load(f)

    def save_data(self):
        """Save sorted data to JSON."""
        self.data["panel_models"].sort(key=lambda x: x["name"])
        self.data["rails"].sort(key=lambda x: int(x))
        with open(self.file_path, 'w') as f:
            dump(self.data, f, indent=4)

    def get_panel_models(self):
        """Return list of panel models."""
        return self.data.get("panel_models", [])

    def get_rails(self):
        """Return list of rail lengths."""
        return self.data.get("rails", [])

    def add_panel_model(self):
        self.data["panel_models"].append({"name": "", "width": "", "height": ""})

    def delete_panel_model(self, index):
        self.data["panel_models"].pop(index)

    def update_panel_model(self, index, key, value):
        self.data["panel_models"][index][key] = value

    def add_rail(self):
        self.data["rails"].append("")

    def delete_rail(self, index):
        self.data["rails"].pop(index)

    def update_rail(self, index, length):
        self.data["rails"][index] = length
