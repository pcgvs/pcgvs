import numpy as np

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
        