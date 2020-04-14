import os
import tkinter as tk
from tkinter import *
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
import multiprocessing as mp
from multiprocessing import Process, Value


parser = argparse.ArgumentParser(description='image following by face tracking')
#移動平均フィルタ (効果として，section大で顔位置静止時の画像のブレが小さくなるが，大きすぎると，画像の動きに遅延を感じる)
parser.add_argument('--section', default=3, type=int, help='section number of moving average')
parser.add_argument('--bg_img_path', default="../data/bg.jpg", type=str, help="background image to display")
parser.add_argument('--layer1_img_path', default='../data/layer1.png', type=str, help="layer1 foreground image to display")
# parser.add_argument('--layer2_img_path', default='../data/layer2.png', type=str, help="layer2 foreground image to display")
parser.add_argument('--windowframe', default="../data/windowframe.png", type=str, help="window frame image to display")
args = parser.parse_args()

global detector, predictor, vs
# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("../data/shape_predictor_68_face_landmarks.dat")
# initialize the video stream and allow the cammera sensor to warmup
vs = VideoStream(usePiCamera=-1 > 0).start()
frame = vs.read()


class MainWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.attributes('-fullscreen', True)
        self.master.title("facetracking")
        self.master.resizable(width=False, height=False)
        self.canvas=tk.Canvas(self.master, width=self.master.winfo_width(), height=self.master.winfo_height(), bg="white")
        self.canvas.pack()
        print("MainWindowSize:", self.master.winfo_width(), self.master.winfo_height()) #(1440,900)
        self.mainwindowsize = (self.master.winfo_width(), self.master.winfo_height())
        print('camera-ON')
        self.frame_size = (255,400,3)

        try:
            self.bg_img = Image.open(open(args.bg_img_path, "rb"))
            self.bg_img_ = self.bg_img.resize(self.mainwindowsize)
            self.bg_img = ImageTk.PhotoImage(self.bg_img_)

            self.l1_img = Image.open(open(args.layer1_img_path, "rb"))
            self.l1_img = self.l1_img.resize(self.mainwindowsize) 

            self.l1_img = ImageTk.PhotoImage(self.l1_img)

            # self.l2_img = Image.open(open(args.layer2_img_path, "rb"))
            # self.l2_img = self.l2_img.resize(self.mainwindowsize)
            # self.l2_img = ImageTk.PhotoImage(self.l2_img)

            # # add Windowframe
            # self.wf_img = Image.open(open(args.windowframe, "rb"))
            # self.wf_img = self.wf_img.resize(self.mainwindowsize)
            # self.wf_img = ImageTk.PhotoImage(self.wf_img)

        except:
            import sys
            print("error-----")
            print(sys.exec_info()[0])
            print(sys.exec_info()[1])
            '''終了時の処理はここでは省略します。
            c.release()
            cv2.destroyAllWindows()'''

        self.afterId = self.after(1,self.update)      
        self.shareX = Value("i", int(self.mainwindowsize[0]/2))
        self.shareY = Value("i", int(self.mainwindowsize[1]/2))
        self.SubProcess = Process(target=SubProcess, args=(self.shareX, self.shareY,))
        self.SubProcess.daemon = True
        self.SubProcess.start()

    
    def __del__(self):
        print("killing me")
        self.SubProcess.terminate()

    def update(self):#update
        """
        start face tracking
        grab the frame from the threaded video stream, resize it to
        have a maximum width of 400 pixels, and convert it to
        """
        t1 = time.time()
        #delete all images -> not to press memory
        self.canvas.delete("BGIMG")
        self.canvas.delete("L1IMG")
        # canvas.delete("L2IMG")
        # self.canvas.delete("WFIMG")
        print("(X,Y):", self.shareX.value, self.shareY.value)

        #background
        #顔の垂直方向の位置によって画像を縮小拡大する（上なら縮小，下なら拡大）
        # self.bg_img_ = self.bg_img_.resize((self.mainwindowsize[0],int(round(self.mainwindowsize[1]*(1+((self.shareY.value-self.frame_size[1]/2)/(self.frame_size[1]/2))*0.1)))))
        # print(self.bg_img_.size)
        # self.bg_img = ImageTk.PhotoImage(self.bg_img_)
        
        self.canvas.create_image(
            self.mainwindowsize[0]/2+(self.shareX.value-self.frame_size[1]/2)*0.1, #移動平均で平滑化
            self.mainwindowsize[1]/2+(self.shareY.value-self.frame_size[0]/2)*0.1,
            image = self.bg_img,
            tag = "BGIMG"
            )

        #layer1
        #背景の移動に対して前景のレイヤは1.1倍の速さで動かす
        self.canvas.create_image(
            self.mainwindowsize[0]/2+(self.shareX.value-self.frame_size[1]/2)*0.11,
            self.mainwindowsize[1]/2+(self.shareY.value-self.frame_size[0]/2)*0.11,
            image = self.l1_img,
            tag = "L1IMG"
        )

        ##layer2
        # self.canvas.create_image(
        #     self.mainwindowsize[0]/2+(sum(X)/len(X)-frame_size[1]/2)*0.15,
        #     self.mainwindowsize[1]/2+(sum(Y)/len(Y)-frame_size[0]/2)*0.15,
        #     image = self.l2_img,
        #     tag = "L2IMG"
        # )
        
        # #window frame
        # self.canvas.create_image(
        #     self.mainwindowsize[0]/2,
        #     self.mainwindowsize[1]/2,
        #     image = self.wf_img,
        #     tag = "WFIMG"
        #     )

        # #add virtual window frame
        # self.canvas.create_line(
        #     0,0,
        #     0,self.mainwindowsize[1],
        #     fill="black",
        #     width=30
        # )
        # self.canvas.create_line(
        #     0,self.mainwindowsize[1],
        #     self.mainwindowsize[0],self.mainwindowsize[1],
        #     fill="black",
        #     width=30
        # )
        # self.canvas.create_line(
        #     self.mainwindowsize[0],self.mainwindowsize[1],
        #     self.mainwindowsize[0],0,
        #     fill="black",
        #     width=30
        # )
        # self.canvas.create_line(
        #     self.mainwindowsize[0],0,
        #     0,0,
        #     fill="black",
        #     width=30
        # )

        # self.canvas.pack()

        self.afterId = self.after(1,self.update) #ms
        t2 = time.time()
        elapsed_time = t2-t1
        print("processing time:", elapsed_time)
        print("fps: ", 1/elapsed_time)

def SubProcess(shareX, shareY):
    X = deque([])
    Y = deque([])
    # loop over the face detections
    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        frame_size = frame.shape #camera window size(255,400,3)
        cv2.imshow("camera",cv2.flip(frame,1)) #顔ウィンドウを表示させると動作が重くなる
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # grayscale

        # detect faces in the grayscale frame
        rects = detector(gray, 0) #the number of person in the frame
        if rects:
            for rect in rects:
                # determine the facial landmarks for the face region, then
                # convert the facial landmark (x, y)-coordinates to a NumPy
                # array
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
            center = np.mean(shape, axis=0)

            X.append(frame_size[1]-int(round(center[0])))
            Y.append(int(round(center[1])))
            if(len(X)>args.section):
                X.popleft()
                Y.popleft()
            shareX.value = int(round(sum(X)/len(X)))
            shareY.value = int(round(sum(Y)/len(Y)))
            print("re(X,Y):", X, Y)
        else:
            pass

if __name__ == '__main__': 
    root=tk.Tk()
    app = MainWindow(master=root)
    app.mainloop()
