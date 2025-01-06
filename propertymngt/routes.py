from flask import Blueprint, render_template, request, Response
import cv2
import numpy as np
from queue import Queue

propertymngt = Blueprint('propertymngt', __name__)

# Queue to hold frames received from the camera
frame_queue = Queue(maxsize=10)

def gen_frames():
    """Generate frames for video streaming."""
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # If no frames are available, send a placeholder frame (optional)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + b'\r\n')

@propertymngt.route('/')
def index():
    """Serve the index page."""
    return render_template('index.html')

@propertymngt.route('/video')
def video():
    """Stream video frames to clients."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@propertymngt.route('/video_stream', methods=['POST'])
def video_stream():
    """Receive video frames from the camera."""
    if 'frame' in request.files:
        frame = request.files['frame'].read()
        # Add the frame to the queue
        if frame_queue.full():
            frame_queue.get()  # Remove the oldest frame
        frame_queue.put(frame)
        return "Frame received", 200
    return "No frame received", 400
