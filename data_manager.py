import os
import sys
from json import dump, load


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
        """Determine the correct file path for data.json in the AppData folder."""
        appdata_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
        return os.path.join(appdata_dir, file_name)

    def load_data(self):
        """Load data from JSON, creating the file with default data if it doesn't exist."""
        if not os.path.exists(self.file_path):
            # Create default data if the file doesn't exist
            self.copy_default_data()
        
        # Load the data from the file
        with open(self.file_path) as f:
            return load(f)

    def copy_default_data(self):
        """Copy the default data.json from MEIPASS to the AppData folder."""
        if getattr(sys, "frozen", False):
            # Running in a PyInstaller bundle
            source_path = os.path.join(sys._MEIPASS, self._file_name)
        else:
            # Running in a normal script execution
            source_path = os.path.join(os.path.dirname(__file__), self._file_name)
        
        # Ensure the AppData directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        # Copy the file to the AppData directory
        with open(source_path, 'rb') as src_file:
            with open(self.file_path, 'wb') as dest_file:
                dest_file.write(src_file.read())

    def save_data(self):
        """Save sorted data to JSON."""
        self.data["panel_models"].sort(key=lambda x: x["name"])
        self.data["rails"].sort(key=lambda x: int(x))
        with open(self.file_path, "w") as f:
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

