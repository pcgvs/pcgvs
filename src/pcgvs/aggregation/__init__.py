from typing import List

from pcgvs.aggregation.coloring import color_graph, tubes_starting_time
from pcgvs.aggregation.graph import PCG
from pcgvs.aggregation.relations import RelationsMap
from pcgvs.extraction import Tube

def solve(tubes: List[Tube], q=3):
    print('computing the relations')
    relations = RelationsMap(tubes)
    print('Generating the potential collision graph')
    pcg = PCG(tubes, relations)
    print('Applying graph coloring algorithm')
    color_graph(pcg)
    return tubes_starting_time(pcg, q)


def add_ss_to_dataframe(dataframe, tubes, tubes_ss):
    """ Add the new starting time (frame) in the 
        extracted tubes dataframe.  
    """
    new_frames = []
    sframes = {}
    for tube in tubes:
        sframes[tube.tag] = tube.sframe
    for idx, row in dataframe.iterrows():
        if row['tag'] not in sframes: continue
        new_frame_start = row['frame'] - sframes[row['tag']] + tubes_ss[row['tag']]
        new_frames.append(new_frame_start)
    df = dataframe.copy()
    df = df.loc[df['tag'].isin(sframes.keys())]
    df = df.assign(newframe=new_frames)
    return df