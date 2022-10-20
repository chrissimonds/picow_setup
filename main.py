import rp2
import network
import ubinascii
import machine
# import urequests as requests
import time
# import utime

# Load WiFi login data below
from secrets import secrets
import socket
import sys

print('Welcome, here is the system info:')
print (str(sys.implementation))
print()

# Set country to avoid possible errors
rp2.country('US')
print ('US WiFi country')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print ('Power-saving mode ON')
# Below disables powersaving mode
# wlan.config(pm = 0xa11140)
# print ('Power-saving mode OFF')

# See the MAC address in the wireless chip OTP
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('MAC = ' + mac)
print('WLAN is connected = ' + str(wlan.isconnected()))
print ('WLAN Scan: ')
print(wlan.scan())


# Load WiFi login data from different file for safety reasons
ssid = secrets['ssid']
pw = secrets['pw']

wlan.connect(ssid, pw)

# Wait for connection with 10 second timeout
timeout = 10
while timeout > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    timeout -= 1
    print('Waiting for connection...')
    time.sleep(1)

# Define blinking function for onboard LED to indicate error codes    
def blink_onboard_led(num_blinks):
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_blinks):
        time.sleep(.2)
        led.off()
        time.sleep(.2)

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
    raise RuntimeError('Wi-Fi connection failed')
    print(str(wlan_status))
else:
    print('Connected')
    print('WLAN Status code = ' + str(wlan_status))
    status = wlan.ifconfig()
    print('IP = ' + status[0])
    print('Subnet = ' + status[1])
    print('Gateway = ' + status[2])
    print('DNS = ' + status[3])
    

# WLAN Library documentation
# https://docs.micropython.org/en/latest/library/network.WLAN.html
print('SSID '+ str(wlan.config('essid')))
print('WLAN Channel '+ str(wlan.config('channel')))
print('WLAN Security '+ str(wlan.config('security')))
print('TXPower ' + str(wlan.config('txpower')))

# Other parameters appear not fully suported by Pico W
# hidden - Whether SSID is hidden (boolean))
# key - Access key (string)
# hostname - The hostname that will be sent to DHCP (STA interfaces) and mDNS (if supported, both STA and AP)
# reconnects - Number of reconnect attempts to make (integer, 0=none, -1=unlimited)


# Read and print the CPU temperature 
sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)
reading = sensor_temp.read_u16() * conversion_factor
temperature = 27 - (reading - 0.706)/0.001721
fahrenheit= temperature * (9 / 5) + 32
print('Temperature = ' + str(temperature) + ' C  ' + str(fahrenheit) + ' F')

# Onboard LED Setup
led = machine.Pin("LED", machine.Pin.OUT)
led.off()
led.toggle()
