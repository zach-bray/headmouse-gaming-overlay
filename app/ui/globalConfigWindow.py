import AppKit
import objc

class GlobalConfigDelegate(AppKit.NSObject):
    def initWithWindow_(self, window):
        self = objc.super(GlobalConfigDelegate, self).init()
        if self:
            self.window = window
        return self
    
    def opacityChanged_(self, sender):
        self.window.opacityChanged(sender.floatValue())

class GlobalConfigWindow:
    def __init__(self, model, controller):
        self.model = model
        self.controller = controller
        self.delegate = GlobalConfigDelegate.alloc().initWithWindow_(self)
        
        self.setupWindow()
        self.setupUI()
        self.window.makeKeyAndOrderFront_(None)

    def setupWindow(self):
        winWidth = 300
        winHeight = 150
        
        screen = AppKit.NSScreen.mainScreen().frame()
        x = (screen.size.width - winWidth) / 2
        y = (screen.size.height - winHeight) / 2
        rect = AppKit.NSMakeRect(x, y, winWidth, winHeight)
        
        style = (AppKit.NSWindowStyleMaskTitled | 
                 AppKit.NSWindowStyleMaskClosable |
                 AppKit.NSWindowStyleMaskUtilityWindow)
                 
        self.window = AppKit.NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, style, AppKit.NSBackingStoreBuffered, False
        )
        self.window.setFloatingPanel_(True)
        self.window.setTitle_("Global Config")

    def setupUI(self):
        contentView = self.window.contentView()
        
        # Opacity Label
        label = AppKit.NSTextField.labelWithString_("Panel Opacity:")
        label.setFrame_(AppKit.NSMakeRect(20, 100, 100, 20))
        contentView.addSubview_(label)
        
        # Opacity Slider
        currentOpacity = getattr(self.model.config, 'opacity', 0.75)
        slider = AppKit.NSSlider.sliderWithValue_minValue_maxValue_target_action_(
            currentOpacity, 0.1, 1.0, self.delegate, "opacityChanged:"
        )
        slider.setFrame_(AppKit.NSMakeRect(130, 98, 150, 24))
        contentView.addSubview_(slider)
        
    def opacityChanged(self, value):
        self.model.config.opacity = value
        self.controller.updateGlobalSettings()
