from multiprocessing import Pipe, Process, Array, Value
import cv2
import time
#from camera import Camera


class Detector():
    def __init__(self):
        self.__input_frame_parent, self.__input_frame_child = Pipe()
        self.__box_coord = Array('i',[0,0,0,0])
        self.__FPS = Value('f',0)
        
    def __detection(self, input_conn):
        inconn = input_conn
        net = cv2.dnn_DetectionModel('./data/face-detection-adas-0001.xml',
                                './data/face-detection-adas-0001.bin')
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
        start_time = time.time()
        x = 5 # compute the frame rate mean for 5 second
        counter = 0
        while True:
            frame = inconn.recv()
            _, confidences, boxes = net.detect(frame, confThreshold=0.5)
            if len(boxes)==0:
                self.__box_coord[:] = [0,0,0,0]
            else:
                for _,box in zip(list(confidences), boxes):
                    self.__box_coord[:] = box
            counter +=1
            if (time.time() - start_time) > x :
                self.__FPS.value = counter / (time.time() - start_time)
                counter = 0
                start_time = time.time()
                    
    def start(self):
        self.__detector_process = Process(target=self.__detection,args=(self.__input_frame_child,))
        self.__detector_process.start()

    def stop(self):
        self.__detector_process.terminate()

    def get_pipe(self):
        return self.__input_frame_parent

    def get_box_coord(self):
        if self.__box_coord[2]==0 and self.__box_coord[3]==0:
            return None
        else: 
            return self.__box_coord[:]
    
    def get_center_coord(self):
        if self.__box_coord[2]==0 and self.__box_coord[3]==0:
            return None
        else: 
            x= self.__box_coord[0]+ (self.__box_coord[2]//2)
            y= self.__box_coord[1]+ (self.__box_coord[3]//2)
            return (x,y)
    
    def get_FPS(self):
        return self.__FPS.value

# if __name__ == '__main__':
#     cam = Camera((320,240),180,15)
#     cam.start()
#     d = Detector()
#     d.start()
#     fps=0
#     while True:
#         d.get_pipe().send(cam.get_frame())
#         if d.get_box_coord()!=None:
#             print(d.get_box_coord())
#             print(d.get_center_coord())
#         if fps!=d.get_FPS():
#             print("FPS: ", d.get_FPS())
#             fps=d.get_FPS()