#!/usr/bin/python
"""
Module to parse the traffic information provided by the Department for Transport

Currently supported:
 - Journey time
"""
import xml.etree.ElementTree as ET
import requests
import time
import logging

class DftTraffic(object):
    # Settings
    TRAFFIC_URL = "http://hatrafficinfo.dft.gov.uk/feeds/datex/England/JourneyTimeData/content.xml"
    SECTION_URL = "http://hatrafficinfo.dft.gov.uk/feeds/datex/England/PredefinedLocationJourneyTimeSections/content.xml"
    xml_data = ''
    journeys = {}
    locations = {}
    updated_at = 0
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.keep_data_updated()
        self.section_data = requests.get(self.SECTION_URL).text
        self.load_sections()

    def keep_data_updated(self):
        self.logger.info("keep_data_updated entered - last update: %d" % self.updated_at)
        if time.time() - self.updated_at > 600:
            self.logger.info("retrieving data")
            self.xml_data = requests.get(self.TRAFFIC_URL).text
            self.updated_at = time.time()

    def load_sections(self):
        """Return the section details for the search provided"""
        try:
            root = ET.fromstring(self.section_data)
            locations = root.find('{http://datex2.eu/schema/1_0/1_0}payloadPublication').find('{http://datex2.eu/schema/1_0/1_0}predefinedLocationSet')
        except:
            locations = []
        for child in locations:
            try:
                section_id=child.attrib['id'].replace('Section','')
                self.locations[section_id] = child[0][0].text.replace('Journey Time Section for ','')
            except Exception as e:
                self.logger.exception(e)

    def find_section(self,search):
        return_list = {}
        for loc in self.locations:
            if search in self.locations[loc]:
                return_list[loc] = self.locations[loc]
        return return_list

    def journey_times(self, route_id):
        """Return the journey time for route (identified by route_id) in seconds"""
        times = { "updatedAt": 0 }

        if route_id in self.journeys:
            times = self.journeys[route_id]

        if time.time() - times['updatedAt'] > 600:
            # Get the feed over http
            self.keep_data_updated()

            # Parse the XML
            root = ET.fromstring(self.xml_data)

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
#        times['updatedAtStr'] = time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(times['updatedAt']))
        if route_id in self.locations:
            times['description'] = self.locations[route_id]
        return times
#{
#            "expected":times.get('normallyExpectedTravelTime'),
#            "current":times.get('travelTime'),
#            "delay":delay
#        }
if __name__ == "__main__":
    dft = DftTraffic()
    dft.find_section("M27")

