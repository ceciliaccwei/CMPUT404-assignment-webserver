#  coding: utf-8
import socketserver
import os
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print("Got a request of: %s\n" % self.data)
        # https://stackoverflow.com/questions/47726865/html-page-not-displaying-using-python-socket-programming
        # https://stackoverflow.com/questions/29643544/python-a-bytes-like-object-is-required-not-str
        data = self.data.decode().split('\r\n')
        http_request = data[0].split()
        for i in data:
            # https://www.tutorialspoint.com/python/string_startswith.htm
            if i.startswith("Host: "):
                host = "http://"+i[6:]
                break
        if len(http_request) != 3 or http_request[0] != "GET":
            msg = "HTTP/1.1 405 Method Not Allowed\nContent-Type: text/html\n\n"
            self.request.sendall(msg.encode())
        http_request = http_request[1]
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'www')
        # print(http_request)
        if os.path.isfile(root+os.path.abspath(http_request)):
            msg = "HTTP/1.1 200 OK\nContent-Type: {}\n\n"
            if http_request[-4:] == ".css":
                msg = msg.format("text/css")
                content = open(root+http_request).read()
                msg = msg + content
                self.request.sendall(msg.encode())
            elif http_request[-5:] == ".html":
                msg = msg.format("text/html")
                content = open(root+http_request).read()
                msg = msg + content
                self.request.sendall(msg.encode())
        elif os.path.isdir(root+os.path.abspath(http_request)):
            if http_request[-1] != "/":
                new = host + http_request + "/"
                msg = "HTTP/1.1 301 Moved Permanently\nLocation: {}\n\n".format(new)
                self.request.sendall(msg.encode())
            content = open(os.path.join(
                root+http_request, "index.html")).read()
            msg = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n"
            msg = msg + content
            self.request.sendall(msg.encode())
        else:
            #https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#4xx_Client_errors
            msg = "HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n"
            content = """
                <html>
                <body>
                <h2></h2><h1>Not Found</h1> The requested URL/{} was not found on this server.
                </body>
                </html>
            """.format(http_request)

            msg = msg + content
            self.request.sendall(msg.encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
