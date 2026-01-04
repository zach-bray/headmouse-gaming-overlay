from core.utils import *
from types import SimpleNamespace

class Model():
    def __init__(self):
        self.presets = self.loadPresets()        
        self.config = self.loadConfig()
    
    def loadPresets(self):
        presets = []

        try:
            files = os.listdir(PRESET_DIR)

            for filename in files:
                if filename.endswith(".json"):
                    path = os.path.join(PRESET_DIR, filename)

                    try:
                        with open(path, 'r') as file:
                            data = json.load(file, object_hook=lambda d: SimpleNamespace(**d))
                            presets.append(data)
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Failed to load {filename}: e")
        except FileNotFoundError:
            print(f"Direcotry no found: {PRESET_DIR}")
        
        return presets
    
    def loadConfig(self):
        return
    