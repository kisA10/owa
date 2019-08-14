#!/usr/bin/env python
"""
BlueRov video capture class modified by ak
"""
import sys
import cv2
import gi
import numpy as np

import logging
import socket
from contextlib import closing
import threading

gi.require_version('Gst', '1.0')
from gi.repository import Gst

log = logging.getLogger()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


class Command_input(threading.Thread):
    def __init__(self,com_port=5800):
        super(Command_input, self).__init__()
        #self.port = com_port
        self.command = "0"

    def stop(self):
        self.__stop = True

    def run(self):
        host = '127.0.0.1'
        port = 4002
        bufsize = 4096
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        with closing(sock):
            sock.bind((host, port))

            while True:
                self.command = sock.recv(bufsize).decode()
                log.info(self.command)

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

    def __init__(self, port):
        """Summary

        Args:
            port (int, optional): UDP port
        """
        #super(Video, self).__init__()
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

    #@staticmethod
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
    port = 5603#argvs[1]
    cam_name = "cam1"#argvs[2]

    video1 = Video(5603)
    #video1.start()

    video2 = Video(5604)
    #video2.start()

    command_input = Command_input()
    command_input.start()



    while True:
        # Wait for the next frame
        if not video1.frame_available():
            continue

        if command_input.command == "1":
            break
        
        print(command_input.command)

        frame1 = video1.frame()
        cv2.imshow(cam_name, frame1)

        frame2 = video2.frame()
        cv2.imshow(cam_name, frame2)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            command_input.stop()
            break
