# !/usr/bin/python3py

# To execute remotely use:
# DISPLAY=:0.0 python3 ChipFlowApp.py

import contextlib
from collections import OrderedDict
import json
from pathlib import Path
import os
import serial
from datetime import datetime
from cd_alpha.Device import Device, get_updates
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.core.window import Window
from kivy.logger import Logger
from pkg_resources import resource_filename
from pathlib import Path
from cd_alpha.KivyScreenFactory import KivyScreenFactory, HomeScreen, ProtocolChooser, SummaryScreen, UserActionScreen, MachineActionScreen, ActionDoneScreen, ChipFlowScreen
from cd_alpha.Protocol import Protocol
from cd_alpha.ProtocolFactory import JSONProtocolEncoder, JSONProtocolParser
from cd_alpha.Step import Step
from cd_alpha.ChipController import ChipController
from cd_alpha.software_testing.SerialStub import SerialStub
from kivy.utils import platform
from cd_alpha.protocols.protocol_tools import ProcessProtocol
kivy.require("2.0.0")

Builder.load_file(resource_filename("cd_alpha", "gui-elements/widget.kv"))
Builder.load_file(
    resource_filename("cd_alpha", "gui-elements/roundedbutton.kv")
)
Builder.load_file(resource_filename("cd_alpha", "gui-elements/abortbutton.kv"))
Builder.load_file(
    resource_filename("cd_alpha", "gui-elements/useractionscreen.kv")
)
Builder.load_file(
    resource_filename("cd_alpha", "gui-elements/machineactionscreen.kv")
)
Builder.load_file(
    resource_filename("cd_alpha", "gui-elements/actiondonescreen.kv")
)
Builder.load_file(
    resource_filename("cd_alpha", "gui-elements/processwindow.kv")
)
Builder.load_file(resource_filename("cd_alpha", "gui-elements/progressdot.kv"))
Builder.load_file(resource_filename("cd_alpha", "gui-elements/circlebutton.kv"))
Builder.load_file(resource_filename("cd_alpha", "gui-elements/errorpopup.kv"))
Builder.load_file(resource_filename("cd_alpha", "gui-elements/abortpopup.kv"))
Builder.load_file(resource_filename("cd_alpha", "gui-elements/homescreen.kv"))
Builder.load_file(
    resource_filename("cd_alpha", "gui-elements/summaryscreen.kv")
)
Builder.load_file(
    resource_filename("cd_alpha", "gui-elements/protocolchooser.kv")
)


class ProcessScreenManager(ScreenManager):
    def __init__(self, *args, **kwargs):
        self.main_window = kwargs.pop("main_window")
        super().__init__(*args, **kwargs)

    def next_screen(self):
        current = self.current
        next_screen = self.next()

        # Don't go to protocol_chooser as a next step, go home instead
        if self.next() == "protocol_chooser":
            next_screen = "home"
        Logger.debug(f"CDA: Next screen, going from {current} to {next_screen}")
        self.current = next_screen

    def next_step(self):
        """Propagate this command one level up."""
        self.main_window.next_step()

    def show_fatal_error(self, *args, **kwargs):
        self.main_window.show_fatal_error(*args, **kwargs)

    def start_over(self, dt):
        # TODO: any cleanup to be done?
        self.main_window.start_over()


class ProgressDot(Widget):
    status = StringProperty()

    def __init__(self, *args, **kwargs):
        self.status = "future"
        super().__init__(*args, **kwargs)

    def set_status(self, status):
        if status in ["past", "present", "future"]:
            self.status = status
        else:
            raise TypeError(f"Status should be either of: 'past', 'present', 'future'. Got: '{status}'")


