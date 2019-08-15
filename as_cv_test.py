#!/usr/bin/env python
"""
BlueRov video capture class modified by ak
"""
import sys
import cv2
#import gi
import numpy as np
import time

import logging
import socket
from contextlib import closing
import threading

#gi.require_version('Gst', '1.0')
#from gi.repository import Gst

log = logging.getLogger()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


class Command_input(threading.Thread):
    def __init__(self,com_port):
        super(Command_input, self).__init__()
        self.port = int(com_port)
        self.command = ""
        self.host = '127.0.0.1'
        self.bufsize = 16
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #with closing(self.sock):
        self.sock.bind((self.host, self.port))

 

    def run(self):


        while True:
            self.command = self.sock.recv(self.bufsize).decode()
            log.info(self.command)
            time.sleep(0.01)


if __name__ == '__main__':
    # Create the video object
    # Add port= if is necessary to use a different one

    argvs = sys.argv  # コマンドライン引数を格納したリストの取得
    # argc = len(argvs) # 引数の個数
    # argvs[1]にportを入れて呼び出す
    #port = 5603#argvs[1]
    cam_name = argvs[2]
    command_port = int(argvs[3])

    #video1 = Video(5603)
    #video1.start()

 

    command_input = Command_input(command_port)
    command_input.start()



    while True:
        # Wait for the next frame
        #if not video1.frame_available():
        #    continue
        time.sleep(0.001)

        if command_input.command == "g":
            print(cam_name + " command g incomming")
            command_input.command = ""
            #break
        
        #print(command_input.command)

        #frame1 = video1.frame()
        #cv2.imshow(cam_name, frame1)

        #frame2 = video2.frame()
        #cv2.imshow(cam_name, frame2)


        #if cv2.waitKey(1) & 0xFF == ord('q'):
         #   command_input.stop()
         #   break
