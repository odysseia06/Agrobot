from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2
from datetime import datetime
import time
import numpy as np

COLOR_DICT_HSV = {'black': [[180, 255, 30], [0, 0, 0]],
              'white': [[180, 18, 255], [0, 0, 231]],
              'red1': [[180, 255, 255], [159, 50, 70]],
              'red2': [[9, 255, 255], [0, 50, 70]],
              'green': [[89, 255, 255], [36, 50, 70]],
              'blue': [[128, 255, 255], [90, 50, 70]],
              'yellow': [[35, 255, 255], [25, 50, 70]],
              'lineyellow': [[30, 255, 255], [20, 100, 100]],
              'purple': [[158, 255, 255], [129, 50, 70]],
              'orange': [[24, 255, 255], [10, 50, 70]],
              'gray': [[180, 18, 230], [0, 0, 40]]}

class Stream: #modifying imutils.video.PiVideoStream
    def __init__(self, resolution=(320,240), framerate=32, show_cam = True, put_iter=True, **kwargs):
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        
        #set optional camera parameters (refer to PiCamera docs)
        for (arg, value) in kwargs.items():
            setattr(self.camera, arg, value)
        #initialize the stream 
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port = True)
        
        self.frame = None
        self.stopped = False
        self.show_cam = show_cam
        self.put_iter = put_iter
        if self.put_iter:
            self.cps = CountsPerSec().start()
        
    def start(self):
        #start the thread to read frames from the video stream
        t = Thread(target = self.update, args=())
        t.daemon = True
        t.start()
        return self
    
    def update(self):
        #keep looping infinitely until the thread is stopped
        for f in self.stream:
            #grab the frame from the stream and clear the stream in preperation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)
            
            if self.put_iter:
                self.frame = putIterationsPerSec(self.frame, self.cps.countsPerSec())
                self.cps.increment()
            if self.show_cam:
                cv2.imshow("Stream", self.frame)
            if cv2.waitKey(1) == ord("q"):
                self.stopped = True
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                cv2.destroyAllWindows()
                return
            
    def read(self):
        #return the frame most recently read
        return self.frame
    
    def stop(self):
        #indicate that the thread should be stopped
        self.stopped = True
        
class CountsPerSec:
    ''' Class that determines the framerate per second for the camera applications on the Raspberry Pi. Call increment() method in the loop
and countsPerSecond() returns the iterations of the loop per second.'''
    def __init__(self):
        self._start_time = None
        self._num_occurences = 0
    def start(self):
        self._start_time = datetime.now()
        return self
    def increment(self):
        self._num_occurences += 1
    def countsPerSec(self):
        elapsed_time = (datetime.now() - self._start_time).total_seconds()
        if elapsed_time > 0:
            return self._num_occurences / elapsed_time
        else:
            return 1
        
def putIterationsPerSec(frame, iterations_per_sec, location=(20,20)):
    ''' Put the iterations per second from CountPerSec class and show it on the screen using OpenCV. Third parameter location is a tuple represents where the text
        will be on the screen. First value is x and the second is y. Origin of the screen is on the top left and x value increases to the right and y value increases
        to the bottom. '''
    cv2.putText(frame, "{:.0f} iterations/sec".format(iterations_per_sec), location, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
    return frame
 
def setup_frame(frame, threshold_max_value, rotation, crop, threshold, erode_dilate):
    if rotation:
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    if crop:
        frame = frame[0:crop, :]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)
    if threshold == "Global Threshold":
        ret, thresh = cv2.threshold(blur, 30, threshold_max_value, cv2.THRESH_BINARY_INV)
    elif threshold == "Adaptive Threshold":
        thresh = cv2.adaptiveThreshold(blur, threshold_max_value, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 8)
    if erode_dilate:
        kernel = np.ones((3,3), np.uint8)
        thresh = cv2.erode(thresh, kernel, iterations=1)
        thresh = cv2.dilate(thresh, kernel, iterations=1)
    return frame, thresh

def get_line_cx(frame, thresh, draw_contour=True):
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        cx = int(M["m10"]/(M["m00"]+0.001))
        cy = int(M["m01"]/(M["m00"]+0.001))
        if draw_contour:
            cv2.line(frame, (cx,0), (cx,240), (255,0,0), 1)
            cv2.line(frame, (0,cy), (320,cy), (255,0,0), 1)
            cv2.drawContours(frame, contours, -1, (0,255,0), 1)
        return frame, cx
    else:
        return frame, None
    
def detect_color(frame, color, draw_rect=True, draw_contour=True):
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array(COLOR_DICT_HSV[color][1], np.uint8)
    upper = np.array(COLOR_DICT_HSV[color][0], np.uint8)
    mask = cv2.inRange(hsvFrame, lower, upper)
    kernel = np.ones((5,5), "uint8")
    mask = cv2.dilate(mask, kernel)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if draw_contour:
        cv2.drawContours(frame, contours, -1, (0,255,0), 1)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area>300:
            if draw_rect:
                x,y,w,h = cv2.boundingRect(contour)
                frame = cv2.rectangle(frame, (x,y), (x+w, y+h), (255, 255, 255), 2)
                cv2.putText(frame, color, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
            M = cv2.moments(contour)
            cx = int(M["m10"]/(M["m00"]+0.001))
            cy = int(M["m01"]/(M["m00"]+0.001))
            if draw_contour:
                cv2.line(frame, (cx,0), (cx,240), (255,0,0), 1)
                cv2.line(frame, (0,cy), (320,cy), (255,0,0), 1)
            return frame, cx, cy
        else:
            return frame, None, None
    return frame, None, None