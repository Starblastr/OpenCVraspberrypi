import cv2

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    
    if not success:
        break
    img_flipped = cv2.rotate(img, cv2.ROTATE_180)
    cv2.imshow('Flipped Frame', img_flipped)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()