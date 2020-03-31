import copy
from os.path import join
from threading import Thread
import time

from sensortag_classes import SensorTag

INIT_WAIT = 1
WAIT_BETWEEN_READINGS_IN_MILLISECONDS = 1000
DATA_FOLDER = '/media/kasun/b6473291-3674-4adc-bc71-f6c16459baf3/data/smart_building/desc_images_mar16/'
SECONDS_TO_RUN = -1

SENSOR_TAG_LIST = [
    {
        "ble_mac": "54:6C:0E:53:45:B7",
        "label": "a"
    },
#     {
#         "ble_mac": "54:6C:0E:53:3B:0A",
#         "label": "b"
#     },
# {
#         "ble_mac": "54:6C:0E:53:46:44",
#         "label": "c"
#     },
{
        "ble_mac": "54:6C:0E:53:3F:77",
        "label": "d"
    },
# {
#         "ble_mac": "54:6C:0E:78:BE:82",
#         "label": "e"
#     },
{
        "ble_mac": "F0:F8:F2:86:31:86",
        "label": "f"
    },
]

SENSOR_TAGS = []
LUX_READINGS = []

for sensor_tag in SENSOR_TAG_LIST:
    SENSOR_TAGS.append(sensor_tag['ble_mac'])

start_time = 0


def is_time_to_stop():
    if SECONDS_TO_RUN == -1:
        return False
    now = int(time.time())
    return now > start_time + SECONDS_TO_RUN


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


def collect_frames(label, ble_mac):
    print("start lux reading for :", ble_mac)
    tag = SensorTag(ble_mac)
    tag.char_write_cmd(0x47, 0o1)  # Enable Luminance
    time.sleep(0.5)
    while 1:
        if is_time_to_stop():
            print('stopped collecting frames at', time.time())
            break

        hex_lux = tag.char_read_hnd(0x44, "luminance")
        dec_lux = hexLum2Lux(hex_lux)
        timestamp = int(time.time())
        LUX_READINGS.append({'label':label, 'lux_reading':dec_lux, 'timestamp':timestamp})
        time.sleep(1)
        # print(label, timestamp, dec_lux)


def process_readings():
    # global threshold
    print "processing started"
    while 1:
        if is_time_to_stop():
            print('stopped processing frames at', time.time())
            break
        current_records_number = len(LUX_READINGS)
        print "processing records", current_records_number
        if current_records_number >0:
            i = 0
            with open("/home/pi/records.txt",'a') as f:
                while i < current_records_number:
                    record = LUX_READINGS.pop()
                    f.write("{},{},{}\n".format(record['label'], record['timestamp'],record['lux_reading']))
                    # print i, record
                    i+=1
        print "going for sleep"
        time.sleep(5)


if __name__ == "__main__":
    for sensor_tag in SENSOR_TAG_LIST:
        Thread(target=collect_frames, args=(sensor_tag["label"], sensor_tag["ble_mac"])).start()
    start_time = int(time.time())
    print('start time', start_time)
    print("going to sleep for seconds", INIT_WAIT)
    time.sleep(INIT_WAIT)
    process_readings()
