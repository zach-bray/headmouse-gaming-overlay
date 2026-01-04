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

from AppKit import NSEvent, NSKeyDown, NSWorkspace

# from ui.panel import Panel

from threading import Timer
import objc

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
