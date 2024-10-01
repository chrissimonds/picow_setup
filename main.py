import sys
import rp2
import machine
import network
import time
import binascii

# Load WiFi login data
from secrets import secrets

# import socket

print("Welcome, here is the system info:")
print(str(sys.implementation))
print("----------")

# This was built with
# MicroPython v1.22.2 on 2024-02-22; Raspberry Pi Pico W with RP2040

# Firmware: micropython-firmware-pico-w-130623 - Bluetooth version
# System info:
# (name='micropython', version=(1, 22, 2, ''), _machine=
# 'Raspberry Pi Pico W with RP2040', _mpy=4614)

# Set country to avoid possible errors
rp2.country("US")
print("WiFi country = " + rp2.country())

# WLAN Library documentation
# https://docs.micropython.org/en/latest/library/network.WLAN.html

wlan = network.WLAN()  # network.WLAN(network.STA_IF)
wlan.active(True)

# See the driver for more details:
# https://github.com/georgerobotics/cyw43-driver/
# In partifular see the variable headers in cyw43.h

# The main difference in Power management modes is this variable:
# pm2_sleep_ret_ms
# The maximum time to wait before going back to sleep for CYW43_PM2_POWERSAVE_MODE mode
# Value measured in milliseconds and must be between 10 and 2000ms and divisible by 10


# Below sets to DEFAULT power savings
# This is not needed as the driver sets this value by default
# wlan.config(pm = 0xa11142)
# print("Power-saving mode ON DEFAULT")
# This set pm2_sleep_ret_ms to 200ms
# Saves power when there is no wifi activity

# Below sets to AGRESSIVE power savings
# wlan.config(pm = 0xa11c82)
# print("Power-saving mode ON AGRESSIVE")
# This set pm2_sleep_ret_ms to 2000ms
# Aggressive power management mode for optimal power usage at the cost of performance.

# Below sets to PERFORMANCE power savings
# wlan.config(pm = 0x111022)
# print("Power-saving mode ON PERFORMANCE")
# This set pm2_sleep_ret_ms to 20ms
# This also changes the variable li_assoc from 10 to 1ms
# which is the Wake interval sent to the access point
# Performance power management mode where more power is used to increase performance

# Below disables powersaving mode
# wlan.config(pm = 0xa11140)
# print('Power-saving mode OFF')
# The last digit sets the pm_mode so in this case 0
# The difference between the default 0xa11142 and 0xa11140 is that it changes
# PM mode from "Power saving with High throughput (preferred)" to "No power saving"
# See Driver documentation for more details:
# https://github.com/georgerobotics/cyw43-driver/blob/main/src/cyw43.h
#
#  * pm_mode                  | Meaning
#  * -------------------------|--------
#  * CYW43_NO_POWERSAVE_MODE  | No power saving
#  * CYW43_PM1_POWERSAVE_MODE | Aggressive power saving which reduces wifi throughput
#  * CYW43_PM2_POWERSAVE_MODE | Power saving with High throughput (preferred).
#      Saves power when there is no wifi activity for some time.


powerm = hex(wlan.config("pm"))
print("Power Management = " + powerm)
if powerm == "0xa11142":
    print("Power-saving mode ON DEFAULT")
if powerm == "0xa11140":
    print("Power-saving mode OFF")
if powerm == "0xa11c82":
    print("Power-saving mode ON AGRESSIVE")
if powerm == "0x111022":
    print("Power management mode ON PERFORMANCE")


# See Driver documentation for more details:
# https://github.com/georgerobotics/cyw43-driver/blob/main/src/cyw43.h

# Default power management mode - Power-saving mode ON
# CYW43_DEFAULT_PM = 0xa11142

# Aggressive power management mode for optimal power usage at the cost of performance
# CYW43_AGGRESSIVE_PM = 0xa11c82

# Performance power management mode where more power is used to increase performance
# CYW43_PERFORMANCE_PM = 0x111022

# Essentially the difference in PM settings is sleep return timer: pm2_sleep_ret
# DEFAULT is 200ms with AGGRESSIVE being 2000ms and PERFORMANCE 20ms
# Recommendation is DEFAULT