class SteppedProgressBar(GridLayout):
    def __init__(self, *args, **kwargs):
        noof_steps = kwargs.pop("steps")
        super().__init__(
            *args, cols=noof_steps, padding=kwargs.pop("padding", 5), **kwargs
        )

        self.steps = [ProgressDot() for _ in range(noof_steps)]
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
        elif self.position > len(self.steps) - 1:
            self.position = len(self.steps) - 1
        # Set all steps to correct status
        for n, s in enumerate(self.steps):
            if self.position > n:
                s.set_status("past")
            elif self.position == n:
                s.set_status("present")
            elif self.position < n:
                s.set_status("future")


class ErrorPopup(Popup):
    description_text = StringProperty()
    confirm_text = StringProperty()
    confirm_action = ObjectProperty()
    primary_color = ObjectProperty((1, 0.33, 0.33, 1))

    def __init__(self, *args, **kwargs):
        self.description_text = kwargs.pop("description", "An error occurred")
        self.confirm_text = kwargs.pop("confirm_text", "An error occurred")
        self.confirm_action = kwargs.pop("confirm_action", lambda: print(2))
        self.primary_color = kwargs.pop("primary_color", (0.33, 0.66, 1, 1))
        super().__init__(*args, **kwargs)

    def confirm(self):
        Logger.debug("CDA: Error acknowledged by user")
        self.disabled = True
        self.confirm_action()
        self.dismiss()


class AbortPopup(Popup):
    description_text = StringProperty()
    dismiss_text = StringProperty()
    confirm_text = StringProperty()
    confirm_action = ObjectProperty()
    primary_color = ObjectProperty((1, 0.33, 0.33, 1))

    def __init__(self, *args, **kwargs):
        self.description_text = kwargs.pop("description")
        self.dismiss_text = kwargs.pop("dismiss_text")
        self.confirm_text = kwargs.pop("confirm_text")
        self.confirm_action = kwargs.pop("confirm_action")
        self.primary_color = kwargs.pop("primary_color", (0.33, 0.66, 1, 1))
        super().__init__(*args, **kwargs)

    def confirm(self):
        Logger.debug("CDA: Error acknowledged by user")
        self.disabled = True
        self.confirm_action()
        self.dismiss()


class CircleButton(Widget):
    pass


class RoundedButton(Widget):
    pass


class AbortButton(Button):
    pass


class LoadButton(Button):
    pass


class RefreshButton(Button):
    pass


class ProcessWindow(BoxLayout):
    pass


