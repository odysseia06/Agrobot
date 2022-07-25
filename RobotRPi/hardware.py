import pigpio
import time
import RPi.GPIO as GPIO
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

class Motor:
    ''' To control the motor, 3 pins are necessary. Pwm pin generates pwm signal to control the voltage of the dc motor. On a constant frequency,
        voltage is controlled with changing the dutycycle of the signal. Start pin is to start the motor when opened. Direction pin is to determine
        the direction of the rotation of the motor. '''
    def __init__(self, pwm, start, direction):
        ''' Parameters:
            pwm = pwm_pin: int
            start = (start_pin, start_enable {1 or 0}): tuple
            direction = (direction_pin, direction_forward_enable {1 or 0}): tuple
        '''
        self.pwm = pwm
        self.start = start
        self.dir = direction
        self.freq = 50
        self.dutycycle = 0
        self.pi = pigpio.pi()
        
    def nmdc(self, dutycycle):
        '''hardware_PWM(pin, freq, dutycycle) function of the pigpiod accept dutycycle parameter over 1million. This class method
            converts dutycycle percentage to over 1 million. '''
        if dutycycle > 0 and dutycycle <= 100:
            return int(round(dutycycle*10000))
        if dutycycle <= 0:
            return 0
        if dutycycle > 100:
            return 1000000
        
    def init_motor(self):
        self.pi.set_mode(self.pwm, pigpio.OUTPUT)
        self.pi.set_mode(self.start[0], pigpio.OUTPUT)
        self.pi.set_mode(self.dir[0], pigpio.OUTPUT)
        
        if self.start[1] == 0:
            self.pi.write(self.start[0], 1)
        elif self.start[0]==1:
            self.pi.write(self.start[0], 0)
        if self.dir[1] == 0:
            self.pi.write(self.dir[0], 0)
        elif self.dir[1] == 1:
            self.pi.write(self.dir[0], 1)
        self.pi.hardware_PWM(self.pwm, self.freq, 0)
        self.dutycycle = 0
        
    def start_motor(self, dc, forward=True):
        if forward:
            self.pi.write(self.dir[0], self.dir[1])
        else:
            if self.dir[1] == 1:
                self.pi.write(self.dir[0], 0)
            elif self.dir[1] == 0:
                self.pi.write(self.dir[0], 1)
        
        self.pi.write(self.start[0], self.start[1])
        self.pi.hardware_PWM(self.pwm, self.freq, self.nmdc(dc))
        self.dutycycle = dc
        
    def stop_motor(self):
        self.pi.hardware_PWM(self.pwm, self.freq, 0)
        self.dutycycle = 0
        
    def set_dc(self, dc):
        self.pi.hardware_PWM(self.pwm, self.freq, self.nmdc(dc))
        self.dutycycle = dc
        
    def terminate(self):
        self.pi.hardware_PWM(self.pwm, self.freq, 0)
        if self.start[1] == 0:
            self.pi.write(self.start[0], 1)
        elif self.start[1] == 1:
            self.pi.write(self.start[0], 0)
        self.dutycycle = 0
        self.pi.set_mode(self.pwm, pigpio.INPUT)
        self.pi.set_mode(self.start[0], pigpio.INPUT)
        self.pi.set_mode(self.dir[0], pigpio.INPUT)
        self.pi.set_pull_up_down(self.pwm, pigpio.PUD_OFF)
        self.pi.set_pull_up_down(self.start[0], pigpio.PUD_OFF)
        self.pi.set_pull_up_down(self.dir[0], pigpio.PUD_OFF)
        self.pi.stop()
    
