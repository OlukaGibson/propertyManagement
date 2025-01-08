# import face_recognition
import cv2
import numpy as np
import os

def load_known_faces(faces_dir):
    known_face_encodings = []
    known_face_names = []

    for person_name in os.listdir(faces_dir):
        person_dir = os.path.join(faces_dir, person_name)
        if os.path.isdir(person_dir):
            image_path = os.path.join(person_dir, f"{person_name}.jpg")
            image = face_recognition.load_image_file(image_path)
            face_encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(face_encoding)
            known_face_names.append(person_name)

    return known_face_encodings, known_face_names

# Paths
unknown_image_path = "/home/gibson/propertyManagement/propertymngt/unknown.jpg"
faces_dir = "/home/gibson/propertyManagement/propertymngt/faces"

# Load known faces
known_face_encodings, known_face_names = load_known_faces(faces_dir)

# Load the unknown image
unknown_image = face_recognition.load_image_file(unknown_image_path)
rgb_unknown_image = unknown_image[:, :, ::-1]

# Find all the faces and face encodings in the unknown image
face_locations = face_recognition.face_locations(rgb_unknown_image)
face_encodings = face_recognition.face_encodings(rgb_unknown_image, face_locations)

face_names = []
for face_encoding in face_encodings:
    # See if the face is a match for the known face(s)
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
    name = "Unknown"

    # Or instead, use the known face with the smallest distance to the new face
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
    best_match_index = np.argmin(face_distances)
    if matches[best_match_index]:
        name = known_face_names[best_match_index]

    face_names.append(name)

# Display the results
for (top, right, bottom, left), name in zip(face_locations, face_names):
    # Draw a box around the face
    cv2.rectangle(rgb_unknown_image, (left, top), (right, bottom), (0, 0, 255), 2)

    # Draw a label with a name below the face
    cv2.rectangle(rgb_unknown_image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(rgb_unknown_image, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

# Display the resulting image
cv2.imshow('Image', rgb_unknown_image)
cv2.waitKey(0)
cv2.destroyAllWindows()