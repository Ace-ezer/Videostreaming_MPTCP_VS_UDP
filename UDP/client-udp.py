from __future__ import division
import cv2
import numpy as np
import socket
import struct
import argparse
from datetime import datetime

MAX_DGRAM = 2**12

def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        print(seg[0])
        if struct.unpack("B", seg[0:1])[0] == 1:
            print("finish emptying buffer")
            break

def startClient(host, port, dsize):
    """ Getting image udp frame &
    concate before decode and output image """
    
    # Set up socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    dat = b''
    dump_buffer(sock)

    print('Connected to server')
    starttime = datetime.now()
    print('Started Video Streaming at :', starttime.strftime('%I:%M:%S'), starttime.strftime('%d-%m-%Y'))

    frame_count = 0
    fd = open('result/res'+str(dsize)+'/client_udp_fps.txt', 'w')
    previousTime = datetime.now()

    while True:
        seg, addr = sock.recvfrom(MAX_DGRAM)

        if seg == b'exit':
            break

        if struct.unpack("B", seg[0:1])[0] > 1:
            dat += seg[1:]
        else:
            dat += seg[1:]
            img = cv2.imdecode(np.frombuffer(dat, dtype=np.uint8), 1)
            cv2.imshow('frame', img)
            frame_count += 1

            if frame_count%10 == 0:
                currentTime = datetime.now()
                fps = 10/(currentTime - previousTime).total_seconds()
                time = (currentTime - starttime).total_seconds()
                fd.writelines(str(fps)+" "+str(time)+"\n")
                previousTime = currentTime

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''

    endtime = datetime.now()
    print('Ended video streaming at: ', endtime.strftime('%I:%M:%S'), endtime.strftime('%d-%m-%Y'))
    print('Frames Received from server: ', frame_count)
    fps_avg = frame_count/(endtime - starttime).total_seconds()
    print('  FPS (Frames Per Second): ', fps_avg)
    fd.writelines('Average '+str(fps_avg))
    fd.close()
    cv2.destroyAllWindows()
    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send and Receive over Multipath TCP ( MPTCP )')
    parser.add_argument('host', help='Interface the server listens at;'
                        ' host the client sends to')
    parser.add_argument('-p', metavar='PORT', type=int, default=8080,
                        help='TCP port (default 8080)')
    parser.add_argument('-d', type=int, default=720, help='Frame resolution')
    args = parser.parse_args()
    startClient(args.host, args.p, args.d)