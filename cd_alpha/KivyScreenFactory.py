from dataclasses import dataclass
from cd_alpha.ProtocolFactory import JSONScreenBuilder
from kivy.uix.screenmanager import ScreenManager, Screen
import logging 
from kivy.clock import Clock
from kivy.app import App
from kivy.properties import NumericProperty
from cd_alpha.protocols.protocol_tools import ProcessProtocol
from kivy.uix.label import Label
from functools import partial
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
        for action, params in self.action.items():
            if action == "PUMP":
                if params["target"] == "waste":
                    addr = WASTE_ADDR
                if params["target"] == "lysate":
                    addr = LYSATE_ADDR
                rate_mh = params["rate_mh"]
                vol_ml = params["vol_ml"]
                eq_time = params.get("eq_time", 0)
                self.time_total = abs(vol_ml / rate_mh) * 3600 + eq_time
                self.time_elapsed = 0
                self._extracted_from_start_13("Addr = ", addr, rate_mh, vol_ml)
                self.app.scheduled_events.append(
                    Clock.schedule_interval(
                        self.set_progress, self.app.progressbar_update_interval
                    )
                )

            if action == "INCUBATE":
                self.time_total = params["time"]
                self.time_elapsed = 0
                self.app.scheduled_events.append(
                    Clock.schedule_interval(
                        self.set_progress, self.app.progressbar_update_interval
                    )
                )

            if action == "RESET":
                if self.app.device.DEVICE_TYPE == "R0":
                    logging.info(
                        "No RESET work to be done on the R0, passing to end of program"
                    )
                    return
                for addr in [self.app.WASTE_ADDR, self.app.LYSATE_ADDR]:
                    self.app.pumps.purge(1, addr)
                time.sleep(1)
                for addr in [self.app.WASTE_ADDR, self.app.LYSATE_ADDR]:
                    self.app.pumps.stop(addr)
                    self.app.pumps.purge(-1, addr)
                self.reset_stop_counter = 0
                self.app.scheduled_events.append(
                    Clock.schedule_interval(
                        partial(
                            self.switched_reset, "d2", WASTE_ADDR, 2, self.next_step
                        ),
                        self.app.switch_update_interval,
                    )
                )

                self.app.scheduled_events.append(
                    Clock.schedule_interval(
                        partial(
                            self.switched_reset, "d3", LYSATE_ADDR, 2, self.next_step
                        ),
                        self.app.switch_update_interval,
                    )
                )

            if action == "RESET_WASTE":
                if self.app.device.DEVICE_TYPE == "R0":
                    logging.info(
                        "No RESET work to be done on the R0, passing to end of program"
                    )
                    return
                for addr in [WASTE_ADDR]:
                    self.app.pumps.purge(1, addr)
                time.sleep(1)
                for addr in [WASTE_ADDR]:
                    self.app.pumps.stop(addr)
                    self.app.pumps.purge(-1, addr)
                self.reset_stop_counter = 0
                self.app.scheduled_events.append(
                    Clock.schedule_interval(
                        partial(
                            self.switched_reset, "d2", WASTE_ADDR, 1, self.next_step
                        ),
                        self.app.switch_update_interval,
                    )
                )

            if action == "GRAB":
                if self.app.POST_RUN_RATE_MM_CALIBRATION:
                    logging.debug("Using calibration post run rate values")
                    post_run_rate_mm = self.app.POST_RUN_RATE_MM_CALIBRATION
                else:
                    post_run_rate_mm = params["post_run_rate_mm"]
                if self.app.POST_RUN_VOL_ML_CALIBRATION:
                    logging.debug("Using calibration post run volume values")
                    post_run_vol_ml = self.app.POST_RUN_VOL_ML_CALIBRATION
                else:
                    post_run_vol_ml = params["post_run_vol_ml"]
                logging.debug(
                    f"Using Post Run Rate MM: {post_run_rate_mm}, ML : {post_run_vol_ml}"
                )

                for addr in [WASTE_ADDR, LYSATE_ADDR]:
                    logging.debug(f"CDA: Grabbing pump {addr}")
                    self.app.pumps.purge(1, addr)
                self.grab_stop_counter = 0
                swg1 = Clock.schedule_interval(
                    partial(
                        self.switched_grab,
                        "d4",
                        WASTE_ADDR,
                        2,
                        self.next_step,
                        post_run_rate_mm,
                        post_run_vol_ml,
                    ),
                    self.app.switch_update_interval,
                )

                self.app.scheduled_events.append(swg1)
                swg2 = Clock.schedule_interval(
                    partial(
                        self.switched_grab,
                        "d5",
                        LYSATE_ADDR,
                        2,
                        self.next_step,
                        post_run_rate_mm,
                        post_run_vol_ml,
                    ),
                    self.app.switch_update_interval,
                )

                self.app.scheduled_events.append(swg2)
                self.grab_overrun_check_schedule = Clock.schedule_once(
                    partial(self.grab_overrun_check, [swg1, swg2]),
                    self.app.grab_overrun_check_interval,
                )

                self.app.scheduled_events.append(self.grab_overrun_check_schedule)
            if action == "GRAB_WASTE":
                post_run_rate_mm = params["post_run_rate_mm"]
                post_run_vol_ml = params["post_run_vol_ml"]
                for addr in [WASTE_ADDR]:
                    logging.debug(f"CDA: Grabbing pump {addr}")
                    self.app.pumps.purge(1, addr)
                self.grab_stop_counter = 0
                swg1 = Clock.schedule_interval(
                    partial(
                        self.switched_grab,
                        "d4",
                        WASTE_ADDR,
                        1,
                        self.next_step,
                        post_run_rate_mm,
                        post_run_vol_ml,
                    ),
                    self.app.switch_update_interval,
                )

                self.app.scheduled_events.append(swg1)
                self.grab_overrun_check_schedule = Clock.schedule_once(
                    partial(self.grab_overrun_check, [swg1]),
                    self.app.grab_overrun_check_interval,
                )

                self.app.scheduled_events.append(self.grab_overrun_check_schedule)
            if action == "CHANGE_SYRINGE":
                diameter = params["diam"]
                pump_addr = params["pump_addr"]
                self.app.pumps.set_diameter(diameter, pump_addr)
                logging.debug(
                    f"Switching current loaded syringe to {diameter} diam on pump {pump_addr}"
                )

            if action == "RELEASE":
                if params["target"] == "waste":
                    addr = WASTE_ADDR
                if params["target"] == "lysate":
                    addr = LYSATE_ADDR
                rate_mh = params["rate_mh"]
                vol_ml = params["vol_ml"]
                eq_time = params.get("eq_time", 0)
                self._extracted_from_start_13(
                    "SENDING RELEASE COMMAND TO: Addr = ", addr, rate_mh, vol_ml
                )

    # TODO Rename this here and in `start`
    def _extracted_from_start_13(self, arg0, addr, rate_mh, vol_ml):
        logging.info(f"{arg0}{addr}")
        self.app.pumps.set_rate(rate_mh, "MH", addr)
        self.app.pumps.set_volume(vol_ml, "ML", addr)
        self.app.pumps.run(addr)

    def switched_reset(self, switch, addr, max_count, final_action, dt):
        if self.app.nano is None:
            raise IOError("No switches on the R0 should not be calling a switch reset!")
        self.app.nano.update()
        if not getattr(self.app.nano, switch):
            logging.info(f"CDA: Switch {switch} actived, stopping pump {addr}")
            self.app.pumps.stop(addr)
            self.reset_stop_counter += 1
            if self.reset_stop_counter == max_count:
                logging.debug(f"CDA: Both pumps homed")
                final_action()
            return False

    def switched_grab(
        self,
        switch,
        addr,
        max_count,
        final_action,
        post_run_rate_mm,
        post_run_vol_ml,
        dt,
    ):
        if self.app.nano is None:
            raise IOError("No switches on the R0 should not be calling switch grab!")
        self.app.nano.update()
        if not getattr(self.app.nano, switch):
            logging.info(f"CDA: Pump {addr} has grabbed syringe (switch {switch}).")
            logging.debug(
                f"CDA: Running extra {post_run_vol_ml} ml @ {post_run_rate_mm} ml/min to grasp firmly."
            )

            self.app.pumps.stop(addr)
            self.app.pumps.set_rate(post_run_rate_mm, "MM", addr)
            self.app.pumps.set_volume(post_run_vol_ml, "ML", addr)
            self.app.pumps.run(addr)
            self.grab_stop_counter += 1
            if self.grab_stop_counter == max_count:
                logging.debug("CDA: Both syringes grabbed")
                self.grab_overrun_check_schedule.cancel()
                final_action()
            return False

    def grab_overrun_check(self, swgs, dt):
        if self.app.nano is None:
            raise IOError(
                "No switches on the R0, should not be calling grab_overrrun_check!"
            )

        self.app.nano.update()
        overruns = []
        if getattr(self.app.nano, "d4"):
            overruns.append("1 (waste)")
            swgs[0].cancel()
        if getattr(self.app.nano, "d5"):
            overruns.append("2 (lysate)")
            swgs[1].cancel()
        if overruns:
            self.app.pumps.stop_all_pumps(self.app.list_of_pumps)
            overruns_str = " and ".join(overruns)
            plural = "s" if len(overruns) > 1 else ""
            logging.warning(f"CDA: Grab overrun in position{plural} {overruns_str}.")
            self.show_fatal_error(
                title=f"Syringe{plural} not detected",
                description=f"Syringe{plural} not inserted correctly in positions{plural} {overruns_str}.\nPlease start the test over.",
                confirm_text="Start over",
                confirm_action="abort",
                primary_color=(1, 0.33, 0.33, 1),
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

    def skip(self):
        # Check that the motor is not moving
        # TODO make this work for pressure drive by checking if we've finished a step
        number_of_stopped_pumps = 0
        for pump in self.app.list_of_pumps:
            status = self.app.pumps.status(addr=pump)
            logging.info("Pump number {} status was: {}".format(pump, status))
            if status == "S":
                number_of_stopped_pumps += 1

        if number_of_stopped_pumps == len(self.app.list_of_pumps):
            logging.info("Skip button pressed. Moving to next step. ")
            Clock.unschedule(self.set_progress)
            self.next_step()
        else:
            logging.warning(
                "Pump not stopped! Step cannot be skipped while motors are moving. Not skipping. Status: {}".format(
                    status
                )
            )


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