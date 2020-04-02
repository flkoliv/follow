from flask import Response
from flask import Flask
from flask import render_template
from flask import request
import cv2
import argparse
from camera import Camera
from detector import Detector
from pantilthat import PanTiltHat


app = Flask(__name__)
cam = Camera((320,240),180,25)

@app.route("/", methods = ['GET', 'POST'])
def index():
    global move
    if request.method == "POST" and request.form['stop'] == "False":
        move = True
        print(move)
        buttonclicked = request.form['button']
        print(buttonclicked)
        moveCam(buttonclicked,1)
        
        return render_template("index.html")
    elif request.method == "POST" and request.form['stop'] == "True":
        move = False
        print(move)
        return render_template("index.html")
    elif request.method == "GET":
        return render_template("index.html")
    else:
        print(request.form['stop'])

def generate():
    while True:
        outputFrame = cam.get_frame()
        if outputFrame is None:
            continue
        (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
        if not flag:
            continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")
    
# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
        help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
        help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
        help="# of frames used to construct the background model")
    args = vars(ap.parse_args())
    #start camera
    detect = Detector()
    detect.start()
    pantilt = PanTiltHat()
    pantilt.start()
    cam.set_detector(detect)
    cam.set_pantilthat(pantilt)
    cam.start()
    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
        threaded=True, use_reloader=False)
    cam.stop()
    detect.stop()
    pantilt.stop()