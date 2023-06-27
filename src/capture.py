import face_recognition
import cv2
import numpy as np


class CameraSwap:
    def __init__(self) -> None:
        self.capture = cv2.VideoCapture(0)
        self.face = cv2.imread("lianpu.png", cv2.IMREAD_UNCHANGED)
        self.end = False

    def one_frame(self):
        while not self.end:
            ret, frame = self.capture.read()
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)  # 各方向缩小 1/ 4, 方便处理
            rgb_small_frame = small_frame[:, :, ::-1]  # BGR (opencv) 转为 RGB, 即第三个维度反转
            face_locations = face_recognition.face_locations(rgb_small_frame)
            for top, right, bottom, left in face_locations:
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                top = max(0, top - int((bottom - top) / 4))
                # cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)  # 绘制方框
                swap = cv2.resize(self.face, (right - left, bottom - top))
                for i in range(3):
                    frame[top:bottom, left:right, i] = np.where(swap[:,:,3] == 0, frame[top:bottom, left:right, i], swap[:,:,i])
            frame=cv2.resize(frame,(960,540))
            imgencode=cv2.imencode('.jpg',frame)[1]
            stringData=imgencode.tostring()
            yield (b'--frame\r\n'
                b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

    def release(self):
        self.capture.release()
        self.end = True
