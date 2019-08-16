#!/usr/bin/env python
"""
BlueRov video capture class modified by ak
"""
import sys
import cv2
import gi
import numpy as np
import time

import logging
import socket
from contextlib import closing
import threading


gi.require_version('Gst', '1.0')
from gi.repository import Gst

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
            time.sleep(0.1)

class Video():
    """BlueRov video capture class constructor

    Attributes:
        port (int): Video UDP port
        video_codec (string): Source h264 parser
        video_decode (string): Transform YUV (12bits) to BGR (24bits)
        video_pipe (object): GStreamer top-level pipeline
        video_sink (object): Gstreamer sink element
        video_sink_conf (string): Sink configuration
        video_source (string): Udp source ip and port
    """

    def __init__(self, port=5700):
        """Summary

        Args:
            port (int, optional): UDP port
        """

        Gst.init(None)

        self.port = port
        self._frame = None

        # [Software component diagram](https://www.ardusub.com/software/components.html)
        # UDP video stream (:5600)
        self.video_source = 'udpsrc port={}'.format(self.port)
        # [Rasp raw image](http://picamera.readthedocs.io/en/release-0.7/recipes2.html#raw-image-capture-yuv-format)
        # Cam -> CSI-2 -> H264 Raw (YUV 4-4-4 (12bits) I420)
        self.video_codec = '! application/x-rtp, payload=96 ! rtph264depay ! h264parse ! avdec_h264'
        # Python don't have nibble, convert YUV nibbles (4-4-4) to OpenCV standard BGR bytes (8-8-8)
        self.video_decode = \
            '! decodebin ! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert'
        # Create a sink to get data
        self.video_sink_conf = \
            '! appsink emit-signals=true sync=false max-buffers=2 drop=true'

        self.video_pipe = None
        self.video_sink = None

        self.run()

    def start_gst(self, config=None):
        """ Start gstreamer pipeline and sink
        Pipeline description list e.g:
            [
                'videotestsrc ! decodebin', \
                '! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
                '! appsink'
            ]

        Args:
            config (list, optional): Gstreamer pileline description list
        """

        if not config:
            config = \
                [
                    'videotestsrc ! decodebin',
                    '! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
                    '! appsink'
                ]

        command = ' '.join(config)
        self.video_pipe = Gst.parse_launch(command)
        self.video_pipe.set_state(Gst.State.PLAYING)
        self.video_sink = self.video_pipe.get_by_name('appsink0')

    @staticmethod
    def gst_to_opencv(sample):
        """Transform byte array into np array

        Args:
            sample (TYPE): Description

        Returns:
            TYPE: Description
        """
        buf = sample.get_buffer()
        caps = sample.get_caps()
        array = np.ndarray(
            (
                caps.get_structure(0).get_value('height'),
                caps.get_structure(0).get_value('width'),
                3
            ),
            buffer=buf.extract_dup(0, buf.get_size()), dtype=np.uint8)
        return array

    def frame(self):
        """ Get Frame

        Returns:
            iterable: bool and image frame, cap.read() output
        """
        return self._frame

    def frame_available(self):
        """Check if frame is available

        Returns:
            bool: true if frame is available
        """
        return type(self._frame) != type(None)

    def run(self):
        """ Get frame to update _frame
        """

        self.start_gst(
            [
                self.video_source,
                self.video_codec,
                self.video_decode,
                self.video_sink_conf
            ])

        self.video_sink.connect('new-sample', self.callback)

    def callback(self, sink):
        sample = sink.emit('pull-sample')
        new_frame = self.gst_to_opencv(sample)
        self._frame = new_frame

        return Gst.FlowReturn.OK


        

if __name__ == '__main__':
    # Create the video object
    # Add port= if is necessary to use a different one

    argvs = sys.argv  # コマンドライン引数を格納したリストの取得
    # argc = len(argvs) # 引数の個数
    # argvs[1]にportを入れて呼び出す
    
    udp_port = int(argvs[1])
    cam_name = argvs[2]
    com_port = int(argvs[3])
    frame_x =  int(argvs[4])
    frame_y =  int(argvs[5])

    rot_c_x = float(argvs[6])
    rot_c_y = float(argvs[7])
    rot_ang = float(argvs[8])
    scale = float(argvs[9])

    



    
    video = Video(udp_port)
    

 

    command_input = Command_input(com_port)
    command_input.start()

    framesize = "resize"



    while True:
        # Wait for the next frame
        if not video.frame_available():
            continue
        
        

        frame = video.frame()
        frame_h = frame.shape[0]
        frame_w = frame.shape[1]
        rot_center = ( int(frame_w*(1+rot_c_x/100)/2) , int(frame_h*(1+rot_c_y/100)/2))

        trans = cv2.getRotationMatrix2D(rot_center, rot_ang , scale)
        frame = cv2.warpAffine(frame, trans, (frame_w,frame_h))

        resized_frame = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),(int(frame_w/3), int(frame_h/3)))
        
        if framesize == "normal":
            cv2.imshow(cam_name, frame)
        elif framesize == "resize":
            resized_frame = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),(int(frame_w/3), int(frame_h/3)))
            cv2.imshow(cam_name, resized_frame)
            cv2.moveWindow(cam_name, frame_x,frame_y)

        if command_input.command == "g":
            print(cam_name + " command g incomming")
            #command clear
            command_input.command = ""
            cv2.imwrite(cam_name+'frame.png', frame)
            #break
        
        elif command_input.command == "fr":
            command_input.command = ""
            framesize = "resize"
        
        elif command_input.command == "fn":
            command_input.command = ""
            framesize = "normal"

        
        #time.sleep(0.01)

        if cv2.waitKey(100) & 0xFF == ord('q'):
           break
