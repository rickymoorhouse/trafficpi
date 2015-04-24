#!/usr/bin/python
"""
Module to parse the traffic information provided by the Department for Transport

Currently supported:
 - Journey time
"""
import xml.etree.ElementTree as ET
import urllib2

# Settings
TRAFFIC_URL = "http://hatrafficinfo.dft.gov.uk/feeds/datex/England/JourneyTimeData/content.xml"

def journey_times(route_id):
    """Return the journey time for route (identified by route_id) in seconds"""
    # Get the feed over http
    traffic_xml = urllib2.urlopen(TRAFFIC_URL)
 
    # Parse the XML
    tree = ET.parse(traffic_xml)
    root = tree.getroot()

    # Dictionary to store the data for the location we're interested in
    times = {}

    # Loop through the elaboratedData sections
    for elab in root[1]:
        # If it has an id and the id contains our route_id
        if (elab.attrib.get('id')) and (route_id in elab.attrib.get('id')):
            # Load each item into our dictionary
            for tagdata in elab[1]:
                if "Time" in tagdata.tag:
                    times[tagdata.tag.replace('{http://datex2.eu/schema/1_0/1_0}', '')] = tagdata.text
                    # Calculate delay from normally expected time (seconds)
                    if times.get('travelTime') < 0:
                        delay = 0
                    else:
                        try:
                            delay = float(times.get('travelTime')) - float(times.get('freeFlowTravelTime'))
                        except:
                            print times
    return {
        "expected":times.get('normallyExpectedTravelTime'),
        "current":times.get('travelTime'),
        "delay":delay
    }
