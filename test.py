import AppKit
import objc
import sys

class MyBox(AppKit.NSView):
    def drawRect_(self, rect):
        # Fill background - 400px (14.11 cm) base scale
        AppKit.NSColor.systemBlueColor().set()
        AppKit.NSRectFill(self.bounds())
        
        # Draw border
        AppKit.NSColor.blackColor().set()
        path = AppKit.NSBezierPath.bezierPathWithRect_(self.bounds())
        path.setLineWidth_(2.0)
        path.stroke()

class MyContainer(AppKit.NSView):
    def initWithFrame_(self, frame):
        self = objc.super(MyContainer, self).initWithFrame_(frame)
        if self:
            self.setAutoresizingMask_(AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable)
        return self

    def setupBox(self):
        bounds = self.bounds()
        
        # 90% logic: 360px (12.7 cm) at default window size
        w, h = bounds.size.width * 0.9, bounds.size.height * 0.9
        x, y = (bounds.size.width - w) / 2, (bounds.size.height - h) / 2
        
        box_frame = AppKit.NSMakeRect(x, y, w, h)
        self.box = MyBox.alloc().initWithFrame_(box_frame)
        
        self.box.setAutoresizingMask_(
            AppKit.NSViewWidthSizable | 
            AppKit.NSViewHeightSizable | 
            AppKit.NSViewMinXMargin | 
            AppKit.NSViewMaxXMargin | 
            AppKit.NSViewMinYMargin | 
            AppKit.NSViewMaxYMargin
        )
        self.addSubview_(self.box)

class MyPanel(AppKit.NSPanel):
    def init(self):
        rect = AppKit.NSMakeRect(0, 0, 400, 400)
        style = (AppKit.NSWindowStyleMaskTitled | 
                 AppKit.NSWindowStyleMaskClosable | 
                 AppKit.NSWindowStyleMaskResizable | 
                 AppKit.NSWindowStyleMaskUtilityWindow)
        
        self = objc.super(MyPanel, self).initWithContentRect_styleMask_backing_defer_(
            rect, style, AppKit.NSBackingStoreBuffered, False
        )
        
        if self:
            self.setTitle_(f"NSView drawRect (400px / 14.11cm)")
            self.container = MyContainer.alloc().initWithFrame_(rect)
            self.setContentView_(self.container)
            self.container.setupBox()
        return self

class AppDelegate(AppKit.NSObject):
    def applicationDidFinishLaunching_(self, notification):
        self.panel = MyPanel.alloc().init()
        self.panel.makeKeyAndOrderFront_(None)
        self.panel.center()
        AppKit.NSApp.activateIgnoringOtherApps_(True)

if __name__ == "__main__":
    app = AppKit.NSApplication.sharedApplication()
    app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyRegular)
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()