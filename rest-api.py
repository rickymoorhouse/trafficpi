import json
import cherrypy
import DftTraffic
import os

class JourneyTime(object):
    dft = None

    def __init__(self):
        self.dft = DftTraffic.DftTraffic()

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def route(self,route_id=1):
#	try:	
	return self.dft.journey_times(route_id)
#	except:
#		raise cherrypy.HTTPError(404,"Route not found")
    @cherrypy.tools.json_out()
    @cherrypy.expose
    def sections(self,search):
        output = {}
        results = self.dft.find_section(search)
        for result in results:
            output[results[result]] = "/route/%s" % result
        return output

current_dir = os.path.dirname(os.path.abspath(__file__))
conf = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.getenv('VCAP_APP_PORT',8004)),
    },
    '/': {
        'tools.staticdir.on': True,
        'tools.staticdir.index': 'index.html',
        'tools.staticdir.dir': os.path.join(current_dir, 'docs'),
        'tools.staticdir.content_types': {
            'yaml': 'application/x-yaml'
        }
    }
}
cherrypy.quickstart(JourneyTime(), '/', config=conf)
