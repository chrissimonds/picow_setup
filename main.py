import rp2
import network
import ubinascii
import machine
import time

# Load WiFi login data
from secrets import secrets

# import socket
import sys


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

wlan = network.WLAN()  # network.WLAN(network.STA_IF)
wlan.active(True)
powerm = hex(wlan.config("pm"))
print("Power Management = " + powerm)
if powerm == "0xa11142":
    print("Power-saving mode ON")
if powerm == "0xa11140":
    print("Power-saving mode OFF")
if powerm == "0xA11C82":
    print("Power-saving mode ON AGRESSIVE")
if powerm == "0x111022":
    print("Power management mode INCREASE PERFORMANCE")
# Below disables powersaving mode
# wlan.config(pm = 0xa11140)
# print('Power-saving mode OFF')

# Default power management mode - Power-saving mode ON
# CYW43_DEFAULT_PM = 0xA11142

# Aggressive power management mode for optimal power usage at the cost of performance
# CYW43_AGGRESSIVE_PM = 0xA11C82

# Performance power management mode where more power is used to increase performance
# CYW43_PERFORMANCE_PM = 0x111022

# See the MAC address in the wireless chip OTP
mac = ubinascii.hexlify(network.WLAN().config("mac"), ":").decode()
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
        ubinascii.hexlify(w[1], ":").decode(),
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

wlan.connect(ssid, pw)

# Wait for connection with 10 second timeout
timeout = 10
while timeout > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    timeout -= 1
    print("Waiting for connection...")
    time.sleep(1)
# Define blinking function for onboard LED to indicate error codes
def blink_onboard_led(num_blinks):
    led = machine.Pin("LED", machine.Pin.OUT)
    for i in range(num_blinks):
        time.sleep(0.2)
        led.off()
        time.sleep(0.2)


# Wlan Status Codes
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
blink_onboard_led(wlan_status)

if wlan_status != 3:
    raise RuntimeError("Wi-Fi connection failed")
    print(str(wlan_status))
else:
    print("Connected to " + str(wlan.config("essid")))
    print("WLAN Status code = " + str(wlan_status))
    status = wlan.ifconfig()
    print("IP = " + status[0])
    print("Subnet = " + status[1])
    print("Gateway = " + status[2])
    print("DNS = " + status[3])
# WLAN Library documentation
# https://docs.micropython.org/en/latest/library/network.WLAN.html
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
# hostname - Deprecated use below instead
print("Hostname = " + str(network.hostname()))
# reconnects - Number of reconnect attempts to make (integer, 0=none, -1=unlimited)


# Read and print the CPU temperature
sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)
reading = sensor_temp.read_u16() * conversion_factor
temperature = 27 - (reading - 0.706) / 0.001721
fahrenheit = temperature * (9 / 5) + 32
print("Temperature = " + str(temperature) + " C  " + str(fahrenheit) + " F")

print("----------")

# Onboard LED Setup
led = machine.Pin("LED", machine.Pin.OUT)
led.off()
led.toggle()

