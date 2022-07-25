import time
from hardware import *
import cv2
from stream import *
import socket
import threading

frame_width = 160
allowed_x_interval = 2
speed_dif = 8
half_frame = 80
optimum_speed = 20
integral = 0
derivative = 0
last_error = 0
HOST = '192.168.1.192'
PORT = 8888
RUNNING = False
CHARGE = False
def client_connection():
    global RUNNING
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.sendall(bytes("{}".format("HELLO FROM ROBOT").encode("utf-8")))
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

s = Stream((160,128), show_cam = False).start()
time.sleep(1)
mr = Motor(13, (26,1), (21,0))
ml = Motor(12, (20,1), (19,1))
robot = Robot(ml, mr)
robot.init_robot()
robot.start(20)



while True:
    try:
        frame = s.read()
        frame, thresh = setup_frame(frame, 30, False, 80, "Adaptive Threshold", True)
        frame1, cx = get_line_cx(frame.copy(), thresh)
        frame2, a, b = detect_color(frame.copy(), "lineyellow")
        frame3, c, d = detect_color(frame.copy(), "red1")
        time.sleep(0.1)
        cv2.imshow("Adaptive Threshold", frame1)

        plt.plot(robot.x_axis, robot.proportional_array)
        plt.plot(robot.x_axis, robot.integral_array)
        plt.plot(robot.x_axis, robot.derivative_array)
        plt.plot(robot.x_axis, robot.cx)
        plt.show()

        if RUNNING:
            #robot.line_movement(cx, frame_width, allowed_x_interval, speed_dif, half_frame, optimum_speed)
            #robot.line_movement_P(cx, 19.0, 80)
            robot.line_movement_PID(cx, 18.0, 80, integral, derivative, last_error)
        else:
            robot.stop()
        if c is not None and CHARGE:
            robot.terminate()
            s.stop()
            break
        if a is not None and not CHARGE:
            print(a)
            robot.stop()
            client_socket.sendall(bytes("{}".format("DONE").encode("utf-8")))
            RUNNING = False
            #s.stop()
            CHARGE = True
        if cv2.waitKey(1)==ord("q"):
            s.stop()
            cv2.destroyAllWindows()
            break        
    except KeyboardInterrupt:
        robot.terminate()
        client_socket.sendall(bytes("{}".format("DONE").encode("utf-8")))
        s.stop()
        break
