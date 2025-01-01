from flask import Blueprint, redirect, url_for, render_template, request, send_file, jsonify, Response
import os
from .extentions import db
from .models import Users, Guests
# from google.cloud import storage
import io
import json
from dotenv import load_dotenv
# from intelhex import IntelHex
from datetime import datetime
import cv2

load_dotenv()

propertymngt = Blueprint('propertymngt', __name__)

camera = cv2.VideoCapture(1)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            print('Camera not found!')
            break
        else:
            # detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            # eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            # faces = detector.detectMultiScale(frame, 1.1, 7)
            # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # # rectangle of faces
            # for (x, y, w, h) in faces:
            #     cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            #     roi_gray = gray[y:y+h, x:x+w]
            #     roi_color = frame[y:y+h, x:x+w]
            #     eyes = eye_cascade.detectMultiScale(roi_gray)
            #     for (ex, ey, ew, eh) in eyes:
            #         cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

 
@propertymngt.route('/')
def index():
    print('Device storage is full!')
    return render_template('index.html')
    # return {'message': 'Device storage is full!'}

@propertymngt.route('/video')
def video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')