from http.server import SimpleHTTPRequestHandler, HTTPServer
import logging
from enum import Enum, unique

#Set the inital version on server start up
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


def _get_version():
    """ Return the current version"""
    return semantic_version + "_" + str(build_version)


@unique
class HttpStatusCode(Enum):
    """ Enum for different status codes. Each code must be unique"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500


class RequestHandler(SimpleHTTPRequestHandler):
    """ Request handler based on SimpleHTTPRequestHandler.
    Takes all requests and do actions based on the requests
    """
    def do_HEAD(self):
        """ Send the header information with status code 200"""
        # Set response
        self.send_response(HttpStatusCode.OK.value)

        # Set headers
        self.send_header('Content-type', 'text/html')

        # Finish response
        self.end_headers()

    def do_GET(self):
        """ Handle all get requests.
        Allowed path is 'server:port/models/core' in all other cases a internal server error will be returned
        """
        # List of possible path which allow get
        paths = {
            '/models/core': {'status': HttpStatusCode.OK.value}
        }

        # Check if path exists and throw internal server error if not
        if self.path in paths:
            # Call response function
            self.respond_get(paths[self.path])
        else:
            # Call response function
            self.respond_get({'status': HttpStatusCode.INTERNAL_SERVER_ERROR.value})

    def respond_get(self, opts):
        """ Handle a given get request.

        It takes a request with an If-None-Match header
        and compare it with the current version to check if the requesting server is up to date.
        If the model is up to date a 204 No Content will be returned, if not the current model will be send to the server

        Parameters:
        ----------
        opts:   dict
                dictionary with information like status code
        """
        content = b''
        # Check if request hash matches current version
        # If it does a 204 wil be returned if not a new model will be returned as zip
        if self.headers["If-None-Match"] == _get_version() \
                or self.headers["If-None-Match"] == "\"" + _get_version() + "\"":
            self.send_response(HttpStatusCode.NO_CONTENT.value)
        else:
            global semantic_version
            self.send_response(opts['status'])
            # Send new ETag for next check
            self.send_header('ETag', _get_version())
            self.send_header('Content-type', 'application/zip')
            # Read model of current version
            f = open("model_"+semantic_version+".zip", "rb")
            content = f.read()

        self.end_headers()

        self.wfile.write(content)

    def do_POST(self):
        """ Handle all post requests.
        Allowed path is 'server:port/models/core' in all other cases a internal server error will be returned
        """
        # List of possible path which allow get
        paths = {
            '/models/core': {'status': HttpStatusCode.CREATED.value}
        }

        # Check if path exists and throw internal server error if not
        if self.path in paths:
            # Call response function
            self.respond_post(paths[self.path])
        else:
            # Call response function
            self.respond_post({'status': HttpStatusCode.INTERNAL_SERVER_ERROR.value})

    def respond_post(self, opts):
        """ Handle a given post request.

        It takes a request with an new model as zip and store it in the filesystem.
        Then it updates the current version.

        Parameters:
        ----------
        opts:   dict
                dictionary with information like status code
        """
        global build_version
        global semantic_version
        self.send_response(opts['status'])
        # Check if a version was send with the request
        if self.headers['version'] is not None:
            semantic_version = str(self.headers['version'])
        # Read the model from the request and save it
        content_length = int(self.headers['Content-Length'])
        output_file = open("model_"+semantic_version+".zip", "wb")
        output_file.write(self.rfile.read(content_length))
        output_file.close()
        self.end_headers()
        # update the build version
        build_version += 1
        logger.info("Current Version: " + _get_version())
        self.wfile.write(b'')


def run_server(hostname="0.0.0.0", port=8000):
    """ Serve an http server.

    A http server that takes models and save them to provide them requesting instances of rasa core

    Parameters:
    ----------
    hostname:   str
                name of the host
    port:       int
                The port on which the server will listen
    """
    # Creates a new server with the custom request handler
    server_class = HTTPServer
    httpd = server_class((hostname, port), RequestHandler)
    logger.info("Start Server for Host: " + str(hostname) + " Port: " + str(port))

    # Serve the server
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logger.info("Stop Server for Host: " + str(hostname) + " Port: " + str(port))


# Run command
run_server()
