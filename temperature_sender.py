#!/usr/bin/env python
import zmq, json, sys, sched, time, signal, os, logging, urllib.request
from datetime import datetime, timedelta

api_url = os.getenv('OUTSIDE_API_URL')
report_time = float(os.getenv('OUTSIDE_REPORT_TIME', 3600))
socket_address = os.getenv('OUTSIDE_SOCKET').strip()
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect(socket_address)
logging.info('Connected to address %s',socket_address)
s = sched.scheduler(time.time, time.sleep)

def signal_handler(signal, frame):
  print('You pressed Ctrl+C! Shutting down')
  socket.close(linger=1)
  sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def send(sensor):
  value = sensor.get_value()
  logging.debug('Send value: %s to server',value)
  socket.send_json(value) 

def report_temperature_job(sc, sensor): 
  send(sensor)
  sc.enter(report_time, 1, report_temperature_job, (sc,sensor))

class TempSensor:
  def __init__(self, name):
      self.dict = {}
      self.dict['name'] = name
      self.dict['type'] = 'external_api'
      self.dict['sensor'] = 'temperature'

  def __is_within_hour(self, item): 
    date = datetime.strptime(item['validTime'], "%Y-%m-%dT%H:%M:%SZ")
    return datetime.now() < date < (datetime.now() + timedelta(hours=1))

  def __get_data_from_api(self):
    response = urllib.request.urlopen(api_url).read()
    return json.loads(response.decode('utf-8'))

  def __get_nearest_item(self, forcast):
    return next(item['t'] for item in forcast if self.__is_within_hour(item))

  def get_value(self):
    try:  
      forcast = self.__get_data_from_api()['timeseries']
      self.dict['value'] = float(self.__get_nearest_item(forcast))
      return self.dict
    except IOError:
      return {'error': 'Could not connect to API', 'name': self.dict['name']}

s.enter(report_time, 1, report_temperature_job, (s,TempSensor('Outside')))
logging.info('Add report jobb to scheduler, will run every %s second', report_time)
s.run()
