import click

from os.path import join
from pcgvs.extraction import extract_tubes, extract_patches, extract_background, load_tubes_from_pandas_dataframe, load_tubes_with_pandas
from pcgvs.aggregation import solve, add_ss_to_dataframe
from pcgvs.synopsis import generate_frames, generate_synopsis

@click.command()
@click.option('-i',                 help='Source video path', required=True)
@click.option('-o',                 help='Path of the synopsis folder', required=True)
@click.option('-q',                 help="q parameter of L(q)-coloring problem.", default=3, show_default=True)
def synopsis(i, o, q):
    tubes_path = extract_tubes(source=i, outputdir=o)
    patches_path = extract_patches(source=i, outputdir=o, path_tubes=tubes_path)
    background_path = extract_background(source=i, outputdir=o, path_tubes=tubes_path)
    
    dataframe = load_tubes_with_pandas(tubes_path)
    tubes = load_tubes_from_pandas_dataframe(dataframe)
    starting_times = solve(tubes, q)

    df = add_ss_to_dataframe(dataframe, tubes, starting_times)
    frames = generate_frames(df, patches_path)
    generate_synopsis(frames, o, 30, background_path, True)


if __name__ == '__main__': synopsis()