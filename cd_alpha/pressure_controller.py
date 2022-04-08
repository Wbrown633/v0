#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

from ast import While
import serial,time


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
                        answer=arduino.readlines()
                        print(answer)
                        #remove data after reading
                    arduino.reset_input_buffer()
            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")