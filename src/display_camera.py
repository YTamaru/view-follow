import tkinter as tk
import cv2
from PIL import Image,ImageTk
import numpy as np

root=tk.Tk()
root.title("camera")
root.geometry("720x480")
root.resizable(width=False, height=False)
canvas=tk.Canvas(root, width=640, height=480, bg="white")
canvas.pack()

def capStart():
    print('camera-ON')
    try:
        global c, w, h, img
        c=cv2.VideoCapture(0)
        w, h= c.get(cv2.CAP_PROP_FRAME_WIDTH), c.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print('w:'+str(w)+'px+h:'+str(h)+'px')
    except:
        import sys
        print("error-----")
        print(sys.exec_info()[0])
        print(sys.exec_info()[1])
        '''終了時の処理はここでは省略します。
        c.release()
        cv2.destroyAllWindows()'''

def u():#update
    global img
    ret, frame =c.read()
    if ret:
        img=ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        canvas.create_image(w/2,h/2,image=img)
    else:
        print("u-Fail")
    root.after(1,u)

capStart()
u()
root.mainloop()