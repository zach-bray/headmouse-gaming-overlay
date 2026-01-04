import AppKit

class Box(AppKit.NSView):
    
    def drawRect_(self, rect):

        AppKit.NSColor.systemBlueColor().set()
        AppKit.NSRectFill(self.bounds())
        
        # Draw border
        AppKit.NSColor.blackColor().set()
        path = AppKit.NSBezierPath.bezierPathWithRect_(self.bounds())
        path.setLineWidth_(2.0)
        path.stroke()