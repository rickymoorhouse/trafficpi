import pytest
#import inspect

def test_sections():
    import DftTraffic
    dft = DftTraffic.DftTraffic()
    roads = dft.find_section("M27")
    assert 'M27' in roads['10185']
def test_time():
    import DftTraffic
    dft = DftTraffic.DftTraffic()
    times = dft.journey_times("10185")
    assert 'updatedAt' in times
    assert 'description' in times
    assert 'normallyExpectedTravelTime' in times
