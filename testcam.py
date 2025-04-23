import serial
import time
import requests
import re
import cv2
import datetime
import os
import threading

# Serial port
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

# Open both cameras
cam0 = cv2.VideoCapture('/dev/video0')  # Camera for Room1
cam1 = cv2.VideoCapture('/dev/video2')  # Camera for Room2

if not cam0.isOpened():
    print("Camera 0 not accessible")
if not cam1.isOpened():
    print("Camera 1 not accessible")

# Image storage
base_dir = "/home/gibson/Propertymanagement/images"
image_url = "https://delicate-factually-mastiff.ngrok-free.app/recognize"

# Data values
current1_values = []
current2_values = []
relay1_status = 0
relay2_status = 0

lock = threading.Lock()

def send_data():
    with lock:
        if not current1_values or not current2_values:
            return
        
        avg_current1 = sum(current1_values) / len(current1_values)
        avg_current2 = sum(current2_values) / len(current2_values)

        url = f"https://delicate-factually-mastiff.ngrok-free.app/devices/update?id=1&id=2&field1_1={relay1_status}&field2_1={avg_current1:.2f}&field1_2={relay2_status}&field2_2={avg_current2:.2f}"
        try:
            response = requests.get(url)
            print("Sent sensor data:", response.status_code, response.text)
        except Exception as e:
            print("Error sending sensor data:", e)

        current1_values.clear()
        current2_values.clear()

def send_image_to_endpoint(image_path, room_name):
    print(f"Sending image for room: {room_name}")  # Debugging log
    with open(image_path, 'rb') as image_file:
        files = {'file': image_file}
        data = {'room_name': room_name}  # Include room_name in the POST request
        response = requests.post(image_url, files=files, data=data)
        print(f"[{room_name}] Image sent. Response: {response.json()}")

def capture_image(room_name, camera):
    print(f"Capturing image for room: {room_name}")  # Print the room_name attribute
    ret, frame = camera.read()
    if not ret:
        print(f"[{room_name}] Failed to capture image")
        return

    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    hour = now.strftime("%H")
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    save_dir = os.path.join(base_dir, date, hour)
    os.makedirs(save_dir, exist_ok=True)

    filename = os.path.join(save_dir, f"{room_name}_{timestamp}.png")
    cv2.imwrite(filename, frame)
    print(f"[{room_name}] Image captured:", filename)

    send_image_to_endpoint(filename, room_name)

# Background timer to send sensor data every 30 seconds
def timer_loop():
    while True:
        time.sleep(30)
        send_data()

threading.Thread(target=timer_loop, daemon=True).start()

# Main loop
while True:
    try:
        line = ser.readline().decode('utf-8').strip()
        if line:
            print("Serial:", line)

            if "Relay 1 is ON" in line:
                relay1_status = 1
                threading.Thread(target=capture_image, args=("room1", cam0), daemon=True).start()
            elif "Relay 1 is OFF" in line:
                relay1_status = 0
            elif "Relay 2 is ON" in line:
                relay2_status = 1
                threading.Thread(target=capture_image, args=("room2", cam1), daemon=True).start()
            elif "Relay 2 is OFF" in line:
                relay2_status = 0

            match1 = re.search(r"Current 1:\s*([\d.]+)\s*A", line)
            match2 = re.search(r"Current 2:\s*([\d.]+)\s*A", line)

            with lock:
                if match1:
                    current1_values.append(float(match1.group(1)))
                if match2:
                    current2_values.append(float(match2.group(1)))

    except Exception as e:
        print("Error in main loop:", e)
