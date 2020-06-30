#!/usr/bin/env python3

"""
A python script to get battery level from Samsung Galaxy Buds devices
"""

# License: GPL-3.0
# Author: @ThePBone
# 06/30/2020

from bluetooth import *
import sys
import argparse


def parse_message(data):
    if data[0] != 0xFE:
        print("Invalid SOM")
        exit(2)
    if data[3] != 97:
        # Wrong message id
        return

    battery_left = data[6]
    battery_right = data[7]
    print("{},{}".format(battery_left, battery_right))
    exit()


def parse_message_wear_status(data):
    if data[0] != 0xFE:
        print("Invalid SOM")
        exit(2)
    if data[3] != 97:
        # Wrong message id
        return

    state = data[10]
    if state == 0:
        print("None")
    elif state == 1:
        print("Right")
    elif state == 16:
        print("Left")
    elif state == 17:
        print("Both")
    exit()


def main():
    parser = argparse.ArgumentParser(description='Read battery values of the Samsung Galaxy Buds (2019)')
    parser.add_argument('mac', metavar='MAC-Address', type=str, nargs=1,
                        help='MAC-Address of your Buds')
    parser.add_argument('-w', '--wearing-status', action='store_true', help="Print wearing status instead")
    parser.add_argument('-v', '--verbose', action='store_true', help="Print debug information")
    args = parser.parse_args()

    verbose = args.verbose

    if verbose:
        print("Searching for the RFCOMM interface...")
    uuid = "00001102-0000-1000-8000-00805f9b34fd"
    service_matches = find_service(uuid=uuid, address=str(args.mac[0]))

    if len(service_matches) == 0:
        print("Couldn't find the proprietary RFCOMM service")
        sys.exit(1)

    port = service_matches[0]["port"]
    host = service_matches[0]["host"]

    if verbose:
        print("RFCOMM interface found. Establishing connection...")
    sock = BluetoothSocket(RFCOMM)
    sock.connect((host, port))

    if verbose:
        print("Connected. Waiting for incoming data...")

    try:
        while True:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            if args.wearing_status:
                parse_message_wear_status(data)
            else:
                parse_message(data)
    except IOError:
        pass


if __name__ == "__main__":
    main()