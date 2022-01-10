
# Script written for Griffin breast cancer QiaZol elution experiment
# 2.5 mL sample volume
# 20 mL syringe waste
# 5 mL syringe lysate


from collections import OrderedDict
import json
import sys
import os
import RPi.GPIO as GPIO

# RasPi Pin definitions
Sw1 = 16 # User Switch supply
Sw2 = 12 # User Switch read

# Pin setup
GPIO.setmode(GPIO.BCM) # Broadcom pin numbering scheme
GPIO.setup(Sw1, GPIO.OUT) # User switch pin set as output
GPIO.setup(Sw2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   # user switch pin set as input
GPIO.output(Sw1, GPIO.HIGH)  #provide power for user switch

#from NanoController import Nano
from NewEraPumps import PumpNetwork
from functools import partial
import serial
import time
from datetime import datetime
import logging
time_now_str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
logging.basicConfig(
    filename=f"/home/pi/cd-alpha/logs/cda_{time_now_str}.log",
    filemode='w',
    datefmt="%Y-%m-%d_%H:%M:%S",
    level=logging.DEBUG)

logging.info("Logging started")

DEBUG_MODE = False

if not DEBUG_MODE:
    # Make sure the 'real' protocol is used
    PROTOCOL_FILE_NAME = "cda-protocol-v01.json"
else:
    logging.warning("CDA: *** DEBUG MODE ***")

logging.info(f"CDA: Using protocol: '{PROTOCOL_FILE_NAME}''")

ser = serial.Serial("/dev/ttyUSB0", 19200, timeout=2)
pumps = PumpNetwork(ser)
WASTE_ADDR = 2
#LYSATE_ADDR = 2
WASTE_DIAMETER_mm = 20.10
LYSATE_DIAMETER_mm = 12.45

scheduled_events = []

def stop_all_pumps():
    logging.debug("CDA: Stopping all pumps.")
    for addr in [WASTE_ADDR]:
        try:
            pumps.stop(addr)
        except IOError as err:
            if str(err)[-3:] == "?NA":
                logging.debug(f"CDA: Pump {addr:02} already stopped.")
            else:
                raise


def cleanup():
    logging.debug("CDA: Cleaning upp")
    global scheduled_events
    logging.debug("CDA: Unscheduling events")
    for se in scheduled_events:
        try:
            se.cancel()
        except AttributeError: pass
    scheduled_events = []
    stop_all_pumps()

def shutdown():
    logging.info("Shutting down...")
    cleanup()
    if DEBUG_MODE:
        logging.warning("CDA: In DEBUG mode, not shutting down for real, only ending program.")
        App.get_running_app().stop()
    else:
        os.system('sudo shutdown --poweroff now')

def reboot():
    cleanup()
    logging.info("CDA: Rebooting...")
    if DEBUG_MODE:
        logging.warning("CDA: In DEBUG mode, not rebooting down for real, only ending program.")
        App.get_running_app().stop()
    else:
        os.system('sudo reboot --poweroff now')
        # call("sudo reboot --poweroff now", shell=True)

logging.info("CDA: Starting main script.")

stop_all_pumps()

pumps.set_diameter(diameter_mm=WASTE_DIAMETER_mm, addr=WASTE_ADDR)
#pumps.set_diameter(diameter_mm=LYSATE_DIAMETER_mm, addr=LYSATE_ADDR)

#nano = Nano(8, 7)

#progressbar_update_interval = .5
#switch_update_interval = .1
#grab_overrun_check_interval = 20

addr = WASTE_ADDR
#print("STOP:", pumps.stop(addr))

# MM=ml/min, MH=ml/hr, UH=μl/hr, UM=μl/min

print("load 20 mL syringe")

while True:
    if GPIO.input(Sw2) == 0:
        break

##ENGAGE PUMP

print("Rate:", pumps.set_rate(-5, 'MM', addr))
print("Volume:", pumps.set_volume(0.8, 'ML',  addr))
print("Run:", pumps.run(addr))

while True:
    stat = pumps.status(addr)
    if stat == 'S':
        print("engagement complete")
        break

##F127

pumps.buzz(WASTE_ADDR)
print("add 1.8 mL F127, then push 'ok'")

while True:
    if GPIO.input(Sw2) == 0:
        break

print("Rate:", pumps.set_rate(-50, 'MH', addr))
print("Volume:", pumps.set_volume(1, 'ML',  addr))
print("Run:", pumps.run(addr))

while True:
    stat = pumps.status(addr)
    if stat == 'S':
        print("F127 fast step complete")
        break
#60 minute pause. 0.500ML/0.5 MH = 1H = 60 min

print("running slow flow for 60 minutes")
print("Rate:", pumps.set_rate(-500, 'UH', addr))
print("Volume:", pumps.set_volume(0.5, 'ML',  addr))
print("Run:", pumps.run(addr))

while True:
    stat = pumps.status(addr)
    if stat == 'S':
        print("F127 slow step complete")
        break
    
###PBS wash

pumps.buzz(WASTE_ADDR)
print("add 1 mL 1x PBS, then push 'ok'")

while True:
    if GPIO.input(Sw2) == 0:
        break

print("running PBS wash") 
print("Rate:", pumps.set_rate(-50, 'MH', addr))
print("Volume:", pumps.set_volume(1, 'ML',  addr))
print("Run:", pumps.run(addr))

while True:
    stat = pumps.status(addr)
    if stat == 'S':
        print("PBS wash step complete")
        break
    
#2 minute pause. 0.003ML/0.1 MH = 0.03H = 2 min

print("running slow flow for 2 minutes")
print("Rate:", pumps.set_rate(-100, 'UH', addr))
print("Volume:", pumps.set_volume(0.003, 'ML',  addr))
print("Run:", pumps.run(addr))

while True:
    stat = pumps.status(addr)
    if stat == 'S':
        print("PBS slow step complete")
        break
    
###Sample flow step

pumps.buzz(WASTE_ADDR)
print("add 2 mL Sample, then push 'ok'")

while True:
    if GPIO.input(Sw2) == 0:
        break
    
print("running sample") 
print("Rate:", pumps.set_rate(-10, 'MH', addr))
print("Volume:", pumps.set_volume(2.2, 'ML',  addr))
print("Run:", pumps.run(addr))

while True:
    stat = pumps.status(addr)
    if stat == 'S':
        print("Sample flow complete")
        break
    
###PBS wash 1

pumps.buzz(WASTE_ADDR)
print("add 200 uL 1x PBS, then push 'ok'")

while True:
    if GPIO.input(Sw2) == 0:
        break
    
print("running first PBS wash") 
print("Rate:", pumps.set_rate(-10, 'MH', addr))
print("Volume:", pumps.set_volume(0.2, 'ML',  addr))
print("Run:", pumps.run(addr))

while True:
    stat = pumps.status(addr)
    if stat == 'S':
        print("First PBS wash complete")
        break
    
###PBS wash 2

pumps.buzz(WASTE_ADDR)
print("add 800 uL 1x PBS, then push 'ok'")

while True:
    if GPIO.input(Sw2) == 0:
        break
    
print("running second PBS wash") 
print("Rate:", pumps.set_rate(-10, 'MH', addr))
print("Volume:", pumps.set_volume(0.4, 'ML',  addr))
print("Run:", pumps.run(addr))

while True:
    stat = pumps.status(addr)
    if stat == 'S':
        print("Second PBS wash complete")
        break

print("running second half of PBS wash 2") 
print("Rate:", pumps.set_rate(-50, 'MH', addr))
print("Volume:", pumps.set_volume(0.4, 'ML',  addr))
print("Run:", pumps.run(addr))

while True:
    stat = pumps.status(addr)
    if stat == 'S':
        print("Second PBS wash complete")
        break
###PBS wash 3

pumps.buzz(WASTE_ADDR)
print("add 1000 uL 1x PBS, then push 'ok'")

while True:
    if GPIO.input(Sw2) == 0:
        break
    
print("running third PBS wash") 
print("Rate:", pumps.set_rate(-50, 'MH', addr))
print("Volume:", pumps.set_volume(1, 'ML',  addr))
print("Run:", pumps.run(addr))

while True:
    stat = pumps.status(addr)
    if stat == 'S':
        print("Third PBS wash complete")
        break
       
###  LYSIS

pumps.buzz(WASTE_ADDR)
print("Add 600 uL QiaZOL, and push 'ok'")

while True:
    if GPIO.input(Sw2) == 0:
        break

print("pulling in QiaZOL") 
print("Rate:", pumps.set_rate(-50, 'MH', addr))
print("Volume:", pumps.set_volume(0.6, 'ML',  addr))
print("Run:", pumps.run(addr))

while True:
    stat = pumps.status(addr)
    if stat == 'S':
        print("QiaZOL pull-in complete")
        break


pumps.buzz(WASTE_ADDR)
print("Switch to 5 mL lysate syringe")

pumps.buzz(WASTE_ADDR)

pumps.set_diameter(diameter_mm=LYSATE_DIAMETER_mm, addr=WASTE_ADDR)

print("incubating QiaZOL 2 minutes, Switch to 5 mL lysate syringe") 
print("Rate:", pumps.set_rate(-500, 'UH', addr))
print("Volume:", pumps.set_volume(0.016, 'ML',  addr))
print("Run:", pumps.run(addr))

while True:
    stat = pumps.status(addr)
    if stat == 'S':
        print("QiaZOL incubation complete")
        break

pumps.buzz(WASTE_ADDR)


###PBS wash post lysis

pumps.buzz(WASTE_ADDR)
print("add 1 mL 1x PBS, then push 'ok'")

while True:
    if GPIO.input(Sw2) == 0:
        break
    
print("running post-lysis PBS wash") 
print("Rate:", pumps.set_rate(-50, 'MH', addr))
print("Volume:", pumps.set_volume(0.7, 'ML',  addr))
print("Run:", pumps.run(addr))

while True:
    stat = pumps.status(addr)
    if stat == 'S':
        print("Post-lysis PBS wash complete")
        break


GPIO.cleanup() # clean up all GPIO 
