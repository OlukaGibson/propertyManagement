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
