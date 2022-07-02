import click

from pcgvs.extraction import extract_tubes, extract_patches, extract_background, load_tubes_from_pandas_dataframe, load_tubes_with_pandas
from pcgvs.aggregation import solve, add_ss_to_dataframe
from pcgvs.synopsis import generate_frames, generate_synopsis

@click.command()
@click.option('-i',                     help='Source video path', required=True)
@click.option('-o',                     help='Path of the synopsis folder', required=True)
@click.option('-q',                     help="q parameter of L(q)-coloring problem.", default=3, show_default=True)
@click.option('-t',                     help="Threads used in Strong Sort algorithm.", default=1, show_default=True)
@click.option('-c',                     help="Confidence threshold for Yolov5.", default=0.15, show_default=True)
@click.option('--interp/--no-interp',   help="Interpolates the missing bounding boxes", default=True)
def synopsis(i, o, q, t, c, interp):

    # Extraction
    tubes_path = extract_tubes(source=i, outputdir=o, conf_thres=c, threads=t)
    patches_path = extract_patches(source=i, outputdir=o, path_tubes=tubes_path)
    background_path = extract_background(source=i, outputdir=o, path_tubes=tubes_path)

    # Aggregation
    dataframe = load_tubes_with_pandas(tubes_path)
    tubes = load_tubes_from_pandas_dataframe(dataframe)
    starting_times = solve(tubes, q)

    # Synopsis
    df = add_ss_to_dataframe(dataframe, tubes, starting_times)
    frames = generate_frames(df, patches_path)
    generate_synopsis(frames, o, 30, background_path, interp)


if __name__ == '__main__': synopsis()