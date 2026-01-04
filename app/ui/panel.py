import AppKit
import Quartz
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

    def close(self):
        self.panel.close()

    def setup_view(self):
        rect = self.panel.contentView().bounds()
        self.container = FlippedContainer.alloc().initWithFrame_preset_(rect, self.preset)
        
        self.container.setWantsLayer_(True)
        self.container.layer().setBorderWidth_(2.0) # 0.028 in / 0.71 mm
        self.container.layer().setBorderColor_(AppKit.NSColor.grayColor().CGColor())
        self.container.setPostsFrameChangedNotifications_(True)
        self.container.setAutoresizingMask_(AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable)
        self.container.setTranslatesAutoresizingMaskIntoConstraints_(True)
        
        self.panel.setPreservesContentDuringLiveResize_(False)

        self.panel.setContentView_(self.container)
        

class FlippedContainer(AppKit.NSView):
    def initWithFrame_preset_(self, frame, preset):
        self = objc.super(FlippedContainer, self).initWithFrame_(frame)
        if self:
            self.setAutoresizingMask_(AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable)

        self.preset = preset
        self.createButtons()
        self.setupGridLayer()
        self.updateGridLines()
        return self

    def isFlipped(self):
        return True
    
    def setupGridLayer(self):
        self.setWantsLayer_(True)
        self.gridLayer = Quartz.CAShapeLayer.layer()
        self.gridLayer.setStrokeColor_(AppKit.NSColor.lightGrayColor().CGColor())
        self.gridLayer.setLineWidth_(1.0)
        self.gridLayer.setFillColor_(None)
        self.layer().addSublayer_(self.gridLayer)

    def updateGridLines(self):
        size = self.bounds().size
        gridW = size.width / self.preset.width
        gridH = size.height / self.preset.height
        
        path = Quartz.CGPathCreateMutable()
        
        # Draw Vertical Lines
        for i in range(self.preset.width + 1):
            x = i * gridW
            Quartz.CGPathMoveToPoint(path, None, x, 0)
            Quartz.CGPathAddLineToPoint(path, None, x, size.height)
            
        # Draw Horizontal Lines
        for i in range(self.preset.height + 1):
            y = i * gridH
            Quartz.CGPathMoveToPoint(path, None, 0, y)
            Quartz.CGPathAddLineToPoint(path, None, size.width, y)
            
        self.gridLayer.setPath_(path)

    def setFrameSize_(self, newSize):
        objc.super(FlippedContainer, self).setFrameSize_(newSize)
        
        if self.preset is not None:
            self.updateGridLines()

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