import cv2
import numpy as np

from pcgvs.utils import get_video_duration, get_video_resolution


def FR(synopsis_video_path: str, original_video_path: str):
    """ Frame condensation ratio """
    Ts = get_video_duration(synopsis_video_path)
    Ti = get_video_duration(original_video_path)
    return Ts / Ti


def CR(synopsis_video_path: str, frames: dict):
    """ Frame compact rate """
    w, h = get_video_resolution(synopsis_video_path)
    multiplier = 1 / (w * h * len(frames))
    foreg_area = 0
    for objects in frames.values():
        for obj in objects:
            x, y, _w, _h = obj['x'], obj['y'], obj['w'], obj['h']
            foreg_area += min(_w, w - x) * min(_h, h - y)
    _CR = multiplier * foreg_area
    return _CR


def OR(synopsis_video_path: str, frames: dict):
    """ Overlap ratio """
    w, h = get_video_resolution(synopsis_video_path)
    multiplier = 1 / (w * h * len(frames))
    overlap_area = 0
    for objects in frames.values():
        F = np.zeros((w, h))
        for obj in objects:
            x, y, _w, _h = obj['x'], obj['y'], obj['w'], obj['h'] 
            F[x:(x+_w), y:(y+_h)] += np.ones((min(_w, w - x), min(_h, h - y)))
        overlap_area += (F > 1).sum()
    _OR = multiplier * overlap_area
    return _OR