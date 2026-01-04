#!/usr/bin/env python3
import sys
import objc
from PyObjCTools import AppHelper
from Cocoa import (
    NSApplication, NSWindow, NSApp, NSButton, NSTextField, NSScrollView, NSPanel,
    NSMakeRect, NSBackingStoreBuffered, NSTitledWindowMask, NSClosableWindowMask,
    NSMiniaturizableWindowMask, NSFloatingWindowLevel, NSApplicationActivationPolicyAccessory,
    NSNonactivatingPanelMask, NSView, NSMakeSize, NSNotificationCenter, NSColor, NSBezierPath,
    NSTrackingArea, NSTrackingMouseEnteredAndExited, NSTrackingMouseMoved, NSTrackingActiveAlways,
    NSTimer
)
from AppKit import NSEvent, NSKeyDown, NSWorkspace
import math
from Quartz import CGEventCreateKeyboardEvent, CGEventPost, kCGHIDEventTap, CGEventSetFlags, CGEventPostToPid
from Quartz import kCGEventFlagMaskCommand, kCGEventFlagMaskControl, kCGEventFlagMaskShift, kCGEventFlagMaskAlternate
import json
import os
import time

class JoystickView(NSView):
    """Custom view that acts as a hover joystick"""
    def initWithFrame_(self, frame):
        self = objc.super(JoystickView, self).initWithFrame_(frame)
        if self is None:
            return None
        
        self.controller = None
        self.current_direction = None
        self.held_keys = set()  # Track multiple held keys for diagonal movement
        self.mouse_inside = False
        self.last_mouse_location = None
        
        # Default joystick key mappings (can be configured)
        self.key_mappings = {
            "up": 0x7E,      # Up arrow
            "down": 0x7D,    # Down arrow
            "left": 0x7B,    # Left arrow
            "right": 0x7C    # Right arrow
        }
        
        # Start a timer to check mouse position
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.05,  # Check every 50ms
            self,
            "timerFired:",
            None,
            True
        )
        
        return self
    
    def setKeyMappings_(self, mappings):
        """Set custom key mappings for the joystick"""
        self.key_mappings = mappings
    
    def setController_(self, controller):
        self.controller = controller
    
    def updateTrackingAreas(self):
        """Set up mouse tracking"""
        # Remove old tracking areas
        for area in self.trackingAreas():
            self.removeTrackingArea_(area)
        
        # Add new tracking area
        tracking_area = NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
            self.bounds(),
            NSTrackingMouseEnteredAndExited | NSTrackingMouseMoved | NSTrackingActiveAlways,
            self,
            None
        )
        self.addTrackingArea_(tracking_area)
    
    def drawRect_(self, rect):
        """Draw the joystick circle"""
        # Fill background
        NSColor.colorWithRed_green_blue_alpha_(0.9, 0.9, 0.9, 1.0).setFill()
        NSBezierPath.fillRect_(self.bounds())
        
        # Draw outer circle
        bounds = self.bounds()
        size = min(bounds.size.width, bounds.size.height) - 20
        center_x = bounds.size.width / 2
        center_y = bounds.size.height / 2
        
        circle = NSBezierPath.bezierPath()
        circle.appendBezierPathWithOvalInRect_(
            NSMakeRect(center_x - size/2, center_y - size/2, size, size)
        )
        NSColor.colorWithRed_green_blue_alpha_(0.7, 0.7, 0.7, 1.0).setStroke()
        circle.setLineWidth_(2)
        circle.stroke()
        
        # Draw direction indicators
        if self.current_direction:
            NSColor.colorWithRed_green_blue_alpha_(0.3, 0.6, 1.0, 0.5).setFill()
            circle.fill()
        
        # Draw crosshair
        NSColor.colorWithRed_green_blue_alpha_(0.5, 0.5, 0.5, 1.0).setStroke()
        
        # Horizontal line
        h_line = NSBezierPath.bezierPath()
        h_line.moveToPoint_((center_x - size/2 + 10, center_y))
        h_line.lineToPoint_((center_x + size/2 - 10, center_y))
        h_line.stroke()
        
        # Vertical line
        v_line = NSBezierPath.bezierPath()
        v_line.moveToPoint_((center_x, center_y - size/2 + 10))
        v_line.lineToPoint_((center_x, center_y + size/2 - 10))
        v_line.stroke()
    
    def mouseMoved_(self, event):
        """Handle mouse movement over joystick"""
        location = self.convertPoint_fromView_(event.locationInWindow(), None)
        self.last_mouse_location = location
    
    def mouseEntered_(self, event):
        """Handle mouse entering joystick area"""
        self.mouse_inside = True
    
    def mouseExited_(self, event):
        """Handle mouse leaving joystick area"""
        self.mouse_inside = False
        self.last_mouse_location = None
        
        # Release all held keys
        for keycode in list(self.held_keys):
            self.controller.release_key(keycode)
        self.held_keys.clear()
        
        self.current_direction = None
        self.setNeedsDisplay_(True)
    
    def timerFired_(self, timer):
        """Timer callback to continuously check mouse position"""
        if not self.mouse_inside or not self.last_mouse_location or not self.controller:
            return
        
        location = self.last_mouse_location
        bounds = self.bounds()
        center_x = bounds.size.width / 2
        center_y = bounds.size.height / 2
        
        dx = location.x - center_x
        dy = location.y - center_y
        
        # Calculate distance
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 20:  # Dead zone in center
            # Release all keys if we're in dead zone
            for keycode in list(self.held_keys):
                self.controller.release_key(keycode)
            self.held_keys.clear()
            self.current_direction = None
            self.setNeedsDisplay_(True)
            return
        
        # Determine which keys should be pressed based on position
        keys_to_press = set()
        
        # Vertical component
        if dy > 10:  # Up threshold
            keys_to_press.add(self.key_mappings["up"])
        elif dy < -10:  # Down threshold
            keys_to_press.add(self.key_mappings["down"])
        
        # Horizontal component
        if dx > 10:  # Right threshold
            keys_to_press.add(self.key_mappings["right"])
        elif dx < -10:  # Left threshold
            keys_to_press.add(self.key_mappings["left"])
        
        # Release keys that are no longer needed
        keys_to_release = self.held_keys - keys_to_press
        for keycode in keys_to_release:
            self.controller.release_key(keycode)
        
        # Press new keys
        keys_to_add = keys_to_press - self.held_keys
        for keycode in keys_to_add:
            self.controller.press_key(keycode)
        
        # Update held keys
        if self.held_keys != keys_to_press:
            self.held_keys = keys_to_press
            
            # Update direction string for display
            directions = []
            if self.key_mappings["up"] in keys_to_press:
                directions.append("up")
            if self.key_mappings["down"] in keys_to_press:
                directions.append("down")
            if self.key_mappings["left"] in keys_to_press:
                directions.append("left")
            if self.key_mappings["right"] in keys_to_press:
                directions.append("right")
            
            self.current_direction = "+".join(directions) if directions else None
            self.setNeedsDisplay_(True)

