import cv2
import pymysql
import datetime

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = 'haarcascade_files/haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascadePath);
font = cv2.FONT_HERSHEY_COMPLEX

id = 0

con = pymysql.connect(host="localhost", user="root", password="root", database="test2")
cur = con.cursor()
cur.execute("select * from user_information")
rows = cur.fetchall()

names = ['Никто']
last = 1
for row in rows:
    names.append(row[1])
cur.execute("select * from enters order by id desc")
row = cur.fetchone()
lastEnter = 1
print(names)

cam = cv2.VideoCapture(0)
cam.set(3, 640)  # widht
cam.set(4, 480)  # height

minW = 0.1 * cam.get(3)
minH = 0.1 * cam.get(4)
while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(int(minW), int(minH)),
    )
    if len(faces) > 1:
        if lastEnter != 2:
            cur.execute(
                "insert into enters(user_id,datetime,action) values(%s,%s,%s)",
                (
                    row[1], datetime.datetime.now(), 'Несколько лиц'
                ))
            con.commit()
        lastEnter = 2
    elif len(faces) == 0:
        if lastEnter != 0:
            cur.execute(
                "insert into enters(user_id,datetime,action) values(%s,%s,%s)",
                (
                    row[1], datetime.datetime.now(), 'Нет лиц'
                ))
            con.commit()
        lastEnter = 0
    else:
        lastEnter = 1

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

        if (confidence < 70):
            id = names[id]

            confidence = "  {0}%".format(round(100 - confidence))
            cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)
        else:
            id = "неопознанный"
            cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)

    cv2.imshow('camera', img)
    k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
    if k == 27:
        break

print("\nВыход из программы")
cam.release()
cv2.destroyAllWindows()
