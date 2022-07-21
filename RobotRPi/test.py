import cv2
from stream import *
import time
import socket
import threading

HOST = '192.168.1.192'
PORT = 8888
RUNNING = False

def client_connection():
    global RUNNING
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.sendall(bytes("{}".format("HELLO").encode("utf-8")))
    while True:
        data = client_socket.recv(4096).decode()
        if len(data) == 0:
            pass
        else:
            if data == "GO":
                RUNNING = True
            if data == "STOP":
                RUNNING = False
'''
t1 = threading.Thread(target=client_connection, args=())
t1.daemon = True
t1.start()
'''

s = Stream((160,128)).start()
time.sleep(2)
while True:
    try:
        frame = s.read()
        frame, thresh = setup_frame(frame, 30, False, 80, "Adaptive Threshold", True)
        frame1, cx = get_line_cx(frame.copy(), thresh)
        frame2, a, b = detect_color(frame.copy(), "red1")
        #time.sleep(0.1)
        cv2.imshow("Adaptive Threshold", frame1)
        cv2.imshow("HSV Color Detection", frame2)
        print(a)
        if cv2.waitKey(1)==ord("q"):
            s.stop()
            cv2.destroyAllWindows()
            break
    except KeyboardInterrupt:
        s.stop()
        break
