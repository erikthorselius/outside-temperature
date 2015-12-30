#!/usr/bin/env python
import zmq, json, sys, os
from datetime import datetime, timedelta

socket_address = os.getenv('OUTSIDE_SOCKET')
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.bind(socket_address)
socket.setsockopt_string(zmq.SUBSCRIBE, 'sensor')

if __name__ == '__main__':
    while True:
        topic, message = socket.recv_multipart()
        print("%s %s" % (topic, message))
