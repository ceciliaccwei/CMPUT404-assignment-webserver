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

# Author: lappet
# Discussion topic: serve html page via socketserver
# URL: https://stackoverflow.com/questions/47726865/html-page-not-displaying-using-python-socket-programming
# Usage in code: Inspired by this answer on how to send the content of a file through the socketserver
#
# Author: valentin
# Discussion topic: parse encoded data
# URL: https://stackoverflow.com/questions/29643544/python-a-bytes-like-object-is-required-not-str
# Usage in code: Referred to this post on how to decode and parse data
# Reference for HTTP status code
# https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#4xx_Client_errors
# Function to check the prefix of a string. 
# https://www.tutorialspoint.com/python/string_startswith.htm

class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # Parse the data
        data = self.data.decode().split('\r\n')
        http_request = data[0].split()
        for i in data:
            # find the host
            if i.startswith("Host: "):
                host = "http://"+i[6:]
                break
        # if the http header is invalid
        # or if the method is not allowed
        if len(http_request) != 3 or http_request[0] != "GET":
            msg = "HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\n\r\n"
            self.request.sendall(msg.encode())
        # get the requested path
        http_request = http_request[1]
        # find the file
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'www')
        if os.path.isfile(root+os.path.abspath(http_request)):
            # format the response header when the request is valid
            # HTTP code 200 OK
            msg = "HTTP/1.1 200 OK\r\nContent-Type: {}\r\nContent-Length: {}\r\n\r\n"
            # MIME type for css file
            if http_request[-4:] == ".css":
                content = open(root+http_request).read()
                msg = msg.format("text/css", len(content))
                msg = msg + content
                self.request.sendall(msg.encode())
            # MIME type for html file
            elif http_request[-5:] == ".html":
                content = open(root+http_request).read()
                msg = msg.format("text/html", len(content))
                msg = msg + content
                self.request.sendall(msg.encode())
        # find the directory
        elif os.path.isdir(root+os.path.abspath(http_request)):
            # redirect HTTP code 301
            if http_request[-1] != "/":
                new = host + http_request + "/"
                msg = "HTTP/1.1 301 Moved Permanently\r\nLocation: {}\r\n\r\n".format(
                    new)
                self.request.sendall(msg.encode())
            # HTTP code 200
            content = open(os.path.join(
                root+http_request, "index.html")).read()
            msg = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n"
            msg = msg.format(len(content))
            msg = msg + content
            self.request.sendall(msg.encode())
        # if no such directory/file
        else:
            msg = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
            content = """
                <html>
                <body>
                <h2></h2><h1>Not Found</h1> The requested URL {} was not found on this server.
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
