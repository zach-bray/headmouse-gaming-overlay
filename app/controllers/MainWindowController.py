import AppKit
import objc
from ui.window import PresetsView
from ui.preset import Preset

class MainWindowController(AppKit.NSObject):
    def initWithModel_(self, model):
        self = objc.super(MainWindowController, self).init()
        if not self: return None
        
        self.model = model
        self.openPresets = {}
        
        self.setupWindow()
        
        # Initialize PresetsView with self as target
        self.presetsView = PresetsView.alloc().initWithFrame_model_target_(
             self.mainWindow.contentView().bounds(),
             self.model,
             self
        )
        self.presetsView.setAutoresizingMask_(AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable)
        self.mainWindow.setContentView_(self.presetsView)
        
        # Set delegate
        self.mainWindow.setDelegate_(self)
        
        return self

    def showWindow(self):
        self.mainWindow.makeKeyAndOrderFront_(None)
    
    def setupWindow(self):
        self.winW = 200
        self.winH = 100

        mask = AppKit.NSTitledWindowMask | AppKit.NSClosableWindowMask | AppKit.NSMiniaturizableWindowMask

        screen = AppKit.NSScreen.mainScreen().frame()
        x = (screen.size.width - self.winW) / 2
        y = (screen.size.height - self.winH) / 2
        rect = AppKit.NSMakeRect(x, y, self.winW, self.winH)

        self.mainWindow = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, mask, AppKit.NSBackingStoreBuffered,False
        )
        
        self.mainWindow.setTitle_("4one7")
        self.mainWindow.setAlphaValue_(0.95)
    
    def openPreset_(self, sender):
        tag = sender.tag()
        if tag in self.openPresets:
            print(f"Closing preset {tag}")
            try:
                self.openPresets[tag].close()
            except Exception as e:
                print(f"Error closing preset {tag}: {e}")
            finally:
                del self.openPresets[tag]
        else:
            print(f"Opening preset {tag}")
            # Ensure model.presets is accessed correctly
            preset_data = self.model.presets[tag]
            self.openPresets[tag] = Preset(preset_data, self.model)
            
    def editPreset_(self, sender):
        tag = sender.tag()
        # Ensure the preset is open before editing
        if tag not in self.openPresets:
             print(f"Opening preset {tag} for edit")
             preset_data = self.model.presets[tag]
             self.openPresets[tag] = Preset(preset_data, self.model)
        
        self.openPresets[tag].toggle_edit()

    def windowShouldClose_(self, sender):
        AppKit.NSApp.terminate_(None)
        return True
