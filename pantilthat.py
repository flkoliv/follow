#!/usr/bin/python

from PCA9685 import PCA9685
from pid import PIDController
import time
import sys
import signal
from multiprocessing import Value, Process
import logging

# ============================================================================
# PanTilt Hat servo control
# ============================================================================

class PanTiltHat:
    SERVO_MIN = -90
    SERVO_MAX = 90
    RESOLUTION = (320, 320)
    CENTER = (RESOLUTION[0] // 2, RESOLUTION[1] // 2)

    def __init__(self):
        self.panAngle = Value('i', 0)
        self.tiltAngle = Value('i', 0)
        self.pwm = PCA9685()
        self.pwm.setPWMFreq(50)
        self.target_x = Value('i', 0)
        self.target_y = Value('i', 0)
        self.target_x.value = PanTiltHat.RESOLUTION[0] // 2
        self.target_y.value = PanTiltHat.RESOLUTION[1] // 2
        
        # PID gains for panning
        self.pan_p = Value('f', 0.05)
        self.pan_i = Value('f', 0.1)
        self.pan_d = Value('f', 0)

        # PID gains for tilting
        self.tilt_p = Value('f', 0.15)
        self.tilt_i = Value('f', 0.2)
        self.tilt_d = Value('f', 0)

            
    def in_range(self, val, start, end):
        return (val >= start and val <= end)

    def setPanAngle(self,angle):
        self.panAngle.value = angle

    def setTiltAngle(self,angle):
        self.tiltAngle.value = angle

    def setPosition(self,pAngle, tAngle):
        self.panAngle.value = pAngle
        self.tiltAngle.value = tAngle

    def set_servos(self, pan, tilt):
        while True:
            pAngle = pan.value
            tAngle = tilt.value
            if self.in_range(pAngle, PanTiltHat.SERVO_MIN, PanTiltHat.SERVO_MAX):
                self.pwm.setRotationAngle(1, pAngle+90)
            else:
                logging.info(f'pan_angle not in range {pAngle}')
            if self.in_range(tAngle, PanTiltHat.SERVO_MIN, PanTiltHat.SERVO_MAX):
                self.pwm.setRotationAngle(0, tAngle+90)
            else:
                logging.info(f'tilt_angle not in range {tAngle}')

    def pid_process(self, output, p, i, d, box_coord, origin_coord, action):
        p = PIDController(p.value, i.value, d.value)
        p.reset()
        while True:
            error = origin_coord - box_coord.value
            out = p.update(error)
            output.value = int(out)
            print(action + " - " + str(error) + " - "+ str(output.value) + "-"+str(out))

    def start(self):
        self.pan_process = Process(target=self.pid_process,
                              args=(self.panAngle, self.pan_p, self.pan_i, self.pan_d, self.target_x, PanTiltHat.CENTER[0], 'pan'))
        self.tilt_process = Process(target=self.pid_process,
                               args=(self.tiltAngle, self.tilt_p, self.tilt_i, self.tilt_d, self.target_y, PanTiltHat.CENTER[1], 'tilt'))
        self.servo_process = Process(target=self.set_servos, args=(self.panAngle, self.tiltAngle))
        
        self.servo_process.start()
    
    def pid_start(self):
        self.pan_process.start()
        self.tilt_process.start()

    def pid_stop(self):
        if self.pan_process.is_alive():
            self.pan_process.terminate()
        if self.tilt_process.is_alive():
            self.tilt_process.terminate()
    
    def stop(self):
        self.pid_stop()
        time.sleep(0.5)
        self.setPosition(0,0)
        time.sleep(0.5)
        self.pwm.exit_PCA9685()
        self.servo_process.terminate()
        sys.exit()
    

if __name__ == '__main__':
    p = PanTiltHat()
    p.start()
    p.pid_start()
    time.sleep(2)
    # p.setPosition(120,120)
    # time.sleep(2)
    p.target_x.value = 0
    p.target_y.value = 0
    # p.setPosition(30,30)
    # time.sleep(2)
    # p.setPosition(60,60)
    time.sleep(10)
    p.stop()

