import AppKit
import objc
from core.utils import *
from ui.panel import Panel
from types import SimpleNamespace

class Window(AppKit.NSObject):
    def initWithModel_(self, model):
        self = objc.super(Window, self).init() # type:ignore
        if not self:
            return

        self.presets = model.presets

        self.createWindow()

        self.drawPresets()

        self.panel = None

        # self.openPreset_(SimpleNamespace(tag=0))

        return self
    
    def createWindow(self):
        self.win_w = 200
        self.win_h = 100

        mask = AppKit.NSTitledWindowMask | AppKit.NSClosableWindowMask | AppKit.NSMiniaturizableWindowMask

        screen = AppKit.NSScreen.mainScreen().frame()
        x = (screen.size.width - self.win_w) / 2
        y = (screen.size.height - self.win_h) / 2
        rect = AppKit.NSMakeRect(x, y, self.win_w, self.win_h)

        self.window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, mask, AppKit.NSBackingStoreBuffered,False
        )
        
        self.window.setTitle_("4one7")
        self.window.setAlphaValue_(0.95)
        
        # Show window without activating
        self.window.orderFront_(None)
        
        # Set window delegate to handle close event
        self.window.setDelegate_(self)

    def drawPresets(self):
        scroll = AppKit.NSScrollView.alloc().initWithFrame_(AppKit.NSRect((0,0),(200,300)))
        scroll.setHasVerticalScroller_(True)

        stack = AppKit.NSStackView.stackViewWithViews_([])
        stack.setOrientation_(AppKit.NSUserInterfaceLayoutOrientationVertical)
        stack.setSpacing_(8)
        stack.setEdgeInsets_((10,10,10,10))


        for i, preset in enumerate(self.presets):
            btn = AppKit.NSButton.buttonWithTitle_target_action_(preset.name, self, "openPreset:")
            btn.setTag_(i)
            btn.setBezelStyle_(AppKit.NSBezelStyleRounded)
            stack.addArrangedSubview_(btn)


        scroll.contentView().setWantsLayer_(True)  # Must be True for borders to show
        scroll.contentView().layer().setBorderWidth_(2.0) # 0.028 in / 0.70 mm
        scroll.contentView().layer().setBorderColor_(AppKit.NSColor.redColor().CGColor())
        stack.setWantsLayer_(True)  # Must be True for borders to show
        stack.layer().setBorderWidth_(2.0) # 0.028 in / 0.70 mm
        stack.layer().setBorderColor_(AppKit.NSColor.blueColor().CGColor())

        scroll.setDocumentView_(stack)
        self.window.contentView().addSubview_(scroll)

    def openPreset_(self, sender):
        if self.panel is None:
            self.panel = Panel(self.presets[sender.tag()])
        else:
            print("close")
            self.panel.close()
            self.panel = None
        

    def windowShouldClose_(self, sender):
        AppKit.NSApp.terminate_(None)
        return True