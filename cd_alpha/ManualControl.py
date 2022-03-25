from distutils.log import info
import kivy
kivy.require('2.0.0')
#from NanoController import Nano
#from NewEraPumps import PumpNetwork

from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty


class RedPumps:
    pass

class ManualControlApp(App):
    def build(self):
        return ManualControl(info="0.00")


class ManualControl(FloatLayout):
    '''Create a controller that receives a custom widget from the kv lang file.

    Add an action to be called from the kv lang file.
    '''
    label_wid = ObjectProperty()
    info = StringProperty()
    run_status = StringProperty()

    run_status = "START"

    def do_action(self):
        print("Doing Action")
        self.run_status = "STOP"

if __name__ == '__main__':
    ManualControlApp().run()