"""
video()classをスレッドとして必要数作成したかったが、
なぜかエラーにてvideoclassを複数作成できないため、カメラ台数分のプロセスを
起動することにした。
プロセス番号をproxに記録し、終了時はkillすることにした。
"""



#!/usr/bin/env python
import subprocess as sb
import os
import signal
import time
import socket
from contextlib import closing


pro1 = sb.Popen(['python3','as_cv.py','5603','CAM1','5703'],preexec_fn=os.setsid)
pro2 = sb.Popen(['python3','as_cv.py','5604','CAM2','5704'],preexec_fn=os.setsid)
pro3 = sb.Popen(['python3','as_cv.py','5605','CAM3','5705'],preexec_fn=os.setsid)
pro4 = sb.Popen(['python3','as_cv.py','5606','CAM4','5706'],preexec_fn=os.setsid)

host = '127.0.0.1'
port1 = 5703
sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

with closing(sock1):








#ここからコマンドを送信する

    while True:
        command = input('>> ')
        if command == 'q':
            os.killpg(os.getpgid(pro1.pid), signal.SIGTERM)  # Send the signal to all the process groups
            os.killpg(os.getpgid(pro2.pid), signal.SIGTERM)  # Send the signal to all the process groups
            os.killpg(os.getpgid(pro3.pid), signal.SIGTERM)  # Send the signal to all the process groups
            os.killpg(os.getpgid(pro4.pid), signal.SIGTERM)  # Send the signal to all the process groups
            break

        elif command == 'g':
            print("send command")
            sock1.sendto(command.encode(), (host, port1))
        



