
import cv2
from nanotreackv2.core.nano_tracker import NanoTracker
from nanotreackv2.wrapper import TrackerWrapper
import numpy as np
import json
import sys
import time
import os

class VideoProcessor:
    def __init__(self, video_path, roi):

        self.video_path = video_path
        self.roi = roi
        self.treacker = NanoTracker()
        self.tracker_wrapper = TrackerWrapper(self.treacker)

        self.name="nanotreackerv2"
        self.output_file  = open(f"{os.path.splitext(self.video_path)[0]}_{self.name}.txt", 'w')
        self.display_name="nanotreackerv2"

    def process(self):
        # Это просто пример, вы можете добавить сюда свою логику обработки видео
        print(f"Обработка видео: {self.video_path}")
        print(f"Используя ROI: {self.roi}")

        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print(f"Не удалось открыть видеофайл {self.video_path}")
            return
        
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        frame_fps=  int(cap.get(5))
      
        video_writer = cv2.VideoWriter(f"{os.path.splitext(self.video_path)[0]}_{self.name}.avi", cv2.VideoWriter_fourcc('M','J','P','G'), frame_fps, (frame_width, frame_height))
        frame_count=0
        ret, frame = cap.read()
         
        frame_last = frame.copy()
        self.tracker_wrapper.init(frame, frame, self.roi)
        


        while True:
                    ret, frame = cap.read()
                    frame_count+=1
          
                    if frame is None:
                        break

                    frame_disp = frame.copy()

                    # Draw box
                    font_color = (0, 0, 0)
                   
                        
        
                    bbox, score, technical_rect,(x_point,y_point) = self.tracker_wrapper.track(frame, frame_last)
                    x, y, w, h = bbox
                    
                    
                    norm_x = x / frame_width
                    norm_y = y / frame_height
                    norm_w = w / frame_width
                    norm_h = h / frame_height

                    self.output_file.write(f"{frame_count:.6f} {norm_x:.6f} {norm_y:.6f} {norm_w:.6f} {norm_h:.6f}\n")
                    
                    
                    
                    x1, y1, x2, y2 = int(x), int(y), \
                    int(x + w), int(y + h)
                    cv2.rectangle(frame_disp, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                    frame_disp = cv2.circle(frame_disp, (int(x_point),int(y_point)), 5, (255,0,255), 2) 
                    cv2.rectangle(frame_disp, (int(technical_rect[0]), int(technical_rect[1])), (int(technical_rect[0]+technical_rect[2]), int(technical_rect[1]+technical_rect[3])), (255, 255, 0), 2)
                        
                        
                    cv2.putText(frame_disp, 'Tracking! ' + str(score), (20, 130), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                            font_color, 1)

                    cv2.putText(frame_disp, 'Press q to quit', (20, 80), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                            font_color, 1)           
                    
                    frame_last = frame.copy()
                    cv2.imshow(self.display_name, frame_disp)
                    video_writer.write(frame_disp)
                    key = cv2.waitKey(1)
                    if key == ord('q'):
                        break
                   

                # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()
        video_writer.release()
        self.output_file.close()
                
        

    