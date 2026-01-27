import AppKit
import Quartz
import objc
from ui.box import Box

class PanelView(AppKit.NSView):
    def initWithFrame_preset_(self, frame, preset):
        self = objc.super(PanelView, self).initWithFrame_(frame)
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
        self.gridLayer.setHidden_(True)  # Hidden by default, shown in edit mode
        self.layer().addSublayer_(self.gridLayer)
    
    @objc.python_method
    def setGridVisible(self, visible):
        """Show or hide the grid layer."""
        if hasattr(self, 'gridLayer') and self.gridLayer:
            self.gridLayer.setHidden_(not visible)

    def updateGridLines(self):
        size = self.bounds().size
        
        # Safety check if width/height are 0
        pWidth = getattr(self.preset, 'width', 1)
        pHeight = getattr(self.preset, 'height', 1)
        
        if pWidth == 0: pWidth = 1
        if pHeight == 0: pHeight = 1

        gridW = size.width / pWidth
        gridH = size.height / pHeight
        
        path = Quartz.CGPathCreateMutable()
        
        # Draw Vertical Lines
        for i in range(pWidth + 1):
            x = i * gridW
            Quartz.CGPathMoveToPoint(path, None, x, 0)
            Quartz.CGPathAddLineToPoint(path, None, x, size.height)
            
        # Draw Horizontal Lines
        for i in range(pHeight + 1):
            y = i * gridH
            Quartz.CGPathMoveToPoint(path, None, 0, y)
            Quartz.CGPathAddLineToPoint(path, None, size.width, y)
            
        self.gridLayer.setPath_(path)
        
        # Update button positions and sizes when grid changes
        self.updateButtons()
    
    def updateButtons(self):
        """Update button positions and sizes based on current grid dimensions."""
        bounds = self.bounds().size
        
        pWidth = getattr(self.preset, 'width', 1)
        pHeight = getattr(self.preset, 'height', 1)
        if pWidth == 0: pWidth = 1
        if pHeight == 0: pHeight = 1
        
        gridW = bounds.width / pWidth
        gridH = bounds.height / pHeight
        
        # Find all Box subviews and update their frames
        for subview in self.subviews():
            if hasattr(subview, 'x') and hasattr(subview, 'y'):
                # This is a Box with grid position
                new_rect = AppKit.NSMakeRect(
                    subview.x * gridW, 
                    subview.y * gridH, 
                    gridW, 
                    gridH
                )
                subview.setFrame_(new_rect)

    def setFrameSize_(self, newSize):
        objc.super(PanelView, self).setFrameSize_(newSize)
        
        if self.preset is not None:
            self.updateGridLines()

    def createButtons(self):
        bounds = self.bounds().size
        
        pWidth = getattr(self.preset, 'width', 1)
        pHeight = getattr(self.preset, 'height', 1)
        if pWidth == 0: pWidth = 1
        if pHeight == 0: pHeight = 1
        
        gridW = bounds.width / pWidth
        gridH = bounds.height / pHeight
        
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
