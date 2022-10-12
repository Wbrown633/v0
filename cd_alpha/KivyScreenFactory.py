from dataclasses import dataclass
from cd_alpha.ProtocolFactory import JSONScreenBuilder
from kivy.uix.screenmanager import ScreenManager, Screen
import logging 
from kivy.clock import Clock
from kivy.app import App
from kivy.properties import NumericProperty
from cd_alpha.Step import Step
from cd_alpha.protocols.protocol_tools import ProcessProtocol
from cd_alpha.Protocol import Protocol
from kivy.uix.label import Label
import time

class ChipFlowScreen(Screen):
    def __init__(self, *args, **kwargs):
        self.header_text = kwargs.pop("header", "Header")
        self.description_text = kwargs.pop("description", "Description.")
        super().__init__(**kwargs)

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
        self.next_text = kwargs.pop("next_text", "Next")
        super().__init__(*args, **kwargs)


class HomeScreen(ChipFlowScreen):
    def __init__(self, *args, **kwargs):
        self.next_text = kwargs.pop("next_text", "Next")
        super().__init__(*args, **kwargs)

    def load_protocol(self, *args, **kwargs):
        logging.info("Load button pressed!")
        self.manager.current = "protocol_chooser"

class FinishedScreen(ChipFlowScreen):
    def __init__(self, *args, **kwargs):
        self.app = App.get_running_app()
        super().__init__(*args, **kwargs)
    def on_enter(self):
        self.app.scheduled_events.append(Clock.schedule_once(self.start_over, 3))



class ProtocolChooser(Screen):

    def __init__(self, **kw):
        self.app = App.get_running_app()
        super().__init__(**kw)

    def load(self, path, filename):
        try:
            filename = filename[0]
            logging.info(f"Filename List: {filename}")
        except Exception:
            return
        logging.info(f"Filename: {filename}  was chosen. Path: {path}")
        try:
            self.manager.main_window.load_protocol(filename)
        except BaseException as err:
            logging.error(f"Invalid Protocol: {filename}")
            logging.error(f"Unexpected Error: {err}, {type(err)}")

    def get_file_path(self):
        return self.app.PATH_TO_PROTOCOLS

    def cancel(self):
        logging.info("Cancel")
        self.manager.current = "home"


class SummaryScreen(Screen):
    def __init__(self, *args, **kwargs):
        self.next_text = kwargs.pop("next_text", "Next")
        self.header_text = kwargs.pop("header_text", "Summary")
        self.app = App.get_running_app()
        self.protocol_process = ProcessProtocol(self.app.PATH_TO_PROTOCOLS + self.app.PROTOCOL_FILE_NAME)
        super().__init__(*args, **kwargs)
        self.add_rows()

    def add_rows(self):
        """Return content of rows as one formatted string, roughly table shape."""
        summary_layout = self.ids.summary_layout
        for line in self.protocol_process.list_steps():
            for entry in line:
                summary_layout.add_widget(Label(text=str(entry)))



class MachineActionScreen(ChipFlowScreen):
    time_remaining_min = NumericProperty(0)
    time_remaining_sec = NumericProperty(0)
    progress = NumericProperty(0.0)

    def __init__(self, *args, **kwargs):
        self.time_total = 0
        self.time_elapsed = 0
        self.app = App.get_running_app()
        super().__init__(*args, **kwargs)

    # TODO this code is re-written multiple times and tied directly to GUI logic, desperately needs re-factor
    # TODO writing a protocol parser may help both loading and running protocols
    def start(self):
        WASTE_ADDR = self.app.WASTE_ADDR
        LYSATE_ADDR = self.app.LYSATE_ADDR

        # TODO should this be done with a controller?
        # how do we keep all of these classes testable
        # prevent App from leaking into classes where possible
        self.app.chip_controller.next()


class ActionDoneScreen(ChipFlowScreen):
    def __init__(self, *args, **kwargs):
        self.app = App.get_running_app()
        super().__init__(*args, **kwargs)
    def on_enter(self):
        self.app.pumps.buzz(repetitions=3, addr=self.app.WASTE_ADDR)
        self.app.scheduled_events.append(Clock.schedule_once(self.next_step, 1))

@dataclass
class KivyScreenFactory:
    '''Given a list of JSONScreenbuilders, return a list of Kivy screens'''

    list_of_screenbuilders:list[JSONScreenBuilder]
    

    def make_kivy_screens(self) -> list[Screen]:
        list_of_screens = []
        for builder in self.list_of_screenbuilders:
            step = builder.stepdict
            name = builder.step_name
            screen_type = step.get("type", None)
            if screen_type == "UserActionScreen":
                if name == "home":
                    this_screen = HomeScreen(
                        name,
                        header=step.get("header", "NO HEADER"),
                        description=step.get("description", "NO DESCRIPTION"),
                        next_text=step.get("next_text", "Start"),
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
                if not App.get_running_app().DEBUG_MODE:
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
            list_of_screens.append(this_screen)

            completion_msg = step.get("completion_msg", None)
            if completion_msg:
                list_of_screens.append(
                    ActionDoneScreen(
                        name=this_screen.name + "_done", header=completion_msg
                    )
                )


        return list_of_screens