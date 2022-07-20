#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

from typing import List
import serial,time
import logging
from cd_alpha.PressureController import PressureController

class PressureControllerStub(PressureController):
            
    def __enter__(self) -> None: 
        logging.info("Debug, not opening  Serial connection")
        time.sleep(1)
        print("{} connected!".format("Debug port"))
        init_msg = self._read_input()
        print("Got init msg: {}".format(init_msg))
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        print("Closing Stub serial port")

    def _send_command_str(self, cmd: str) -> List[str]:
        list_of_input = ["DUMMY RESPONSE FOR DEBUG"]
        print("DEBUG CMD YOU SENT: {}".format(cmd))
        return list_of_input

    def _read_input(self) -> str:
        confirmation_msg = ["DUMMY CONFIRMATION MSG FROM READ"]
        return confirmation_msg


if __name__ == '__main__':

    print("Pyserial Version:", serial.__version__)
    print('Running. Press CTRL-C to exit.')
    with PressureControllerStub() as pres:
        #while True:
            #cmd = input("Enter Command: {PUMP (float), RESSWITCH (0/1), DUMPSWITCH (0/1)")
            #print(pres.parse_command(cmd))
        pres.set_volume(1.0)
        pres.set_rate(15.0)
        pres.run()
        


