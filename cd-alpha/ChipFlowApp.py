# !/usr/bin/python3

# To execute remotely use:
# DISPLAY=:0.0 python3 ChipFlowApp.py

from collections import OrderedDict
import json
import sys
import os

from NanoController import Nano
from NewEraPumps import PumpNetwork
from functools import partial
import serial
import time
from datetime import datetime
import logging
time_now_str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
logging.basicConfig(
    filename=f"/home/pi/cd-alpha/logs/cda_{time_now_str}.log",
    filemode='w',
    datefmt="%Y-%m-%d_%H:%M:%S",
    level=logging.DEBUG)

logging.info("Logging started")

import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty


kivy.require('1.11.0')

Builder.load_file("gui-elements/widget.kv")
Builder.load_file("gui-elements/roundedbutton.kv")
Builder.load_file("gui-elements/abortbutton.kv")
Builder.load_file("gui-elements/useractionscreen.kv")
Builder.load_file("gui-elements/machineactionscreen.kv")
Builder.load_file("gui-elements/actiondonescreen.kv")
Builder.load_file('gui-elements/processwindow.kv')
Builder.load_file('gui-elements/progressdot.kv')
Builder.load_file('gui-elements/circlebutton.kv')
Builder.load_file('gui-elements/errorpopup.kv')
Builder.load_file('gui-elements/abortpopup.kv')



DEBUG_MODE = False

# logging.basicConfig(filename='cda.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging_level)

# TODO: make a "/protocols" folder to organize things more
# Change the value here and below to edit which protocol is in use
PROTOCOL_FILE_NAME = "v0-protocol-14v0.json"

# TODO: why are these here?
# PROTOCOL_FILE_NAME = "cda-protocol-v02.json"
# PROTOCOL_FILE_NAME = "cda-quick-run.json"
# PROTOCOL_FILE_NAME = "cda-custom.json"


if not DEBUG_MODE:
    # Make sure the 'real' protocol is used
    # Also change protocol name here when adjusting which protocol is in use
    PROTOCOL_FILE_NAME = "v0-protocol-14v0.json" # TODO: address double setting file name
else:
    logging.warning("CDA: *** DEBUG MODE ***")

logging.info(f"CDA: Using protocol: '{PROTOCOL_FILE_NAME}''")

ser = serial.Serial("/dev/ttyUSB0", 19200, timeout=2)
pumps = PumpNetwork(ser)
WASTE_ADDR = 1
LYSATE_ADDR = 2
WASTE_DIAMETER_mm = 12.55
LYSATE_DIAMETER_mm = 12.55

scheduled_events = []

def stop_all_pumps():
    logging.debug("CDA: Stopping all pumps.")
    for addr in [WASTE_ADDR, LYSATE_ADDR]:
        try:
            pumps.stop(addr)
        except IOError as err:
            if str(err)[-3:] == "?NA":
                logging.debug(f"CDA: Pump {addr:02} already stopped.")
            else:
                raise


def cleanup():
    logging.debug("CDA: Cleaning upp")
    global scheduled_events
    logging.debug("CDA: Unscheduling events")
    for se in scheduled_events:
        try:
            se.cancel()
        except AttributeError: pass
    scheduled_events = []
    stop_all_pumps()


def shutdown():
    logging.info("Shutting down...")
    cleanup()
    if DEBUG_MODE:
        logging.warning("CDA: In DEBUG mode, not shutting down for real, only ending program.")
        App.get_running_app().stop()
    else:
        os.system('sudo shutdown --poweroff now')


def reboot():
    cleanup()
    logging.info("CDA: Rebooting...")
    if DEBUG_MODE:
        logging.warning("CDA: In DEBUG mode, not rebooting down for real, only ending program.")
        App.get_running_app().stop()
    else:
        os.system('sudo reboot --poweroff now')
        # call("sudo reboot --poweroff now", shell=True)


logging.info("CDA: Starting main script.")

stop_all_pumps()

pumps.set_diameter(diameter_mm=WASTE_DIAMETER_mm, addr=WASTE_ADDR)
pumps.set_diameter(diameter_mm=LYSATE_DIAMETER_mm, addr=LYSATE_ADDR)

