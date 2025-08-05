import cv2
import os
import imutils

dataPath = r'C:\Users\Alejandra\Desktop\980-Proyectos\Tarea 03\Data'
personName = 'Leslie'
personPath = os.path.join(dataPath, personName)

if not os.path.exists(personPath):
    print('Carpeta creada: ', personPath)
    os.makedirs(personPath)

video_path = r'C:\Users\Alejandra\Desktop\980-Proyectos\Tarea 03\Leslie.mp4'

cap = cv2.VideoCapture(video_path)

faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
count = 0

while True:
    ret, frame = cap.read()
    if ret == False: break

    frame = imutils.resize(frame, width=640)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    auxFrame = frame.copy()

    faces = faceClassif.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3)
    

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        rostro = auxFrame[y:y+h, x:x+w]
        rostro = cv2.resize(rostro, (150,150), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(os.path.join(personPath, f'rostro_{count}.jpg'), rostro)
        count += 1

    cv2.imshow('frame', frame)

    k = cv2.waitKey(1)
    if k == 27 or count >= 600:  
        break

cap.release()
cv2.destroyAllWindows()
