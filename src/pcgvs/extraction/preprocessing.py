import cv2

from os import path

def resize_from_center(videopath: str, new_w=1280) -> str:
    """ Resize the video resolution given a width and 
        returns the path of the resized video. 
    """
    basename = path.basename(videopath)
    resizename = '-resized.'.join(basename.split('.'))
    resizepath = path.join(path.dirname(videopath), resizename)

    cap = cv2.VideoCapture(videopath)

    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    new_h = int((new_w * h) / w)
    
    needs_crop = new_h > new_w
        
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(resizepath,fourcc, int(fps), (new_w, new_w if needs_crop else new_h))

    while True:
        ret, frame = cap.read()
        if ret == True:
            b = cv2.resize(frame,(new_w, new_h),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
            if needs_crop:
                center = b.shape[0] / 2, b.shape[1] / 2
                x = center[1] - new_w/2
                y = center[0] - new_h/2
                b = b[int(y):int(y+new_w), int(x):int(x+new_w)]
            out.write(b)
        else: break
    
    cap.release()
    out.release()
    return resizepath