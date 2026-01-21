import AppKit
import json
from types import SimpleNamespace
from ui.panel import Panel

# Preset Controller manages a single preset entity
# Creates all the panels inside the preset
# Controlls configuration

class Preset:
    def __init__(self, preset_data, model):
        print("Preset init")
        self.preset_data = preset_data
        self.model = model
        self.panels = []
        
        # The loaded data (SimpleNamespace) now matches the JSON structure:
        # { "name": "...", "panels": [ ... ] }
        
        panels_data = getattr(self.preset_data, 'panels', [])
        
        # Fallback if panels is not present or if data structure is unexpected
        if not panels_data:
             print("No panels found in preset data")

        for panel_data in panels_data:
            self.panels.append(Panel(panel_data))
            
        self.is_editing = False

    def close(self):
        for panel in self.panels:
            try:
                panel.close()
            except Exception as e:
                print(f"Error closing panel: {e}")
        self.save()
            
    def toggle_edit(self):
        self.is_editing = not self.is_editing
        print(f"Edit mode: {self.is_editing}")

    def save(self):
        if self.model:
            self.model.save_preset(self.preset_data)
        else:
            print("No model available to save preset")