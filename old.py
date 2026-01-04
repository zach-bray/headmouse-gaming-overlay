#!/usr/bin/env python3
import sys
import objc
from PyObjCTools import AppHelper

import AppKit
from Quartz import CGEventCreateKeyboardEvent, CGEventPost, kCGHIDEventTap, CGEventSetFlags, CGEventPostToPid
from AppKit import (
    NSScreen, NSApplication, NSWindow, NSApp, NSButton, NSTextField, NSScrollView, NSPanel,
    NSMakeRect, NSBackingStoreBuffered, NSTitledWindowMask, NSClosableWindowMask,
    NSMiniaturizableWindowMask, NSFloatingWindowLevel, NSApplicationActivationPolicyRegular,
    NSNonactivatingPanelMask, NSView, NSMakeSize, NSNotificationCenter, NSColor, NSBezierPath,
    NSTrackingArea,NSWindowCollectionBehaviorCanJoinAllSpaces, NSWindowCollectionBehaviorFullScreenAuxiliary,NSTrackingMouseEnteredAndExited, NSTrackingMouseMoved, NSTrackingActiveAlways,
    NSTimer, NSStackView,NSFont,NSStackViewDistributionFillEqually,NSForegroundColorAttributeName,NSFontAttributeName,NSString,NSCenterTextAlignment
)
from Foundation import NSTimer

from AppKit import NSEvent, NSKeyDown, NSWorkspace

from threading import Timer
import objc

class HotkeyWindow:
    def __init__(self):
        self.app = NSApplication.sharedApplication()
        self.app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
        
        self.win_w = 200
        self.win_h = 100

        screen = NSScreen.mainScreen().frame()
        x = (screen.size.width - self.win_w) / 2
        y = (screen.size.height - self.win_h) / 2
        win_rect = NSMakeRect(x, y, self.win_w, self.win_h)

        # Create window using NSPanel which can be non-activating
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            win_rect,
            NSTitledWindowMask | 
                NSClosableWindowMask | 
                NSMiniaturizableWindowMask,
            NSBackingStoreBuffered,
            False
        )
        
        self.window.setTitle_("4one7")
        self.window.setAlphaValue_(0.95)
        
        # Show window without activating
        self.window.orderFront_(None)
        
        # Set window delegate to handle close event
        self.window.setDelegate_(self)


        self.btn = NSButton.alloc().initWithFrame_(NSMakeRect(0,0,150,40))
        self.btn.setTitle_("DOS2")
        self.btn.setTarget_(self)
        self.btn.setAction_("showPanel:")
        self.window.contentView().addSubview_(self.btn)
        
        self.panel = None

    def showPanel_(self, sender):
        if not self.panel:
            self.panel = ZPanel()
    
   
    def windowShouldClose_(self, sender):
        NSApp.terminate_(None)
        return True
    
    def run(self):
        """Start the application"""
        AppHelper.runEventLoop()


