import AppKit

class Box(AppKit.NSView):
    
    def drawRect_(self, rect):
        pd = 3
        bounds = self.bounds()
        rect = AppKit.NSMakeRect(
            bounds.origin.x + pd,
            bounds.origin.y + pd,
            bounds.size.width - pd * 2,
            bounds.size.height - pd * 2,
            )

        AppKit.NSColor.systemBlueColor().set()
        AppKit.NSRectFill(rect)
        
        # Draw border
        AppKit.NSColor.blackColor().set()
        path = AppKit.NSBezierPath.bezierPathWithRect_(rect)
        path.setLineWidth_(2.0)
        path.stroke()