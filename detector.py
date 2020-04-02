from multiprocessing import Pipe, Process, Array
import cv2
import time
import datetime
from camera import Camera


class Detector():
    def __init__(self):
        self.input_frame_parent, self.input_frame_child = Pipe()
        self.output_frame_parent, self.output_frame_child = Pipe()
        self.box_coord = Array('i',[0,0,0,0])
        
    def detection(self, input_conn):
        inconn = input_conn
        net = cv2.dnn_DetectionModel('./data/face-detection-adas-0001.xml',
                                './data/face-detection-adas-0001.bin')
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
        while True:
            frame = inconn.recv()
            _, confidences, boxes = net.detect(frame, confThreshold=0.5)
            if len(boxes)==0:
                self.box_coord[:] = [0,0,0,0]
            else:
                for _,box in zip(list(confidences), boxes):
                    self.box_coord[:] = box
                    
    def start(self):
        self.detector_process = Process(target=self.detection,args=(self.input_frame_child,))
        self.detector_process.start()

    def get_input_pipe(self):
        return self.input_frame_parent

    def get_box_coord(self):
        if self.box_coord[2]==0 and self.box_coord[3]==0:
            return None
        else: 
            return self.box_coord[:]
    
    def get_center_coord(self):
        if self.box_coord[2]==0 and self.box_coord[3]==0:
            return None
        else: 
            x= self.box_coord[0]+ (self.box_coord[2]//2)
            y= self.box_coord[1]+ (self.box_coord[3]//2)
            return (x,y)


if __name__ == '__main__':
    cam = Camera((320,240),180,15)
    cam.start()
    d = Detector()
    d.start()
    start_time = time.time()
    x = 5 # displays the frame rate every 1 second
    counter = 0
    while True:
        d.get_input_pipe().send(cam.get_frame())
        if d.get_box_coord()!=None:
            print(d.get_box_coord())
            print(d.get_center_coord())
        counter +=1
        if (time.time() - start_time) > x :
            print("FPS: ", counter / (time.time() - start_time))
            counter = 0
            start_time = time.time()