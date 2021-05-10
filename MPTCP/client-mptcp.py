# lets make the client code
import socket
import cv2
import pickle
import struct
import argparse
from datetime import datetime

def startClient(host, port, dsize, num_paths):
    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((host,port))
    data = b""
    payload_size = struct.calcsize("Q")

    print('Connected to server')

    starttime = datetime.now()
    print('Started Video Streaming at :', starttime.strftime('%I:%M:%S'), starttime.strftime('%d-%m-%Y'))

    frame_count = 0

    previousTime = datetime.now()
    fd = open('result/res'+str(dsize)+'/client_mptcp_fps'+str(num_paths)+'.txt', 'w')
    while True:
        while len(data) < payload_size:
            packet = sock.recv(64*1024) # 4K
            if not packet: break
            data+=packet
            
        if not data:
            break
        
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        
        while len(data) < msg_size:
            data += sock.recv(4*1024)
        frame_data = data[:msg_size]
        data  = data[msg_size:]
        frame = pickle.loads(frame_data)
        cv2.imshow("RECEIVING VIDEO",frame)
        frame_count += 1

        if frame_count%10 == 0:
            currentTime = datetime.now()
            fps = 10/(currentTime - previousTime).total_seconds()
            time = (currentTime - starttime).total_seconds()
            print(fps, time)
            # Save data to file
            fd.writelines(str(fps)+" "+str(time)+"\n")
            previousTime = currentTime

        key = cv2.waitKey(1) & 0xFF
        if key  == ord('q'):
            break

    endtime = datetime.now()
    print('Ended video streaming at: ', endtime.strftime('%I:%M:%S'), endtime.strftime('%d-%m-%Y'))
    print('Frames Received from server: ', frame_count)
    fps_avg = frame_count/(endtime - starttime).total_seconds()
    print('  FPS (Frames Per Second): ', fps_avg)
    fd.writelines('Average '+str(fps_avg))
    fd.close()
    cv2.destroyAllWindows()
    sock.close()
    print('Connection Closed with Server')   

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send and Receive over Multipath TCP ( MPTCP )')
    parser.add_argument('host', help='Interface the server listens at;'
                        ' host the client sends to')
    parser.add_argument('-p', metavar='PORT', type=int, default=8080,
                        help='TCP port (default 8080)')
    parser.add_argument('-d', type=int, default=720, help='Frame resolution')
    parser.add_argument('num_paths', type=int)
    args = parser.parse_args()
    startClient(args.host, args.p, args.d, args.num_paths)