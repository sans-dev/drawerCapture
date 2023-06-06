import cv2

cap = cv2.VideoCapture('/dev/video4')

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Error: could not read frame")
        break
    
    cv2.imshow('frame', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
