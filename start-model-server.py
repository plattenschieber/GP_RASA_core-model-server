from http.server import SimpleHTTPRequestHandler, HTTPServer
import time
import logging

class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.version = 1
        super(RequestHandler, self).__init__(request, client_address, server)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        paths = {
            '/models/core': {'status': 200}
        }
        if self.path in paths:
            self.respond_get(paths[self.path])
        else:
            self.respond_get({'status': 500})

    def respond_get(self, opts):
        content = b''
        if self.headers["If-None-Match"] == str(self.version) or self.headers["If-None-Match"] == "\"" + str(self.version) + "\"":
            self.send_response(204)
        else:
            self.send_response(opts['status'])
            self.send_header('ETag', str(self.version))
            self.send_header('Content-type', 'application/zip')
            f = open("model.zip", "rb")
            content = f.read()

        self.end_headers()

        self.wfile.write(content)

    def do_POST(self):
        paths = {
            '/models/core': {'status': 201}
        }

        if self.path in paths:
            self.respond_post(paths[self.path])
        else:
            self.respond_post({'status': 500})

    def respond_post(self, opts):
        self.send_response(opts['status'])
        content_length = int(self.headers['Content-Length'])
        output_file = open("model.zip", "wb")
        output_file.write(self.rfile.read(content_length))
        output_file.close()
        self.end_headers()
        self.version = self.version + 1
        self.log_message("Next Version: " + self.version)
        self.wfile.write(b'')


def run_server(hostname="0.0.0.0", port=8000):
    server_class = HTTPServer
    httpd = server_class((hostname, port), RequestHandler)
    logging.info(time.asctime(), 'Server Starts - %s:%s' % (hostname, port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info(time.asctime(), 'Server Stops - %s:%s' % (hostname, port))

run_server()