import cv2
import datetime
import os
import time

# Load the pre-trained Haar cascades for face and eye detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Open the default camera (0)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot access camera")
    exit()

# Base directory for saving images
base_dir = "/home/gibson/Propertymanagement/images"

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Convert the frame to grayscale (Haar cascades work with grayscale images)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Loop through detected faces
    for (x, y, w, h) in faces:
        # Focus on the face region for eye detection
        face_roi_gray = gray[y:y+h, x:x+w]

        # Detect eyes within the face region
        eyes = eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(15, 15))
        
        # If both face and eyes are detected, save the frame
        if len(eyes) > 0:
            # Get the current date and time
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d")
            hour = now.strftime("%H")
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

            # Create the directory structure
            save_dir = os.path.join(base_dir, date, hour)
            os.makedirs(save_dir, exist_ok=True)

            # Save the frame as an image
            filename = os.path.join(save_dir, f"detected_{timestamp}.png")
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")

    # Add a short delay to avoid overloading the CPU
    time.sleep(0.1)

# Release the video capture
cap.release()


# import cv2
# import datetime
# import os
# import face_recognition
# import numpy as np

# # Load the pre-trained Haar cascades for face and eye detection
# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# # Open the default camera (0)
# cap = cv2.VideoCapture(0)
# if not cap.isOpened():
#     print("Cannot access camera")
#     exit()

# # Base directory for saving images
# base_dir = "/home/gibson/Propertymanagement/images"

# # Known faces directory
# KNOWN_FACES_DIR = "/home/gibson/Propertymanagement/faces"

# # Arrays to hold known face encodings and names
# known_face_encodings = []
# known_face_names = []

# # Load known faces from the directory
# for folder_name in os.listdir(KNOWN_FACES_DIR):
#     folder_path = os.path.join(KNOWN_FACES_DIR, folder_name)
#     if os.path.isdir(folder_path):
#         # Load the image named after the folder
#         image_path = os.path.join(folder_path, f"{folder_name}.jpg")
#         if os.path.exists(image_path):
#             image = face_recognition.load_image_file(image_path)
#             encoding = face_recognition.face_encodings(image)[0]
#             known_face_encodings.append(encoding)
#             known_face_names.append(folder_name)

# # Function to recognize faces
# def recognize_faces(image):
#     unknown_face_locations = face_recognition.face_locations(image)
#     unknown_face_encodings = face_recognition.face_encodings(image, unknown_face_locations)

#     results = []

#     for face_encoding, face_location in zip(unknown_face_encodings, unknown_face_locations):
#         # See if the face is a match for the known faces
#         matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#         name = "Unknown"

#         # Use the known face with the smallest distance to the new face
#         face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
#         best_match_index = np.argmin(face_distances)
#         if matches[best_match_index]:
#             name = known_face_names[best_match_index]

#         # Append the result
#         top, right, bottom, left = face_location
#         results.append({
#             "name": name,
#             "location": {
#                 "top": top,
#                 "right": right,
#                 "bottom": bottom,
#                 "left": left
#             }
#         })

#     return results

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Failed to grab frame")
#         break

#     # Convert the frame to grayscale (Haar cascades work with grayscale images)
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # Detect faces in the frame
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

#     # Loop through detected faces
#     for (x, y, w, h) in faces:
#         # Focus on the face region for eye detection
#         face_roi_gray = gray[y:y+h, x:x+w]

#         # Detect eyes within the face region
#         eyes = eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(15, 15))

#         # If both face and eyes are detected, process the frame
#         if len(eyes) > 0:
#             # Get the current date and time
#             now = datetime.datetime.now()
#             date = now.strftime("%Y-%m-%d")
#             hour = now.strftime("%H")
#             timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

#             # Create the directory structure
#             save_dir = os.path.join(base_dir, date, hour)
#             os.makedirs(save_dir, exist_ok=True)

#             # Save the frame as an image
#             filename = os.path.join(save_dir, f"detected_{timestamp}.png")
#             cv2.imwrite(filename, frame)
#             print(f"Saved: {filename}")

#             # Perform face recognition on the saved frame
#             results = recognize_faces(frame)

#             # Print recognition results
#             print(f"Recognition Results: {results}")

#             # Break after processing one frame to avoid overlap
#             break

# # Release the video capture
# cap.release()
