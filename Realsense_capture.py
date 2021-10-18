# -*- coding: utf-8 -*-

#############################################
import pyrealsense2 as rs
import numpy as np
import cv2

import tkinter as tk
import tkinter.filedialog as tkfile

import threading
import csv

#depth_gray_image=[]
color_image=[]
depth_csv = []

depth_frame=[]

def realsense_main():
    #global depth_gray_image
    global color_image
    global depth_frame

    # ストリーム(Color/Depth)の設定
    config = rs.config()
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

    # ストリーミング開始
    pipeline = rs.pipeline()
    profile = pipeline.start(config)

    try:
        while True:
            # フレーム待ち(Color & Depth)
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()
            if not depth_frame or not color_frame:
                continue
            color_image = np.asanyarray(color_frame.get_data())
            # Depth画像
            depth_color_frame = rs.colorizer().colorize(depth_frame)
            depth_color_image = np.asanyarray(depth_color_frame.get_data())
            
            
            # 表示
            cv2.namedWindow('RGB', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('RGB',640,360)
            cv2.imshow('RGB', color_image)

            depth_gray_image = cv2.split(depth_color_image)[1]
            cv2.namedWindow('Depth', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Depth',640,360)
            cv2.imshow('Depth', depth_gray_image)


            if cv2.waitKey(1) & 0xff == 27:
                break

    finally:
        # ストリーミング停止
        pipeline.stop()
        cv2.destroyAllWindows()

##### Tkinter ###################################################################
class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.geometry('400x400')
        #self.fullScreenState = True
        self.switch_frame(page1)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

class page1(tk.Frame):
    count = 0
    path = []

    depth_csv=[]
    data_save=[]

    def __init__(self, master):
        tk.Frame.__init__(self, master, width=400, height=400)
        tk.Label(self, text="Capture", font=('Helvetica', 18, "bold")).place(x=30,y=30)
        capture_btn=tk.Button(self)
        capture_btn.configure(text="Capture", command=lambda: page1.capture_frame(0))
        capture_btn.place(x=180, y=180)
        page1.select_folder(0)

    def capture_frame(self):

        save_name_rgb=page1.path+'\capture_'+str(page1.count)+'_RGB.jpg'
        save_name_dep=page1.path+'\capture_'+str(page1.count)+'_DEP.csv'
        cv2.imwrite(save_name_rgb,color_image)
        #cv2.imwrite(save_name_dep,depth_gray_image)

        #page1.depth_csv.clear()
        with open(save_name_dep,'w',newline="") as f:
            writer = csv.writer(f)
            print([depth_frame.get_height(),depth_frame.get_width()])
            for i in range(depth_frame.get_height()):
                page1.data_save.clear()
                for j in range(depth_frame.get_width()):
                    page1.data_save.append(depth_frame.get_distance(j,i))
                #page1.depth_csv.append(page1.data_save)
                writer.writerow(page1.data_save)            

        page1.count = page1.count+1

    def select_folder(self):
        save_ret = tkfile.askdirectory(title='select save folder', mustexist = True)
        page1.path.clear()
        page1.path=save_ret

##### Main ###############################################################
if __name__ == "__main__":
    t1 = threading.Thread(target=realsense_main)
    t1.start()
    app = SampleApp()
    app.mainloop()