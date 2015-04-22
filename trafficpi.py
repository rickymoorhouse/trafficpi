#!/usr/bin/python
import DftTraffic
import argparse

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


# Locations:    10501 - M3 to M275 along the M27 Eastbound
#    						10710 - M275 to M3 along the M27 Westbound

# TODO: Add support for combined routes, where the journey is split in the source data
# TODO: Change the defaults to be based on percentage of clear journey time or expected journey time

# Parse Parameters
parser = argparse.ArgumentParser(description='Traffic indicator using LedBorg - Green, Amber or Red based on journey time.')
parser.add_argument('--location', default="10710", help='specify the location code to check default: 10710 (M275 to M3)')
parser.add_argument('--warn', default=1500, help='Specify the minimum journey time to warn on default: 25')
parser.add_argument('--alert', default=1800, help='Specify the minimum journey time to alert on default: 30')
parser.add_argument('--notify', default='console', help='How to notify - mqtt,  piglow or console')

args = parser.parse_args()
if args.location:
    selected_location = args.location




# Get the feed over http
times = DftTraffic.journey_times(args.location)


# Current travel time in minutes
travelTime = times['current']
if travelTime < 0:
    travelTime = times['expected']

if travelTime < args.warn:
    # If it's lower than this let's glow green
    colour = "00ff00" 
elif travelTime < args.alert:
    # Between amber and red - must be amber
    colour = "996600"
else:
    # Glow red
    colour = "ff0000"

if args.notify == 'mqtt':
    import paho.mqtt.client as paho
    # Connect to mqtt server
    mqttc = paho.Client()
    mqttc.connect("localhost", 1883, 60)
    mqttc.publish("traffic/%s" % args.location, travelTime, qos=0, retain=True)
    mqttc.publish("traffic", travelTime, qos=0, retain=True)
    mqttc.publish("light/rgb", colour, qos=0, retain=True)
elif args.notify == 'piglow':
    from PyGlow import PyGlow
    (r, g, b) = hex_to_rgb(colour)
    PyGlow().led(1, r)
    PyGlow().led(4, g)
    PyGlow().led(5, b)
else:
    print "expected:  %s" % times['expected']
    print "current:   %s" % times['current']
    print "delay:     %f" % times['delay']
    print "colour:    %s" % colour

