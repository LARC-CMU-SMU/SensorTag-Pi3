#!/usr/bin/env python
import pexpect
import sys
import time
import json
import select
import requests
import warnings
import datetime
import traceback
import httplib
import math
import struct

from sensortag_classes import *
from sensortag_calcs import *

from base64 import b64encode, b64decode
from hashlib import sha256
from urllib import quote_plus, urlencode
from hmac import HMAC
import os


def hexLum2Lux(raw_luminance):	
  m ="0FFF"
  e ="F000" 
  raw_luminance = int(raw_luminance,16)
  m = int(m, 16) #Assign initial values as per the CC2650 Optical Sensor Dataset
  exp = int(e, 16) #Assign initial values as per the CC2650 Optical Sensor Dataset	
  m = (raw_luminance & m) 		#as per the CC2650 Optical Sensor Dataset
  exp = (raw_luminance & exp) >> 12 	#as per the CC2650 Optical Sensor Dataset
  luminance = (m*0.01*pow(2.0,exp)) 	#as per the CC2650 Optical Sensor Dataset	
  return luminance #returning luminance in lux

  
def twos_complement(hexstr,bits):
  value = int(hexstr,16)
  if value & (1 << (bits-1)):
    value -= 1 << bits
  return value


def s16(value):
    # 0x8000 --> -32768
    # 0x7fff --> +32767
    return -(value & 0x8000) | (value & 0x7fff)  


def main():
  # bluetooth_adr = sys.argv[1] # this line to be uncommented if need to run from command prompt and there are several Sensor-Tags.
  bluetooth_adr = "54:6C:0E:53:45:B7"
  print "INFO: [re]starting.."
  tag  = SensorTag(bluetooth_adr) #pass the Bluetooth Address
  counter = 0  

  tag.char_write_cmd(0x47,01) # Enable Luminance
  time.sleep(0.5)
  
  while True:
    """GETTING THE LUMINANCE"""
    hex_lux = tag.char_read_hnd(0x44, "luminance")
    print hex_lux
    lux_luminance = hexLum2Lux(hex_lux)
    timestamp = int(time.time())
    data_str = ("{}, {}\n".format(timestamp, lux_luminance))
    print data_str
    with open(bluetooth_adr+'luminance.txt', 'a') as f:
        f.write(data_str)
    time.sleep(1)
    

if __name__ == "__main__":
  main()

