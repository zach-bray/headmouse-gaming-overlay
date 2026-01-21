#!/usr/bin/env python3
from PyObjCTools import AppHelper

import objc
import AppKit

from controllers.MainWindowController import MainWindowController
from model import Model
import objc

class AppController(AppKit.NSObject):
    def init(self):
        self = objc.super(AppController, self).init()
        if not self: return None
        
        self.app = AppKit.NSApplication.sharedApplication()
        self.app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyRegular)
        
        self.model = Model()
        self.windowController = MainWindowController.alloc().initWithModel_(self.model)
        self.windowController.showWindow()
        
        return self

    def run(self):
        AppHelper.runEventLoop()

if __name__ == "__main__":
    app = AppController.alloc().init()
    app.run()