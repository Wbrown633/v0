import contextlib
from dataclasses import dataclass
from typing import Any
from kivy.app import App
from kivy.clock import Clock
import logging
import time
from cd_alpha.NewEraPumps import PumpNetwork
from cd_alpha.Protocol import Protocol
from functools import partial
import os


@dataclass
class ChipController:
    protocol: Protocol
    app: App
    pumps: PumpNetwork
    ser: Any

    def run(self):
        '''Launch Kivy App.'''
        self.app.run()

    def cleanup(self):
        logging.debug("CDA: Cleaning upp")
        logging.debug("CDA: Unscheduling events")
        for se in self.app.scheduled_events:
            with contextlib.suppress(AttributeError):
                se.cancel()
        self.app.scheduled_events = []
        self.pumps.stop_all_pumps(self.app.list_of_pumps)

    def is_debug(self):
        return self.app.DEBUG_MODE

    def reboot(self):
        self.cleanup()
        logging.info("CDA: Rebooting...")
        if self.DEBUG_MODE:
            logging.warning(
                "CDA: In DEBUG mode, not rebooting down for real, only ending program."
            )
            self.app.stop()
        else:
            os.system("sudo reboot --poweroff now")

    def next(self):
        '''Advance iterator to the next step in the protocol.'''
        step = self.protocol.list_of_steps.pop(0)
        logging.info("Made it to controller!")

        for action in step.list_of_actions:
            if type(action).__name__ == "Pump":
                if action.target == "lysate":
                    addr = self.app.LYSATE_ADDR
                elif action.target == "waste":
                    addr = self.app.WASTE_ADDR
                rate_mh = float(action.rate_mh)
                vol_ml = float(action.vol_ml)
                eq_time = int(action.eq_time)
                self.time_total = abs(vol_ml / rate_mh) * 3600 + eq_time
                self.time_elapsed = 0
                self.run_pumps("Addr = ", addr, rate_mh, vol_ml)
                self.app.scheduled_events.append(
                    Clock.schedule_interval(
                        self.set_progress, self.app.progressbar_update_interval
                    )
                )

            elif type(action).__name__ == "Incubate":
                self.time_total = action.time
                self.time_elapsed = 0
                self.app.scheduled_events.append(
                    Clock.schedule_interval(
                        self.set_progress, self.app.progressbar_update_interval
                    )
                )

            elif type(action).__name__ == "Reset":
                if self.app.device.DEVICE_TYPE == "R0":
                    logging.info(
                        "No RESET work to be done on the R0, passing to end of program"
                    )
                    return
                for addr in [self.app.WASTE_ADDR, self.app.LYSATE_ADDR]:
                    self.pumps.purge(1, addr)
                time.sleep(1)
                for addr in [self.app.WASTE_ADDR, self.app.LYSATE_ADDR]:
                    self.pumps.stop(addr)
                    self.pumps.purge(-1, addr)
                self.reset_stop_counter = 0
                self.app.scheduled_events.append(
                    Clock.schedule_interval(
                        partial(
                            self.switched_reset, "d2", self.app.WASTE_ADDR, 2, self.next
                        ),
                        self.app.switch_update_interval,
                    )
                )

                self.app.scheduled_events.append(
                    Clock.schedule_interval(
                        partial(
                            self.switched_reset, "d3", self.app.LYSATE_ADDR, 2, self.next
                        ),
                        self.app.switch_update_interval,
                    )
                )

            if type(action).__name__ == "RESET_WASTE":
                if self.app.device.DEVICE_TYPE == "R0":
                    logging.info(
                        "No RESET work to be done on the R0, passing to end of program"
                    )
                    return
                for addr in [self.app.WASTE_ADDR]:
                    self.pumps.purge(1, addr)
                time.sleep(1)
                for addr in [self.app.WASTE_ADDR]:
                    self.pumps.stop(addr)
                    self.pumps.purge(-1, addr)
                self.reset_stop_counter = 0
                self.app.scheduled_events.append(
                    Clock.schedule_interval(
                        partial(
                            self.switched_reset, "d2", self.app.WASTE_ADDR, 1, self.next
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

                for addr in [self.app.WASTE_ADDR, self.app.LYSATE_ADDR]:
                    logging.debug(f"CDA: Grabbing pump {addr}")
                    self.pumps.purge(1, addr)
                self.grab_stop_counter = 0
                swg1 = Clock.schedule_interval(
                    partial(
                        self.switched_grab,
                        "d4",
                        self.app.WASTE_ADDR,
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
                        self.app.LYSATE_ADDR,
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
                for addr in [self.app.WASTE_ADDR]:
                    logging.debug(f"CDA: Grabbing pump {addr}")
                    self.app.pumps.purge(1, addr)
                self.grab_stop_counter = 0
                swg1 = Clock.schedule_interval(
                    partial(
                        self.switched_grab,
                        "d4",
                        self.app.WASTE_ADDR,
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
                self.pumps.set_diameter(diameter, pump_addr)
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

        self.app.process.next_step()

    def run_pumps(self, arg0, addr, rate_mh, vol_ml):
        logging.info(f"{arg0}{addr}")
        self.pumps.set_rate(rate_mh, "MH", addr)
        self.pumps.set_volume(vol_ml, "ML", addr)
        self.pumps.run(addr)

    def switched_reset(self, switch, addr, max_count, final_action, dt):
        if self.app.nano is None:
            raise IOError("No switches on the R0 should not be calling a switch reset!")
        self.app.nano.update()
        if not getattr(self.app.nano, switch):
            logging.info(f"CDA: Switch {switch} actived, stopping pump {addr}")
            self.pumps.stop(addr)
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

            self.pumps.stop(addr)
            self.pumps.set_rate(post_run_rate_mm, "MM", addr)
            self.pumps.set_volume(post_run_vol_ml, "ML", addr)
            self.pumps.run(addr)
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
            self.pumps.stop_all_pumps(self.list_of_pumps)
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
            status = self.pumps.status(addr=pump)
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
