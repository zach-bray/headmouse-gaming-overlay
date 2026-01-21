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
        return

    def save_preset(self, preset_data):
        if not hasattr(preset_data, 'filepath'):
            print("No filepath to save preset")
            return
            
        # Convert SimpleNamespace to dict recursively
        def to_dict(obj):
            if isinstance(obj, SimpleNamespace):
                return {k: to_dict(v) for k, v in vars(obj).items() if k != 'filepath'}
            elif isinstance(obj, list):
                return [to_dict(i) for i in obj]
            else:
                return obj

        data = to_dict(preset_data)
        
        try:
            with open(preset_data.filepath, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Saved preset to {preset_data.filepath}")
        except Exception as e:
            print(f"Failed to save preset: {e}")
    