class ProcessWindow(BoxLayout):
    def __init__(self, *args, **kwargs):
        self.protocol_file_name = kwargs.pop("protocol_file_name")
        super().__init__(*args, **kwargs)

        self.process_sm = ProcessScreenManager(main_window=self)
        self.progress_screen_names = []

        self.app = App.get_running_app()

        # TODO: break protocol loading into its own method
        protocol_location = self.app.PATH_TO_PROTOCOLS + self.protocol_file_name
        with open(protocol_location, "r") as f:
            protocol = json.loads(f.read(), object_pairs_hook=OrderedDict)

        protocol_obj = JSONProtocolParser(Path(protocol_location)).make_protocol()

        gui_screens = JSONProtocolParser(Path(protocol_location)).json_to_gui_model()
        logging.info(protocol_obj)
        logging.info(gui_screens)

        list_of_kivy_screens = KivyScreenFactory(gui_screens).make_kivy_screens()

        if self.app.START_STEP not in protocol.keys():
            raise KeyError(f"{self.app.START_STEP} not a valid step in the protocol.")

        # if we're supposed to start at a step other than 'home' remove other steps from the protocol
        protocol_copy = OrderedDict()
        keep_steps = False
        for name, step in protocol.items():
            if name == self.app.START_STEP:
                keep_steps = True
            if keep_steps:
                protocol_copy[name] = step

        protocol = protocol_copy

        for builder in gui_screens:
            pass

        for name, step in protocol.items():
            screen_type = step.get("type", None)
            if screen_type == "UserActionScreen":
                if name == "home":
                    this_screen = HomeScreen(
                        name,
                        header=step.get("header", "NO HEADER"),
                        description=step.get("description", "NO DESCRIPTION"),
                        next_text=step.get("next_text", "Next"),
                    )

                elif name == "summary":
                    this_screen = SummaryScreen(next_text=step.get("next_text", "Next"))
                else:
                    this_screen = UserActionScreen(
                        name=name,
                        header=step.get("header", "NO HEADER"),
                        description=step.get("description", "NO DESCRIPTION"),
                        next_text=step.get("next_text", "Next"),
                    )
            elif screen_type == "MachineActionScreen":

                this_screen = MachineActionScreen(
                    Step(None, None),
                    name=name,
                    header=step["header"],
                    description=step.get("description", ""),
                )

                # TODO: clean up how this works
                if step.get("remove_progress_bar", False):
                    this_screen.children[0].remove_widget(
                        this_screen.ids.progress_bar_layout
                    )
                    this_screen.children[0].remove_widget(
                        this_screen.ids.skip_button_layout
                    )

                # Don't offer skip button in production
                if not self.app.DEBUG_MODE:
                    this_screen.children[0].remove_widget(
                        this_screen.ids.skip_button_layout
                    )
            else:
                if screen_type is None:
                    raise TypeError(
                        "Corrupt protocol. Every protocol step must contain a 'type' key."
                    )
                else:
                    raise TypeError(
                        "Corrupt protocol. Unrecognized 'type' key: {}".format(
                            screen_type
                        )
                    )
            self.progress_screen_names.append(this_screen.name)
            self.process_sm.add_widget(this_screen)

            completion_msg = step.get("completion_msg", None)
            if completion_msg:
                self.process_sm.add_widget(
                    ActionDoneScreen(
                        name=this_screen.name + "_done", header=completion_msg
                    )
                )

        self.load_protocol(file_path)
        self.overall_progress_bar = SteppedProgressBar(
            steps=len(self.progress_screen_names)
        )

        self.abort_btn = AbortButton(
            disabled=False, size_hint_x=None, on_release=self.show_abort_popup
        )

        self.refresh_btn = RefreshButton(disabled=False, on_release=self.get_updates)

        protocol_chooser = ProtocolChooser(name="protocol_chooser")
        self.process_sm.add_widget(protocol_chooser)
        self.ids.top_bar.add_widget(self.overall_progress_bar)
        self.ids.top_bar.add_widget(self.abort_btn)
        self.ids.main.add_widget(self.process_sm)
        logging.info(f"Widgets in process screen manager: {self.process_sm.screen_names}")

    def show_abort_popup(self, btn):
        popup_outside_padding = 60
        if self.process_sm.current == "home":
            abort_poup = AbortPopup(
                title="Shut down device?",
                description=(
                    "Do you want to shut the device down? Once it has been"
                    "shut down, you may safely turn it off with the switch located on"
                    " the back side of the device."
                ),
                dismiss_text="Cancel",
                confirm_text="Shut down",
                confirm_action=self.shutdown,
                primary_color=(0.33, 0.66, 1, 1),
                size_hint=(None, None),
                size=(800 - popup_outside_padding, 480 - popup_outside_padding),
            )
        elif self.process_sm.current == "protocol_chooser":
            abort_poup = AbortPopup(
                title="Exit device?",
                description=(
                    "Do you want to exit the device? This should be used for development only."
                ),
                dismiss_text="Cancel",
                confirm_text="Exit",
                confirm_action=self.exit,
                primary_color=(1, 0.66, 0, 1),
                size_hint=(None, None),
                size=(800 - popup_outside_padding, 480 - popup_outside_padding),
            )

        else:
            abort_poup = AbortPopup(
                title="Abort entire test?",
                description="Do you want to abort the test? You will need to discard all single-use equipment (chip and syringes).",
                dismiss_text="Continue test",
                confirm_text="Abort test",
                confirm_action=self.abort,
                primary_color=(1, 0.33, 0.33, 1),
                size_hint=(None, None),
                size=(800 - popup_outside_padding, 480 - popup_outside_padding),
            )
        abort_poup.open()

    def abort(self):
        self.cleanup()
        self.process_sm.current = self.progress_screen_names[0]
        self.overall_progress_bar.set_position(0)

    def shutdown(self):
        self.cleanup()
        self.app.shutdown()

    def reboot(self):
        self.cleanup()
        self.app.reboot()

    def exit(self):
        self.cleanup()
        App.get_running_app().stop()

    def show_fatal_error(self, *args, **kwargs):
        Logger.debug("CDA: Showing fatal error popup")
        popup_outside_padding = 60
        confirm_action = kwargs.pop("confirm_action", self.reboot)
        if confirm_action == "shutdown":
            confirm_action = self.shutdown
        if confirm_action == "reboot":
            confirm_action = self.reboot
        if confirm_action == "abort":
            confirm_action = self.abort
        error_window = ErrorPopup(
            title=kwargs.pop("header", "Fatal Error"),
            description=kwargs.pop(
                "description",
                "A fatal error occurred. Discard all used kit equipment and restart the test.",
            ),
            confirm_text=kwargs.pop("confirm_text", "Reboot now"),
            confirm_action=confirm_action,
            size_hint=(None, None),
            size=(800 - popup_outside_padding, 480 - popup_outside_padding),
            primary_color=kwargs.pop("primary_color", (0.33, 0.66, 1, 1)),
        )
        error_window.open()
        self.app.pumps.buzz(addr=self.app.WASTE_ADDR, repetitions=5)

    def start_over(self):
        Logger.info("Sending Program to home screen")
        self.process_sm.current = "home"

    def next_step(self):
        self.process_sm.next_screen()
        # check if this screen has an action
        if type(self.process_sm.current_screen) == MachineActionScreen:
            logging.info("Found Machine Action Screen")
            self.app.controller.next()
        if self.process_sm.current in self.progress_screen_names:
            pos = self.progress_screen_names.index(self.process_sm.current)
            self.overall_progress_bar.set_position(pos)

    def cleanup(self):
        # Global cleanup
        pass
        # TODO: Any local cleanup?

    # TODO for testability instead of mutating the current App, we could return a Protocol object
    def load_protocol(self, path_to_protocol) -> ProcessScreenManager:
        
        load_protocol_screenmanager = ProcessScreenManager(main_window=self)

        with open(path_to_protocol, "r") as f:
            protocol = json.loads(f.read(), object_pairs_hook=OrderedDict)

        self.progress_screen_names = []

        # TODO: break protocol loading into its own method
        with open(path_to_protocol, "r") as f:
            protocol = json.loads(f.read(), object_pairs_hook=OrderedDict)

        if self.app.START_STEP not in protocol.keys():
            raise KeyError(f"{self.app.START_STEP} not a valid step in the protocol.")

        # if we're supposed to start at a step other than 'home' remove other steps from the protocol
        protocol_copy = OrderedDict()
        keep_steps = False
        for name, step in protocol.items():
            if name == self.app.START_STEP:
                keep_steps = True
            if keep_steps:
                protocol_copy[name] = step

        protocol = protocol_copy

        for name, step in protocol.items():
            screen_type = step.get("type", None)
            if screen_type == "UserActionScreen":
                if name == "home":
                    this_screen = HomeScreen(
                        name,
                        header=step.get("header", "NO HEADER"),
                        description=step.get("description", "NO DESCRIPTION"),
                        next_text=step.get("next_text", "Next"),
                    )

                elif name == "summary":
                    this_screen = SummaryScreen(next_text=step.get("next_text", "Next"))
                else:
                    this_screen = UserActionScreen(
                        name=name,
                        header=step.get("header", "NO HEADER"),
                        description=step.get("description", "NO DESCRIPTION"),
                        next_text=step.get("next_text", "Next"),
                    )
            elif screen_type == "MachineActionScreen":

                this_screen = MachineActionScreen(
                    name=name,
                    header=step["header"],
                    description=step.get("description", ""),
                    action=step["action"],
                )
                # TODO: clean up how this works
                if step.get("remove_progress_bar", False):
                    this_screen.children[0].remove_widget(
                        this_screen.ids.progress_bar_layout
                    )
                    this_screen.children[0].remove_widget(
                        this_screen.ids.skip_button_layout
                    )

                # Don't offer skip button in production
                if not self.app.DEBUG_MODE:
                    this_screen.children[0].remove_widget(
                        this_screen.ids.skip_button_layout
                    )
            else:
                if screen_type is None:
                    raise TypeError(
                        "Corrupt protocol. Every protocol step must contain a 'type' key."
                    )
                else:
                    raise TypeError(
                        "Corrupt protocol. Unrecognized 'type' key: {}".format(
                            screen_type
                        )
                    )
            self.progress_screen_names.append(this_screen.name)
            self.process_sm.add_widget(this_screen)

            completion_msg = step.get("completion_msg", None)
            if completion_msg:
                self.process_sm.add_widget(
                    ActionDoneScreen(
                        name=this_screen.name + "_done", header=completion_msg
                    )
                )

        self.overall_progress_bar = SteppedProgressBar(
            steps=len(self.progress_screen_names)
        )

        self.abort_btn = AbortButton(
            disabled=False, size_hint_x=None, on_release=self.show_abort_popup
        )
        protocol_chooser = ProtocolChooser(name="protocol_chooser")
        self.process_sm.add_widget(protocol_chooser)
        self.ids.top_bar.add_widget(self.overall_progress_bar)
        self.ids.top_bar.add_widget(self.abort_btn)
        self.ids.main.add_widget(self.process_sm)
        logging.info(f"Widgets in process screen manager: {self.process_sm.screen_names}")

        return load_protocol_screenmanager

    def screenduplicates(self, screen_names):
        list_of_screen_names = {}
        for name in screen_names:
            if name not in list_of_screen_names:
                list_of_screen_names[name] = 1
            else:
                list_of_screen_names[name] += 1
        return list_of_screen_names


