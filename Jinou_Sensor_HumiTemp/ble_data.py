# Using Hexiwear with Python
# Script to get the device data and append it to a file
# Usage
# python GetData.py <device>
# e.g. python GetData.py "00:29:40:08:00:01"
import pexpect
import time
import sys
import os

# ---------------------------------------------------------------------
# function to transform hex string like "0a cd" into signed integer
# -----------------------------Temp----------------------------------------
def hexStrToInt(hexstr):
  
    val = int(hexstr[0:2],16) + (int(hexstr[3:5],16))
    if ((val&0x8000)==0x8000): # treat signed 16bits
        val = -((val^0xffff)+1)
    return val
# -----------------------------Hum----------------------------------------
def hexStrToIntHum(hexstr):
    #print(hexstr)
    val = int(hexstr[0:2],16) + (int(hexstr[3:5],16))
    if ((val&0x8000)==0x8000): # treat signed 16bits
        val = -((val^0xffff)+1)
    return val
#-----------------------------------------------------------------------
def hexStrToIntBattL(hexstr):
  val = int(hexstr[0:2])
  return val


#--------------------------------------------------------------------------
def celsius_to_fahrenheit(value):
    return (value * 1.8) + 32
#----------------------------------------------------------------------------

DEVICE = "ca:67:02:0d:60:1d"   # device #24

if len(sys.argv) == 2:
  DEVICE = str(sys.argv[1])

# Run gatttool interactively.
child = pexpect.spawn("gatttool -I")

# Connect to the device.
print("Connecting to:"),
print(DEVICE)

NOF_REMAINING_RETRY = 6

while True:
  try:
    child.sendline("connect {0}".format(DEVICE))
    child.expect("Connection successful", timeout=5)
  except pexpect.TIMEOUT:
    NOF_REMAINING_RETRY = NOF_REMAINING_RETRY-1
    if (NOF_REMAINING_RETRY>0):
      print ("timeout, retry...")
      continue
    else:
      print ("timeout, giving up.")
      break
  else:
    print("Connected!")
    break
  
if NOF_REMAINING_RETRY>0:
  unixTime = int(time.time())
  unixTime += 60*60 # GMT+1
  unixTime += 60*60 # added daylight saving time of one hour
while True:
  # open file
  file = open("data.csv", "a")
  if (os.path.getsize("data.csv")==0):
    file.write("Device\tTime\tTemperature\tHumidity\tBattery Level\n")

  file.write(DEVICE)
  file.write("\t")
  file.write(str(unixTime)) # Unix timestamp in seconds 
  file.write("\t")


  #    Printing MAC Address
  print(f"Mac: {DEVICE}") 

  # Temperature (0x2012)
  child.sendline("char-read-hnd 0x0023")
  child.expect("Characteristic value/descriptor: ", timeout=5)
  child.expect("\r\n", timeout=5)
  #print(child.before),
  temperature = float(hexStrToInt(child.before[0:5]))
  temperature = celsius_to_fahrenheit(temperature)
  print(f"Temperature: {round(temperature)}°F")

  file.write(str(temperature))
  file.write("\t")

  # Humidity (0x2013)
  child.sendline("char-read-hnd 0x0023")
  child.expect("Characteristic value/descriptor: ", timeout=5)
  child.expect("\r\n", timeout=5)
  humidity = float(hexStrToIntHum(child.before[9:14]))
  print(f"Humidity: {round(humidity)}%")

  file.write(str(float(hexStrToIntHum(child.before[9:14]))))
  file.write("\t")

  # Battery Level (0x001f)
  child.sendline("char-read-hnd 0x001f")
  child.expect("Characteristic value/descriptor: ", timeout=5)
  child.expect("\r\n", timeout=5)
  batteryLevel = child.before
  batteryLevel = hexStrToIntBattL(batteryLevel)
  print(f"Battery: {batteryLevel}%")
   
  file.write(str(batteryLevel))
  file.write("\t")

  file.write("\n")
  file.close()
  print("done!")
  time.sleep(10) 
  #sys.exit(0)
else:
  print("FAILED!")
  sys.exit(-1)