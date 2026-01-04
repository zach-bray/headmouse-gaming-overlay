import os
import sys
import json


def getResourcePath(relativePath):
    
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller temporary folder
        basePath = sys._MEIPASS
    else:
        # Development folder (root of your project)
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)

PRESET_DIR = getResourcePath("resources/presets")