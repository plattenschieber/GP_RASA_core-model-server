from http.server import SimpleHTTPRequestHandler, HTTPServer
import time
import logging
from enum import Enum, unique

semantic_version = "1.0.0"
build_version = 0

#Logging section
logger = logging.getLogger("Http-Server")
logger.setLevel(logging.INFO)
# create file handler
fh = logging.FileHandler('server.log')
fh.setLevel(logging.INFO)
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def _version():
    return semantic_version + "_" + str(build_version)


@unique
class httpStatusCode(Enum):
        OK = 200
        CREATED = 201
        NO_CONTENT = 204
        BAD_REQUEST = 400
        NOT_FOUND = 404
        INTERNAL_SERVER_ERROR = 500


class RequestHandler(SimpleHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(httpStatusCode.OK.value)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        paths = {
            '/models/core': {'status': httpStatusCode.OK.value}
        }
        if self.path in paths:
            self.respond_get(paths[self.path])
        else:
            self.respond_get({'status': httpStatusCode.INTERNAL_SERVER_ERROR.value})

    def respond_get(self, opts):
        content = b''
        if self.headers["If-None-Match"] == _version() \
                or self.headers["If-None-Match"] == "\"" + _version() + "\"":
            self.send_response(httpStatusCode.NO_CONTENT.value)
        else:
            global semantic_version
            self.send_response(opts['status'])
            self.send_header('ETag', _version())
            self.send_header('Content-type', 'application/zip')
            f = open("model_"+semantic_version+".zip", "rb")
            content = f.read()

        self.end_headers()

        self.wfile.write(content)

    def do_POST(self):
        paths = {
            '/models/core': {'status': httpStatusCode.CREATED.value}
        }

        if self.path in paths:
            self.respond_post(paths[self.path])
        else:
            self.respond_post({'status': httpStatusCode.INTERNAL_SERVER_ERROR.value})

    def respond_post(self, opts):
        global build_version
        global semantic_version
        self.send_response(opts['status'])
        if self.headers['version'] is not None:
            semantic_version = str(self.headers['version'])
        content_length = int(self.headers['Content-Length'])
        output_file = open("model_"+semantic_version+".zip", "wb")
        output_file.write(self.rfile.read(content_length))
        output_file.close()
        self.end_headers()
        build_version += 1
        logger.info("Current Version: " + _version())
        self.wfile.write(b'')


def run_server(hostname="0.0.0.0", port=8000):
    server_class = HTTPServer
    httpd = server_class((hostname, port), RequestHandler)
    logger.info("Start Server for Host: " + str(hostname) + " Port: " + str(port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logger.info("Stop Server for Host: " + str(hostname) + " Port: " + str(port))

run_server()