class Robot:
    ''' Class to control the robot. Input parameters are left and right motors which they have their own class Motor.
        The robot will listen the commands on the main program. '''
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.left.pi.set_mode(6, pigpio.OUTPUT) #Relay1 (POT)
        self.left.pi.set_mode(16, pigpio.OUTPUT) #Relay2 (MANUAL CANCEL)
        self.left.pi.set_mode(8, pigpio.OUTPUT) #FRONT CAMERA LED
        self.left.pi.set_mode(7, pigpio.OUTPUT) #FRONT CAMERA FAN
        self.left.pi.write(6, 0)
        self.left.pi.write(16, 0)
        self.left.pi.write(8, 1)
        self.left.pi.write(7, 1)

    def init_robot(self):
        ''' Initialize the motors and set robot to ready to move. '''
        self.left.init_motor()
        self.right.init_motor()
        self.proportional_array = np.array([])
        self.integral_array = np.array([])
        self.derivative_array = np.array([])
        self.x_axis = np.array([])
        self.x=0

    def start(self, dc, forward=True):
        ''' Start the robot with the given speed. '''
        self.left.start_motor(dc, forward=forward)
        self.right.start_motor(dc, forward=forward)
        
    def stop(self):
        ''' Stop the robot. '''
        self.left.stop_motor()
        self.right.stop_motor()
        
    def turn_left(self, dc):
        self.stop()
        time.sleep(0.5)
        self.left.start_motor(dc, forward=False)
        self.right.start_motor(dc)
        
    def turn_right(self, dc):
        self.stop()
        time.sleep(0.5)
        self.right.start_motor(dc, forward=False)
        self.left.start_motor(dc)
        
    def terminate(self):
        ''' Terminate the robot and motors as well. Release pigpio GPIO's and stop pigpio connection.'''
        self.left.pi.write(6, 1)
        self.left.pi.write(16, 1)
        self.left.pi.write(8, 0)
        self.left.pi.write(7, 0)
        self.left.pi.set_mode(6, pigpio.INPUT)
        self.left.pi.set_mode(16, pigpio.INPUT)
        self.left.pi.set_mode(8, pigpio.INPUT)
        self.left.pi.set_mode(7, pigpio.INPUT)
        self.left.pi.set_pull_up_down(6, pigpio.PUD_OFF)
        self.left.pi.set_pull_up_down(16, pigpio.PUD_OFF)
        self.left.pi.set_pull_up_down(8, pigpio.PUD_OFF)
        self.left.pi.set_pull_up_down(7, pigpio.PUD_OFF)
        self.left.terminate()
        self.right.terminate()

    def line_movement(self, cx, frame_width, allowed_x_interval, speed_dif, half_frame, optimum_speed):
        diff = half_frame - cx
        if abs(diff) <= allowed_x_interval:
            self.right.set_dc(optimum_speed)
            self.left.set_dc(optimum_speed)
        elif diff > 0:
            self.left.set_dc(optimum_speed - (speed_dif/half_frame)*diff)
        elif diff < 0:
            self.right.set_dc(optimum_speed - (speed_dif/half_frame)*abs(diff))
        print("Left: %s , Right: %s , cx = %s" %(self.left.dutycycle, self.right.dutycycle, cx))
        
    def line_movement_P(self, cx, drive_speed, half_frame): #proportional line follower
        proportional_gain = 0.15
        error = cx - half_frame
        turn_rate = proportional_gain * error
        self.left.set_dc(drive_speed + turn_rate)
        self.right.set_dc(drive_speed - turn_rate)
        print("Left: %s , Right: %s , cx = %s" %(self.left.dutycycle, self.right.dutycycle, cx))
        
    def line_movement_PID(self, cx, drive_speed, half_frame, integral, derivative, last_error):  #PID line follower
        proportional_gain = 0.03
        integral_gain = 0.005
        derivative_gain = 0.001
        error = cx - half_frame
        integral = integral + error
        derivative = error - last_error
        turn_rate = proportional_gain * error + integral_gain * integral + derivative_gain * derivative
        self.left.set_dc(drive_speed + turn_rate)
        self.right.set_dc(drive_speed - turn_rate)       
        last_error = error
        print("Left: %s , Right: %s , cx = %s" %(self.left.dutycycle, self.right.dutycycle, cx))

    def plot_movement(self, cx, drive_speed, half_frame, integral, derivative, last_error):
            proportional_gain = 0.03
            integral_gain = 0.005
            derivative_gain = 0.001
            error = cx - half_frame
            integral = integral + error
            derivative = error - last_error
            turn_rate = proportional_gain * error + integral_gain * integral + derivative_gain * derivative
            self.left.set_dc(drive_speed + turn_rate)
            self.right.set_dc(drive_speed - turn_rate)       
            last_error = error
            print("Left: %s , Right: %s , cx = %s" %(self.left.dutycycle, self.right.dutycycle, cx))
           
            x = x + 1
            self.x_axis.append(x)
            self.proportional_array.append(error)
            self.integral_array.append(integral)
            self.derivative_array.append(derivative)