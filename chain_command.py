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

host = '127.0.0.1'
port1 = '5703'
sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port2 = '5704'
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port3 = '5705'
sock3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port4 = '5706'
sock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



pro1 = sb.Popen(['python3','as_cv_test.py','5603','CAM1',port1],preexec_fn=os.setsid)
pro2 = sb.Popen(['python3','as_cv_test.py','5604','CAM2',port2],preexec_fn=os.setsid)
pro3 = sb.Popen(['python3','as_cv_test.py','5605','CAM3',port3],preexec_fn=os.setsid)
pro4 = sb.Popen(['python3','as_cv_test.py','5606','CAM4',port4],preexec_fn=os.setsid)



#ここからコマンドを送信する

while True:
    command = input('>> ')
        
    if command == 'q':
        print ("proceses killing!")
        os.killpg(os.getpgid(pro1.pid), signal.SIGTERM)  # Send the signal to all the process groups
        os.killpg(os.getpgid(pro2.pid), signal.SIGTERM)  # Send the signal to all the process groups
        os.killpg(os.getpgid(pro3.pid), signal.SIGTERM)  # Send the signal to all the process groups
        os.killpg(os.getpgid(pro4.pid), signal.SIGTERM)  # Send the signal to all the process groups
        break
            

    elif command == 'g':
        print("send command g")
        sock1.sendto(command.encode(), (host, int(port1)))
        sock2.sendto(command.encode(), (host, int(port2)))
        sock3.sendto(command.encode(), (host, int(port3)))
        sock4.sendto(command.encode(), (host, int(port4)))

sock1.close()
sock2.close()
sock3.close()
sock4.close()
        