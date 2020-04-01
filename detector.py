from multiprocessing import Pipe, Process
import cv2


class Detector():
    def __init__(self):
        self.input_frame, self.output_frame = Pipe()



    def detection(self, frameCount):
        global vs, outputFrame, lock, detectcoord
        net = cv2.dnn_DetectionModel('face-detection-adas-0001.xml',
                                'face-detection-adas-0001.bin')
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
        while True:
            _, confidences, boxes = net.detect(frame, confThreshold=0.5)
            with lock:
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
            fps.update()