class HotkeyWindow:
    def __init__(self):
        self.app = NSApplication.sharedApplication()
        self.app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        
        # Load hotkeys
        self.hotkeys = [
            {"label": "Jump", "keys": ["space"]},
            {"label": "Attack", "keys": ["control", "space"]},
            {"label": "Inventory", "keys": ["i"]},
            {"label": "Map", "keys": ["m"]},
            {"label": "Pause", "keys": ["escape"]},
            {"label": "Save", "keys": ["command", "s"]},
        ]
        self.load_hotkeys()
        
        # Joystick configuration
        self.joystick_config = {
            "up": "up",
            "down": "down", 
            "left": "left",
            "right": "right"
        }
        self.load_joystick_config()
        
        # Store button-to-hotkey mapping
        self.button_hotkey_map = {}
        
        # Create window using NSPanel which can be non-activating
        self.window = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(50, 500, 220, 400),
            NSTitledWindowMask | NSClosableWindowMask | NSMiniaturizableWindowMask | NSNonactivatingPanelMask | (1 << 3),  # Add NSResizableWindowMask
            NSBackingStoreBuffered,
            False
        )
        
        self.window.setTitle_("Game Hotkeys")
        self.window.setLevel_(NSFloatingWindowLevel)
        self.window.setAlphaValue_(0.95)
        self.window.setFloatingPanel_(True)
        self.window.setBecomesKeyOnlyIfNeeded_(True)
        self.window.setMinSize_(NSMakeRect(0, 0, 200, 200).size)
        
        # Show window without activating
        self.window.orderFront_(None)
        
        # Set window delegate to handle close event
        self.window.setDelegate_(self)
        
        # Store references to buttons and labels for resizing
        self.buttons = []
        self.labels = []
        self.joystick_view = None
        
        # Listen for window resize events
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self, 
            "windowDidResize:",
            "NSWindowDidResizeNotification",
            self.window
        )
        
        self.create_buttons()
        
    def load_hotkeys(self):
        """Load custom hotkeys from config file if it exists"""
        if os.path.exists("hotkeys_config.json"):
            try:
                with open("hotkeys_config.json", "r") as f:
                    self.hotkeys = json.load(f)
            except:
                pass
    
    def save_hotkeys(self):
        """Save current hotkeys to config file"""
        with open("hotkeys_config.json", "w") as f:
            json.dump(self.hotkeys, f, indent=2)
    
    def load_joystick_config(self):
        """Load joystick configuration from file"""
        if os.path.exists("joystick_config.json"):
            try:
                with open("joystick_config.json", "r") as f:
                    self.joystick_config = json.load(f)
            except:
                pass
    
    def save_joystick_config(self):
        """Save joystick configuration to file"""
        with open("joystick_config.json", "w") as f:
            json.dump(self.joystick_config, f, indent=2)
    
    def get_keycode(self, key_name):
        """Get macOS keycode for a key name"""
        keycode_map = {
            "a": 0x00, "s": 0x01, "d": 0x02, "f": 0x03, "h": 0x04,
            "g": 0x05, "z": 0x06, "x": 0x07, "c": 0x08, "v": 0x09,
            "b": 0x0B, "q": 0x0C, "w": 0x0D, "e": 0x0E, "r": 0x0F,
            "y": 0x10, "t": 0x11, "1": 0x12, "2": 0x13, "3": 0x14,
            "4": 0x15, "5": 0x17, "6": 0x16, "7": 0x1A, "8": 0x1C,
            "9": 0x19, "0": 0x1D, "o": 0x1F, "u": 0x20, "i": 0x22,
            "p": 0x23, "l": 0x25, "j": 0x26, "k": 0x28, "n": 0x2D,
            "m": 0x2E, "space": 0x31, "escape": 0x35, "tab": 0x30,
            "return": 0x24, "delete": 0x33,
            "up": 0x7E, "down": 0x7D, "left": 0x7B, "right": 0x7C
        }
        return keycode_map.get(key_name.lower(), 0x31)  # Default to space
    
    def create_buttons(self):
        """Create buttons for each hotkey that resize with window"""
        content_view = self.window.contentView()
        
        # Create joystick control at the top
        self.joystick_view = JoystickView.alloc().initWithFrame_(NSMakeRect(0, 0, 100, 100))
        self.joystick_view.setController_(self)
        
        # Set joystick key mappings from config
        key_mappings = {
            "up": self.get_keycode(self.joystick_config["up"]),
            "down": self.get_keycode(self.joystick_config["down"]),
            "left": self.get_keycode(self.joystick_config["left"]),
            "right": self.get_keycode(self.joystick_config["right"])
        }
        self.joystick_view.setKeyMappings_(key_mappings)
        
        content_view.addSubview_(self.joystick_view)
        
        # Add config button for joystick
        config_button = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 30, 20))
        config_button.setTitle_("⚙️")
        config_button.setBezelStyle_(1)
        config_button.setTarget_(self)
        config_button.setAction_("configureJoystick:")
        content_view.addSubview_(config_button)
        self.joystick_config_button = config_button
        
        for idx, hotkey in enumerate(self.hotkeys):
            # Create button (size will be set by layout_buttons)
            button = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 100, 40))
            button.setTitle_(hotkey["label"])
            button.setBezelStyle_(1)  # Rounded button
            button.setTag_(idx)
            button.setTarget_(self)
            button.setAction_("executeHotkey:")
            
            content_view.addSubview_(button)
            self.buttons.append(button)
            
            # Add key label
            keys_str = " + ".join(hotkey["keys"])
            label = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, 100, 15))
            label.setStringValue_(f"({keys_str})")
            label.setEditable_(False)
            label.setBordered_(False)
            label.setBackgroundColor_(None)
            
            content_view.addSubview_(label)
            self.labels.append(label)
        
        # Do initial layout
        self.layout_buttons()
    
    def layout_buttons(self):
        """Layout buttons to fill the window"""
        content_view = self.window.contentView()
        window_width = content_view.frame().size.width
        window_height = content_view.frame().size.height
        
        padding = 10
        
        # Position config button in top-right corner
        if hasattr(self, 'joystick_config_button'):
            self.joystick_config_button.setFrame_(NSMakeRect(window_width - 40, window_height - 30, 30, 20))
        
        # Position joystick at top - make it square based on window width
        joystick_size = min(window_width - 2 * padding, 150)
        joystick_y = window_height - joystick_size - padding
        self.joystick_view.setFrame_(NSMakeRect(padding, joystick_y, window_width - 2 * padding, joystick_size))
        
        # Calculate space for buttons below joystick
        available_height = joystick_y - padding
        
        num_buttons = len(self.hotkeys)
        if num_buttons == 0:
            return
        
        # Calculate button dimensions
        label_height = 18
        label_spacing = 5
        button_spacing = 10
        
        total_label_space = num_buttons * (label_height + label_spacing)
        total_button_spacing = (num_buttons + 1) * button_spacing
        
        available_for_buttons = available_height - total_label_space - total_button_spacing
        button_height = max(30, available_for_buttons / num_buttons)
        button_width = window_width - (2 * padding)
        
        y_pos = joystick_y - button_spacing
        
        for idx in range(num_buttons):
            self.buttons[idx].setFrame_(NSMakeRect(padding, y_pos - button_height, button_width, button_height))
            self.labels[idx].setFrame_(NSMakeRect(padding, y_pos - button_height - label_spacing - label_height, button_width, label_height))
            y_pos -= (button_height + label_height + label_spacing + button_spacing)
    
    def windowDidResize_(self, notification):
        """Handle window resize events"""
        self.layout_buttons()
    
    def windowShouldClose_(self, sender):
        """Handle window close button - quit the app"""
        NSApp.terminate_(None)
        return True
    
    def executeHotkey_(self, sender):
        """Execute the hotkey when button is clicked"""
        idx = sender.tag()
        if 0 <= idx < len(self.hotkeys):
            hotkey = self.hotkeys[idx]
            # Send keys immediately - they go to the frontmost app
            self.send_keys(hotkey["keys"])
    
    def send_keys(self, keys):
        """Send keyboard events using Quartz"""
        # Key code mapping
        keycode_map = {
            "a": 0x00, "s": 0x01, "d": 0x02, "f": 0x03, "h": 0x04,
            "g": 0x05, "z": 0x06, "x": 0x07, "c": 0x08, "v": 0x09,
            "b": 0x0B, "q": 0x0C, "w": 0x0D, "e": 0x0E, "r": 0x0F,
            "y": 0x10, "t": 0x11, "1": 0x12, "2": 0x13, "3": 0x14,
            "4": 0x15, "5": 0x17, "6": 0x16, "7": 0x1A, "8": 0x1C,
            "9": 0x19, "0": 0x1D, "o": 0x1F, "u": 0x20, "i": 0x22,
            "p": 0x23, "l": 0x25, "j": 0x26, "k": 0x28, "n": 0x2D,
            "m": 0x2E, "space": 0x31, "escape": 0x35, "tab": 0x30,
            "return": 0x24, "delete": 0x33,
        }
        
        # Determine modifiers
        flags = 0
        regular_key = None
        
        for key in keys:
            key_lower = key.lower()
            if key_lower in ["command", "cmd"]:
                flags |= kCGEventFlagMaskCommand
            elif key_lower in ["control", "ctrl"]:
                flags |= kCGEventFlagMaskControl
            elif key_lower in ["shift"]:
                flags |= kCGEventFlagMaskShift
            elif key_lower in ["option", "alt"]:
                flags |= kCGEventFlagMaskAlternate
            else:
                regular_key = key_lower
        
        # Get keycode
        if regular_key and regular_key in keycode_map:
            keycode = keycode_map[regular_key]
            
            # Create and post key down event
            event = CGEventCreateKeyboardEvent(None, keycode, True)
            if flags:
                CGEventSetFlags(event, flags)
            CGEventPost(kCGHIDEventTap, event)
            
            # Create and post key up event
            event = CGEventCreateKeyboardEvent(None, keycode, False)
            CGEventPost(kCGHIDEventTap, event)
    
    def send_arrow_key(self, keycode):
        """Send arrow key press (used by joystick) - DEPRECATED, use press/release instead"""
        # Try to get the frontmost app to send keys directly to it
        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        
        if active_app:
            pid = active_app.processIdentifier()
            
            # Send key down
            event = CGEventCreateKeyboardEvent(None, keycode, True)
            CGEventPostToPid(pid, event)
            
            # Small delay
            time.sleep(0.001)
            
            # Send key up
            event = CGEventCreateKeyboardEvent(None, keycode, False)
            CGEventPostToPid(pid, event)
        else:
            # Fallback to system-wide posting
            event = CGEventCreateKeyboardEvent(None, keycode, True)
            CGEventPost(kCGHIDEventTap, event)
            
            event = CGEventCreateKeyboardEvent(None, keycode, False)
            CGEventPost(kCGHIDEventTap, event)
    
    def press_key(self, keycode):
        """Press and hold a key"""
        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        
        if active_app:
            pid = active_app.processIdentifier()
            event = CGEventCreateKeyboardEvent(None, keycode, True)
            CGEventPostToPid(pid, event)
        else:
            event = CGEventCreateKeyboardEvent(None, keycode, True)
            CGEventPost(kCGHIDEventTap, event)
    
    def release_key(self, keycode):
        """Release a held key"""
        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        
        if active_app:
            pid = active_app.processIdentifier()
            event = CGEventCreateKeyboardEvent(None, keycode, False)
            CGEventPostToPid(pid, event)
        else:
            event = CGEventCreateKeyboardEvent(None, keycode, False)
            CGEventPost(kCGHIDEventTap, event)
    
    def run(self):
        """Start the application"""
        AppHelper.runEventLoop()

if __name__ == "__main__":
    print("Starting Hotkey Window...")
    print("Look for a floating window titled 'Game Hotkeys'")
    app = HotkeyWindow()
    app.run()