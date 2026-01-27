import AppKit
import json
from types import SimpleNamespace
from controllers.panelController import PanelController
from ui.presetConfigWindow import PresetConfigWindow

# Preset Controller manages a single preset entity
# Creates all the panels inside the preset
# Controlls configuration

class Preset:
    def __init__(self, presetData, model):
        print("Preset init")
        self.presetData = presetData
        self.model = model
        self.panels = []
        
        # The loaded data (SimpleNamespace) now matches the JSON structure:
        # { "name": "...", "panels": [ ... ] }
        
        panelsData = getattr(self.presetData, 'panels', [])
        
        # Fallback if panels is not present or if data structure is unexpected
        if not panelsData:
             print("No panels found in preset data")

        for panelData in panelsData:
            self.panels.append(PanelController(panelData))
            
        self.isEditing = False
        self.configWindow = None

    def close(self):
        for panel in self.panels:
            try:
                panel.close()
            except Exception as e:
                print(f"Error closing panel: {e}")
        # Close config window if open
        if self.configWindow:
            self.configWindow.close()
            self.configWindow = None
        # Note: Save removed - will be handled at app termination
            
    def updatePanelGrid(self, panel_index):
        """Update the grid display for a specific panel when its dimensions change."""
        if panel_index < len(self.panels):
            panel = self.panels[panel_index]
            if hasattr(panel, 'container') and panel.container:
                panel.container.updateGridLines()
    
    def toggleEdit(self):
        self.isEditing = not self.isEditing
        print(f"Edit mode: {self.isEditing}")
        
        # Toggle grid visibility on all panels
        for panel in self.panels:
            panel.setGridVisible(self.isEditing)
        
        if self.isEditing:
            # Open configuration window, pass self so it can update panels
            self.configWindow = PresetConfigWindow(self.presetData, self.model, self)
        else:
            # Close configuration window
            if self.configWindow:
                self.configWindow.close()
                self.configWindow = None

    def configWindowDidClose(self):
        """Called when the config window closes itself."""
        if self.isEditing:
            self.isEditing = False
            print("Edit mode disabled via window close")
            # Hide grids
            for panel in self.panels:
                panel.setGridVisible(False)
            self.configWindow = None

    def save(self):
        if self.model:
            self.model.savePreset(self.presetData)
        else:
            print("No model available to save preset")