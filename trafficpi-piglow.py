#!/usr/bin/python
import xml.etree.ElementTree as ET
import urllib2
import argparse
from PyGlow import PyGlow

def glow(colour):
	PyGlow().led(1,int(colour[0])*100)
	PyGlow().led(4,int(colour[1])*100)
	PyGlow().led(5,int(colour[2])*100)


# Settings
trafficfeed = "http://hatrafficinfo.dft.gov.uk/feeds/datex/England/JourneyTimeData/content.xml"

# Locations:	10501 - M3 to M275 along the M27 Eastbound
#							10710 - M275 to M3 along the M27 Westbound

# TODO: Add support for combined routes, where the journey is split in the source data
# TODO: Change the defaults to be based on percentage of clear journey time or expected journey time

# Parse Parameters
parser = argparse.ArgumentParser(description='Traffic indicator using LedBorg - Green, Amber or Red based on journey time.')
parser.add_argument('--location',default="10710",help='specify the location code to check default: 10710 (M275 to M3)')
parser.add_argument('--warn',default=25,help='Specify the minimum journey time to warn on default: 25')
parser.add_argument('--alert',default=30,help='Specify the minimum journey time to alert on default: 30')
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

# Current travel time in minutes
travelTime=float(times.get('travelTime')) / 60



if travelTime < args.warn:
	# If it's lower than this let's glow green 
	glow("020")
elif travelTime < args.alert:
	# Between amber and red - must be amber
	glow("120")
else:
	# Glow red
	glow("200")