nano = Nano(8, 7)

progressbar_update_interval = .5
switch_update_interval = .1
grab_overrun_check_interval = 20


class ProcessScreenManager(ScreenManager):

    def __init__(self, *args, **kwargs):
        self.main_window = kwargs.pop("main_window")
        super().__init__(*args, **kwargs)

    def next_screen(self):
        logging.debug(f"CDA: Next screen, going from {self.current} to {self.next()}")
        self.current = self.next()

    def next_step(self):
        '''Propagate this command one level up.'''
        self.main_window.next_step()

    def show_fatal_error(self, *args, **kwargs):
        self.main_window.show_fatal_error(*args, **kwargs)

    def start_over(self, dt):
        # TODO: any cleanup to be done?
        self.main_window.start_over()


class ChipFlowScreen(Screen):

    def __init__(self, *args, **kwargs):
        self.header_text = kwargs.pop("header", "Header")
        self.description_text = kwargs.pop("description", "Description.")
        super().__init__(*args, **kwargs)

    def next_step(self, *args, **kwargs):
        self.parent.next_step()

    def show_fatal_error(self, *args, **kwargs):
        logging.debug("SCREEN: SFE")
        logging.debug(self)
        self.parent.show_fatal_error(*args, **kwargs)

    def start_over(self, dt):
        # TODO: any cleanup to be done?
        self.parent.start_over()


class UserActionScreen(ChipFlowScreen):

    def __init__(self, *args, **kwargs):
        self.next_text = kwargs.pop('next_text', 'Next')
        super().__init__(*args, **kwargs)


