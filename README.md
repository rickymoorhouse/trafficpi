[![Stories in Ready](https://badge.waffle.io/rickymoorhouse/trafficpi.png?label=ready&title=Ready)](https://waffle.io/rickymoorhouse/trafficpi)[ ![Codeship Status for rickymoorhouse/trafficpi](https://codeship.com/projects/07b50fe0-6dc8-0133-e3ec-666194911eaf/status?branch=master)](https://codeship.com/projects/115728)
# trafficpi


Script to use the Raspberry Pi &amp; LedBorg to show traffic conditions

Run as follows:

	python trafficpi.pi --location=10501

The LedBorg will then display a colour based on the traffic conditions at that time.


## Example location codes
 - 10501 - M3 to M275 along the M27 Eastbound
 - 10710 - M275 to M3 along the M27 Westbound

 TODO: Add support for combined routes, where the journey is split in the source data
 TODO: Change the defaults to be based on percentage of clear journey time or expected journey time
