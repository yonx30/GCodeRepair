


"""
# # Opens the inbuilt camera of laptop to capture video. 
# cap = cv2.VideoCapture(0) 
# i = 0
fileDir = os. getcwd()
# print(f"{fileDir}/Webcam Images/Frame {str(i)}.jpg")

# while(cap.isOpened()): 
#     ret, frame = cap.read() 
      
#     # This condition prevents from infinite looping  
#     # incase video ends. 
#     if ret == False: 
#         break
      
#     # Save Frame by Frame into disk using imwrite method 
#     cv2.imwrite(f"{fileDir}/Webcam Images/Frame {str(i)}.jpg", frame) 
#     i += 1
  
# cap.release() 
# cv2.destroyAllWindows()
"""
import os
import cv2 
import numpy as np
import time
from mss import mss
# from PIL import Image

fileDir = os. getcwd()

class screenRecorder:
    def __init__(self) -> None:
        self.bounding_box = {'top': 300, 'left': 500, 'width': 600, 'height': 600}
        self.sct = mss()

    def screenshot(self):
        
        sct_img = self.sct.grab(self.bounding_box)
        #print(sct_img)
        npImg = np.array(sct_img)
        #print(1, npImg)
        return npImg

