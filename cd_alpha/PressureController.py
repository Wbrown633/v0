#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

from typing import List
import serial,time
import logging

class PressureController:
    def __init__(self) -> None:
        self.max_pressure_set_point_kPa = 3.0
            
    def __enter__(self) -> None: 
        logging.info("Opening Serial connection")
        self.arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
        time.sleep(0.1)
        logging.info("{} connected!".format(self.arduino.port))
        self.arduino.write("")
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        logging.info("Closing serial port.")
        self.arduino.close()

    def _send_command_str(self, cmd: str) -> List[str]:
        assert self.arduino.isOpen(), "Serial port not open."
        self.arduino.write(cmd.encode())
        time.sleep(0.1) #wait for arduino to answer
        if self.arduino.out_waiting > 0:
            self.arduino.reset_output_buffer()
        time.sleep(0.1)
        if  self.arduino.in_waiting > 0: 
            confirmation_msg = self.arduino.readlines(self.arduino.in_waiting)
            self.arduino.reset_input_buffer
        return confirmation_msg

    def _switch_status(self, switch_name:str, status:bool) -> str:
        '''Change the status of the Reservoir switch. Return the response string.'''
        switch_status = 0
        if status:
            switch_status = 1
        cmd_string = "{}:{};".format(switch_name, switch_status)
        response = self._send_command_str(self, cmd_string)
        return response[-1]
        
    def res_switch(self, status:bool) -> str:
        return self._switch_status("RESSWITCH", status)
    
    def dump_switch(self, status:bool) -> str:
        '''Change the status of the pressure dump switch. Return the response string.'''
        return self._switch_status("DUMPSWITCH", status)
        

    def set_pressure_pump(self, pressure_set_kPa: float) -> str:
        '''Change the pressure set point for the pump.'''
        assert pressure_set_kPa < self.max_pressure_set_point_kPa, "Invalid pressure"
        cmd_string = "PUMP:{};".format(pressure_set_kPa)
        response = self._send_command_str(cmd_string)
        return response[-1]
        



if __name__ == '__main__':
    
    print('Running. Press CTRL-C to exit.')
    with PressureController() as pres:
        print(pres.set_pressure_pump(-15.0))