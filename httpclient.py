#!/usr/bin/env python3
# coding: utf-8
# Copyright 2022 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Xuantong Ma
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # get the stauts code from data, we split the data by a space
        # data format example: HTTP/1.0 200 OK
        code = int(data.split(' ')[1])
        return code

    def get_headers(self,data):
        # get the headers from data
        headers = data.split('\r\n\r\n')[0]
        return headers

    def get_body(self, data):
        # get the content body from data
        body = data.split('\r\n\r\n')[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        
        # Parse URLs to split URLs so that we can easily get the different components
        o = urlparse(url)
        
        # Get the path and port from the URLs
        if o.path:
            path = o.path
        else:
            path = '/'

        if o.port:
            port = o.port
        else:
            port = 80

        # connect to the server
        self.connect(o.hostname,port)

        # form a request and send it out
        status_code = "GET {} HTTP/1.1\r\n".format(path)
        host = "Host: {}\r\n".format(o.hostname)
        connection = "Connection: close\r\n\r\n"
        send = status_code + host + connection
        self.sendall(send)

        # receive a response from the socket and get the body and status code
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)

        # print the result to stdout
        print("Code: {}\nBody: {}".format(code, body))
        
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        
        # similar to GET(), but we need to check if the args is empty or not
        o = urlparse(url)
        if o.path:
            path = o.path
        else:
            path = '/'

        if o.port:
            port = o.port
        else:
            port = 80

        if args == None:
            args = ''
        else:
            args = urlencode(args) # method from urllib to convert strings to urlencode and query string format
        self.connect(o.hostname,port)

        # form a request and send it out
        status_code = "POST {} HTTP/1.1\r\n".format(path)
        host = "Host: {}\r\n".format(o.hostname)
        content_type = "Content-Type: application/x-www-form-urlencoded\r\n"
        content_length = "Content-Length: {}\r\n".format(len(args))
        connection = "Connection: close\r\n"
        send = status_code + host + content_type + content_length + connection + '\r\n' + args
        self.sendall(send)

        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        
        # print the result to stdout
        # print('#######################################')
        print("Code: {}\nBody: {}".format(code, body))

        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
