# Welcome to PyShine

# This code is for the server 
# Lets import the libraries
import socket
import cv2
import pickle
import struct
import imutils
import argparse
from datetime import datetime

MAX_FRAME_LIMIT = 500

def startServer(host, port, dsize):
    # Socket Create
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_host_name = socket.gethostname()
    server_host_ip = socket.gethostbyname(server_host_name)
    socket_address = (server_host_ip,port)

    # Socket Bind
    sock.bind(('0.0.0.0', port))

    # Socket Listen
    sock.listen(5)
    print("Server running at: ",socket_address)

    # Socket Accept
    while True:
        conn, addr = sock.accept()
        print('Accepted a Client Connection from:',addr)

        if conn:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                conn.close()
                raise IOError('Cannot open webcam')

            starttime = datetime.now()
            print('  Started Video Streaming at :', starttime.strftime('%I:%M:%S'), starttime.strftime('%d-%m-%Y'))

            frame_count = 0
            previousTime = datetime.now()

            while(cap.isOpened() and frame_count < MAX_FRAME_LIMIT):
                img,frame = cap.read()
                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (dsize,dsize), fx=0, fy=0, interpolation = cv2.INTER_CUBIC) #imutils.resize(frame,width=480, height=480, inter=cv2.INTER_CUBIC)
                a = pickle.dumps(frame)
                message = struct.pack("Q",len(a))+a
                conn.sendall(message)

                frame_count += 1

                if frame_count%10 == 0:
                    currentTime = datetime.now()
                    print('  FPS (Frames Per Second): ', 10/(currentTime - previousTime).total_seconds())
                    previousTime = currentTime

                # cv2.imshow('TRANSMITTING VIDEO',frame)
                # key = cv2.waitKey(1) & 0xFF
                # if key == ord('q'):
                #     conn.close()
            # When everything is done, release the capture
            cap.release()
            cv2.destroyAllWindows()

        endtime = datetime.now()
        print('  Ended video streaming at: ', endtime.strftime('%I:%M:%S'), endtime.strftime('%d-%m-%Y'))
        print('  Frames Sent to client: ', frame_count)
        print('  Average FPS (Frames Per Second): ', frame_count/(endtime - starttime).total_seconds())
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send and Receive over Multipath TCP ( MPTCP )')
    parser.add_argument('host', help='Interface the server listens at;'
                        ' host the client sends to')
    parser.add_argument('-p', metavar='PORT', type=int, default=8080,
                        help='TCP port (default 8080)')
    parser.add_argument('-d', type=int, default=720, help='Frame resolution')
    args = parser.parse_args()
    startServer(args.host, args.p, args.d)