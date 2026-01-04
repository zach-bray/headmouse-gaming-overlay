import AppKit
import objc

class Button(AppKit.NSButton):

    def initWithFrame_(self, frame):
        self = objc.super(Button, self).initWithFrame_(frame)