class ChipFlowApp(App):
    def __init__(self, **kwargs):
        kivy.require("2.0.0")
        self.device = Device(resource_filename("cd_alpha", "device_config.json"))
        # Change the value in the config file to change which protocol is in use
        self.PROTOCOL_FILE_NAME = self.device.DEFAULT_PROTOCOL
        self.PATH_TO_PROTOCOLS = resource_filename("cd_alpha", "protocols/")
        self.DEBUG_MODE = self.device.DEBUG_MODE
        self.SERIAL_PATH = self.device.PUMP_SERIAL_ADDR
        self.DEV_MACHINE = self.device.DEV_MACHINE
        self.START_STEP = self.device.START_STEP
        self.POST_RUN_RATE_MM_CALIBRATION = self.device.POST_RUN_RATE_MM
        self.POST_RUN_VOL_ML_CALIBRATION = self.device.POST_RUN_VOL_ML
        self.controller = None
        

        # Branch below allows for the GUI App to be tested locally on a Windows machine without needing to connect the syringe pump or arduino

        # TODO fix these logic blocks using kivy built in OS testing
        # TODO fix file path issues using resource_filename() as seen above
        if self.DEV_MACHINE:
            LOCAL_TESTING = True
            time_now_str = (
                datetime.now().strftime("%Y-%m-%d_%H:%M:%S").replace(":", ";")
            )
            logging.basicConfig(
                filename=f"/home/pi/cd_alpha/logs/cda_{time_now_str}.log",
                filemode="w",
                datefmt="%Y-%m-%d_%H:%M:%S",
                level=logging.DEBUG,
            )
            logging.info("Logging started")
            from cd_alpha.software_testing.NanoControllerTestStub import Nano
            from cd_alpha.software_testing.NewEraPumpsTestStub import PumpNetwork
            from cd_alpha.software_testing.SerialStub import SerialStub

            SPLIT_CHAR = "\\"
        else:
            # Normal production mode
            from NanoController import Nano
            # For R0 debug
            Window.fullscreen = "auto"
            LOCAL_TESTING = False
            time_now_str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            logging.basicConfig(
                filename=f"/home/pi/cd-alpha/logs/cda_{time_now_str}.log",
                filemode="w",
                datefmt="%Y-%m-%d_%H:%M:%S",
                level=logging.DEBUG,
            )
            logging.info("Logging started")
            SPLIT_CHAR = "/"

        if self.DEBUG_MODE:
            logging.warning("CDA: *** DEBUG MODE ***")
            logging.warning("CDA: System will not reboot after exiting program.")

        logging.info(f"CDA: Using protocol: '{self.PROTOCOL_FILE_NAME}''")

        # Set constants
        if self.device.DEVICE_TYPE == "R0":
            self.WASTE_ADDR = self.device.PUMP_ADDR[0]
            self.WASTE_DIAMETER_mm = self.device.PUMP_DIAMETER[0]
        else:
            self.WASTE_ADDR = self.device.PUMP_ADDR[0]
            self.LYSATE_ADDR = self.device.PUMP_ADDR[1]
            self.WASTE_DIAMETER_mm = self.device.PUMP_DIAMETER[0]
            self.LYSATE_DIAMETER_mm = self.device.PUMP_DIAMETER[1]

        self.scheduled_events = []
        self.list_of_pumps = self.device.PUMP_ADDR

        # ---------------- MAIN ---------------- #

        logging.info("CDA: Starting main script.")

        self.nano = Nano(8, 7) if self.device.DEVICE_TYPE == "V0" else None

        # TODO why are magic numbers being defined mid initialization?
        self.progressbar_update_interval = 0.5
        self.switch_update_interval = 0.1
        self.grab_overrun_check_interval = 20

        super().__init__(**kwargs)

    def build(self):
        logging.debug("CDA: Creating main window")
        self.process = ProcessWindow(protocol_file_name=self.PROTOCOL_FILE_NAME)
        return self.process

    def on_close(self):
        self.cleanup()
        if not self.DEBUG_MODE:
            self.reboot()
        else:
            Logger.warning("DEBUG MODE: Not rebooting, just closing...")

    def shutdown(self):
        logging.info("Shutting down...")
        self.cleanup()
        if self.DEBUG_MODE:
            logging.warning(
                "CDA: In DEBUG mode, not shutting down for real, only ending program."
            )
            App.get_running_app().stop()
        else:
            os.system("sudo shutdown --poweroff now")

    def reboot(self):
        self.cleanup()
        logging.info("CDA: Rebooting...")
        if self.DEBUG_MODE:
            logging.warning(
                "CDA: In DEBUG mode, not rebooting down for real, only ending program."
            )
            App.get_running_app().stop()
        else:
            os.system("sudo reboot --poweroff now")


def main():
    try:
        chip_app = ChipFlowApp()
        # Establish serial connection to the pump controllers if on linux
        pumps = None
        if platform == 'linux':
            from cd_alpha.NewEraPumps import PumpNetwork
            ser = serial.Serial("/dev/ttyUSB0", 19200, timeout=2)
            pumps = PumpNetwork(ser)
        else:
            from cd_alpha.software_testing.NewEraPumpsTestStub import PumpNetwork
            ser = SerialStub()
            pumps = PumpNetwork(ser)
        default_protocol = JSONProtocolParser(Path(chip_app.PATH_TO_PROTOCOLS + chip_app.PROTOCOL_FILE_NAME)).make_protocol(chip_app.PROTOCOL_FILE_NAME)
        chip_controller = ChipController(protocol=default_protocol, app=chip_app, pumps=pumps, ser=ser)
        chip_app.controller = chip_controller
        chip_controller.run()
    except Exception:
        chip_controller.cleanup()
        if not chip_controller.is_debug():
            chip_controller.reboot()
        else:
            Logger.warning("DEBUG MODE: Not rebooting, just re-raising error...")
            raise


if __name__ == "__main__":
    main()


