import AppKit
import objc

class ButtonDelegate(AppKit.NSObject):
    """Helper delegate to handle button actions."""
    
    def initWithConfigWindow_(self, config_window):
        self = objc.super(ButtonDelegate, self).init()
        if self:
            self.config_window = config_window
        return self
    
    def incrementWidth_(self, sender):
        self.config_window.incrementWidth(sender.tag())
    
    def decrementWidth_(self, sender):
        self.config_window.decrementWidth(sender.tag())
    
    def incrementHeight_(self, sender):
        self.config_window.incrementHeight(sender.tag())
    
    def decrementHeight_(self, sender):
        self.config_window.decrementHeight(sender.tag())
    
    def windowWillClose_(self, notification):
        if self.config_window.preset:
            self.config_window.preset.configWindowDidClose()

class PresetConfigWindow:
    """Configuration window for editing preset panel dimensions."""
    
    def __init__(self, preset_data, model, preset=None):
        self.preset_data = preset_data
        self.model = model
        self.preset = preset  # Reference to the Preset object to update live panels
        
        # Create button delegate
        self.button_delegate = ButtonDelegate.alloc().initWithConfigWindow_(self)
        
        # Create window
        self.setupWindow()
        self.setupUI()
        self.window.makeKeyAndOrderFront_(None)
    
    def setupWindow(self):
        """Create the configuration panel."""
        # Panel dimensions
        win_width = 400
        win_height = 300
        
        # Center the panel on screen
        screen = AppKit.NSScreen.mainScreen().frame()
        x = (screen.size.width - win_width) / 2
        y = (screen.size.height - win_height) / 2
        rect = AppKit.NSMakeRect(x, y, win_width, win_height)
        
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
        self.window.setDelegate_(self.button_delegate)
        
        preset_name = getattr(self.preset_data, 'name', 'Preset')
        self.window.setTitle_(f"Configure {preset_name}")
        self.window.setAlphaValue_(0.95)
    
    def setupUI(self):
        """Setup the UI elements in the window."""
        content_view = self.window.contentView()
        bounds = content_view.bounds()
        
        # Create scroll view for panel list
        scroll_view = AppKit.NSScrollView.alloc().initWithFrame_(
            AppKit.NSMakeRect(20, 20, bounds.size.width - 40, bounds.size.height - 40)
        )
        scroll_view.setHasVerticalScroller_(True)
        scroll_view.setHasHorizontalScroller_(False)
        scroll_view.setBorderType_(AppKit.NSBezelBorder)
        scroll_view.setAutoresizingMask_(
            AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable
        )
        
        # Create document view (container for panel items)
        panels = getattr(self.preset_data, 'panels', [])
        num_panels = len(panels)
        item_height = 60
        total_height = max(num_panels * item_height + 20, bounds.size.height - 40)
        
        doc_view = AppKit.NSView.alloc().initWithFrame_(
            AppKit.NSMakeRect(0, 0, bounds.size.width - 60, total_height)
        )
        
        # Create UI for each panel
        for i, panel_data in enumerate(panels):
            y_pos = total_height - (i + 1) * item_height
            self.createPanelRow(doc_view, panel_data, i, y_pos, item_height)
        
        scroll_view.setDocumentView_(doc_view)
        content_view.addSubview_(scroll_view)
    
    def createPanelRow(self, parent_view, panel_data, index, y_pos, height):
        """Create a row for one panel with its width/height controls."""
        row_width = parent_view.bounds().size.width
        
        # Panel label
        label = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(10, y_pos + 20, 80, 20)
        )
        label.setStringValue_(f"Panel {index + 1}:")
        label.setBezeled_(False)
        label.setDrawsBackground_(False)
        label.setEditable_(False)
        label.setSelectable_(False)
        parent_view.addSubview_(label)
        
        # Width controls
        width_label = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(100, y_pos + 20, 50, 20)
        )
        width_label.setStringValue_("Width:")
        width_label.setBezeled_(False)
        width_label.setDrawsBackground_(False)
        width_label.setEditable_(False)
        width_label.setSelectable_(False)
        parent_view.addSubview_(width_label)
        
        # Width minus button
        width_minus = AppKit.NSButton.alloc().initWithFrame_(
            AppKit.NSMakeRect(160, y_pos + 18, 30, 24)
        )
        width_minus.setTitle_("-")
        width_minus.setBezelStyle_(AppKit.NSRoundedBezelStyle)
        width_minus.setTarget_(self.button_delegate)
        width_minus.setAction_("decrementWidth:")
        width_minus.setTag_(index)
        parent_view.addSubview_(width_minus)
        
        # Width value display
        current_width = getattr(panel_data, 'width', 1)
        width_value = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(195, y_pos + 20, 40, 20)
        )
        width_value.setStringValue_(str(current_width))
        width_value.setBezeled_(False)
        width_value.setDrawsBackground_(False)
        width_value.setEditable_(False)
        width_value.setAlignment_(AppKit.NSTextAlignmentCenter)
        # Tag it so we can update it later
        width_value.setIdentifier_(f"width_{index}")
        parent_view.addSubview_(width_value)
        
        # Width plus button
        width_plus = AppKit.NSButton.alloc().initWithFrame_(
            AppKit.NSMakeRect(240, y_pos + 18, 30, 24)
        )
        width_plus.setTitle_("+")
        width_plus.setBezelStyle_(AppKit.NSRoundedBezelStyle)
        width_plus.setTarget_(self.button_delegate)
        width_plus.setAction_("incrementWidth:")
        width_plus.setTag_(index)
        parent_view.addSubview_(width_plus)
        
        # Height controls
        height_label = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(100, y_pos - 5, 50, 20)
        )
        height_label.setStringValue_("Height:")
        height_label.setBezeled_(False)
        height_label.setDrawsBackground_(False)
        height_label.setEditable_(False)
        height_label.setSelectable_(False)
        parent_view.addSubview_(height_label)
        
        # Height minus button
        height_minus = AppKit.NSButton.alloc().initWithFrame_(
            AppKit.NSMakeRect(160, y_pos - 7, 30, 24)
        )
        height_minus.setTitle_("-")
        height_minus.setBezelStyle_(AppKit.NSRoundedBezelStyle)
        height_minus.setTarget_(self.button_delegate)
        height_minus.setAction_("decrementHeight:")
        height_minus.setTag_(index)
        parent_view.addSubview_(height_minus)
        
        # Height value display
        current_height = getattr(panel_data, 'height', 1)
        height_value = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(195, y_pos - 5, 40, 20)
        )
        height_value.setStringValue_(str(current_height))
        height_value.setBezeled_(False)
        height_value.setDrawsBackground_(False)
        height_value.setEditable_(False)
        height_value.setAlignment_(AppKit.NSTextAlignmentCenter)
        # Tag it so we can update it later
        height_value.setIdentifier_(f"height_{index}")
        parent_view.addSubview_(height_value)
        
        # Height plus button
        height_plus = AppKit.NSButton.alloc().initWithFrame_(
            AppKit.NSMakeRect(240, y_pos - 7, 30, 24)
        )
        height_plus.setTitle_("+")
        height_plus.setBezelStyle_(AppKit.NSRoundedBezelStyle)
        height_plus.setTarget_(self.button_delegate)
        height_plus.setAction_("incrementHeight:")
        height_plus.setTag_(index)
        parent_view.addSubview_(height_plus)
    
    @objc.python_method
    def updateDisplay(self, index, field_type):
        """Update the displayed value for width or height."""
        panels = getattr(self.preset_data, 'panels', [])
        if index >= len(panels):
            return
            
        panel_data = panels[index]
        value = getattr(panel_data, field_type, 1)
        
        # Find the text field with the matching identifier
        identifier = f"{field_type}_{index}"
        content_view = self.window.contentView()
        scroll_view = content_view.subviews()[0]
        doc_view = scroll_view.documentView()
        
        for subview in doc_view.subviews():
            if hasattr(subview, 'identifier') and subview.identifier() == identifier:
                subview.setStringValue_(str(value))
                break
    
    def incrementWidth(self, index):
        """Increment the width of a panel."""
        panels = getattr(self.preset_data, 'panels', [])
        if index < len(panels):
            panel_data = panels[index]
            current_width = getattr(panel_data, 'width', 1)
            panel_data.width = current_width + 1
            self.updateDisplay(index, 'width')
            # Update the live panel grid
            if self.preset:
                self.preset.updatePanelGrid(index)
    
    def decrementWidth(self, index):
        """Decrement the width of a panel."""
        panels = getattr(self.preset_data, 'panels', [])
        if index < len(panels):
            panel_data = panels[index]
            current_width = getattr(panel_data, 'width', 1)
            if current_width > 1:  # Prevent going below 1
                panel_data.width = current_width - 1
                self.updateDisplay(index, 'width')
                # Update the live panel grid
                if self.preset:
                    self.preset.updatePanelGrid(index)
    
    def incrementHeight(self, index):
        """Increment the height of a panel."""
        panels = getattr(self.preset_data, 'panels', [])
        if index < len(panels):
            panel_data = panels[index]
            current_height = getattr(panel_data, 'height', 1)
            panel_data.height = current_height + 1
            self.updateDisplay(index, 'height')
            # Update the live panel grid
            if self.preset:
                self.preset.updatePanelGrid(index)
    
    def decrementHeight(self, index):
        """Decrement the height of a panel."""
        panels = getattr(self.preset_data, 'panels', [])
        if index < len(panels):
            panel_data = panels[index]
            current_height = getattr(panel_data, 'height', 1)
            if current_height > 1:  # Prevent going below 1
                panel_data.height = current_height - 1
                self.updateDisplay(index, 'height')
                # Update the live panel grid
                if self.preset:
                    self.preset.updatePanelGrid(index)
    
    def close(self):
        """Close the configuration window."""
        self.window.close()
