import AppKit
import objc
from core.utils import *
from types import SimpleNamespace

# The main window. Lists the presets

class PresetsView(AppKit.NSView):
    def initWithFrame_model_target_(self, frame, model, target):
        self = objc.super(PresetsView, self).initWithFrame_(frame)
        if not self:
            return None

        self.model = model
        self.target = target
        self.presets = model.presets

        self.drawPresets()

        return self

    def drawPresets(self):
        # Create scroll view to match the view's bounds
        scroll = AppKit.NSScrollView.alloc().initWithFrame_(self.bounds())
        scroll.setHasVerticalScroller_(True)
        scroll.setAutoresizingMask_(AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable)

        stack = AppKit.NSStackView.stackViewWithViews_([])
        stack.setOrientation_(AppKit.NSUserInterfaceLayoutOrientationVertical)
        stack.setSpacing_(8)
        stack.setEdgeInsets_((10,10,10,10))


        for i, preset in enumerate(self.presets):
            # setup row for buttons
            row = AppKit.NSStackView.stackViewWithViews_([])
            row.setOrientation_(AppKit.NSUserInterfaceLayoutOrientationHorizontal)
            row.setSpacing_(8.0)
            
            # preset button, click to toggle
            btn = AppKit.NSButton.buttonWithTitle_target_action_(preset.name, self.target, "openPreset:")
            btn.setTag_(i)
            btn.setBezelStyle_(AppKit.NSBezelStyleRounded)
            # Use PushOnPushOff to allow persistent active state
            btn.setButtonType_(AppKit.NSButtonTypePushOnPushOff)

            # edit button
            editIcon = AppKit.NSImage.imageWithSystemSymbolName_accessibilityDescription_("pencil", "Edit")
            editBtn = AppKit.NSButton.buttonWithImage_target_action_(editIcon, self.target, "editPreset:")
            editBtn.setTag_(i)
            editBtn.setBezelStyle_(AppKit.NSBezelStyleRounded)

            # add to view
            row.addArrangedSubview_(btn)
            row.addArrangedSubview_(editBtn)
            stack.addArrangedSubview_(row)


        scroll.contentView().setWantsLayer_(True)  # Must be True for borders to show
        scroll.contentView().layer().setBorderWidth_(2.0) # 0.028 in / 0.70 mm
        scroll.contentView().layer().setBorderColor_(AppKit.NSColor.redColor().CGColor())
        stack.setWantsLayer_(True)  # Must be True for borders to show
        stack.layer().setBorderWidth_(2.0) # 0.028 in / 0.70 mm
        stack.layer().setBorderColor_(AppKit.NSColor.blueColor().CGColor())

        scroll.setDocumentView_(stack)
        self.addSubview_(scroll)