import cv2

import time
import gpiozero
import signal
import sys

buzzer = gpiozero.Buzzer(17)

#thres = 0.45 # Threshold to detect object

classNames = []
classFile = "/home/pi/Desktop/Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/pi/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    #print(classIds,bbox)
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects: 
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    
                    # sound buzzer on and off when the specified object(s) are dectected
                    buzzer.on()
                    time.sleep(1)
                    buzzer.off()
    
    return img,objectInfo

def cleanup():
    print("Cleaning up GPIO...")
    for pin in pins:
        pin.off()
        pin.close()
def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":

    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)
    #cap.set(10,70)
    
    try:

        while True:
            success, img = cap.read()
            # If your camera feed was upside down like mine was the following line will rotate it 180 degrees, otherwise you may want to comment out the next line
            img=cv2.rotate(img, cv2.ROTATE_180)
            result, objectInfo = getObjects(img,0.45,0.2, objects=['person'])
            cv2.imshow("Output",img)
            cv2.waitKey(1)
    # use Ctrl + C to keyboard interrupt to stop the program. This will ensure cleanup() is called and the pi's GPIO pins will be closed off.
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()