import AppKit
import objc

class ButtonDelegate(AppKit.NSObject):
    """Helper delegate to handle button actions."""
    
    def initWithConfigWindow_(self, configWindow):
        self = objc.super(ButtonDelegate, self).init()
        if self:
            self.configWindow = configWindow
        return self
    
    def incrementWidth_(self, sender):
        self.configWindow.incrementWidth(sender.tag())
    
    def decrementWidth_(self, sender):
        self.configWindow.decrementWidth(sender.tag())
    
    def incrementHeight_(self, sender):
        self.configWindow.incrementHeight(sender.tag())
    
    def decrementHeight_(self, sender):
        self.configWindow.decrementHeight(sender.tag())
    
    def windowWillClose_(self, notification):
        if self.configWindow.preset:
            self.configWindow.preset.configWindowDidClose()

class PresetConfigWindow:
    """Configuration window for editing preset panel dimensions."""
    
    def __init__(self, presetData, model, preset=None):
        self.presetData = presetData
        self.model = model
        self.preset = preset  # Reference to the Preset object to update live panels
        
        # Create button delegate
        self.buttonDelegate = ButtonDelegate.alloc().initWithConfigWindow_(self)
        
        # Create window
        self.setupWindow()
        self.setupUI()
        self.window.makeKeyAndOrderFront_(None)
    
    def setupWindow(self):
        """Create the configuration panel."""
        # Panel dimensions
        winWidth = 400
        winHeight = 300
        
        # Center the panel on screen
        screen = AppKit.NSScreen.mainScreen().frame()
        x = (screen.size.width - winWidth) / 2
        y = (screen.size.height - winHeight) / 2
        rect = AppKit.NSMakeRect(x, y, winWidth, winHeight)
        
        # Panel style - utility window that floats
        style = (AppKit.NSWindowStyleMaskTitled | 
                 AppKit.NSWindowStyleMaskClosable | 
                 AppKit.NSWindowStyleMaskResizable |
                 AppKit.NSWindowStyleMaskUtilityWindow)
        
        # Use NSPanel instead of NSWindow for floating utility behavior
        self.window = AppKit.NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, style, AppKit.NSBackingStoreBuffered, False
        )
        
        # Configure panel behavior
        self.window.setFloatingPanel_(True)
        self.window.setBecomesKeyOnlyIfNeeded_(True)
        self.window.setDelegate_(self.buttonDelegate)
        
        presetName = getattr(self.presetData, 'name', 'Preset')
        self.window.setTitle_(f"Configure {presetName}")
        self.window.setAlphaValue_(0.95)
    
    def setupUI(self):
        """Setup the UI elements in the window."""
        contentView = self.window.contentView()
        bounds = contentView.bounds()
        
        # Create scroll view for panel list
        scrollView = AppKit.NSScrollView.alloc().initWithFrame_(
            AppKit.NSMakeRect(20, 20, bounds.size.width - 40, bounds.size.height - 40)
        )
        scrollView.setHasVerticalScroller_(True)
        scrollView.setHasHorizontalScroller_(False)
        scrollView.setBorderType_(AppKit.NSBezelBorder)
        scrollView.setAutoresizingMask_(
            AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable
        )
        
        # Create document view (container for panel items)
        panels = getattr(self.presetData, 'panels', [])
        numPanels = len(panels)
        itemHeight = 60
        totalHeight = max(numPanels * itemHeight + 20, bounds.size.height - 40)
        
        docView = AppKit.NSView.alloc().initWithFrame_(
            AppKit.NSMakeRect(0, 0, bounds.size.width - 60, totalHeight)
        )
        
        # Create UI for each panel
        for i, panelData in enumerate(panels):
            yPos = totalHeight - (i + 1) * itemHeight
            self.createPanelRow(docView, panelData, i, yPos, itemHeight)
        
        scrollView.setDocumentView_(docView)
        contentView.addSubview_(scrollView)
    
    def createPanelRow(self, parentView, panelData, index, yPos, height):
        """Create a row for one panel with its width/height controls."""
        rowWidth = parentView.bounds().size.width
        
        # Panel label
        label = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(10, yPos + 20, 80, 20)
        )
        label.setStringValue_(f"Panel {index + 1}:")
        label.setBezeled_(False)
        label.setDrawsBackground_(False)
        label.setEditable_(False)
        label.setSelectable_(False)
        parentView.addSubview_(label)
        
        # Width controls
        widthLabel = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(100, yPos + 20, 50, 20)
        )
        widthLabel.setStringValue_("Width:")
        widthLabel.setBezeled_(False)
        widthLabel.setDrawsBackground_(False)
        widthLabel.setEditable_(False)
        widthLabel.setSelectable_(False)
        parentView.addSubview_(widthLabel)
        
        # Width minus button
        widthMinus = AppKit.NSButton.alloc().initWithFrame_(
            AppKit.NSMakeRect(160, yPos + 18, 30, 24)
        )
        widthMinus.setTitle_("-")
        widthMinus.setBezelStyle_(AppKit.NSRoundedBezelStyle)
        widthMinus.setTarget_(self.buttonDelegate)
        widthMinus.setAction_("decrementWidth:")
        widthMinus.setTag_(index)
        parentView.addSubview_(widthMinus)
        
        # Width value display
        currentWidth = getattr(panelData, 'width', 1)
        widthValue = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(195, yPos + 20, 40, 20)
        )
        widthValue.setStringValue_(str(currentWidth))
        widthValue.setBezeled_(False)
        widthValue.setDrawsBackground_(False)
        widthValue.setEditable_(False)
        widthValue.setAlignment_(AppKit.NSTextAlignmentCenter)
        # Tag it so we can update it later
        widthValue.setIdentifier_(f"width_{index}")
        parentView.addSubview_(widthValue)
        
        # Width plus button
        widthPlus = AppKit.NSButton.alloc().initWithFrame_(
            AppKit.NSMakeRect(240, yPos + 18, 30, 24)
        )
        widthPlus.setTitle_("+")
        widthPlus.setBezelStyle_(AppKit.NSRoundedBezelStyle)
        widthPlus.setTarget_(self.buttonDelegate)
        widthPlus.setAction_("incrementWidth:")
        widthPlus.setTag_(index)
        parentView.addSubview_(widthPlus)
        
        # Height controls
        heightLabel = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(100, yPos - 5, 50, 20)
        )
        heightLabel.setStringValue_("Height:")
        heightLabel.setBezeled_(False)
        heightLabel.setDrawsBackground_(False)
        heightLabel.setEditable_(False)
        heightLabel.setSelectable_(False)
        parentView.addSubview_(heightLabel)
        
        # Height minus button
        heightMinus = AppKit.NSButton.alloc().initWithFrame_(
            AppKit.NSMakeRect(160, yPos - 7, 30, 24)
        )
        heightMinus.setTitle_("-")
        heightMinus.setBezelStyle_(AppKit.NSRoundedBezelStyle)
        heightMinus.setTarget_(self.buttonDelegate)
        heightMinus.setAction_("decrementHeight:")
        heightMinus.setTag_(index)
        parentView.addSubview_(heightMinus)
        
        # Height value display
        currentHeight = getattr(panelData, 'height', 1)
        heightValue = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(195, yPos - 5, 40, 20)
        )
        heightValue.setStringValue_(str(currentHeight))
        heightValue.setBezeled_(False)
        heightValue.setDrawsBackground_(False)
        heightValue.setEditable_(False)
        heightValue.setAlignment_(AppKit.NSTextAlignmentCenter)
        # Tag it so we can update it later
        heightValue.setIdentifier_(f"height_{index}")
        parentView.addSubview_(heightValue)
        
        # Height plus button
        heightPlus = AppKit.NSButton.alloc().initWithFrame_(
            AppKit.NSMakeRect(240, yPos - 7, 30, 24)
        )
        heightPlus.setTitle_("+")
        heightPlus.setBezelStyle_(AppKit.NSRoundedBezelStyle)
        heightPlus.setTarget_(self.buttonDelegate)
        heightPlus.setAction_("incrementHeight:")
        heightPlus.setTag_(index)
        parentView.addSubview_(heightPlus)
    
    @objc.python_method
    def updateDisplay(self, index, fieldType):
        """Update the displayed value for width or height."""
        panels = getattr(self.presetData, 'panels', [])
        if index >= len(panels):
            return
            
        panelData = panels[index]
        value = getattr(panelData, fieldType, 1)
        
        # Find the text field with the matching identifier
        identifier = f"{fieldType}_{index}"
        contentView = self.window.contentView()
        scrollView = contentView.subviews()[0]
        docView = scrollView.documentView()
        
        for subview in docView.subviews():
            if hasattr(subview, 'identifier') and subview.identifier() == identifier:
                subview.setStringValue_(str(value))
                break
    
    def incrementWidth(self, index):
        """Increment the width of a panel."""
        panels = getattr(self.presetData, 'panels', [])
        if index < len(panels):
            panelData = panels[index]
            currentWidth = getattr(panelData, 'width', 1)
            panelData.width = currentWidth + 1
            self.updateDisplay(index, 'width')
            # Update the live panel grid
            if self.preset:
                self.preset.updatePanelGrid(index)
    
    def decrementWidth(self, index):
        """Decrement the width of a panel."""
        panels = getattr(self.presetData, 'panels', [])
        if index < len(panels):
            panelData = panels[index]
            currentWidth = getattr(panelData, 'width', 1)
            if currentWidth > 1:  # Prevent going below 1
                panelData.width = currentWidth - 1
                self.updateDisplay(index, 'width')
                # Update the live panel grid
                if self.preset:
                    self.preset.updatePanelGrid(index)
    
    def incrementHeight(self, index):
        """Increment the height of a panel."""
        panels = getattr(self.presetData, 'panels', [])
        if index < len(panels):
            panelData = panels[index]
            currentHeight = getattr(panelData, 'height', 1)
            panelData.height = currentHeight + 1
            self.updateDisplay(index, 'height')
            # Update the live panel grid
            if self.preset:
                self.preset.updatePanelGrid(index)
    
    def decrementHeight(self, index):
        """Decrement the height of a panel."""
        panels = getattr(self.presetData, 'panels', [])
        if index < len(panels):
            panelData = panels[index]
            currentHeight = getattr(panelData, 'height', 1)
            if currentHeight > 1:  # Prevent going below 1
                panelData.height = currentHeight - 1
                self.updateDisplay(index, 'height')
                # Update the live panel grid
                if self.preset:
                    self.preset.updatePanelGrid(index)
    
    def close(self):
        """Close the configuration window."""
        self.window.close()
