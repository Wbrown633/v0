#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

from typing import List
import serial,time
import logging

class PressureController:
    def __init__(self) -> None:
        self.max_pressure_set_point_kPa = 120
        self.flow_rate_ml_per_hr = None
        self.volume_ml = None
            
    def __enter__(self) -> None: 
        logging.info("Opening Serial connection")
        self.arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=0) #for pi its "/dev/ttyACM0" for win it's usually "COM3"
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

    def _calculate_time_secs(self) -> int:
        '''Given a the flowrate and volume to be pumped calculate the time required.'''
        # TODO make sure this level of accuracy is enough, int rounding could lose information
        return int(self.volume_ml / self.flow_rate_ml_per_hr * 3600)

    def _pressure_from_flowrate(self) -> float:
        '''Using provided calibration curves calculate the pressure needed to achieve the desired flowrate.'''

        #TODO these curves may need to depend on the liquid that is being used, make a dictionary of fluid type -> 2 point calibration equation

        return self.flow_rate_ml_per_hr * 0.12 - 100.0  # Totally made up place holder curve
        
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

    def get_pressure_reading(self) -> float:
        # needs to be implemented in the Arduino
        pass 

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

    def set_rate(self, rate, unit="MH", addr=''):
        self.flow_rate_ml_per_hr = rate

    def set_volume(self, volume, unit="ML", addr=''):
        self.volume_ml = volume

    def stop_all_pumps(self, list_of_pumps):
        self.set_pressure_pump(100.0)

    def run(self, addr="0") -> None:

        ''' Step logic:
            - set the pressure of the pump
            - when the pressure in the reservoir is achieved open the res switch
            - keep the res switch open for the duration period
            - close res switch, open dump switch
        '''
        if addr != "0":
            raise ValueError("Pump addresses other than 0 not implemented")

        
        logging.info(self.set_pressure_pump(self._pressure_from_flowrate()))

        # these waits should be re-factored to use either kivy clock or async await, this is just a rough draft

        # Using sleeps for proof of concept, will block GUI and is really ugly

        time.sleep(2) # Wait for the pressure to reach the set point in the reservoir

        # Open the res_switch
        self.res_switch(True)
        
        # Wait for the provided step duration
        #time.sleep(self._calculate_time_secs()) 
        #just print the time don't wait for debug
        print("Seconds to wait for step time: {}".format(self._calculate_time_secs()))

        self.res_switch(False) # at the end of the step close the res switch
        time.sleep(0.5)
        self.dump_switch(True) # open the release valve to stop the pressure on the chip
        time.sleep(0.5) # wait for the pressure to be relieved before moving on to another step
        



if __name__ == '__main__':

    print("Pyserial Version:", serial.__version__)
    print('Running. Press CTRL-C to exit.')
    with PressureController() as pres:
        while True:
            cmd = input("Enter Command: {PUMP (float), RESSWITCH (0/1), DUMPSWITCH (0/1)")
            print(pres.parse_command(cmd))


