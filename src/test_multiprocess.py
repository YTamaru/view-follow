import multiprocessing as mp
from multiprocessing import Process,Manager
import tkinter as tk
import os
from time import sleep

class MainFrame(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.grid()
        self.MainCounter = 0
        self.MainMsg = "main({}):{}".format(\
                             os.getpid(),self.MainCounter)
        self.SubMsg = "sub:"
        self.CreateWidgets()
        self.shareDict = Manager().dict()
        self.SubProcess = Process(target=SubProcess\
                                  , args=(self.shareDict,))
        self.SubProcess.start()
        self.afterId = self.after(1000,self.Update)

        # self.shareDict = Manager().dict()
        # self.SubProcess = Process(target=SubProcess\
        #                           , args=(self.shareDict,))
        # self.SubProcess.start()
    def __del__(self):
        print("killing me")
        self.SubProcess.terminate()
    def CreateWidgets(self):
        self.MainLabel = tk.Label(self\
                ,text = str(self.MainMsg)\
                ,width=32)
        self.MainLabel.grid(row=1,column=1)
        self.SubLabel = tk.Label(self\
                ,text = str(self.SubMsg)\
                ,width=32)
        self.SubLabel.grid(row=1,column=2)
    def Update(self):
        self.MainCounter += 1
        self.MainMsg = "main({}):{}".format(\
                             os.getpid(),self.MainCounter)
        self.MainLabel.configure(text=self.MainMsg)
        self.SubMsg = "sub({}):{}".format(self.shareDict["PID"]\
                           ,self.shareDict["val"])
        self.SubLabel.configure(text=str(self.SubMsg))
        self.afterId = self.after(1000,self.Update)

def SubProcess(shareDict):  
    i = 0
    while i<1000:
        i += 1
        shareDict["PID"] = os.getpid()
        shareDict["val"] = i
        print(i)
        sleep(0.1)

if __name__ == '__main__': 
    root = tk.Tk()
    app = MainFrame(master=root)
    app.mainloop()
    app.__del__()

