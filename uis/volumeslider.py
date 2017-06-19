from remi import gui as gui


class VolumeSlider(gui.Slider):
    def set_on_mousedown_listener(self, callback, *userdata):
        """Registers the listener for the Widget.onmousedown event.

        Note: the listener prototype have to be in the form on_widget_mousedown(self, widget, x, y).

        Args:
            callback (function): Callback function pointer.
        """
        self.attributes[self.EVENT_ONMOUSEDOWN] = \
            "var params={};" \
            "params['x']=event.clientX-this.offsetLeft;" \
            "params['y']=event.clientY-this.offsetTop;" \
            "sendCallbackParam('%s','%s',params);" % (self.identifier, self.EVENT_ONMOUSEDOWN)
        self.eventManager.register_listener(self.EVENT_ONMOUSEDOWN, callback, *userdata)

    def set_on_mouseup_listener(self, callback, *userdata):
        """Registers the listener for the Widget.onmouseup event.

        Note: the listener prototype have to be in the form on_widget_mouseup(self, widget, x, y).

        Args:
            callback (function): Callback function pointer.
        """
        self.attributes[self.EVENT_ONMOUSEUP] = \
            "var params={};" \
            "params['x']=event.clientX-this.offsetLeft;" \
            "params['y']=event.clientY-this.offsetTop;" \
            "sendCallbackParam('%s','%s',params);" % (self.identifier, self.EVENT_ONMOUSEUP)
        self.eventManager.register_listener(self.EVENT_ONMOUSEUP, callback, *userdata)
