import json
import cherrypy
import DftTraffic
import os
import sys
import logging

class JourneyTime(object):
    dft = None
    env = None

    def __init__(self):
        self.dft = DftTraffic.DftTraffic()
        self.dft.logger = logging.getLogger(__name__)
        self.env = json.loads(os.getenv('VCAP_APPLICATION','{}'))

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def route(self,route_id=1):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        return self.dft.journey_times(route_id)

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def sections(self,search):
        output = []
        hostname = ''
        results = self.dft.find_section(search)
        if 'application_uris' in self.env:
            hostname = self.env['application_uris'][0]
        for result in results:
            output.append({'path':"%s/route/%s" % (hostname,result),'description':results[result]})
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
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

logging.basicConfig(stream = sys.stderr, level=logging.WARNING)
cherrypy.quickstart(JourneyTime(), '/', config=conf)