class ZPanel:
    def __init__(self):
        print("Panel init")
        self.panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(50, 500, 110, 60),
            NSTitledWindowMask | 
                NSClosableWindowMask |
                NSMiniaturizableWindowMask | 
                NSNonactivatingPanelMask | 
                (1 << 3),  # Add NSResizableWindowMask
            NSBackingStoreBuffered,
            False
        )
        
        panel_spec = {
            "width": 7,
            "height": 1,
            "actions": [
                {
                    "key": "a",
                    "x": 0,
                    "y": 0,
                    "w": 1,
                    "h": 1
                },
                {
                    "key": "d",
                    "x": 1,
                    "y": 0,
                    "w": 1,
                    "h": 1
                }
            ]
        }

        self.panel.setTitle_("Game Hotkeys")
        self.panel.setLevel_(24)
        self.panel.setAlphaValue_(0.75)
        self.panel.setFloatingPanel_(True)
        self.panel.setBecomesKeyOnlyIfNeeded_(True)
        self.panel.setMinSize_(NSMakeRect(0, 0, 200, 200).size)
        
        # Combines behaviors to stay visible on top of full-screen apps
        self.panel.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces | 
            NSWindowCollectionBehaviorFullScreenAuxiliary
        )

        self.panel.makeKeyAndOrderFront_(None)

        self.setup_panel(panel_spec)

        # self.box = DwellBox.alloc().initWithFrame_key_(NSMakeRect(10,10,40,40), "a")
        # self.box2 = DwellBox.alloc().initWithFrame_key_(NSMakeRect(60,10,40,40), "d")
        # self.panel.contentView().addSubview_(self.box)
        # self.panel.contentView().addSubview_(self.box2)
        # self.box.setNeedsDisplay_(True)

    def setup_panel(self, panel):
        print("setup Panel")
        self.grid = {}
        rs = []
        print(panel)
        for row in range(panel.height):
            print("row")
            rv = []
            for col in range(panel.width):
                print("col")
                container = NSView.alloc().init()
                container.setAutoresizesSubviews_(True)

                rv.append(container)
                self.grid[(row, col)] = container
            
            cv = NSStackView.stackViewWithViews
            cv.setDistribution_(NSStackViewDistributionFillEqually)
            rs.append(cv)
        
        self.main_stack = NSStackView.stackViewWithViews_(rs)
        self.main_stack.setDistribution_(NSStackViewDistributionFillEqually)
        self.panel.setContentView_(self.main_stack)


class DwellBox(NSView):
    def initWithFrame_key_(self, frame, key):
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
            
            self.key = key
            self.keycode = keycode_map[self.key]
            self.is_pressed = False
            print("init Dwell")
            self = objc.super(DwellBox, self).initWithFrame_(frame) # type:ignore

            if self:
                # enter/exit, move, active 
                options = (0x01 | 0x02 | 0x04 | 0x80)

                self.area = NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
                     self.bounds(), options, self, None
                )

                self.addTrackingArea_(self.area)
                self.setWantsLayer_(True)
                self.timer = None
                self.delay = 0.1
                self.label = NSTextField.labelWithString_(self.key)
                self.label.setFrame_(self.bounds())
                self.label.setAlignment_(NSCenterTextAlignment)
                self.label.setTextColor_(NSColor.whiteColor())
                self.label.setFont_(NSFont.systemFontOfSize_(24))
                self.label.setDrawsBackground_(False)
                self.label.setBezeled_(False)
                self.label.setEditable_(False)
                self.label.setSelectable_(False)
                
                self.addSubview_(self.label)

            return self
    
    def drawRect_(self, rect):
        NSColor.systemBlueColor().set()
        NSBezierPath.fillRect_(self.bounds())

    @objc.python_method
    def triggerAction(self):
        self.press_key()
        print("Trigger")
    
    @objc.python_method
    def startTimer(self):
        self.release_key()
        if self.timer: self.timer.cancel()
        self.timer = Timer(self.delay, self.triggerAction)
        self.timer.start()

    def mouseEntered_(self, event):
        # print("Enter")
        self.startTimer()
        
    def mouseMoved_(self, event):
        # print("Move")
        self.startTimer()
    
    def mouseExited_(self, event):
        # print("Exit")
        if self.timer:
            self.timer.cancel()

    def press_key(self):
        print("press")
        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        
        if active_app:
            pid = active_app.processIdentifier()
            event = CGEventCreateKeyboardEvent(None, self.keycode, True)
            CGEventPostToPid(pid, event)
        else:
            event = CGEventCreateKeyboardEvent(None, self.keycode, True)
            CGEventPost(kCGHIDEventTap, event)

        self.is_pressed = True
    
    def release_key(self):
        if not self.is_pressed: return

        print("releease")
        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        
        if active_app:
            pid = active_app.processIdentifier()
            event = CGEventCreateKeyboardEvent(None, self.keycode, False)
            # CGEventPostToPid(pid, event)
            CGEventPost(kCGHIDEventTap, event)
        else:
            print("not active app")
            event = CGEventCreateKeyboardEvent(None, self.keycode, False)
            # CGEventPost(kCGHIDEventTap, event)
            CGEventPost(kCGHIDEventTap, event)

        self.is_pressed = False


if __name__ == "__main__":
    print("Starting tool")
    app = HotkeyWindow()
    app.run()