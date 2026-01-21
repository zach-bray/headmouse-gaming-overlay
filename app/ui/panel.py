import AppKit
import Quartz
import objc

from ui.box import Box

class Panel:
    def __init__(self, preset_data):
        print("Panel init")
        self.preset_data = preset_data
        print(self.preset_data)
        
        # Determine width and height from data, or default
        # Assuming preset_data has width/height as per previous implementation
        self.width = getattr(self.preset_data, 'width', 500)
        self.height = getattr(self.preset_data, 'height', 500)

        # Using a default position or one from data if available
        # screen_x/y/w/h are for the window geometry
        x = getattr(self.preset_data, 'screen_x', 50)
        y = getattr(self.preset_data, 'screen_y', 500)
        w = getattr(self.preset_data, 'screen_width', 500)
        h = getattr(self.preset_data, 'screen_height', 500)
        
        frame_rect = AppKit.NSMakeRect(x, y, w, h)
        
        style = (AppKit.NSWindowStyleMaskTitled | 
                 AppKit.NSWindowStyleMaskClosable | 
                 AppKit.NSNonactivatingPanelMask | 
                 AppKit.NSMiniaturizableWindowMask | 
                 AppKit.NSWindowStyleMaskResizable | 
                 AppKit.NSWindowStyleMaskUtilityWindow)

        # Calculate the content rect relative to the desired frame rect
        # This prevents the window from "growing" or shifting due to title bar differences
        content_rect = AppKit.NSPanel.contentRectForFrameRect_styleMask_(frame_rect, style)

        self.panel = AppKit.NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            content_rect, style, AppKit.NSBackingStoreBuffered, False
        )
        
        self.panel.setLevel_(24)
        self.panel.setAlphaValue_(0.75)
        self.panel.setFloatingPanel_(True)
        self.panel.setBecomesKeyOnlyIfNeeded_(True)
        self.panel.standardWindowButton_(AppKit.NSWindowZoomButton).setHidden_(True)
        self.panel.setShowsResizeIndicator_(True)
        
        self.panel.setCollectionBehavior_(
            AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces | 
            AppKit.NSWindowCollectionBehaviorFullScreenAuxiliary
        )

        self.panel.orderFront_(None)
        
        # Setup delegate to track move/resize
        self.delegate = WindowDelegate.alloc().initWithData_(self.preset_data)
        self.panel.setDelegate_(self.delegate)
        
        self.setup_view()

    def close(self):
        # Ensure delegate is cleaned up or data is finalized if needed
        self.panel.setDelegate_(None)
        self.panel.close()

    def setup_view(self):
        rect = self.panel.contentView().bounds()
        self.container = FlippedContainer.alloc().initWithFrame_preset_(rect, self.preset_data)
        
        self.container.setWantsLayer_(True)
        self.container.layer().setBorderWidth_(2.0)
        self.container.layer().setBorderColor_(AppKit.NSColor.grayColor().CGColor())
        self.container.setPostsFrameChangedNotifications_(True)
        self.container.setAutoresizingMask_(AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable)
        self.container.setTranslatesAutoresizingMaskIntoConstraints_(True)
        
        self.panel.setPreservesContentDuringLiveResize_(False)

        self.panel.setContentView_(self.container)


class WindowDelegate(AppKit.NSObject):
    def initWithData_(self, data):
        self = objc.super(WindowDelegate, self).init()
        if self:
            self.data = data
        return self
    
    def windowDidMove_(self, notification):
        self._update_geometry(notification.object())

    def windowDidResize_(self, notification):
        self._update_geometry(notification.object())

    def _update_geometry(self, window):
        frame = window.frame()
        self.data.screen_x = frame.origin.x
        self.data.screen_y = frame.origin.y
        self.data.screen_width = frame.size.width
        self.data.screen_height = frame.size.height


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
        
        # Safety check if width/height are 0
        p_width = getattr(self.preset, 'width', 1)
        p_height = getattr(self.preset, 'height', 1)
        
        if p_width == 0: p_width = 1
        if p_height == 0: p_height = 1

        gridW = size.width / p_width
        gridH = size.height / p_height
        
        path = Quartz.CGPathCreateMutable()
        
        # Draw Vertical Lines
        for i in range(p_width + 1):
            x = i * gridW
            Quartz.CGPathMoveToPoint(path, None, x, 0)
            Quartz.CGPathAddLineToPoint(path, None, x, size.height)
            
        # Draw Horizontal Lines
        for i in range(p_height + 1):
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
        
        p_width = getattr(self.preset, 'width', 1)
        p_height = getattr(self.preset, 'height', 1)
        if p_width == 0: p_width = 1
        if p_height == 0: p_height = 1
        
        gridW = bounds.width / p_width
        gridH = bounds.height / p_height
        
        actions = getattr(self.preset, 'actions', [])

        for i, act in enumerate(actions):
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