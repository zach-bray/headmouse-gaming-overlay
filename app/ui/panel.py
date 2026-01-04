import AppKit
import objc

from ui.dwellBox import DwellBox
from ui.box import Box

class Panel:
    def __init__(self, preset):
        print("Panel init")
        self.preset = preset
        self.width = 500
        self.height = 500

        rect = AppKit.NSMakeRect(50, 500, self.width, self.height)
        style = (AppKit.NSWindowStyleMaskTitled | 
                 AppKit.NSWindowStyleMaskClosable | 
                 AppKit.NSNonactivatingPanelMask | 
                 AppKit.NSMiniaturizableWindowMask | 
                 AppKit.NSWindowStyleMaskResizable | 
                 AppKit.NSWindowStyleMaskUtilityWindow)

        self.panel = AppKit.NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, style, AppKit.NSBackingStoreBuffered, False
        )
        
        self.panel.setLevel_(24)
        self.panel.setAlphaValue_(0.75)
        self.panel.setFloatingPanel_(True)
        self.panel.setBecomesKeyOnlyIfNeeded_(True)
        # self.panel.setTitlebarAppearsTransparent_(True)
        self.panel.standardWindowButton_(AppKit.NSWindowZoomButton).setHidden_(True)
        # self.panel.setMinSize_(AppKit.NSMakeRect(0, 0, 200, 200).size)
        self.panel.setShowsResizeIndicator_(True)
        
        # Combines behaviors to stay visible on top of full-screen apps
        self.panel.setCollectionBehavior_(
            AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces | 
            AppKit.NSWindowCollectionBehaviorFullScreenAuxiliary
        )

        self.panel.makeKeyAndOrderFront_(None)
        
        self.setup_view()


    def setup_view(self):
        rect = self.panel.contentView().bounds()
        self.container = FlippedContainer.alloc().initWithFrame_(rect)
        
        self.container.setWantsLayer_(True)
        self.container.layer().setBorderWidth_(2.0) # 0.028 in / 0.71 mm
        self.container.layer().setBorderColor_(AppKit.NSColor.grayColor().CGColor())
        self.container.setPostsFrameChangedNotifications_(True)
        self.container.setAutoresizingMask_(AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable)
        self.container.setTranslatesAutoresizingMaskIntoConstraints_(True)
        
        self.panel.setPreservesContentDuringLiveResize_(False)

        self.panel.setContentView_(self.container)
        
        self.container.setPreset_(self.preset)


class FlippedContainer(AppKit.NSView):
    def initWithFrame_(self, frame):
        self = objc.super(FlippedContainer, self).initWithFrame_(frame)
        if self:
            self.setAutoresizingMask_(AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable)
        return self

    def isFlipped(self):
        return True
    
    def setPreset_(self, preset):
        self.preset = preset
        self.createButtons()

    def createButtons(self):
        bounds = self.bounds().size
        
        gridW = bounds.width / self.preset.width
        gridH = bounds.height / self.preset.height

        for i, act in enumerate(self.preset.actions):
            rect = AppKit.NSMakeRect(act.x * gridW, act.y * gridH, gridW, gridH)
            box = Box.alloc().initWithFrame_(rect)
            box.x = act.x
            box.y = act.y

            box.setAutoresizingMask_(
                AppKit.NSViewWidthSizable | 
                AppKit.NSViewHeightSizable | 
                AppKit.NSViewMinXMargin | 
                AppKit.NSViewMaxXMargin | 
                AppKit.NSViewMinYMargin | 
                AppKit.NSViewMaxYMargin
            )

            self.addSubview_(box)