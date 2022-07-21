import pigpio
import time
import socket
import threading
from picamera import PiCamera

HOST = '192.168.1.192'
PORT = 8889
RUNNING = False
def client_connection():
    global RUNNING
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.sendall(bytes("{}".format("HELLO FROM CAMERA").encode("utf-8")))
    while True:
        data = client_socket.recv(4096).decode()
        if len(data) == 0:
            pass
        else:
            if data == "GO":
                RUNNING = True
            if data == "STOP":
                RUNNING = False

t1 = threading.Thread(target=client_connection, args=())
t1.daemon = True
t1.start()

pi = pigpio.pi()
camera = PiCamera()
FAN = 8
LED = 7
LED2 = 21
WATER_LOW = 14
WATER_MED = 15
WATER_MAX = 18
MOTOR = 23
SINGLE_SPRAY = 25
MULTI_SPRAY = 24

pi.set_mode(FAN, pigpio.OUTPUT)
pi.set_mode(LED, pigpio.OUTPUT)
pi.set_mode(LED2, pigpio.OUTPUT)
pi.set_mode(MOTOR, pigpio.OUTPUT)
pi.set_mode(SINGLE_SPRAY, pigpio.OUTPUT)
pi.set_mode(MULTI_SPRAY, pigpio.OUTPUT)

#pi.set_mode(WATER_LOW, pigpio.INPUT)
#pi.set_mode(WATER_MED, pigpio.INPUT)
#pi.set_mode(WATER_MAX, pigpio.INPUT)

pi.write(LED, 1)
pi.write(FAN, 1)
pi.write(LED2, 0)
time.sleep(1)
#time.sleep(2)

#pi.write(MULTI_SPRAY, 0)
#pi.write(SINGLE_SPRAY, 1)

#pi.write(MOTOR, 0)

while True:
    try:
        pi.write(LED2, 1)
        time.sleep(0.5)
        pi.write(LED2, 0)
        time.sleep(0.5)
        if RUNNING:
            pi.write(FAN, 0)
            time.sleep(0.5)
            pi.write(LED, 0)
            camera.capture("/home/pi/Desktop/img.png")
            time.sleep(2)
            for i in range(10):
                pi.write(LED, 1)
                time.sleep(0.4)
                pi.write(LED, 0)
                time.sleep(0.4)
            pi.write(LED, 1)
            pi.write(LED2, 1)
            client_socket.sendall(bytes("{}".format("DONE").encode("utf-8")))
            break
    except KeyboardInterrupt:
        
        pi.write(FAN, 1)
        #pi.write(MULTI_SPRAY, 1)
        #pi.write(MOTOR, 1)
        pi.write(LED2, 1)
        
        pi.write(LED, 1)
        
        #pi.set_mode(MOTOR, pigpio.INPUT)
        #pi.set_mode(MULTI_SPRAY, pigpio.INPUT)
        
        pi.stop()
        break
