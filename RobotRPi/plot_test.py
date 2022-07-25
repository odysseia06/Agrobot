
import random
import matplotlib.pyplot as plt
import time
from matplotlib.animation import FuncAnimation
from itertools import count

integral = 0
derivative = 0
last_error = 0
half_frame = 80

x_axis = list()
error_array = list()
integral_array = list()
derivative_array = list()
index = count()

def line_movement_PID_test(cx, drive_speed, half_frame):
    global derivative
    global integral
    global last_error
    proportional_gain = 0.03
    integral_gain = 0.005
    derivative_gain = 0.001
    error = cx - half_frame
    integral = integral + error
    derivative = error - last_error
    turn_rate = proportional_gain * error + integral_gain * integral + derivative_gain * derivative
    last_error = error
    print("Left: %s , Right: %s , cx = %s" %(drive_speed + turn_rate, drive_speed - turn_rate, cx))
    print("Left: %s , Right: %s , cx = %s" %(last_error, integral, derivative))
    x_axis.append(next(index))
    error_array.append(last_error)
    integral_array.append(integral)
    derivative_array.append(derivative)
      
    plt.plot(x_axis, error_array, color = "lightsalmon")
    plt.plot(x_axis, integral_array, color = "lightgreen")
    plt.plot(x_axis, derivative_array, color = "skyblue")
    plt.legend(["Error", "Integral", "Derivative"], loc="upper right")
    #plt.plot(self.x_axis, self.cx)

def random_cx():
    return random.randint(1, 159)


while True:
    time.sleep(0.1)
    cx = random_cx()
    line_movement_PID_test(cx, 18.0, 80)

    print(last_error)
    print(derivative)
    print(integral)
    plt.pause(0.05)

plt.show()

