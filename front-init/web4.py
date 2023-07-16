import json
import mimetypes
import pathlib
import socket
import threading
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file(404)

    def send_html_file(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open('storage/error.html', 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [
            el.split('=') for el in data_parse.split('&')]}

        udp_ip = '127.0.0.1'
        udp_port = 5000
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps(data_dict).encode(), (udp_ip, udp_port))

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Success')


class SocketServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.ip, self.port))

    def start(self):
        print(f'Socket server started on {self.ip}:{self.port}')
        while True:
            data, address = self.server_socket.recvfrom(1024)
            message_json = data.decode('utf-8')
            message_dict = json.loads(message_json)
            self.handle_message(message_dict)

    def handle_message(self, message_dict):
        timestamp = datetime.now().isoformat()
        with open('storage/data.json', 'r+') as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                data = {}
            data[timestamp] = {
                'username': message_dict['username'],
                'message': message_dict['message']
            }
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        print('HTTP server started')
        http_thread = threading.Thread(target=http.serve_forever)
        http_thread.start()

        socket_ip = '127.0.0.1'
        socket_port = 5000
        socket_server = SocketServer(socket_ip, socket_port)
        socket_thread = threading.Thread(target=socket_server.start)
        socket_thread.start()

        print('Socket server started')

        while True:
            pass

    except KeyboardInterrupt:
        print('Server stopped')

    http.shutdown()
    http.server_close()
    socket_server.server_socket.close()


if __name__ == '__main__':
    run()
