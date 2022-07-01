from typing import List

from pcgvs.aggregation.coloring import color_graph, tubes_starting_time
from pcgvs.aggregation.graph import PCG
from pcgvs.aggregation.relations import RelationsMap
from pcgvs.extraction import Tube

def solve(tubes: List[Tube], q=3):
    relations = RelationsMap(tubes)
    pcg = PCG(tubes, relations)
    color_graph(pcg)
    return tubes_starting_time(pcg, q)
