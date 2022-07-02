import cv2
import numpy as np
import argparse
import sys

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str, default='', help='file/dir/URL/glob')
    parser.add_argument('--dimension', type=str, default='1280', help='1280 o 640')
    parser.add_argument('--output', type=str, default='output.mp4')
    opt = parser.parse_args()
    if opt.source == '':
        print("Error: you have to specify the source video")
        sys.exit(-1)
    if opt.dimension != '1280' and opt.dimension != '640':
        print("Error: you have to specify 1280 or 640 in dimension")
        sys.exit(-1)
    return opt


def main(source, dimension='1280', output='output.mp4'):
    cap = cv2.VideoCapture(source)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    dimension = int(dimension)
    if dimension == 640:
        out = cv2.VideoWriter(output, fourcc, 30, (640,640))
    else:
        out = cv2.VideoWriter(output, fourcc, 30, (1280,1280))
    
    while True:
        ret, frame = cap.read()
        if ret == True:
            (height, width) = frame.shape[:2]

            #640*640
            if dimension == 640:
                b = frame[int(height/2)-100:int(height/2)+540, int(width/2)-320:int(width/2)+320]

            #1280*1280
            else:
                b = frame[0:int(height), int(width/2)-640:int(width/2)+640]
                b = np.append(b, b[-200:], axis=0)

            out.write(b)
        else:
            break
        
    cap.release()
    out.release()


if __name__ == "__main__":
    opt = parse_opt()
    main(**vars(opt))