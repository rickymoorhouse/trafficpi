#!/usr/bin/python
import xml.etree.ElementTree as ET
import urllib2
import argparse
import paho.mqtt.client as paho

# Settings
trafficfeed = "http://hatrafficinfo.dft.gov.uk/feeds/datex/England/JourneyTimeData/content.xml"

# Locations:	10501 - M3 to M275 along the M27 Eastbound
#							10710 - M275 to M3 along the M27 Westbound

# TODO: Add support for combined routes, where the journey is split in the source data
# TODO: Change the defaults to be based on percentage of clear journey time or expected journey time

# Parse Parameters
parser = argparse.ArgumentParser(description='Traffic indicator using LedBorg - Green, Amber or Red based on journey time.')
parser.add_argument('--location',default="10710",help='specify the location code to check default: 10710 (M275 to M3)')
parser.add_argument('--warn',default=1500,help='Specify the minimum journey time to warn on default: 25')
parser.add_argument('--alert',default=1800,help='Specify the minimum journey time to alert on default: 30')
args = parser.parse_args()
if args.location:
	selected_location = args.location

''' Sample XML
<d2LogicalModel modelBaseVersion="1.0">
	<exchange>
	...
	</exchange>
	<payloadPublication xsi:type="ElaboratedDataPublication" lang="en">
	...

		<elaboratedData id="GUID-2234086-10921">
			<sourceInformation>
				<sourceCountry>gb</sourceCountry>
				<sourceIdentification>10921</sourceIdentification>
				<sourceName><value lang="en">NTCC</value></sourceName>
			</sourceInformation>
			<basicDataValue xsi:type="TravelTimeValue">
				<time>2013-02-03T15:15:00Z</time>
				<affectedLocation>
					<locationContainedInGroup xsi:type="LocationByReference">
						<predefinedLocationReference>Section10921</predefinedLocationReference>
					</locationContainedInGroup>
					</affectedLocation>
				<travelTime>13.0</travelTime>
				<freeFlowTravelTime>14.0</freeFlowTravelTime>
				<normallyExpectedTravelTime>14.0</normallyExpectedTravelTime>
			</basicDataValue>
		</elaboratedData>
	</payloadPublication>
</d2LogicalModel>
'''

mqttc = paho.Client()
mqttc.connect("localhost", 1883, 60)


# Get the feed over http
traffic_xml=urllib2.urlopen(trafficfeed)

# Parse the XML
tree = ET.parse(traffic_xml)
root = tree.getroot()

# Dictionary to store the data for the location we're interested in
times = {}

# Loop through the elaboratedData sections
for elab in root[1]:
	# If it has an id and the id contains our location 
	if (elab.attrib.get('id')) and (args.location in elab.attrib.get('id')):
		# Load each item into our dictionary
		for tagdata in elab[1]:
			if "Time" in tagdata.tag:
				times[tagdata.tag.replace('{http://datex2.eu/schema/1_0/1_0}','')] = tagdata.text

#print times

# Calculate delay from normally expected time (seconds) not currently used
delay = float(times.get('travelTime')) - float(times.get('normallyExpectedTravelTime'))
print times.get('normallyExpectedTravelTime')
print times.get('travelTime')
# Current travel time in minutes
travelTime=times.get('travelTime')
if travelTime < 0:
  travelTime = times.get('normallyExpectedTravelTime')
mqttc.publish("traffic", travelTime,qos=0,retain=True)

if travelTime < args.warn:
	# If it's lower than this let's glow green 
	mqttc.publish("light/10", "120" ,qos=0,retain=False)
	mqttc.publish("light/1", "0" ,qos=0,retain=False)
	mqttc.publish("light/2", "0" ,qos=0,retain=False)
elif travelTime < args.alert:
	# Between amber and red - must be amber
	mqttc.publish("light/2", "255" ,qos=0,retain=False)
	mqttc.publish("light/1", "0" ,qos=0,retain=False)
else:
	# Glow red
	mqttc.publish("light/1", "255" ,qos=0,retain=False)
	mqttc.publish("light/10", "0" ,qos=0,retain=False)
	mqttc.publish("light/2", "0" ,qos=0,retain=False)
