#!/usr/bin/env python2

from time import sleep
from os import path as op
import sys
from subprocess import check_call, check_output
from glob import glob


touchscreen_names = ['ELAN2557:00 04F3:2557', "pen"]
touchpad_names = ['touchpad', 'trackpoint']
disable_touchpads = True


def bdopen(fname):
    return open(op.join(basedir, fname))


def read(fname):
    return bdopen(fname).read()


for basedir in glob('/sys/bus/iio/devices/iio:device*'):
    if 'accel' in read('name'):
        break
else:
    sys.stderr.write("Can't find an accellerator device!\n")
    sys.exit(1)

touchscreen_names = map(lambda x: x.lower(), touchscreen_names)


def get_devices():
    devices = check_output(['xinput', '--list', '--name-only']).splitlines()
    devices_id = check_output(['xinput', '--list', '--id-only']).splitlines()

    touchscreens = [idx for i, idx in zip(devices, devices_id) 
                    if any(j.lower() in i.lower() for j in touchscreen_names) or
                    any(idx == j for j in touchscreen_names)]


    touchpads = [idx for i, idx in zip(devices, devices_id) 
                    if any(j.lower() in i.lower() for j in touchpad_names) or
                    any(idx == j for j in touchpad_names)]
    return devices, touchscreens, touchpads


devices, touchscreens, touchpads = get_devices()

scale = float(read('in_accel_scale'))

g = 7.0  # (m^2 / s) sensibility, gravity trigger

STATES = [
    {'rot': 'normal', 'coord': '1 0 0 0 1 0 0 0 1', 'touchpad': 'enable',
     'check': lambda x, y: y <= -g},
    {'rot': 'inverted', 'coord': '-1 0 1 0 -1 1 0 0 1', 'touchpad': 'disable',
     'check': lambda x, y: y >= g},
    {'rot': 'left', 'coord': '0 -1 1 1 0 0 0 0 1', 'touchpad': 'disable',
     'check': lambda x, y: x >= g},
    {'rot': 'right', 'coord': '0 1 0 -1 0 1 0 0 1', 'touchpad': 'disable',
     'check': lambda x, y: x <= -g},
]



def new_device(devices):
    cur_devices = check_output(['xinput', '--list', '--name-only']).splitlines()
    if len(cur_devices) > len(devices):
        return True
    return False


def rotate(state):
    s = STATES[state]
    check_call(['xrandr', '-o', s['rot']])
    for dev in touchscreens + touchpads:
        try:
            check_call([
                'xinput', 'set-prop', dev,
                'Coordinate Transformation Matrix',
            ] + s['coord'].split())
        except:
            pass
    if disable_touchpads:
        for dev in touchpads:
            print(dev)
            check_call(['xinput', s['touchpad'], dev])


def read_accel(fp):
    fp.seek(0)
    return float(fp.read()) * scale


if __name__ == '__main__':

    accel_x = bdopen('in_accel_x_raw')
    accel_y = bdopen('in_accel_y_raw')
    n_check_new_device = 10
    k_check_device = 0

    current_state = None

    while True:
        x = read_accel(accel_x)
        y = read_accel(accel_y)
        if not (k_check_device % n_check_new_device) and new_device(devices):
            devices, touchscreens, touchpads = get_devices()

        for i in range(4):
            if i == current_state:
                continue
            if STATES[i]['check'](x, y):
                current_state = i
                rotate(i)
                break
        sleep(1)
        k_chek_device = (k_check_device + 1) % n_check_new_device
