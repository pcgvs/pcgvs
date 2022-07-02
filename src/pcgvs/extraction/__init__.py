import cv2
import numpy as np
import os
import sys

from pathlib import Path
from pcgvs.extraction.track import run

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # yolov5 strongsort root directory

class Tube: 
    

    def __init__(self, tag, sframe, eframe):
        self.tag = tag
        self.sframe = sframe 
        self.eframe = eframe 
        self.bbX = [] # bounding box x-axis 
        self.bbY = [] # bounding box y-axis
        self.bbH = [] # bounding box height
        self.bbW = [] # bounding box width


    def __len__(self):
        return len(self.bbX)
    

    def frame_length(self):
        return self.eframe - self.sframe
    

    def next_bounding_box(self, x, y, w, h):
        self.bbX.append(x)
        self.bbY.append(y)
        self.bbW.append(w)
        self.bbH.append(h)

    
    def get_bounding_box_at_frame(self, frame):
        i = frame - self.sframe
        return (self.bbX[i], self.bbY[i], self.bbW[i], self.bbH[i])
         
    
    def __iter__(self):
        self.iteridx = 0
        return self

    
    def __next__(self):
        if self.iteridx < len(self):
            frame = self.sframe + self.iteridx
            x, y, h, w = self.get_bounding_box_at_frame(frame)
            self.iteridx += 1
            return x, y, h, w, frame
        else:
            raise StopIteration
    
    
    def __str__(self):
        return self.tag

    
def extract_tubes(source, yolo_weights, strong_sort_weights):
    if source == '' or source == '0':
        print("ERROR: you have to specify a correct video path")
        sys.exit(-1)
    run(
        source=source, 
        yolo_weights=yolo_weights, 
        strong_sort_weights=strong_sort_weights
    )


def _create_frames_dictionary(source_tubes):
    frames = {}
    with open(source_tubes, 'r') as f:
        for line in f:
            f, id, x, y, w, h = line.split()[0:6]
            if int(f) not in frames.keys():
                frames[int(f)] = []
            frames[int(f)].append([id, int(x), int(y), int(w), int(h)])
    return frames


def extract_sub_images(path_tubes, media_path):
    frames = _create_frames_dictionary(path_tubes)
    cap = cv2.VideoCapture(media_path)
    folder_name = str(ROOT / (media_path.split("/")[-1])[:-4])
    
    try:
        os.mkdir(folder_name)
    except:
        print(f"ERROR: {folder_name} already exist")
        sys.exit(-1)
    
    ret = True
    num_frame = 1
    while ret:
        ret, frame = cap.read()

        if num_frame in frames.keys():
            for id, x, y, w, h in frames[num_frame]:
                ROI = frame[y:y+h, x:x+w].copy()
                cv2.imwrite(folder_name + "/" + str(id) + "_" + str(num_frame) + '.jpg', ROI)
        
        num_frame += 1


def extract_background(path_tubes, media_path):
    frames = _create_frames_dictionary(path_tubes)
    cap = cv2.VideoCapture(media_path)
    
    ret = True
    background = True
    count_bg = 0
    num_frame = 1
    while ret:
        ret, frame = cap.read()

        if num_frame in frames.keys():
            count_bg = 0
        elif background and count_bg > 8:
            background = False
            cv2.imwrite(str(ROOT / ((media_path.split("/")[-1])[:-4] + "_background.jpg")), frame)
            ret = False
        else:
            count_bg += 1
        
        num_frame += 1