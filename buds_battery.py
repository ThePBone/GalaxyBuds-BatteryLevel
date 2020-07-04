#!/usr/bin/env python3

"""
A python script to get battery level from Samsung Galaxy Buds(+) devices
"""

# License: MIT
# Author: @ThePBone
# 06/30/2020

import bluetooth
import sys
import argparse


def parse_message(data, isplus):
    if data[0] != (0xFD if isplus else 0xFE):
        print("Invalid SOM")
        exit(2)
    if data[3] != 97:
        # Wrong message id
        return

    if isplus:
        print("{},{},{}".format(data[6], data[7], data[11]))
    else:
        print("{},{}".format(data[6], data[7]))
    exit()


def parse_message_wear_status(data, isplus):
    if data[0] != (0xFD if isplus else 0xFE):
        print("Invalid SOM")
        exit(2)
    if data[3] != 97:
        # Wrong message id
        return

    state = data[10]
    if isplus:
        left = id_to_placement((state & 240) >> 4)
        right = id_to_placement(state & 15)
        print("{},{}".format(left, right))
    else:
        if state == 0:
            print("None")
        elif state == 1:
            print("Right")
        elif state == 16:
            print("Left")
        elif state == 17:
            print("Both")
    exit()


def id_to_placement(id):
    if id == 0:
        return "Disconnected"
    elif id == 1:
        return "Wearing"
    elif id == 2:
        return "Idle"
    elif id == 3:
        return "InCase"
    elif id == 4:
        return "InClosedCase"


def main():
    parser = argparse.ArgumentParser(description='Read battery values of the Samsung Galaxy Buds or Buds+ '
                                                 '[Left, Right, Case (Buds+)]')
    parser.add_argument('mac', metavar='mac-address', type=str, nargs=1,
                        help='MAC-Address of your Buds')
    parser.add_argument('-w', '--wearing-status', action='store_true', help="Print wearing status instead")
    parser.add_argument('-v', '--verbose', action='store_true', help="Print debug information")
    args = parser.parse_args()

    verbose = args.verbose

    if verbose:
        print("Checking device model...")
    isplus = "Buds+" in str(bluetooth.lookup_name(args.mac[0]))
    if verbose:
        print(str(bluetooth.lookup_name(args.mac[0])))

    if verbose:
        print("Searching for the RFCOMM interface...")
    uuid = ("00001101-0000-1000-8000-00805F9B34FB" if isplus else "00001102-0000-1000-8000-00805f9b34fd")
    service_matches = bluetooth.find_service(uuid=uuid, address=str(args.mac[0]))

    if len(service_matches) == 0:
        print("Couldn't find the proprietary RFCOMM service")
        sys.exit(1)

    port = service_matches[0]["port"]
    host = service_matches[0]["host"]

    if verbose:
        print("RFCOMM interface found. Establishing connection...")
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((host, port))

    if verbose:
        print("Connected. Waiting for incoming data...")

    try:
        while True:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            if args.wearing_status:
                parse_message_wear_status(data, isplus)
            else:
                parse_message(data, isplus)
    except IOError:
        pass


if __name__ == "__main__":
    main()
