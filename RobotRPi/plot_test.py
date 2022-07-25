import random
import matplotlib.pyplot as plt
import time

def line_movement_PID_test(cx, drive_speed, half_frame, integral, derivative, last_error):
    proportional_gain = 0.03
    integral_gain = 0.005
    derivative_gain = 0.001
    error = cx - half_frame
    integral = integral + error
    derivative = error - last_error
    turn_rate = proportional_gain * error + integral_gain * integral + derivative_gain * derivative
    last_error = error
    print("Left: %s , Right: %s , cx = %s" %(drive_speed + turn_rate, drive_speed - turn_rate, cx))

def random_cx():
    return random.randint(1, 159)

integral = 0
derivative = 0
last_error = 0

while True:
    time.sleep(0.1)
    cx = random_cx()
    print(cx)
    line_movement_PID_test(cx, 18.0, 80, integral, derivative, last_error)
