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
        self.arduino = serial.Serial("COM3", 115200, timeout=0) #for pi its "/dev/ttyACM0"
        time.sleep(1)
        print("{} connected!".format(self.arduino.port))
        init_msg = self._read_input()
        print("Got init msg: {}".format(init_msg))
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        print("Closing serial port.")
        self.arduino.flush()
        self.arduino.close()

    def _send_command_str(self, cmd: str) -> List[str]:
        assert self.arduino.isOpen(), "Serial port not open."
        self.arduino.write(cmd.encode())
        list_of_input = self._read_input()
        return list_of_input

    def _read_input(self) -> str:
        confirmation_msg = []
        time.sleep(1.5)
        while self.arduino.in_waiting > 0:
            confirmation_msg.append(self.arduino.readline().decode())
        return confirmation_msg

    def _switch_status(self, switch_name:str, status:bool) -> str:
        '''Change the status of the Reservoir switch. Return the response string.'''
        switch_status = 0
        if status:
            switch_status = 1
        cmd_string = "{}:{};\n".format(switch_name, switch_status)
        response = self._send_command_str(cmd_string)
        return response
        
    def res_switch(self, status:bool) -> str:
        return self._switch_status("RESSWITCH", status)
    
    def dump_switch(self, status:bool) -> str:
        '''Change the status of the pressure dump switch. Return the response string.'''
        return self._switch_status("DUMPSWITCH", status)
        
    def set_pressure_pump(self, pressure_set_kPa: float) -> str:
        '''Change the pressure set point for the pump.'''
        assert pressure_set_kPa < self.max_pressure_set_point_kPa, "Invalid pressure"
        cmd_string = "PUMP:{};\n".format(pressure_set_kPa)
        response = self._send_command_str(cmd_string)
        return response

    def parse_command(self, command_string: str) -> str:
        command_list = command_string.split(" ")
        command_type = command_list[0].upper()
        command_content = command_list[1]
        if command_type == "PUMP":
            return self.set_pressure_pump(float(command_content))
        elif command_type == "RESSWITCH":
            return self.res_switch(command_content == "1")
        elif command_type == "DUMPSWITCH":
            return self.dump_switch(command_content == "1")
        else:
            raise ValueError("Command Type was not one of {PUMP/RESSWITCH/DUMPSWITCH}")
        



if __name__ == '__main__':

    print("Pyserial Version:", serial.__version__)
    print('Running. Press CTRL-C to exit.')
    with PressureController() as pres:
        while True:
            cmd = input("Enter Command: {PUMP (float), RESSWITCH (0/1), DUMPSWITCH (0/1)")
            print(pres.parse_command(cmd))


