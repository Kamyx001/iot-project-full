#!/usr/bin/env python3

from config import *  # pylint: disable=unused-wildcard-import
import RPi.GPIO as GPIO
import time
import threading

alarmOn = False
_thread_lock = threading.Lock()

def buzzer(state):
  GPIO.output(buzzerPin, not state)  # pylint: disable=no-member
  
def _alarm_loop():
  global alarmOn
  try:
    while alarmOn:
      buzzer(True)
      time.sleep(1)
      if not alarmOn:
        break
      buzzer(False)
      time.sleep(1)
  finally:
    buzzer(False)

def turnOnAlarm():
  global alarmOn, _alarm_thread
  with _thread_lock:
    if alarmOn:
      print("Alarm already ON")
      return
    alarmOn = True
    _alarm_thread = threading.Thread(target=_alarm_loop, daemon=True)
    _alarm_thread.start()

def turnOffAlarm():
  global alarmOn
  alarmOn = False