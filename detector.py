from multiprocessing import Pipe, Process
import cv2
import time
import datetime


class Detector():
    def __init__(self):
        self.input_frame_parent, self.input_frame_child = Pipe()
        self.output_frame_parent, self.output_frame_child = Pipe()


    def detection(self, input_conn, output_conn):
        #global vs, outputFrame, lock, detectcoord
        inconn = input_conn
        outconn = output_conn
        net = cv2.dnn_DetectionModel('face-detection-adas-0001.xml',
                                'face-detection-adas-0001.bin')
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
        while True:
            frame = inconn.recv()
            _, confidences, boxes = net.detect(frame, confThreshold=0.5)
            if len(boxes)==0: detectcoord=None
            for _,box in zip(list(confidences), boxes):
                cv2.rectangle(frame, box, color=(0, 255, 0))
                detectcoord = (box[0]+int(box[2]/2),box[1]+int(box[3]/2))
                cv2.circle(frame,detectcoord,10,color=(0, 255, 0),thickness=2)
            timestamp = datetime.datetime.now()
            cv2.putText(frame, timestamp.strftime(
                "%d/%m/%Y %H:%M:%S"), (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.70, (0, 0, 255), 2)
            outputFrame = frame.copy()
            outconn.snd(outputFrame)

    def start(self):
        self.detector_process = Process(target=self.detection,args=(self.input_frame_child,self.output_frame_child))
        self.detector_process.start()

    def get_input_pipe(self):
        return self.input_frame_parent

if __name__ == '__main__':
    d = Detector()
    d.start()