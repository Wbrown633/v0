
# Western RIPA
# 2 mL sample volume
# 20 mL syringe waste
# 5 mL syringe lysate


from asyncio import wait_for
from audioop import add
from collections import OrderedDict
import json
from multiprocessing.connection import wait
import sys
import os
import RPi.GPIO as GPIO
import time

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

def wait_for_switch():
    time.sleep(1)
    while True:
        if GPIO.input(Sw2) == 0:
            break

def wait_for_pump(completion_msg):
    while True:
        stat = pumps.status(addr)
        if stat == 'S':
            print(completion_msg)
            break

def wait_timer(start_msg, complete_msg, wait_time):
    print(start_msg)
    time.sleep(wait_time)
    print(complete_msg)
    pumps.buzz(WASTE_ADDR)

logging.info("CDA: Starting main script. 16v2")

print("Western RIPA")
print("2 mL sample volume")
print("20 mL syringe waste")
print("5 mL syringe Lysate")

stop_all_pumps()

pumps.set_diameter(diameter_mm=WASTE_DIAMETER_mm, addr=WASTE_ADDR)

addr = WASTE_ADDR
#print("STOP:", pumps.stop(addr))

# MM=ml/min, MH=ml/hr, UH=μl/hr, UM=μl/min

print("load 20 mL syringe")

wait_for_switch()

## ENGAGE PUMP

print("Rate:", pumps.set_rate(-5, 'MM', addr))
print("Volume:", pumps.set_volume(0.8, 'ML',  addr))
print("Run:", pumps.run(addr))

wait_for_pump("engagement complete")

print("Insert Chip, reservoir, and tubing.")

wait_for_switch()

## F127

pumps.buzz(WASTE_ADDR)
print("add 1.8 mL F127, then push the switch")

wait_for_switch()

print("Rate:", pumps.set_rate(-50, 'MH', addr))
print("Volume:", pumps.set_volume(1, 'ML',  addr))
print("Run:", pumps.run(addr))

wait_for_pump("F127 fast step complete")

#60 minute pause. 0.500ML/0.5 MH = 1H = 60 min

print("running slow flow for 60 minutes")
print("Rate:", pumps.set_rate(-500, 'UH', addr))
print("Volume:", pumps.set_volume(0.5, 'ML',  addr))
print("Run:", pumps.run(addr))

wait_for_pump("F127 slow step complete")


### PBS wash

pumps.buzz(WASTE_ADDR)
print("add 1 mL 1x PBS, then push the switch")

wait_for_switch()

print("running PBS wash") 
print("Rate:", pumps.set_rate(-50, 'MH', addr))
print("Volume:", pumps.set_volume(1, 'ML',  addr))
print("Run:", pumps.run(addr))

wait_for_pump("PBS wash step complete")

#2 minute pause. 0.003ML/0.1 MH = 0.03H = 2 min

print("running slow flow for 2 minutes")
print("Rate:", pumps.set_rate(-100, 'UH', addr))
print("Volume:", pumps.set_volume(0.003, 'ML',  addr))
print("Run:", pumps.run(addr))

wait_for_pump("PBS slow step complete")


### Sample flow step

pumps.buzz(WASTE_ADDR)
print("add 2 mL Sample, then push the switch")

wait_for_switch()

print("running sample") 
print("Rate:", pumps.set_rate(-10, 'MH', addr))
print("Volume:", pumps.set_volume(2.2, 'ML',  addr))
print("Run:", pumps.run(addr))

wait_for_pump("Sample flow complete")

wait_timer("Waiting for two minutes", "Sample wait complete.", 120)


### PBS wash 1

pumps.buzz(WASTE_ADDR)
print("add 400 uL 1x PBS, then push the switch")

wait_for_switch()
    
print("running first PBS wash") 
print("Rate:", pumps.set_rate(-10, 'MH', addr))
print("Volume:", pumps.set_volume(0.2, 'ML',  addr))
print("Run:", pumps.run(addr))

wait_for_pump("First PBS wash complete")

wait_timer("Waiting for two minutes", "PBS Wash 1 complete", 120)
    
### PBS Wash 2 Part 1

pumps.buzz(WASTE_ADDR)
print("add 800 uL 1x PBS, then push the switch")

wait_for_switch()
    
print("running PBS Wash 2 PT. 1") 
print("Rate:", pumps.set_rate(-10, 'MH', addr))
print("Volume:", pumps.set_volume(0.4, 'ML',  addr))
print("Run:", pumps.run(addr))

wait_for_pump("Second PBS wash complete")

wait_timer("Waiting for two minutes", "PBS wash 2 part 1 wait complete", 120)

### PBS Wash 2 part 2

print("running PBS Wash 2 PT. 2") 
print("Rate:", pumps.set_rate(-50, 'MH', addr))
print("Volume:", pumps.set_volume(0.4, 'ML',  addr))
print("Run:", pumps.run(addr))

wait_for_pump("Second PBS wash complete")

wait_timer("Waiting two minutes", "PBS Wash 2 PT. 2 wait complete", 120)

###PBS wash 3

pumps.buzz(WASTE_ADDR)
print("add 1000 uL 1x PBS, then push the switch")

wait_for_switch()
    
print("running third PBS wash") 
print("Rate:", pumps.set_rate(-50, 'MH', addr))
print("Volume:", pumps.set_volume(1.2, 'ML',  addr))
print("Run:", pumps.run(addr))

wait_for_pump("Third PBS wash complete")

wait_timer("Waiting for two minutes", "PBS Wash 3 wait complete", 120)

       
###  LYSIS

pumps.buzz(WASTE_ADDR)
print("Add 600 uL RIPA, and push the switch")

wait_for_switch()

print("pulling in RIPA") 
print("Rate:", pumps.set_rate(-50, 'MH', addr))
print("Volume:", pumps.set_volume(0.6, 'ML',  addr))
print("Run:", pumps.run(addr))

wait_for_pump("RIPA pull-in complete")

pumps.buzz(WASTE_ADDR)


print("Incubating RIPA 2 minutes.") 
print("Rate:", pumps.set_rate(-500, 'UH', addr))
print("Volume:", pumps.set_volume(0.016, 'ML',  addr))
print("Run:", pumps.run(addr))

wait_for_pump("RIPA slow pull incubation complete")

wait_timer("Waiting 3 more minutes with no pull", "RIPA incubation complete", 180)

print("Switch to 5 mL lysate syringe")

wait_for_switch()

pumps.buzz(WASTE_ADDR)

pumps.set_diameter(diameter_mm=LYSATE_DIAMETER_mm, addr=WASTE_ADDR)
###PBS wash post lysis

pumps.buzz(WASTE_ADDR)
print("add 1 mL 1x PBS, then push the switch")

wait_for_switch()
    
print("running post-lysis PBS wash") 
print("Rate:", pumps.set_rate(-50, 'MH', addr))
print("Volume:", pumps.set_volume(1.1, 'ML',  addr))
print("Run:", pumps.run(addr))

wait_for_pump("Post-lysis PBS wash complete")

wait_timer("Waiting for two minutes", "PBS Chase wait complete", 120)

GPIO.cleanup() # clean up all GPIO 
