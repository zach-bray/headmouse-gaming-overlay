#!/usr/bin/env python3
"""
Dwell Hover Right-Click Application
A lightweight macOS app with a hover box activated by dwelling, which then
triggers a right-click at the cursor location after another dwell period.
"""

from Cocoa import (
    NSApplication, NSWindow, NSView, NSTextField, NSColor, NSBezierPath, NSTimer,
    NSMakeRect, NSBackingStoreBuffered,
    NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
    NSWindowStyleMaskMiniaturizable,
    NSApplicationActivationPolicyRegular, NSCenterTextAlignment,
    NSTrackingArea, NSTrackingMouseEnteredAndExited, 
    NSTrackingActiveAlways, NSTrackingInVisibleRect,
    NSFont, NSFontWeightMedium
)
from Quartz import (
    CGEventCreateMouseEvent, CGEventPost, CGEventCreate, CGEventGetLocation,
    kCGEventRightMouseDown, kCGEventRightMouseUp, 
    kCGMouseButtonRight, kCGHIDEventTap
)
from PyObjCTools import AppHelper
import objc
import time

# Configuration
DWELL_TIME = 0.25  # seconds to hover before activation


class DwellBox(NSView):
    """Custom view that acts as a dwell-activated box."""
    
    def init(self):
        self = objc.super(DwellBox, self).init()
        if self is None:
            return None
        
        self.hover_active = False
        self.is_dwelling = False  # True when mouse is still and timer is running
        self.dwell_timer = None
        self.right_click_pending = False
        self.last_mouse_position = None
        self.dwell_threshold = 5  # pixels of allowed movement
        
        return self
    
    def updateTrackingAreas(self):
        """Set up tracking area for hover detection."""
        # Remove existing tracking areas
        for area in self.trackingAreas():
            self.removeTrackingArea_(area)
        
        # Create new tracking area - also track mouse moved
        from Cocoa import NSTrackingMouseMoved
        tracking_area = NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
            self.bounds(),
            NSTrackingMouseEnteredAndExited | NSTrackingMouseMoved | NSTrackingActiveAlways | NSTrackingInVisibleRect,
            self,
            None
        )
        self.addTrackingArea_(tracking_area)
    
    def drawRect_(self, rect):
        """Draw the box with current state."""
        # Set background color based on state
        if self.right_click_pending:
            NSColor.colorWithRed_green_blue_alpha_(0.2, 0.6, 1.0, 1.0).setFill()
        else:
            NSColor.colorWithRed_green_blue_alpha_(0.3, 0.3, 0.3, 1.0).setFill()
        
        # Draw rounded rectangle
        path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
            self.bounds(),
            10.0,
            10.0
        )
        path.fill()
        
        # Draw border
        NSColor.colorWithRed_green_blue_alpha_(0.6, 0.6, 0.6, 1.0).setStroke()
        path.setLineWidth_(2.0)
        path.stroke()
        
        # Draw text
        if self.right_click_pending:
            text = "DWELL"
        else:
            text = "HOVER"
        
        # Set up text attributes
        from Cocoa import NSAttributedString, NSForegroundColorAttributeName, NSFontAttributeName, NSParagraphStyleAttributeName, NSMutableParagraphStyle
        
        paragraph_style = NSMutableParagraphStyle.alloc().init()
        paragraph_style.setAlignment_(NSCenterTextAlignment)
        
        attrs = {
            NSForegroundColorAttributeName: NSColor.whiteColor(),
            NSFontAttributeName: NSFont.systemFontOfSize_weight_(10, NSFontWeightMedium),
            NSParagraphStyleAttributeName: paragraph_style
        }
        
        attr_string = NSAttributedString.alloc().initWithString_attributes_(text, attrs)
        
        # Calculate text position (centered)
        text_size = attr_string.size()
        text_rect = NSMakeRect(
            (self.bounds().size.width - text_size.width) / 2,
            (self.bounds().size.height - text_size.height) / 2,
            text_size.width,
            text_size.height
        )
        
        attr_string.drawInRect_(text_rect)
    
    def mouseEntered_(self, event):
        """Called when mouse enters the box area."""
        if not self.right_click_pending:
            self.hover_active = True
            self.last_mouse_position = event.locationInWindow()
            self.setNeedsDisplay_(True)
            self.startDwellTimer()
    
    def mouseExited_(self, event):
        """Called when mouse leaves the box area."""
        if not self.right_click_pending:
            self.hover_active = False
            self.last_mouse_position = None
            self.setNeedsDisplay_(True)
            self.cancelDwellTimer()
    
    def mouseMoved_(self, event):
        """Called when mouse moves within the box area."""
        if self.hover_active and not self.right_click_pending:
            current_position = event.locationInWindow()
            
            if self.last_mouse_position is not None:
                # Calculate distance moved
                dx = current_position.x - self.last_mouse_position.x
                dy = current_position.y - self.last_mouse_position.y
                distance = (dx * dx + dy * dy) ** 0.5
                
                # If moved more than threshold, reset timer and visual state
                if distance > self.dwell_threshold:
                    self.is_dwelling = False
                    self.setNeedsDisplay_(True)
                    self.cancelDwellTimer()
                    self.startDwellTimer()
            
            self.last_mouse_position = current_position
    
    def startDwellTimer(self):
        """Start the dwell timer."""
        self.cancelDwellTimer()
        self.is_dwelling = True
        self.setNeedsDisplay_(True)
        self.dwell_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            DWELL_TIME,
            self,
            "dwellTimerFired:",
            None,
            False
        )
    
    def cancelDwellTimer(self):
        """Cancel the dwell timer."""
        if self.dwell_timer is not None:
            self.dwell_timer.invalidate()
            self.dwell_timer = None
    
    def dwellTimerFired_(self, timer):
        """Called when dwell timer completes."""
        self.dwell_timer = None
        self.activateBox()
    
    def activateBox(self):
        """Activate the box and prepare for right-click."""
        from Quartz import CGEventCreate, CGEventGetLocation
        
        self.hover_active = False
        self.is_dwelling = False
        self.right_click_pending = True
        self.setNeedsDisplay_(True)
        
        # Store the activation position - don't start monitoring until mouse moves away
        current_event = CGEventCreate(None)
        self.activation_pos = CGEventGetLocation(current_event)
        self.has_moved_after_activation = False
        
        # Start checking if mouse has moved away
        self.movement_check_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.1,
            self,
            "checkInitialMovement:",
            None,
            True
        )
    
    def checkInitialMovement_(self, timer):
        """Check if cursor has moved away from activation position."""
        from Quartz import CGEventCreate, CGEventGetLocation
        
        current_event = CGEventCreate(None)
        current_pos = CGEventGetLocation(current_event)
        
        # Calculate distance from activation position
        dx = current_pos.x - self.activation_pos.x
        dy = current_pos.y - self.activation_pos.y
        distance = (dx * dx + dy * dy) ** 0.5
        
        # If moved more than threshold, start the dwell monitoring
        if distance > self.dwell_threshold:
            self.movement_check_timer.invalidate()
            self.movement_check_timer = None
            self.startCursorDwellTimer()
    
    def startCursorDwellTimer(self):
        """Start monitoring cursor position for dwell to trigger right-click."""
        from Quartz import CGEventCreate, CGEventGetLocation
        
        # Store initial cursor position
        current_event = CGEventCreate(None)
        self.cursor_start_pos = CGEventGetLocation(current_event)
        self.cursor_dwell_started = time.time()
        
        # Use a repeating timer to check cursor position
        self.cursor_check_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.1,  # Check every 100ms
            self,
            "checkCursorDwell:",
            None,
            True
        )
    
    def checkCursorDwell_(self, timer):
        """Check if cursor has stayed in roughly the same position."""
        from Quartz import CGEventCreate, CGEventGetLocation
        
        # Get current cursor position
        current_event = CGEventCreate(None)
        current_pos = CGEventGetLocation(current_event)
        
        # Calculate distance moved from start position
        dx = current_pos.x - self.cursor_start_pos.x
        dy = current_pos.y - self.cursor_start_pos.y
        distance = (dx * dx + dy * dy) ** 0.5
        
        # If cursor moved too much, reset the dwell timer
        if distance > self.dwell_threshold:
            self.cursor_start_pos = current_pos
            self.cursor_dwell_started = time.time()
        
        # Check if enough time has passed
        if time.time() - self.cursor_dwell_started >= DWELL_TIME:
            self.cursor_check_timer.invalidate()
            self.cursor_check_timer = None
            self.performRightClick()
    
    def performRightClick(self):
        """Simulate a right-click at the current cursor position."""
        # Get current mouse location using CGEvent
        current_event = CGEventCreate(None)
        mouse_location = CGEventGetLocation(current_event)
        
        # Create right mouse down event
        down_event = CGEventCreateMouseEvent(
            None,
            kCGEventRightMouseDown,
            mouse_location,
            kCGMouseButtonRight
        )
        
        # Post mouse down
        CGEventPost(kCGHIDEventTap, down_event)
        
        # Small delay between down and up
        time.sleep(0.05)
        
        # Create right mouse up event
        up_event = CGEventCreateMouseEvent(
            None,
            kCGEventRightMouseUp,
            mouse_location,
            kCGMouseButtonRight
        )
        
        # Post mouse up
        CGEventPost(kCGHIDEventTap, up_event)
        
        # Reset state
        self.resetBox()
    
    def resetBox(self):
        """Reset box to initial state."""
        self.right_click_pending = False
        self.hover_active = False
        self.is_dwelling = False
        self.setNeedsDisplay_(True)
        
        if hasattr(self, 'cursor_check_timer') and self.cursor_check_timer is not None:
            self.cursor_check_timer.invalidate()
            self.cursor_check_timer = None
        
        if hasattr(self, 'movement_check_timer') and self.movement_check_timer is not None:
            self.movement_check_timer.invalidate()
            self.movement_check_timer = None


class AppDelegate(NSView):
    """Application delegate."""
    
    def applicationDidFinishLaunching_(self, notification):
        """Called when application finishes launching."""
        pass
    
    def applicationShouldTerminateAfterLastWindowClosed_(self, app):
        """Quit app when window closes."""
        return True


def main():
    """Main application entry point."""
    # Create application
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
    
    # Create window
    window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(100, 100, 60, 60),
        NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskMiniaturizable,
        NSBackingStoreBuffered,
        False
    )
    window.setTitle_("Dwell")
    window.setLevel_(3)  # Keep window on top
    window.setAlphaValue_(0.8)  # Set transparency
    
    # Create dwell box
    dwell_box = DwellBox.alloc().init()
    dwell_box.setFrame_(NSMakeRect(5, 5, 50, 50))
    
    # Add view to window
    window.contentView().addSubview_(dwell_box)
    
    # Set up delegate
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    
    # Show window and run
    window.makeKeyAndOrderFront_(None)
    app.activateIgnoringOtherApps_(True)
    
    print("\nDwell Right-Click App Started")
    print("Hover over the box to activate\n")
    
    AppHelper.runEventLoop()


if __name__ == "__main__":
    main()