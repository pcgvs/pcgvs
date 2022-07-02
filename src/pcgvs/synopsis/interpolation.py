import numpy as np


def _unique_tags(frames):
    tags = set()
    for frame_content in frames.values():
        for object_data in frame_content:
            tags.add(object_data.get('tag'))
    return tags
    

def extract_frames_by_tag(frames, tag):
    keys = list(frames.keys())
    keys.sort()
    tagframes = {}
    for new_frame in keys:
        for data in frames[new_frame]:
            if tag == data.get('tag'):
                tagframes[new_frame] = data.copy()
                break
    return tagframes
    

def params_to_interpolate_by_tag(tagframes):
    x, y, f = [], [], []
    for content in tagframes.values():
        x.append(content.get('x'))
        y.append(content.get('y'))
        f.append(content.get('frame'))
    return x, y, f
        
    
def complete_frames(frames):
    """ Complete the frames dictionary interpolating the
        missing bounding boxes. 
    """
    tags = _unique_tags(frames)
    last_frame = max(list(frames.keys()))
    interpolated_frames = { i:[] for i in range(1, last_frame + 1) }
    for tag in tags:
        tagframes = extract_frames_by_tag(frames, tag)
        frames_of_tag = list(tagframes.keys())
        frames_of_tag.sort()
        X, Y, F = params_to_interpolate_by_tag(tagframes)
        for i in range(1, len(frames_of_tag)):
            prev_frame = frames_of_tag[i-1]
            curr_frame = frames_of_tag[i]
            xp  = [ prev_frame, curr_frame ]
            ypX = [ tagframes[prev_frame]['x'], tagframes[curr_frame]['x'] ]
            ypY = [ tagframes[prev_frame]['y'], tagframes[curr_frame]['y'] ]
            if curr_frame == prev_frame + 1: continue
            for j in range(prev_frame + 1, curr_frame):     
                x_pred = np.interp(j, xp, ypX)
                y_pred = np.interp(j, xp, ypY)
                tagframes[j] = tagframes[prev_frame].copy()
                tagframes[j]['x'] = x_pred
                tagframes[j]['y'] = y_pred
        for frame in range(1, last_frame):
            if frame not in tagframes:
                continue
            interpolated_frames[frame].append(tagframes[frame])
    return interpolated_frames