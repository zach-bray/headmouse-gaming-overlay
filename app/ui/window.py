import AppKit
import objc
from core.utils import *
from ui.preset import Preset
from types import SimpleNamespace

# The main window. Lists the presets

class Window(AppKit.NSObject):
    def initWithModel_(self, model):
        self = objc.super(Window, self).init() # type:ignore
        if not self:
            return

        self.model = model
        # the json dict of preset data
        self.presets = model.presets

        self.createWindow()

        self.drawPresets()

        self.open_presets = {}

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
            # setup row for buttons
            row = AppKit.NSStackView.stackViewWithViews_([])
            row.setOrientation_(AppKit.NSUserInterfaceLayoutOrientationHorizontal)
            row.setSpacing_(8.0)
            
            # preset button, click to toggle
            btn = AppKit.NSButton.buttonWithTitle_target_action_(preset.name, self, "openPreset:")
            btn.setTag_(i)
            btn.setBezelStyle_(AppKit.NSBezelStyleRounded)

            # edit button
            editIcon = AppKit.NSImage.imageWithSystemSymbolName_accessibilityDescription_("pencil", "Edit")
            editBtn = AppKit.NSButton.buttonWithImage_target_action_(editIcon, self, "editPreset:")
            editBtn.setTag_(i)
            editBtn.setBezelStyle_(AppKit.NSBezelStyleRounded)

            # add to view
            row.addArrangedSubview_(btn)
            row.addArrangedSubview_(editBtn)
            stack.addArrangedSubview_(row)


        scroll.contentView().setWantsLayer_(True)  # Must be True for borders to show
        scroll.contentView().layer().setBorderWidth_(2.0) # 0.028 in / 0.70 mm
        scroll.contentView().layer().setBorderColor_(AppKit.NSColor.redColor().CGColor())
        stack.setWantsLayer_(True)  # Must be True for borders to show
        stack.layer().setBorderWidth_(2.0) # 0.028 in / 0.70 mm
        stack.layer().setBorderColor_(AppKit.NSColor.blueColor().CGColor())

        scroll.setDocumentView_(stack)
        self.window.contentView().addSubview_(scroll)

    def getPreset_(self, sender):
        return self.presets[sender.tag()]

    def openPreset_(self, sender):
        tag = sender.tag()
        if tag in self.open_presets:
            print(f"Closing preset {tag}")
            try:
                self.open_presets[tag].close()
            except Exception as e:
                print(f"Error closing preset {tag}: {e}")
            finally:
                del self.open_presets[tag]
        else:
            print(f"Opening preset {tag}")
            self.open_presets[tag] = Preset(self.presets[tag], self.model)
        
    def editPreset_(self, sender):
        tag = sender.tag()
        # Ensure the preset is open before editing
        if tag not in self.open_presets:
             print(f"Opening preset {tag} for edit")
             self.open_presets[tag] = Preset(self.presets[tag], self.model)
        
        self.open_presets[tag].toggle_edit()

    def windowShouldClose_(self, sender):
        AppKit.NSApp.terminate_(None)
        return True