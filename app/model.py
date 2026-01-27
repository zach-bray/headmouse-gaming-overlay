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
                            data.filepath = path
                            presets.append(data)
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Failed to load {filename}: e")
        except FileNotFoundError:
            print(f"Direcotry no found: {PRESET_DIR}")
        
        return presets
    
    def loadConfig(self):
        try:
            with open(CONFIG_DIR, 'r') as file:
                # check if file is empty
                content = file.read()
                if not content:
                    return SimpleNamespace()
                    
                file.seek(0)
                data = json.load(file, object_hook=lambda d: SimpleNamespace(**d))
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Config not found or invalid at {CONFIG_DIR}, creating new.")
            return SimpleNamespace()

    def _toDict(self, obj):
        if isinstance(obj, SimpleNamespace):
            return {k: self._toDict(v) for k, v in vars(obj).items() if k != 'filepath'}
        elif isinstance(obj, list):
            return [self._toDict(i) for i in obj]
        else:
            return obj

    def savePreset(self, presetData):
        if not hasattr(presetData, 'filepath'):
            print("No filepath to save preset")
            return
            
        data = self._toDict(presetData)
        
        try:
            with open(presetData.filepath, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Saved preset to {presetData.filepath}")
        except Exception as e:
            print(f"Failed to save preset: {e}")
            
    def saveConfig(self):
        if not self.config:
            return
            
        data = self._toDict(self.config)
        
        try:
            with open(CONFIG_DIR, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Saved config to {CONFIG_DIR}")
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def save(self):
        """Save all presets and config to disk."""
        print(f"Saving {len(self.presets)} preset(s)...")
        for presetData in self.presets:
            self.savePreset(presetData)
            
        print("Saving config...")
        self.saveConfig()
        
        print("All saved.")