class MachineActionScreen(ChipFlowScreen):
    time_remaining_min = NumericProperty(0)
    time_remaining_sec = NumericProperty(0)
    progress = NumericProperty(0.0)

    def __init__(self, *args, **kwargs):
        self.action = kwargs.pop('action')
        self.time_total = 0
        self.time_elapsed = 0
        super().__init__(*args, **kwargs)

    def start(self):
        for action, params in self.action.items():
            if action == 'PUMP':
                if params['target'] == 'waste':
                    addr = WASTE_ADDR
                if params['target'] == 'lysate':
                    addr = LYSATE_ADDR
                rate_mh = params['rate_mh']
                vol_ml = params['vol_ml']
                eq_time = params.get('eq_time', 0)
                self.time_total = abs(vol_ml / rate_mh) * 3600 + eq_time
                self.time_elapsed = 0
                pumps.set_rate(rate_mh, 'MH', addr)
                pumps.set_volume(vol_ml, 'ML',  addr)
                pumps.run(addr)
                scheduled_events.append(Clock.schedule_interval(self.set_progress, progressbar_update_interval))

            if action == 'INCUBATE':
                self.time_total = params['time']
                self.time_elapsed = 0
                scheduled_events.append(Clock.schedule_interval(
                    self.set_progress, progressbar_update_interval
                ))

            if action == 'RESET':
                # TODO: set progress bar to be invisible
                # Go down for a little while, in case forks are already in position
                for addr in [WASTE_ADDR, LYSATE_ADDR]:
                    pumps.purge(1, addr)
                time.sleep(1)
                for addr in [WASTE_ADDR, LYSATE_ADDR]:
                    pumps.stop(addr)
                    pumps.purge(-1, addr)
                self.reset_stop_counter = 0
                scheduled_events.append(Clock.schedule_interval(
                    partial(self.switched_reset, 'd2',
                            WASTE_ADDR, 2, self.next_step),
                    switch_update_interval
                ))
                
                scheduled_events.append(Clock.schedule_interval(
                    partial(self.switched_reset, 'd3',
                            LYSATE_ADDR, 2, self.next_step),
                    switch_update_interval
                ))

            if action == 'GRAB':
                post_run_rate_mm = params["post_run_rate_mm"]
                post_run_vol_ml = params["post_run_vol_ml"]
                for addr in [WASTE_ADDR, LYSATE_ADDR]:
                    logging.debug(f"CDA: Grabbing pump {addr}")
                    pumps.purge(1, addr)
                self.grab_stop_counter = 0
                swg1 = Clock.schedule_interval(
                    partial(self.switched_grab, 'd4',
                            WASTE_ADDR, 2, self.next_step,
                            post_run_rate_mm, post_run_vol_ml),
                    switch_update_interval)
                scheduled_events.append(swg1)
                swg2 = Clock.schedule_interval(
                    partial(self.switched_grab, 'd5',
                            LYSATE_ADDR, 2, self.next_step,
                            post_run_rate_mm, post_run_vol_ml),
                    switch_update_interval)
                scheduled_events.append(swg2)
                self.grab_overrun_check_schedule = Clock.schedule_once(
                    partial(self.grab_overrun_check, [swg1, swg2]),
                    grab_overrun_check_interval
                )
                scheduled_events.append(self.grab_overrun_check_schedule)
                

    def switched_reset(self, switch, addr, max_count, final_action, dt):
        nano.update()
        if not getattr(nano, switch):
            logging.info(f"CDA: Switch {switch} actived, stopping pump {addr}")
            pumps.stop(addr)
            self.reset_stop_counter += 1
            if self.reset_stop_counter == max_count:
                logging.debug(f"CDA: Both pumps homed")
                final_action()
            return False

    def switched_grab(self, switch, addr, max_count, final_action, post_run_rate_mm, post_run_vol_ml, dt):
        nano.update()
        if not getattr(nano, switch):
            logging.info(f"CDA: Pump {addr} has grabbed syringe (switch {switch}).")
            logging.debug(f"CDA: Running extra {post_run_vol_ml} ml @ {post_run_rate_mm} ml/min to grasp firmly.")
            pumps.stop(addr)
            pumps.set_rate(post_run_rate_mm, 'MM', addr)
            pumps.set_volume(post_run_vol_ml, 'ML',  addr)
            pumps.run(addr)
            self.grab_stop_counter += 1
            if self.grab_stop_counter == max_count:
                logging.debug(f"CDA: Both syringes grabbed")
                self.grab_overrun_check_schedule.cancel()
                final_action()
            return False

    def grab_overrun_check(self, swgs, dt):
        nano.update()
        overruns = []
        if getattr(nano, 'd4'):
            overruns.append("1 (waste)")
            swgs[0].cancel()
        if getattr(nano, 'd5'):
            overruns.append("2 (lysate)")
            swgs[1].cancel()
        if len(overruns) > 0:
            stop_all_pumps()
            overruns_str = " and ".join(overruns)
            plural = "s" if len(overruns) > 1 else ""
            logging.warning(f"CDA: Grab overrun in position{plural} {overruns_str}.")
            self.show_fatal_error(
                title = f"Syringe{plural} not detected",
                description = f"Syringe{plural} not inserted correctly in positions{plural} {overruns_str}.\nPlease start the test over.",
                confirm_text = "Start over",
                confirm_action = "abort",
                primary_color = (1, .33, .33, 1)
            )


    def set_progress(self, dt):
        self.time_elapsed += dt
        time_remaining = max(self.time_total - self.time_elapsed, 0)
        self.time_remaining_min = int(time_remaining / 60)
        self.time_remaining_sec = int(time_remaining % 60)
        self.progress = self.time_elapsed / self.time_total * 100
        if self.progress >= 100:
            self.progress = 100
            self.next_step()
            return False

    def on_enter(self):
        self.start()


class ActionDoneScreen(ChipFlowScreen):

    def on_enter(self):
        pumps.buzz(repetitions=3, addr=WASTE_ADDR)
        scheduled_events.append(Clock.schedule_once(self.next_step, 1))


class FinishedScreen(ChipFlowScreen):

    def on_enter(self):
        scheduled_events.append(Clock.schedule_once(self.start_over, 3))


class ProgressDot(Widget):
    status = StringProperty()
    
    def __init__(self, *args, **kwargs):
        index = kwargs.pop('index', None)
        self.status = 'future'
        super().__init__(*args, **kwargs)

    def set_status(self, status):
        if status in ['past', 'present', 'future']:
            self.status = status
        else:
            raise TypeError("Status should be either of: 'past', 'present', 'future'. Got: '{}'".format(status))
        


