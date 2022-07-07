import os
import sys
import shutil
import numpy as np
import pandas as pd
import cv2

from tqdm import tqdm
from os import path 
from pathlib import Path
from pcgvs.extraction.track import run
from pcgvs.utils import get_video_nframes, get_video_duration

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


def extract_tubes(source, outputdir, conf_thres=0.15, yolo_weights='yolov5m6.pt', strong_sort_weights='osnet_x1_0_market1501.pt', threads=1):
    weights_folder = path.join(outputdir, 'weights')
    yolo_weights_path = path.join(weights_folder, yolo_weights)
    strong_sort_weights_path = path.join(weights_folder, strong_sort_weights) 
    if source == '' or source == '0':
        print("ERROR: you have to specify a correct video path")
        sys.exit(-1)
    run(
        source=source, 
        yolo_weights=yolo_weights_path, 
        strong_sort_weights=strong_sort_weights_path, 
        project=path.join(outputdir, 'tubes'),
        threads=threads, 
        conf_thres=conf_thres
    )
    tubes_filename = path.basename(source).split('.')[0] + '.txt'
    return path.join(outputdir, f'tubes/exp/tracks/{tubes_filename}')


def load_tubes_with_pandas(path):
    columns = ['frame', 'tag', 'x', 'y', 'w','h']
    with open(path) as output:
        rawdata = [ line.strip().split(' ')[:6] for line in output.readlines() ]
        df = pd.DataFrame(rawdata, columns=columns)
        df = df.astype('int')
    return df


def load_tubes_from_pandas_dataframe(df):
    tubes = []
    nframes = df.frame.max()
    for tag in df.tag.unique():
        ob_df = df[df['tag'] == tag]
        if (len(ob_df) < 10): continue # remove shadows
        ob_df = ob_df.sort_values(by='frame')
        sframe = ob_df.frame.min()
        eframe = ob_df.frame.max() 
        
        # TODO: Fix this check. It's better to determine if an object 
        # is stationary using the coordinates instead of this.  
        if (eframe - sframe >= nframes - 20): continue # remove stationary objects
        
        tube = Tube(tag, sframe, eframe)
        tubes.append(tube)
        for _, r in ob_df.iterrows():
            tube.next_bounding_box(r['x'], r['y'], r['w'], r['h'])
    return tubes 


def _create_frames_dictionary(source_tubes):
    frames = {}
    with open(source_tubes, 'r') as f:
        for line in f:
            f, id, x, y, w, h = line.split()[0:6]
            if int(f) not in frames.keys():
                frames[int(f)] = []
            frames[int(f)].append([id, int(x), int(y), int(w), int(h)])
    return frames


def extract_patches(source, outputdir, path_tubes):
    frames = _create_frames_dictionary(path_tubes)
    cap = cv2.VideoCapture(source)
    patchespath = path.join(outputdir, 'patches')    
    nframes = int(cap. get(cv2. CAP_PROP_FRAME_COUNT))
    pbar = tqdm(total=nframes)

    if path.exists(patchespath):
        shutil.rmtree(patchespath)
    os.mkdir(patchespath)    

    ret = True
    num_frame = 1
    while ret:
        ret, frame = cap.read()
        if frame is not None and num_frame in frames.keys():
            for id, x, y, w, h in frames[num_frame]:
                ROI = frame[y:y+h, x:x+w].copy()
                filename = str(id) + "_" + str(num_frame) + '.jpg'
                cv2.imwrite(path.join(patchespath, filename), ROI)
        num_frame += 1
        pbar.update(1)

    pbar.close()
    return patchespath


def extract_background(source, outputdir, path_tubes):
    frames = _create_frames_dictionary(path_tubes)
    cap = cv2.VideoCapture(source)
    ret = True
    count_bg = 0
    num_frame = 1
    bgpath = path.join(outputdir, 'background.jpg')
    emergencybg = None

    while ret:
        ret, frame = cap.read()
        if emergencybg is None and frame is not None:
            emergencybg = frame
        if num_frame in frames.keys():
            count_bg = 0
        elif count_bg > 10:
            cv2.imwrite(bgpath, frame)
            ret = False
        else:
            count_bg += 1
        num_frame += 1
        print(f'extracting background | frame {num_frame}')

    if count_bg <= 10:
        cv2.imwrite(bgpath, emergencybg)

    return bgpath
    