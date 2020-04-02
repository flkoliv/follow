from imutils.video import VideoStream
import imutils
from multiprocessing import Value, Process, Pipe, Array
import time
import logging


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
        
    
    def cam(self, conn):
        
        vs = VideoStream(
            src=0,
            usePiCamera=True,
            resolution=(self.resolutionX.value,self.resolutionY.value),
            framerate=self.framerate.value).start()
        time.sleep(2) #waiting the camera to start
        while True:
            frame = vs.read()
            #frame = imutils.resize(frame, width=640)
            frame = imutils.rotate(frame,angle=self.rotation.value)
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

if __name__ == '__main__':
    cam = Camera((640,480),180,15)
    cam.start()
    time.sleep(2)
    print(cam.get_frame())
    print(cam.get_frame())
    time.sleep(2)
    print(cam.get_frame())
    cam.stop()