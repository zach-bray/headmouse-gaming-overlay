#!/usr/bin/env python3
from PyObjCTools import AppHelper

import AppKit

from ui.window import Window
from core.utils import *

from model import Model

class AppController:
    def __init__(self):
        self.app = AppKit.NSApplication.sharedApplication()
        self.app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyRegular)
        
        self.model = Model()
        self.window = Window.alloc().initWithModel_(self.model)
    
    def run(self):
        AppHelper.runEventLoop()

if __name__ == "__main__":
    app = AppController()
    app.run()