# -*- coding: utf-8 -*-

import http.server
import urllib.parse
from urllib.parse import urlparse
from helpers import FILE_DIR

from smarthome import *
# import cgi

reqHandler = SmartHomeReqHandler()
get_mappings = {}
post_mappings = {}
mappings = {}


def addGetMappings(path, func):
    get_mappings[path] = func


def addPostMappings(path, func):
    post_mappings[path] = func


class AogServer(http.server.BaseHTTPRequestHandler):
    global reqHandler
    global mappings

    # Handler for the GET requests
    def do_GET(self):
        # print(self.headers)
        self.process_Headers()
        try:
            get_mappings[self.only_path](reqHandler, self)
        except Exception as error:
            self.send_message(404, "Page not found!: %s" % error)

    # Handler for the POST requests
    def do_POST(self):
        # print(self.headers)
        self.form = {}
        self.body = self.rfile.read(int(self.headers['content-length'])).decode('utf-8')
        try:
            if 'x-www-form-urlencoded' in self.headers['content-type']:
                un = urllib.parse.unquote(self.body)
                self.form = dict(qc.split("=") for qc in un.split("&"))
        except (ValueError, Exception):
            pass

        self.process_Headers()
        # self.form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
        try:
            post_mappings[self.only_path](reqHandler, self)
        except Exception as error:
            self.send_message(404, "Page not found!: %s" % error)

    def send_message(self, code, msg, headers=None, b=False):
        if self.path.endswith(".jpg"):
            f = open(FILE_DIR + self.path, 'rb')
            self.send_response(200)
            self.send_header('Content-type', 'image/jpg')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return
        elif self.path.endswith(".js"):
            f = open(FILE_DIR + self.path, 'rb')
            self.send_response(200)
            self.send_header('Content-type', 'text/javascript')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return
        elif self.path.endswith(".css"):
            f = open(FILE_DIR + self.path, 'rb')
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return
        self.send_response(code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        if headers is not None:
            for k, v in headers.items():
                self.send_header(k, v)

        if self.isNewCookie:
            self.send_header('Set-Cookie', self.cookie.OutputString())

        self.end_headers()
        if not b:
            self.wfile.write(bytes(msg, "utf-8"))
        else:
            self.wfile.write(msg)

    def send_json(self, code, json_req, b=False):
        self.send_response(code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        if not b:
            self.wfile.write(bytes(json_req, "utf-8"))
        else:
            self.wfile.write(json_req)

    def redirect(self, path, httptype=307):
        self.send_response(httptype)  # 307 Temporary redirect
        self.send_header('Location', path)
        self.end_headers()

    def process_Headers(self):
        self.isNewCookie, self.cookie = reqHandler._session_cookie(self)
        self.url = urlparse(self.path)
        self.only_path = self.url.path

        try:
            self.query = self.url.query
            self.query_components = dict(qc.split("=") for qc in self.query.split("&"))
        except (ValueError, Exception):
            self.query = ""
            self.query_components = {}