class SteppedProgressBar(GridLayout):

    def __init__(self, *args, **kwargs):
        noof_steps = kwargs.pop('steps')
        super().__init__(
            *args,
            cols = noof_steps,
            padding = kwargs.pop('padding', 5),
            **kwargs
        )
        
        self.steps = [ProgressDot() for i in range(noof_steps)]
        for s in self.steps:
            self.add_widget(s)
        self.position = 0
        self._update()

    def set_position(self, pos):
        self.position = pos
        self._update()

    def _update(self):
        # Check limits
        if self.position < 0:
            self.position = 0
        elif self.position > len(self.steps)-1:
            self.position = len(self.steps)-1
        # Set all steps to correct status
        for n, s in enumerate(self.steps):
            if self.position > n:
                s.set_status('past')
            elif self.position == n:
                s.set_status('present')
            elif self.position < n:
                s.set_status('future')


class ErrorPopup(Popup):
    description_text = StringProperty()
    confirm_text = StringProperty()
    confirm_action = ObjectProperty()
    primary_color = ObjectProperty((1, .33, .33, 1))

    def __init__(self, *args, **kwargs):
        self.description_text = kwargs.pop("description", "An error occurred")
        self.confirm_text = kwargs.pop("confirm_text", "An error occurred")
        self.confirm_action = kwargs.pop("confirm_action", lambda: print(2))
        self.primary_color = kwargs.pop("primary_color", (.33, .66, 1, 1))
        super().__init__(*args, **kwargs)

    def confirm(self):
        logging.debug("CDA: Error acknowledged by user")
        self.disabled = True
        self.confirm_action()
        self.dismiss()



class AbortPopup(Popup):
    description_text = StringProperty()
    dismiss_text = StringProperty()
    confirm_text = StringProperty()
    confirm_action = ObjectProperty()
    primary_color = ObjectProperty((1, .33, .33, 1))

    def __init__(self, *args, **kwargs):
        self.description_text = kwargs.pop("description")
        self.dismiss_text = kwargs.pop("dismiss_text")
        self.confirm_text = kwargs.pop("confirm_text")
        self.confirm_action = kwargs.pop("confirm_action")
        self.primary_color = kwargs.pop("primary_color", (.33, .66, 1, 1))
        super().__init__(*args, **kwargs)

    def confirm(self):
        logging.debug("CDA: Error acknowledged by user")
        self.disabled = True
        self.confirm_action()
        self.dismiss()


class CircleButton(Widget):
    pass


class RoundedButton(Widget):
    pass


class AbortButton(Button):
    pass


