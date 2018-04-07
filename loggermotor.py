##### Libraries #####
from datetime import datetime
from sense_hat import SenseHat
from time import sleep
from threading import Thread

import subprocess
subprocess.call(["ticcmd", "--settings", "bigmotor32.txt"])
subprocess.call(["ticcmd", "--halt-and-set-position", "0"])
subprocess.call(["ticcmd", "--resume"])

pos = 0
lastpos = 0
gain = 2000

sense = SenseHat()
o = sense.get_orientation()
iroll = o["roll"]

freq = raw_input("Enter frequency: ")
print "You entered Freq = ", freq 

amp = raw_input("Enter amplitude: ")
print "You entered Amplitude = ", amp 


##### Logging Settings #####
FILENAME = ""
WRITE_FREQUENCY = 100
TEMP_H=True
TEMP_P=False
HUMIDITY=True
PRESSURE=True
ORIENTATION=True
ACCELERATION=True
MAG=True
GYRO=True
DELAY=0

##### Functions #####
def file_setup(filename):
    header =[]
    if ORIENTATION:
        header.extend(["roll", "weight position"])
    if ACCELERATION:
        header.extend(["accel_y"])
    header.append("timestamp")

    with open(filename,"w") as f:
        f.write(",".join(str(value) for value in header)+ "\n")

def log_data():
    output_string = ",".join(str(value) for value in sense_data)
    batch_data.append(output_string)


def get_sense_data(pos):
    sense_data=[]

    if ORIENTATION:
        o = sense.get_orientation()
        roll = o["roll"]-iroll
        if roll > 180:
            roll = (roll - 360)
        if roll < -180:
            roll = (roll + 360)

        sense_data.extend([roll])
        sense_data.extend([pos])


    if ACCELERATION:
        acc = sense.get_accelerometer_raw()
        y = acc["y"]
        sense_data.extend([y])

    sense_data.append(datetime.now())

    return sense_data

def timed_log():
    while True:
        log_data()
        sleep(DELAY)




##### Main Program #####
sense = SenseHat()
batch_data= []

if FILENAME == "":
    filename = "PantonIPExp-MotorControl-"+freq+"hz-"+amp+"m-"+str(datetime.now())+".csv"
else:
    filename = FILENAME+"-"+str(datetime.now())+".csv"

file_setup(filename)

if DELAY > 0:
    sense_data = get_sense_data()
    Thread(target= timed_log).start()

while True:
    o = sense.get_orientation()
    roll = o["roll"]-iroll
    if roll > 180:
        roll = (roll - 360)
    if roll < -180:
        roll = (roll + 360)

    #roll = sense_data[0]
    lastpos = pos

    pos = int(roll * gain)
    if abs(roll) < 1.6:
        pos = 0
    if pos > 13800:
        pos = 13801
    if pos < -13800:
        pos = -13801

    pos_string = str(pos)
    print " roll = ", round(roll,2), " pos = ", pos_string
    if abs(pos) < 14000 and abs(pos-lastpos) > 750:
        subprocess.call(["ticcmd", "-p", pos_string  ])

    sense_data = get_sense_data(pos)

    if DELAY == 0:
        log_data()

    if len(batch_data) >= WRITE_FREQUENCY:
        print("Writing to file..")
        with open(filename,"a") as f:
            for line in batch_data:
                f.write(line + "\n")
            batch_data = []