# See the MAC address in the wireless chip OTP
mac = binascii.hexlify(network.WLAN().config("mac"), ":").decode()
print("MAC = " + mac)
print("Is WLAN connected = " + str(wlan.isconnected()))

print("----------")

print("WLAN Scan: ")
# print(wlan.scan())
print("#  |  SSID  |  BSSID  |  Channel  |  RSSI  |  auth_mode  |  access point count ")

# Currently last 2 values do not match documentation
# in https://docs.micropython.org/en/latest/library/network.WLAN.html
# Security/auth_mode value has a bug see:
# https://github.com/micropython/micropython/issues/10017
# Also see: https://github.com/micropython/micropython/issues/6430

# This issue is actually explained here:
# https://forums.raspberrypi.com/viewtopic.php?t=348563
# The last field is the count of networks using the same BSSID


accessPoints = wlan.scan()
# list with tuples (ssid, bssid, channel, RSSI, auth_mode,
# count of times access point name was seen)
# accessPoints.sort(key=lambda x:x[3],reverse=True) # sorted on RSSI (3)
for i, w in enumerate(accessPoints):
    print(
        i + 1,
        " | ",
        w[0].decode(),
        " | ",
        binascii.hexlify(w[1], ":").decode(),
        " | ",
        w[2],
        " | ",
        w[3],
        " | ",
        w[4],
        " | ",
        w[5],
    )
print("----------")

# Load WiFi login info from different secrets.py file for safety reasons
ssid = secrets["ssid"]
pw = secrets["pw"]

# To disconnect from the currently connected wireless network
# wlan.disconnect()

wlan.connect(ssid, pw)

# Wait for connection with 10 second timeout
timeout = 10
while timeout > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        print("Connection status")
        print(str(wlan.status()))
        break
    timeout -= 1
    print("Waiting for connection...")
    print(str(wlan.status()))
    time.sleep(1)


# WLAN Status Codes
# Handle connection error
# Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth
wlan_status = wlan.status()

# print(str(wlan_status))
if wlan_status == 0:
    print("WLAN status Link Down")
if wlan_status == 1:
    print("WLAN status Link Join")
if wlan_status == 2:
    print("WLAN status Link NoIp")
if wlan_status == 3:
    print("WLAN status Link Up")
if wlan_status == -1:
    print("WLAN status Link Fail")
if wlan_status == -2:
    print("WLAN status Link NoNet")
if wlan_status == -3:
    print("Link BadAuth")


# If no connection then exit with error 
if wlan_status != 3:
    print(str(wlan_status))
    raise RuntimeError("Wi-Fi connection failed")
else:
    print("WLAN Status code = " + str(wlan_status))
    print("Connected to " + str(wlan.config("essid")))
    status = wlan.ifconfig()
    print("IP = " + status[0])
    print("Subnet = " + status[1])
    print("Gateway = " + status[2])
    print("DNS = " + status[3])


# Display valid WLAN config parameters
print("MAC = " + str(binascii.hexlify(wlan.config("mac"), ":").decode()))
print("SSID " + str(wlan.config("essid")))
print("WLAN Channel " + str(wlan.config("channel")))
print("WLAN Security " + str(wlan.config("security")))
print("TXPower " + str(wlan.config("txpower")))
print("Power Management = " + hex(wlan.config("pm")))

# Other parameters appear not fully suported yet by Pico W
# hidden - Whether SSID is hidden (boolean))
# print('Hidden ' + str(wlan.config('hidden')))
# key - Access key (string)
# print('Key ' + str(wlan.config('key')))
# reconnects - Number of reconnect attempts to make (integer, 0=none, -1=unlimited)
# print (wlan.config('reconnects'))

# print (wlan.config('hostname'))
# The above line works but may be removed in future updates
# hostname - Deprecated for wlan.config so use below instead
print("Hostname = " + str(network.hostname()))

# Read and print the CPU temperature
sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)
reading = sensor_temp.read_u16() * conversion_factor
temperature = 27 - (reading - 0.706) / 0.001721
fahrenheit = temperature * (9 / 5) + 32
print("Temperature = " + str(temperature) + " C  " + str(fahrenheit) + " F")
print ('Time is : ',time.localtime())
print("----------")

# Onboard LED Setup
led = machine.Pin("LED", machine.Pin.OUT)
# led.on()
# led.off()
led.toggle()
