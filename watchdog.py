#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import datetime
import RPi.GPIO as GPIO
import time
import socket, struct

def get_default_gateway():
    """Read the default gateway directly from /proc."""
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue

            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


Relay_Ch1 = 26
address_home = str(get_default_gateway())
address_isp = '8.8.8.8'
ping_timeout = 5
attempts = 4
log_file = '/home/pi/log/ping_test.log'
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Relay_Ch1,GPIO.OUT)

failed_attempts_home = 0
failed_attempts_isp = 0

for i in range(0, attempts):
    result = os.system('/bin/ping -c 1 -w %i %s > /dev/null 2>&1' % (ping_timeout, address_home))
    if result != 0:
        failed_attempts_home += 1

if failed_attempts_home == 0:
        for i in range(0, attempts):
                result = os.system('/bin/ping -c 1 -w %i %s > /dev/null 2>&1' % (ping_timeout, address_isp))
                if result != 0:
                        failed_attempts_isp += 1

        if failed_attempts_isp == attempts:
                with open(log_file, 'a') as logfile:
                        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                        logfile.write("%s 'ping %s' failed attempts: %i. Rebooting GPON terminal...\n" % (now, address_isp, failed_attempts_isp))
                #Control the Channel 1
                GPIO.output(Relay_Ch1,GPIO.LOW)
                time.sleep(0.5)
                GPIO.output(Relay_Ch1,GPIO.HIGH)

elif failed_attempts_home == attempts:
        with open(log_file, 'a') as logfile:
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                logfile.write("%s 'ping %s' failed attempts: %i. Wait router\n" % (now, address_home, failed_attempts_home))
GPIO.cleanup()