class ProcessWindow(BoxLayout):

    def __init__(self, *args, **kwargs):
        protocol_file_name = kwargs.pop("protocol_file_name")
        super().__init__(*args, **kwargs)

        self.process_sm = ProcessScreenManager(main_window=self)
        self.progress_screen_names = []

        # Load protocol and add screens accordingly
        with open("/home/pi/cd-alpha/" + protocol_file_name, 'r') as f:
            protocol = json.loads(f.read(), object_pairs_hook=OrderedDict)

        for name, step in protocol.items():
            screen_type = step.get("type", None)
            if screen_type == "UserActionScreen":
                this_screen = UserActionScreen(
                    name=name,
                    header=step.get('header', 'NO HEADER'),
                    description=step.get('description', 'NO DESCRIPTION'),
                    next_text=step.get('next_text', 'Next')
                )
            elif screen_type == "MachineActionScreen":
                this_screen = MachineActionScreen(
                    name=name,
                    header=step["header"],
                    description=step.get("description", ""),
                    action=step["action"]
                )
                if step.get("remove_progress_bar", False):
                    this_screen.children[0].remove_widget(this_screen.ids.progress_bar_layout)
            else:
                if screen_type is None:
                    raise TypeError(
                        "Corrupt protocol. Every protocol step must contain a 'type' key.")
                else:
                    raise TypeError(
                        "Corrupt protocol. Unrecognized 'type' key: {}".format(screen_type))
            self.progress_screen_names.append(this_screen.name)
            self.process_sm.add_widget(this_screen)
            
            completion_msg = step.get("completion_msg", None)
            if completion_msg:
                self.process_sm.add_widget(
                    ActionDoneScreen(
                        name = this_screen.name + "_done",
                        header = completion_msg
                    )
                )


        self.overall_progress_bar = SteppedProgressBar(steps = len(self.progress_screen_names))#, size_hint_y = 0.15)

        self.abort_btn = AbortButton(
            disabled=False,
            size_hint_x=None,
            on_release=self.show_abort_popup
        )
        self.ids.top_bar.add_widget(self.overall_progress_bar)
        self.ids.top_bar.add_widget(self.abort_btn)
        self.ids.main.add_widget(self.process_sm)

    def show_abort_popup(self, btn):
        popup_outside_padding = 60
        if self.process_sm.current == "home":
            abort_poup = AbortPopup(
                title= "Shut down device?",
                description = "Do you want to shut the device down? Once it has been shut down, you may safely turn it off with the switch located on the back side of the device.",
                dismiss_text= "Cancel",
                confirm_text = "Shut down",
                confirm_action = self.shutdown,
                primary_color = (.33, .66, 1, 1),
                size_hint=(None,None),
                size=(800-popup_outside_padding,480-popup_outside_padding)
            )
        else:
            abort_poup = AbortPopup(
                title= "Abort entire test?",
                description = "Do you want to abort the test? You will need to discard all single-use equipment (chip and syringes).",
                dismiss_text= "Continue test",
                confirm_text = "Abort test",
                confirm_action = self.abort,
                primary_color = (1, .33, .33, 1),
                size_hint=(None,None),
                size=(800-popup_outside_padding,480-popup_outside_padding)
            )
        abort_poup.open()

    def abort(self):
        self.cleanup()
        self.process_sm.current = self.progress_screen_names[0]
        self.overall_progress_bar.set_position(0)

    def shutdown(self):
        self.cleanup()
        shutdown()

    def reboot(self):
        self.cleanup()
        reboot()

    def show_fatal_error(self, *args, **kwargs):
        logging.debug("CDA: Showing fatal error popup")
        popup_outside_padding = 60
        confirm_action = kwargs.pop("confirm_action", self.reboot)
        if confirm_action == 'shutdown':
            confirm_action = self.shutdown
        if confirm_action == 'reboot':
            confirm_action = self.reboot
        if confirm_action == 'abort':
            confirm_action = self.abort
        error_window = ErrorPopup(
            title = kwargs.pop("header", "Fatal Error"),
            description = kwargs.pop("description", "A fatal error occurred. Discard all used kit equipment and restart the test."),
            confirm_text = kwargs.pop("confirm_text", "Reboot now"),
            confirm_action = confirm_action,
            size_hint = (None,None),
            size=(800-popup_outside_padding,480-popup_outside_padding),
            primary_color = kwargs.pop("primary_color", (.33, .66, 1, 1))
        )
        error_window.open()
        pumps.buzz(addr=WASTE_ADDR, repetitions=5)

    def next_step(self):
        self.process_sm.next_screen()
        if self.process_sm.current in self.progress_screen_names:
            pos = self.progress_screen_names.index(self.process_sm.current)
            self.overall_progress_bar.set_position(pos)

    def cleanup(self):
        # Global cleanup
        cleanup()
        #TODO: Any local cleanup?


class ChipFlowApp(App):
    def build(self):
        logging.debug("CDA: Creating main window")
        return ProcessWindow(protocol_file_name=PROTOCOL_FILE_NAME)

    def on_close(self):
        cleanup()
        if not DEBUG_MODE:
            reboot()
        else:
            logging.warning("DEBUG MODE: Not rebooting, just closing...")


if __name__ == '__main__':
    try:
        ChipFlowApp().run()
    except:
        stop_all_pumps()
        ser.close()
        if not DEBUG_MODE:
            reboot()
        else:
            logging.warning("DEBUG MODE: Not rebooting, just re-raising error...")
            raise
