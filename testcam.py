import cv2

cap = cv2.VideoCapture(0)  # 0 is typically the default camera
if not cap.isOpened():
    print("Cannot access camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    cv2.imshow('Camera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()