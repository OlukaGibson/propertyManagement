from flask import Blueprint, render_template, request, Response, jsonify
import cv2
import numpy as np
from queue import Queue
import os
from werkzeug.utils import secure_filename
import face_recognition

propertymngt = Blueprint('propertymngt', __name__)

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the relative path
KNOWN_FACES_DIR = os.path.join(BASE_DIR, "faces")

# Arrays to hold known face encodings and names
known_face_encodings = []
known_face_names = []

# Load known faces from the directory
for folder_name in os.listdir(KNOWN_FACES_DIR):
    folder_path = os.path.join(KNOWN_FACES_DIR, folder_name)
    if os.path.isdir(folder_path):
        # Load the image named after the folder
        image_path = os.path.join(folder_path, f"{folder_name}.jpg")
        if os.path.exists(image_path):
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(encoding)
            known_face_names.append(folder_name)


# Define a route for landing page
@propertymngt.route('/')
def device_storage():
    print('Device storage is full!')
    return {'message': 'Device storage is full!'}

@propertymngt.route('/recognize', methods=['POST'])
def recognize_faces():
    """
    Endpoint to recognize faces from an uploaded image.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save the uploaded image temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join('/tmp', filename)
        file.save(temp_path)

        # Load the uploaded image
        unknown_image = face_recognition.load_image_file(temp_path)

        # Find all face locations and encodings in the uploaded image
        unknown_face_locations = face_recognition.face_locations(unknown_image)
        unknown_face_encodings = face_recognition.face_encodings(unknown_image, unknown_face_locations)

        results = []

        for face_encoding, face_location in zip(unknown_face_encodings, unknown_face_locations):
            # See if the face is a match for the known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            # Append the result
            top, right, bottom, left = face_location
            results.append({
                "name": name,
                "location": {
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "left": left
                }
            })

        # Delete the temporary file
        os.remove(temp_path)

        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500