from __future__ import division
import cv2
import numpy as np
import socket
import struct
import math
import argparse
from datetime import datetime

MAX_LIMIT = 500

class FrameSegment(object):
    """ 
    Object to break down image frame segment
    if the size of image exceed maximum datagram size 
    """
    MAX_DGRAM = 2**12
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64 # extract 64 bytes in case UDP frame overflown
    def __init__(self, sock, port, addr):
        self.sock = sock
        self.port = port
        self.addr = addr

    def udp_frame(self, img):
        """ 
        Compress image and Break down
        into data segments 
        """
        compress_img = cv2.imencode('.jpg', img)[1]
        dat = compress_img.tobytes()
        size = len(dat)
        count = math.ceil(size/(self.MAX_IMAGE_DGRAM))
        array_pos_start = 0
        while count:
            array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
            self.sock.sendto(struct.pack("B", count) +
                dat[array_pos_start:array_pos_end], 
                (self.addr, self.port)
                )
            array_pos_start = array_pos_end
            count -= 1


def startServer(host, port):
    """ Top level main function """
    # Set up UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    fs = FrameSegment(sock, port, host)

    cap = cv2.VideoCapture(0)

    starttime = datetime.now()
    print('  Started Video Streaming at :', starttime.strftime('%I:%M:%S'), starttime.strftime('%d-%m-%Y'))

    frame_count = 0
    previousTime = datetime.now()
    while (cap.isOpened() and frame_count < MAX_LIMIT):
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)
        fs.udp_frame(frame)
        frame_count += 1

        if(frame_count%10 == 0):
            # Print FPS
            currentTime = datetime.now()
            print('  FPS (Frames Per Second): ', 10/(currentTime - previousTime).total_seconds())
            previousTime = currentTime

    message = "exit"
    bytesToSend = str.encode(message)
    sock.sendto(bytesToSend, (host, port))

    cap.release()
    cv2.destroyAllWindows()
    endtime = datetime.now()
    print('  Ended video streaming at: ', endtime.strftime('%I:%M:%S'), endtime.strftime('%d-%m-%Y'))
    print('  Frames Sent to client: ', frame_count)
    print('  Average FPS (Frames Per Second): ', frame_count/(endtime - starttime).total_seconds())
    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send and Receive over Multipath TCP ( MPTCP )')
    parser.add_argument('host', help='Interface the server listens at;'
                        ' host the client sends to')
    parser.add_argument('-p', metavar='PORT', type=int, default=8080,
                        help='TCP port (default 8080)')
    args = parser.parse_args()
    startServer(args.host, args.p)