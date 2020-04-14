import tkinter as tk
import os
from time import sleep
from imutils.video import VideoStream
from imutils import face_utils
import datetime
import imutils
import time
import dlib
import cv2
import numpy as np
from PIL import Image,ImageTk
from collections import deque
import argparse

class Linux_Fullscreen:
    def __init__(self):
        self.window = tk.Tk()
        self.window.attributes('-fullscreen', True)  
        self.fullScreenState = False
        self.window.bind("<F11>", self.toggleFullScreen)
        self.window.bind("<Escape>", self.quitFullScreen)

        self.window.mainloop()

    def toggleFullScreen(self, event):
        self.fullScreenState = not self.fullScreenState
        self.window.attributes("-fullscreen", self.fullScreenState)

    def quitFullScreen(self, event):
        self.fullScreenState = False
        self.window.attributes("-fullscreen", self.fullScreenState)

class FullScreenApp(object):
       def __init__(self, master, **kwargs):
           self.master=master
           pad=3
           self._geom='200x200+0+0'
           master.geometry("{0}x{1}+0+0".format(
               master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
           master.bind('<Escape>',self.toggle_geom)            
       def toggle_geom(self,event):
           geom=self.master.winfo_geometry()
           print(geom,self._geom)
           self.master.geometry(self._geom)
           self._geom=geom

class follow_single_image:
    def __init__(self, section, img_path):
        self.section = section
        self.img_path = img_path
        self.img = Image.open(open(self.img_path, "rb"))
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.title("facetracking")
        self.root.resizable(width=False, height=False)
        # initialize dlib's face detector (HOG-based) and then create
        # the facial landmark predictor
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("../data/shape_predictor_68_face_landmarks.dat")

        # initialize the video stream and allow the cammera sensor to warmup
        self.vs = VideoStream(usePiCamera=-1 > 0).start()
        self.frame = self.vs.read()

        self.X = deque([])
        self.Y = deque([])
        self.canvas=tk.Canvas(self.root, width=self.root.winfo_width(), height=self.root.winfo_height(), bg="white")
        self.canvas.pack()

        self.capStart()
        self.update()
        # self.root.mainloop()
    
    def capStart(self):
        print('camera-ON')
        try:
            self.img = self.img.resize((960, 800))
            w, h= self.img.size[0], self.img.size[1]
            self.img = ImageTk.PhotoImage(self.img)
            print('w:'+str(w)+'px+h:'+str(h)+'px')
        except:
            import sys
            print("error-----")
            print(sys.exec_info()[0])
            print(sys.exec_info()[1])
            '''終了時の処理はここでは省略します。
            c.release()
            cv2.destroyAllWindows()'''

    def update(self):
        #画像の削除
        self.canvas.delete("IMG")

        #start face tracking
        # grab the frame from the threaded video stream, resize it to
        # have a maximum width of 400 pixels, and convert it to
        # grayscale
        self.frame = imutils.resize(self.frame, width=400)
        cv2.imshow("camera",cv2.flip(self.frame,1))
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        # detect faces in the grayscale frame
        rects = self.detector(gray, 0)
        # loop over the face detections
        if rects:
            for rect in rects:
                # determine the facial landmarks for the face region, then
                # convert the facial landmark (x, y)-coordinates to a NumPy
                # array
                shape = self.predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
            center = np.mean(shape, axis=0)
            self.X.append(400-int(round(center[0])))
            self.Y.append(int(round(center[1])))
            if(len(self.X)>self.section):
                self.X.popleft()
                self.Y.popleft()
            print(self.X)
            print(self.Y)
            self.canvas.create_image(
                sum(self.X)/len(self.X), #移動平均で平滑化
                sum(self.Y)/len(self.Y),
                image = self.img,
                tag = "IMG",
                anchor = tk.NW #原点を左上に指定
                )
        else:
            pass
        self.root.after(1,self.update) #ms

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='image following by face tracking')
    #移動平均 (効果として，section大で顔位置静止時の画像のブレが小さくなるが，大きすぎると，画像の動きに遅延を感じる->5がベスト)
    parser.add_argument('--section', default=5, type=int, help='section number of moving average')
    parser.add_argument('--img_path', default="../data/test_figure.png", type=str, help="image to display")
    args = parser.parse_args()

    follow_single_image(args.section, args.img_path).mainloop()
