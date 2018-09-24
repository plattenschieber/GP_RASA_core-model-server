from http.server import SimpleHTTPRequestHandler, HTTPServer
import time
import logging

logging.basicConfig()
logger = logging.getLogger()

class RequestHandler(SimpleHTTPRequestHandler):
    def respond(self, opts):
        response = self.handle_http(opts['status'], self.path)
        self.wfile.write(response)

    def handle_http(self, status_code, path):
        content = ''
        version = "1.0.0"
        if self.headers["If-None-Match"] == version or self.headers["If-None-Match"] == "\""+version+"\"":
            logger.info("No Changes detected")
            self.send_response(204)
        else:
            logger.info("respond with new model and version: " + version)
            self.send_response(status_code)
            self.send_header('ETag', version)
            self.send_header('Content-type', 'application/zip')

            f = open("model.zip", "rb")
            content = f.read()
        self.end_headers()

        return bytes(content)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        paths = {
            '/models': {'status': 200}
        }
        logger.info("got request for " + self.path)
        if self.path in paths:
            self.respond(paths[self.path])
        else:
            self.respond({'status': 500})



def run_server(hostname="0.0.0.0", port=8000):
    server_class = HTTPServer
    httpd = server_class((hostname, port), RequestHandler)
    logger.info(time.asctime(), 'Server Starts - %s:%s' % (hostname, port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logger.info(time.asctime(), 'Server Stops - %s:%s' % (hostname, port))

run_server()