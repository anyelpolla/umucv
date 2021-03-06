#!/usr/bin/env python

# Adapted from:

'''
    Author: Igor Maculan - n3wtron@gmail.com
    A Simple mjpg stream http server
'''
# https://gist.github.com/n3wtron/4624820

import cv2
from PIL import Image
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
from io import StringIO,BytesIO
import time

from umucv.stream import Camera
from umucv.util   import sourceArgs
import signal
import sys

import argparse

parser = argparse.ArgumentParser()
sourceArgs(parser)
parser.add_argument('--quality', help='jpeg quality', type=int, default=30)
args = parser.parse_args()

cam = Camera(args.size, args.dev)

QUALITY = args.quality

stop = False

def signal_handler(signal, frame):
        global stop
        cam.stop()
        stop = True
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while not stop:
                try:
                    img = cam.frame
                    imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                    jpg = Image.fromarray(imgRGB)
                    tmpFile = BytesIO()
                    jpg.save(tmpFile,'JPEG',quality=QUALITY)
                    self.wfile.write("--jpgboundary".encode())
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length',str(tmpFile.getbuffer().nbytes))
                    self.end_headers()
                    self.wfile.write(tmpFile.getvalue())
                    time.sleep(0.05)
                except:
                    break

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def main():
    try:
        server = ThreadedHTTPServer(('', 8087), CamHandler)
        print( "server started")
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

if __name__ == '__main__':
    main()

