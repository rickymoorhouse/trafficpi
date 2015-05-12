#!/usr/bin/python
"""
Module to parse the traffic information provided by the Department for Transport

Currently supported:
 - Journey time
"""
import xml.etree.ElementTree as ET
import urllib2
import time
import logging

class DftTraffic(object):
    # Settings
    TRAFFIC_URL = "http://hatrafficinfo.dft.gov.uk/feeds/datex/England/JourneyTimeData/content.xml"
    xml_data = ''
    journeys = {}
    updated_at = 0
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.keep_data_updated()

    def keep_data_updated(self):
        if time.time() - self.updated_at > 600:
            self.xml_data = urllib2.urlopen(self.TRAFFIC_URL)
            self.updated_at = time.time()
            

    def journey_times(self, route_id):
        """Return the journey time for route (identified by route_id) in seconds"""
        times = { "updatedAt": 0 }
        if route_id in self.journeys:
            times = self.journeys[route_id]
        if time.time() - times['updatedAt'] > 600:
            # Get the feed over http
            self.keep_data_updated()

            # Parse the XML
            tree = ET.parse(self.xml_data)
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
                                    times['delay'] = float(times.get('travelTime')) - float(times.get('freeFlowTravelTime'))
                                except TypeError:
                                    self.logger.warn("Unexpected data back from Web service")
                                    self.logger.warn(times)
                    times['updatedAt'] = self.updated_at
                    self.journeys[route_id] = times
            print self.journeys
        times['updatedAt'] = time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(times['updatedAt']))
        return times
#{
#            "expected":times.get('normallyExpectedTravelTime'),
#            "current":times.get('travelTime'),
#            "delay":delay
#        }
