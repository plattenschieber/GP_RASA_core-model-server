from http.server import SimpleHTTPRequestHandler, HTTPServer
import time

class RequestHandler(SimpleHTTPRequestHandler):
    def respond(self, opts):
        response = self.handle_http(opts['status'], self.path)
        self.wfile.write(response)

    def handle_http(self, status_code, path):
        content = ''

        if self.headers["If-None-Match"] == "1234567" or self.headers["If-None-Match"] == "\"1234567\"":
            print("No Change")
            self.send_response(204)
        else:
            print("respond with new model")
            self.send_response(status_code)
            self.send_header('ETag', '1234567')
            self.send_header('Content-type', 'application/zip')
            f = open("models_123456.zip", "rb")
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
        print("request for " + self.path)
        if self.path in paths:
            self.respond(paths[self.path])
        else:
            self.respond({'status': 500})



def run_server(hostname="0.0.0.0", port=8000):
    server_class = HTTPServer
    httpd = server_class((hostname, port), RequestHandler)
    print(time.asctime(), 'Server Starts - %s:%s' % (hostname, port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server Stops - %s:%s' % (hostname, port))

run_server()