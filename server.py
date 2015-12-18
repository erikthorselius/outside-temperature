#!/usr/bin/env python
import zmq, json, sys, os 
from datetime import datetime, timedelta

socket_address = os.getenv('OUTSIDE_SOCKET')
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind(socket_address)

while True: 
  result = socket.recv_json()
  print(result)

