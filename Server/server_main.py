import socket
import threading
import tkinter as tk
from server_gui import *
import time

HOST=''
ROBOT_PORT = 8888
CAMERA_PORT = 8889
root = tk.Tk()
server_gui = ServerGUI(root)
SERVER_ON = False


def robot_server():
    global rconn
    rs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Robot socket created.\n')
    rs.bind((HOST,ROBOT_PORT))
    rs.listen(10)
    print('Robot socket now listening.\n')
    rconn, addr = rs.accept()
    data = rconn.recv(4096).decode()
    print(data)
    time.sleep(0.5)
    data = rconn.recv(4096).decode()
    print(data)
    if data == "DONE":
        sconn.sendall(bytes("{}".format("GO").encode("utf-8")))

def camera_server():
    global sconn
    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Camera socket created.\n')
    cs.bind((HOST,CAMERA_PORT))
    cs.listen(10)
    print('Camera socket now listening.\n')
    sconn, addr = cs.accept()
    data = sconn.recv(4096).decode()
    print(data)
    time.sleep(0.5)
    data = sconn.recv(4096).decode()
    print(data)
    if data == "DONE":
        rconn.sendall(bytes("{}".format("GO").encode("utf-8")))

def connect():
    global SERVER_ON
    if not SERVER_ON:
        t1 = threading.Thread(target=robot_server, args=())
        t2 = threading.Thread(target=camera_server, args=())
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()
        server_gui.text.insert("insert", "Server is on and ready to accept.\n")
        SERVER_ON = True
        
def start():
    global SERVER_ON
    global rconn
    global sconn
    if SERVER_ON:
        rconn.sendall(bytes("{}".format("GO").encode("utf-8")))

def stop():
    global SERVER_ON
    global rconn
    global sconn
    if SERVER_ON:
        rconn.sendall(bytes("{}".format("STOP").encode("utf-8")))
        rconn.sendall(bytes("{}".format("STOP").encode("utf-8")))




def main():
    server_gui.buttons("Connect", connect)
    server_gui.buttons("Start", start)
    server_gui.buttons("Stop", stop)
    root.mainloop()


if __name__ == "__main__":
    main()