from keras.preprocessing.image import img_to_array
import imutils
import cv2
from keras.models import load_model
import numpy as np
import pymysql
import random
from tkinter import messagebox

face_detection = cv2.CascadeClassifier('haarcascade_files/haarcascade_frontalface_default.xml')
emotion_classifier = load_model('models/_mini_XCEPTION.102-0.66.hdf5', compile=False)
EMOTIONS = ["злость", "отвращение", "страх", "счастье", "грусть", "удивление", "нейтральный"]
con = pymysql.connect(host="localhost", user="root", password="root", database="test2")
cur = con.cursor()

randEMOTIONS = ["злость", "отвращение", "страх", "счастье", "удивление"]
need = random.choice(randEMOTIONS)
cv2.namedWindow("camera")
camera = cv2.VideoCapture(0)
camera.set(3, 640)  # widht
camera.set(4, 480)  # height
messagebox.showinfo("Эмоция", f"Изобразите {str(need)}")
while True:
    frame = camera.read()[1]

    frame = imutils.resize(frame, width=640)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detection.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),
                                            flags=cv2.CASCADE_SCALE_IMAGE)

    canvas = np.zeros((250, 300, 3), dtype="uint8")
    frameClone = frame.copy()

    if len(faces) > 0:
        faces = sorted(faces, reverse=True,
                       key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
        (fX, fY, fW, fH) = faces

        roi = gray[fY:fY + fH, fX:fX + fW]
        roi = cv2.resize(roi, (64, 64))
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)

        preds = emotion_classifier.predict(roi)[0]
        emotion_probability = np.max(preds)
        label = EMOTIONS[preds.argmax()]

        if label == need:
            if emotion_probability > 0.5:
                cur.execute("update settings set value = 1 where id = 2")
                con.commit()
                break
    else:
        continue

    for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds)):
        text = "{}: {:.2f}%".format(emotion, prob * 100)

        w = int(prob * 300)
        cv2.rectangle(canvas, (7, (i * 35) + 5),
                      (w, (i * 35) + 35), (0, 0, 255), -1)
        cv2.putText(canvas, text, (10, (i * 35) + 23), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frameClone, label, (fX, fY - 10), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH), (0, 0, 255), 2)

    cv2.imshow("camera", frameClone)
    cv2.imshow("probabilities", canvas)

    k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
    if k == 27:
        break

camera.release()
cv2.destroyAllWindows()
