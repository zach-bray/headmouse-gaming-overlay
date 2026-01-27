import AppKit
import objc

# Import the view
from ui.panelView import PanelView

class PanelController:
    def __init__(self, presetData):
        print("PanelController init")
        self.presetData = presetData
        print(self.presetData)
        
        # Determine width and height from data, or default
        # Assuming presetData has width/height 
        self.width = getattr(self.presetData, 'width', 500)
        self.height = getattr(self.presetData, 'height', 500)

        # Using a default position or one from data if available
        # screen_x/y/w/h are for the window geometry
        x = getattr(self.presetData, 'screen_x', 50)
        y = getattr(self.presetData, 'screen_y', 500)
        w = getattr(self.presetData, 'screen_width', 500)
        h = getattr(self.presetData, 'screen_height', 500)
        
        frameRect = AppKit.NSMakeRect(x, y, w, h)
        
        style = (AppKit.NSWindowStyleMaskTitled | 
                 AppKit.NSWindowStyleMaskClosable | 
                 AppKit.NSNonactivatingPanelMask | 
                 AppKit.NSMiniaturizableWindowMask | 
                 AppKit.NSWindowStyleMaskResizable | 
                 AppKit.NSWindowStyleMaskUtilityWindow)

        # Calculate the content rect relative to the desired frame rect
        # This prevents the window from "growing" or shifting due to title bar differences
        contentRect = AppKit.NSPanel.contentRectForFrameRect_styleMask_(frameRect, style)

        self.panel = AppKit.NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            contentRect, style, AppKit.NSBackingStoreBuffered, False
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
        self.delegate = WindowDelegate.alloc().initWithData_(self.presetData)
        self.panel.setDelegate_(self.delegate)
        
        self.setupView()

    def close(self):
        # Ensure delegate is cleaned up or data is finalized if needed
        self.panel.setDelegate_(None)
        self.panel.close()
    
    def setGridVisible(self, visible):
        """Show or hide the grid lines based on edit mode."""
        if hasattr(self, 'container') and self.container:
            self.container.setGridVisible(visible)

    def setupView(self):
        rect = self.panel.contentView().bounds()
        # Use PanelView instead of FlippedContainer
        self.container = PanelView.alloc().initWithFrame_preset_(rect, self.presetData)
        
        self.container.setWantsLayer_(True)
        self.container.layer().setBorderWidth_(2.0)
        # Note: AppKit.NSColor.grayColor().CGColor() usage
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
        self._updateGeometry(notification.object())

    def windowDidResize_(self, notification):
        self._updateGeometry(notification.object())

    @objc.python_method
    def _updateGeometry(self, window):
        frame = window.frame()
        self.data.screen_x = frame.origin.x
        self.data.screen_y = frame.origin.y
        self.data.screen_width = frame.size.width
        self.data.screen_height = frame.size.height
