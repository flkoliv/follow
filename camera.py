from imutils.video import VideoStream
import imutils
from multiprocessing import Value, Process, Pipe, Array
import time
import logging
import cv2
from detector import Detector
from pantilthat import PanTiltHat


class Camera():

    def __init__(self, resolution, rotation, framerate ):
        self.frame = None
        self.resolutionX = Value('i',0)
        self.resolutionY = Value('i',0)
        self.rotation = Value('i',0)
        self.framerate = Value('i',0)
        self.resolutionX.value = resolution[0]
        self.resolutionY.value = resolution[1]
        self.rotation.value = rotation
        self.framerate.value = framerate
        self.detector = None
        self.pantilt = None
        
    def cam(self, conn):
        vs = VideoStream(
            src=0,
            usePiCamera=True,
            resolution=(self.resolutionX.value,self.resolutionY.value),
            framerate=self.framerate.value).start()
        time.sleep(2) #waiting the camera to start
        while True:
            frame = vs.read()
            frame = imutils.rotate(frame,angle=self.rotation.value)
            if self.detector != None:
                self.detector.get_pipe().send(frame)
                if self.detector.get_box_coord()!=None:
                    cv2.rectangle(frame, self.detector.get_box_coord(), color=(0, 255, 0))
                    self.pantilt.set_target(self.detector.get_center_coord())
                else:
                    self.pantilt.set_target((self.resolutionX.value//2,self.resolutionY.value//2))
            conn.send(frame)

    def start(self):
        self.frame, child_conn = Pipe()
        self.cam_process = Process(target=self.cam,args=(child_conn,))
        self.cam_process.start()
        time.sleep(2)
        logging.info("Camera process started")

    def stop(self):
        if self.cam_process.is_alive():
            self.cam_process.terminate()
        logging.info("Camera process stopped")

    def get_frame(self):
        return self.frame.recv()
    
    def get_pipe(self):
        return self.frame

    def set_detector(self,detect):
        self.detector=detect

    def set_pantilthat(self,pantilt):
        self.pantilt=pantilt

if __name__ == '__main__':
    cam = Camera((640,480),180,15)
    detect = Detector()
    detect.start()
    pantilt = PanTiltHat()
    pantilt.start()
    cam.set_detector(detect)
    cam.set_pantilthat(pantilt)
    cam.start()


    time.sleep(2)
    print(cam.get_frame())
    print(cam.get_frame())
    time.sleep(2)
    print(cam.get_frame())
    detect.stop()
    cam.stop()