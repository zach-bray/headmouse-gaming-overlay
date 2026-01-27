#!/usr/bin/env python3
from PyObjCTools import AppHelper

import objc
import AppKit

from controllers.mainWindowController import MainWindowController
from model import Model
import objc

class AppController(AppKit.NSObject):
    def init(self):
        self = objc.super(AppController, self).init()
        if not self: return None
        
        self.app = AppKit.NSApplication.sharedApplication()
        self.app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyRegular)
        self.app.setDelegate_(self)  # Set self as app delegate to handle termination
        
        self.model = Model()
        self.windowController = MainWindowController.alloc().initWithModel_(self.model)
        self.windowController.showWindow()
        
        return self
    
    def applicationWillTerminate_(self, notification):
        """Save all preset data when the application is about to quit."""
        print("Application terminating...")
        if self.model:
            self.model.save()

    def run(self):
        AppHelper.runEventLoop()

if __name__ == "__main__":
    app = AppController.alloc().init()
    app.run()