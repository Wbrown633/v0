#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

import serial,time
import logging

class PressureController:
    def __init__(self) -> None:
        pass
            
    def __enter__(self) -> None: 
        logging.info("Opening Serial connection")
        self.arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
        time.sleep(0.1)
        logging.info("{} connected!".format(arduino.port))
        self.arduino.write("")
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        logging.info("Closing serial port.")
        self.arduino.close()

    def _send_command_str(self, cmd: str) -> str:
        assert arduino.isOpen(), "Serial port not open."
        confirmation_msgs = []
        while True:
            prev_msg = confirmation_msg
            arduino.write(cmd.encode())
            time.sleep(0.5) #wait for arduino to answer
            if arduino.out_waiting > 0:
                arduino.reset_output_buffer()
            while arduino.in_waiting == 0: pass
            if  arduino.in_waiting > 0: 
                confirmation_msg = arduino.readline()
                #remove data after reading
                arduino.reset_input_buffer()

    def res_switch(self, status:bool) -> str:
        '''Change the status of the Reservoir switch. Return the response string.'''
        switch_status = 0

        if status:
            switch_status = 1

        cmd_string = "RESSWITCH:{};".format(switch_status)
        self.arduino.write()
        
    
    def dump_switch(self) -> str:
        '''Change the status of the pressure dump switch. Return the response string.'''
        self.arduino.write()
        

    def set_pressure_pump(self, pressure_set_kPa: float) -> str:
        '''Change the pressure set point for the pump.'''
        



if __name__ == '__main__':
    
    print('Running. Press CTRL-C to exit.')
    with serial.Serial("/dev/ttyACM0", 115200, timeout=1) as arduino:
        time.sleep(0.1) #wait for serial to open
        if arduino.isOpen():
            print("{} connected!".format(arduino.port))
            try:
                while True:
                    cmd=input("Enter command : ")
                    arduino.write(cmd.encode())
                    time.sleep(0.5) #wait for arduino to answer
                    if arduino.out_waiting > 0:
                        arduino.reset_output_buffer()
                    while arduino.in_waiting == 0: pass
                    if  arduino.in_waiting > 0: 
                        answer=arduino.readline()
                        print(answer)
                        #remove data after reading
                        arduino.reset_input_buffer()
                        print(arduino.in_waiting)
            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")