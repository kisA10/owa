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

x0='0'
x1='640'
y0='0'
y1='480'

#calibration value
cam1_rot_c_dx = '2.3' #%
cam1_rot_c_dy = '1' #%
cam1_rot_ang = '30'
cam1_scale = '0.5'

cam2_rot_c_dx = '0.5' #%
cam2_rot_c_dy = '-10' #%
cam2_rot_ang = '-5'
cam2_scale = '2'

cam3_rot_c_dx = '40' #%
cam3_rot_c_dy = '10' #%
cam3_rot_ang = '0.5'
cam3_scale = '0.8'

cam4_rot_c_dx = '20' #%
cam4_rot_c_dy = '10' #%
cam4_rot_ang = '10'
cam4_scale = '1'



pro1 = sb.Popen(['python3','as_cv_test.py','5603','CAM1',port1,x0,y0,cam1_rot_c_dx,cam1_rot_c_dy,cam1_rot_ang,cam1_scale],preexec_fn=os.setsid)
pro2 = sb.Popen(['python3','as_cv_test.py','5604','CAM2',port2,x1,y0,cam2_rot_c_dx,cam2_rot_c_dy,cam2_rot_ang,cam2_scale],preexec_fn=os.setsid)
pro3 = sb.Popen(['python3','as_cv_test.py','5605','CAM3',port3,x0,y1,cam3_rot_c_dx,cam3_rot_c_dy,cam3_rot_ang,cam3_scale],preexec_fn=os.setsid)
pro4 = sb.Popen(['python3','as_cv_test.py','5606','CAM4',port4,x1,y1,cam4_rot_c_dx,cam4_rot_c_dy,cam4_rot_ang,cam4_scale],preexec_fn=os.setsid)


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
            

    elif not command == '':
        print("send command "+command)
        sock1.sendto(command.encode(), (host, int(port1)))
        sock2.sendto(command.encode(), (host, int(port2)))
        sock3.sendto(command.encode(), (host, int(port3)))
        sock4.sendto(command.encode(), (host, int(port4)))

sock1.close()

sock2.close()
sock3.close()
sock4.close()   