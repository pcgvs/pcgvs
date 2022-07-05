import cv2
import datetime

from PIL import Image
from os import path
from pcgvs.synopsis.interpolation import complete_frames


def generate_frames(dataframe, patches_path):
    frames = {}
    for idx, row in dataframe.iterrows():
        nf = int(row['newframe'])
        if nf not in frames: frames[nf] = []
        patchpath = path.join(patches_path, f'{row["tag"]}_{row["frame"]}.jpg')
        frames[nf].append({
            'tag': int(row['tag']), 
            'file': patchpath, 
            'x': int(row['x']), 
            'y': int(row['y']), 
            'w': int(row['w']), 
            'h': int(row['h']), 
            'frame': int(row['frame'])
        })     
    return frames


def generate_synopsis(frames, output_dir, fps, bgpath, interp=False):
    """
    """
    output = path.join(output_dir, 'synopsis.avi')
    _frames = frames.copy()
    max_frame = max(list(_frames.keys()))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    width, height = _get_video_shape(bgpath)

    out = cv2.VideoWriter(output, fourcc, fps, (width, height))

    if interp: _frames = complete_frames(_frames)    
    
    for num_frame in range(1, max_frame + 1):
        frame = cv2.imread(bgpath)
        if num_frame in _frames.keys():           
            objects = sorted(_frames[num_frame], key=lambda d: d['tag'], reverse=True) 
            for obj in objects:
                fr = obj.get('frame')
                s_img = cv2.imread(obj.get('file'))
                x = int(obj.get('x'))
                y = int(obj.get('y'))
                w = int(obj.get('w'))
                h = int(obj.get('h'))                
                time = str(datetime.timedelta(seconds=int(fr/30)))
                
                # TODO: When interpolation is activated, some bounding boxes
                # are positioned in ambiguous places and the following assignment 
                # fails. In order to succeed, we need to cut the bounding box according
                # to "frame" dimensions. 

                try:
                    frame[y:y+s_img.shape[0], x:x+s_img.shape[1]] = s_img
                    cv2.rectangle(frame,(x,y),(x+w,y+h), thickness=1, color=(214,73,51))
                    cv2.putText(frame, time,(x,y-20),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (244,43,3), 2)
                except:
                    continue
        try:
            out.write(frame)
        except:
            continue
    out.release()


def _get_video_shape(bgpath: str):
    img = Image.open(bgpath)
    return img.width, img.height