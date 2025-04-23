from flask import Blueprint, render_template, request, Response, jsonify, send_file, redirect, url_for
import cv2
import json
import io
import os
from .extentions import db
from .models import Authentications, Users, Devices, Readings, Rooms, RoomAccess, UserRoomAccess
import numpy as np
from queue import Queue
from werkzeug.utils import secure_filename
import face_recognition

from google.cloud import storage
from google.oauth2 import service_account
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

propertymngt = Blueprint('propertymngt', __name__)

"""
Google storage credentials
"""
google_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
credentials_dict = json.loads(google_credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

"""
Face directory from base and encoding
"""
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWN_FACES_DIR = os.path.join(BASE_DIR, "faces")
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

def clean_data(data):
    return None if data == "" else data

""""
landing page
"""
@propertymngt.route('/')
def device_storage():
    print('Device storage is full!')
    return {'message': 'Device storage is full!'}

""""
User management routes
"""
#add new user
@propertymngt.route('/user/register', methods=['POST'])
def register_user():
    file = request.files['image']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # Upload to Google Cloud Storage
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
    blob = bucket.blob(f'faces/{username}/{username}.jpg')
    blob.upload_from_file(file, content_type='application/octet-stream')

    # Reset the file stream so it can be saved again
    file.seek(0)

    # Save the image locally
    faces_dir = os.path.join('propertymngt', 'faces', username)
    os.makedirs(faces_dir, exist_ok=True)
    local_image_path = os.path.join(faces_dir, f'{username}.jpg')
    file.save(local_image_path)

    # Create and save user in the database
    new_user = Users(
        username=username,
        email=email,
        password=password
    )

    db.session.add(new_user)
    db.session.commit()

    return {'message': 'User successfully registered'}


#login user
@propertymngt.route('/user/login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

    user = db.session.query(Users).filter_by(username=username).first()

    if not user:
        return {'message' : 'User not found'}, 404

    if user.password != password:
        return {'message' : 'Invalid password'}, 401

    return {'message' : 'User logged in successfully'}

#edit user
@propertymngt.route('/user/<int:id>/edit', methods=['POST'])
def edit_user(id):
    user = db.session.query(Users).filter_by(id=id).first()
    
    if not user:
        return {'message' : 'User not found'}, 404
    
    username = request.form.get('username', user.username)
    email = request.form.get('email', user.email)
    password = request.form.get('password', user.password)

    user.username = username
    user.email = email
    user.password = password

    db.session.comit()
    
    return {'message' : 'User updated successfully'}

# display all users
@propertymngt.route('/user/get_users', methods=['GET'])
def get_users():
    users = db.session.query(Users).all()
    user_list = []

    if not users:
        return {'message' : 'No users found'}, 404
    
    for user in users :
        user_dict = {
            'id' : user.id,
            'username' : user.username,
            'email' : user.email
        }

        user_list.append(user_dict)

    return jsonify(user_list)

# display specific user
@propertymngt.route('/user/get_user/<int:id>', methods=['GET'])
def get_specific_user(id):
    user = db.session.query(Users).filter_by(id=id).first()
    
    if not user:
        return {'message' : 'User not found'}, 404

    user_dict = {
        'username' : user.username,
        'email' : user.email,
        'password' : user.password
    }

    return jsonify(user_dict)


""""
Room management routes
"""
# add new room
@propertymngt.route('/room/add', methods=['POST'])
def add_room():
    room_name = clean_data(request.form['room_name'])
    room_number = clean_data(request.form['room_number'])

    new_room = Rooms(
        room_name=room_name,
        room_number=room_number
    )

    db.session.add(new_room)
    db.session.commit()

    return {'message' : 'Room added successfully'}

# display all rooms
@propertymngt.route('/room/get_rooms', methods=['GET'])
def get_rooms():
    rooms = db.session.query(Rooms).all()
    room_list = []

    if not rooms:
        return {'message' : 'No rooms found'}, 404
    
    for room in rooms:
        room_dict = {
            'id' : room.id,
            'room_name' : room.room_name,
            'room_number' : room.room_number
        }

        room_list.append(room_dict)

    return jsonify(room_list)

# display specific room
@propertymngt.route('/room/get_room/<int:id>', methods=['GET'])
def get_specific_room(id):
    room = db.session.query(Rooms).filter_by(id=id).first()
    if not room:
        return {'message': 'Room not found'}, 404

    room_dict = {
        'roomId': room.id,
        'room_name': room.room_name,
        'room_number': room.room_number
    }
    device_list = []
    users_access_list = []
    user_list = []

    # devices attached to the room
    devices = db.session.query(Devices).filter_by(roomID=id).all()
    if devices:
        for device in devices:
            device_dict = {
                'deviceID': device.id,
                # 'roomID': device.roomID,
                'device_type': device.device_type,
                'fields': {},
                'readings': []  # Add readings key to store readings
            }
            for i in range(1, 9):
                if getattr(device, f'field{i}') is not None:
                    device_dict['fields'][f'field{i}'] = getattr(device, f'field{i}')

            # readings from the device
            readings = db.session.query(Readings).filter_by(deviceID=device.id).all()
            if readings:
                for reading in readings:
                    reading_dict = {
                        'readingID': reading.id,
                        'timestamp': reading.created_at,
                        # 'deviceID': reading.deviceID,
                        'fields': {}
                    }
                    for i in range(1, 9):
                        if getattr(reading, f'field{i}') is not None:
                            reading_dict['fields'][f'field{i}'] = getattr(reading, f'field{i}')
                    device_dict['readings'].append(reading_dict)  # Add reading to device's readings

            device_list.append(device_dict)

    # users access to the room
    users_access = db.session.query(UserRoomAccess).filter_by(roomID=id).all()
    if users_access:
        for user in users_access:
            users_access_dict = {
                'userID': user.userID,
                # 'roomID': user.roomID,
                'time_accessed': user.created_at
            }
            users_access_list.append(users_access_dict)

    for user in users_access_list:
        user = db.session.query(Users).filter_by(id=user['userID']).first()
        if user:
            user_dict = {
                'userID': user.id,
                'username': user.username,
                'email': user.email
            }
            user_list.append(user_dict)

    final_user_list = []
    # get the userID, username, email from user_list and add the time_accessed from users_access_list
    for access in users_access_list:
        for user in user_list:
            if user['userID'] == access['userID']:
                access['username'] = user['username']
                access['email'] = user['email']
                final_user_list.append(access)

    room_dict['devices'] = device_list
    room_dict['users_access'] = final_user_list

    return jsonify(room_dict)
# edit room
@propertymngt.route('/room/<int:id>/edit', methods=['POST'])
def edit_room(id):
    room = db.session.query(Rooms).filter_by(id=id).first()

    if not room:
        return {'message' : 'Room not found'}, 404

    room_name = clean_data(request.form.get('room_name', room.room_name))
    room_number = clean_data(request.form.get('room_number', room.room_number))

    room.room_name = room_name
    room.room_number = room_number

    db.session.commit()

    return {'message' : 'Room updated successfully'}


""""
Device managment routes
"""
# add device type
@propertymngt.route('/device/add', methods=['POST'])
def add_device():
    # Extract fields from form data with default value None if not present
    # device_type, field1, field2, field3, field4, field5, field6, field7, field8
    device_type = clean_data(request.form.get('device_type'))
    roomID = clean_data(request.form.get('roomID'))

    if not roomID:
        return {'message': 'roomID is required'}, 400

    # Extract dynamic fields from form data (field1 to field8)
    fields = {}
    for i in range(1, 9):
        fields[f'field{i}'] = clean_data(request.form.get(f'field{i}', None))
    
    # Create a new device object
    new_device = Devices(
        device_type=device_type,
        roomID=roomID,
        **fields
    )

    # Add the new device to the database and commit the transaction
    db.session.add(new_device)
    db.session.commit()

    return {'message': 'New device added successfully!'}

# retrive all devices
@propertymngt.route('/device/get_devices', methods=['GET'])
def get_devices():
    devices = db.session.query(Devices).all()
    devices_list = []
    for device in devices:
        device_dict = {
            'device_type': device.device_type,
            'fields': {}
        }
        for i in range(1, 9):
            if getattr(device, f'field{i}') is not None:
                device_dict['fields'][f'field{i}'] = getattr(device, f'field{i}')
        
        devices_list.append(device_dict)
    
    return jsonify(devices_list)

# retrive specific device
@propertymngt.route('/device/get_device/<int:id>', methods=['GET'])
def get_device(id):
    device = db.session.query(Devices).filter_by(id=id).first()
    if device:
        device_dict = {
            'device_type': device.device_type,
            'fields': {}
        }
        for i in range(1, 9):
            if getattr(device, f'field{i}') is not None:
                device_dict['fields'][f'field{i}'] = getattr(device, f'field{i}')
        
        return jsonify(device_dict)
    
    return {'message': 'Device not found!'}, 404

# Edit device data
@propertymngt.route('/device/<int:id>/edit', methods=['POST'])
def edit_device(id):
    device = db.session.query(Devices).filter_by(id=id).first()

    if not device:
        return {'message': 'Device not found!'}, 404
    
    # Extract form data with default value as current device data if not provided
    device_type = request.form.get('device_type', device.device_type)

    fields = {}
    for i in range(1, 9):
        fields[f'field{i}'] = request.form.get(f'field{i}', getattr(device, f'field{i}'))

    device.name = device_type

    # Update dynamic fields
    for field, value in fields.items():
        setattr(device, field, value)

    # Commit the changes to the database
    db.session.commit()

    return {'message': 'Device updated successfully!'}

""""
Data entry managment routes
"""
# update multiple data
@propertymngt.route('/devices/update', methods=['GET'])
def update_multiple_devices():
    device_ids = request.args.getlist('id')
    if not device_ids:
        return {'message': 'No device IDs provided'}, 400

    for device_id in device_ids:
        device = db.session.query(Devices).filter_by(id=device_id).first()
        if device:
            fields = {}
            for i in range(1, 9):
                fields[f'field{i}'] = request.args.get(f'field{i}_{device_id}', None)

            # Create a new entry in the Readings table
            new_entry = Readings(
                deviceID=device.id,
                **fields
            )

            db.session.add(new_entry)
        else:
            return {'message': f'Device with id {device_id} not found'}, 404

    db.session.commit()
    return {'message': 'Entries updated'}

@propertymngt.route('/device/<int:id>/update', methods=['GET'])
def update_device_data(id):
    device = db.session.query(Devices).filter_by(id=id).first()

    if device :
        fields = {}
        for i in range(1, 9):
            fields[f'field{i}'] = request.args.get(f'field{i}', None)

        # Create a new entry in the MetadataValues table
        new_entry = Readings(
            deviceID=device.id,
            **fields
        )

        db.session.add(new_entry)
        db.session.commit()

        return {'message' : 'Entry updated'}
    return {'message' : 'Device not found'}, 404

# retrieve device data
@propertymngt.route('/device/<int:id>/data', methods=['GET'])
def get_device_data(id):
    device = db.session.query(Devices).filter_by(id=id).first()

    if device:
        entries = db.session.query(Readings).filter_by(deviceID=id).all()
        entry_list = []

        for entry in entries :
            entry_dict = {
                'deviceID' : entry.deviceID,
                'fields': {}
            }
            for i in range(1, 9):
                if getattr(entry, f'field{i}') is not None:
                    entry_dict['fields'][f'field{i}'] = getattr(entry, f'field{i}')
            
            entry_list.append(entry_dict)
        
        return jsonify(entry_list)
    return {'message' : 'device not found'}, 404 

""""
Facial recognition routes
"""
@propertymngt.route('/recognize', methods=['POST'])
def recognize_faces():
    """
    Endpoint to recognize faces from an uploaded image.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    room_name = clean_data(request.form.get('room_name'))

    # Query the room by name
    room = db.session.query(Rooms).filter_by(room_name=room_name).first()
    if not room:
        return jsonify({"error": f"Room with name '{room_name}' not found"}), 404

    room_ID = room.id

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

            if name != "Unknown":
                user = db.session.query(Users).filter_by(username=name).first()
                if user:
                    # Create a new entry in the UserRoomAccess table
                    new_entry = UserRoomAccess(
                        userID=user.id,
                        roomID=room_ID  # Use the valid room_ID here
                    )
            
                    db.session.add(new_entry)
                    db.session.commit()

        # Delete the temporary file
        os.remove(temp_path)

        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500