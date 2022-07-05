import click
import cv2
import torch

from pcgvs.extraction import extract_tubes, extract_patches, extract_background, load_tubes_from_pandas_dataframe, load_tubes_with_pandas
from pcgvs.extraction.preprocessing import resize_from_center
from pcgvs.aggregation import solve, add_ss_to_dataframe
from pcgvs.aggregation.relations import RelationsMap
from pcgvs.aggregation.graph import PCG
from pcgvs.aggregation.coloring import color_graph, tubes_starting_time
from pcgvs.synopsis import generate_frames, generate_synopsis
from pcgvs.utils import get_video_resolution

@click.command()
@click.option('-i',                     help='Source video path', required=True)
@click.option('-o',                     help='Path of the synopsis folder', required=True)
@click.option('-q',                     help="q parameter of L(q)-coloring problem.", default=3, show_default=True)
@click.option('-t',                     help="Threads used in Strong Sort algorithm.", default=1, show_default=True)
@click.option('-c',                     help="Confidence threshold for Yolov5.", default=0.15, show_default=True)
@click.option('--interp/--no-interp',   help="Interpolates the missing bounding boxes", default=True)
def synopsis(i, o, q, t, c, interp):

    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        print('OpenCV is using GPU.')

    if torch.cuda.is_available():
        print('Torch is using GPU', torch.cuda.current_device())

    w, h = get_video_resolution(i)
    if w > 1280 or h > 1280:
        i = resize_from_center(i, 1280)

    # Extraction
    tubes_path = extract_tubes(source=i, outputdir=o, conf_thres=c, threads=t)
    patches_path = extract_patches(source=i, outputdir=o, path_tubes=tubes_path)
    background_path = extract_background(source=i, outputdir=o, path_tubes=tubes_path)

    # Aggregation
    dataframe = load_tubes_with_pandas(tubes_path)
    tubes = load_tubes_from_pandas_dataframe(dataframe)
    print('computing the relations')
    relations = RelationsMap(tubes)
    print(relations)
    print('Generating the potential collision graph')
    pcg = PCG(tubes, relations)
    print('Applying graph coloring algorithm')
    color_graph(pcg, q)
    starting_times = tubes_starting_time(pcg, q)


    # Synopsis
    df = add_ss_to_dataframe(dataframe, tubes, starting_times)
    frames = generate_frames(df, patches_path)
    generate_synopsis(frames, o, 30, background_path, interp)
    print('Video synopsis generated')


if __name__ == '__main__': synopsis()