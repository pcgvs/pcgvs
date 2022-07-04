from cmath import e
import numpy as np
import json

from tqdm import tqdm
from itertools import permutations


class Overlapping:

    def __init__(self, start, end):
        self.sframe = start
        self.eframe = end
    
    def __str__(self):
        return 'OVL'

#---------------------------------------#
#---------------------------------------#
#---------------------------------------#
    
class Intersection:
    
    def __init__(self, frame):
        self.frame = frame
    
    def __str__(self):
        return 'INT'
    
#---------------------------------------#
#---------------------------------------#
#---------------------------------------#

class RelationsMap:

    def __init__(self, tubes):
        self.tubes = tubes
        self.relations = {}
        self._fill_with_irrilevant_relations()
        self._compute()


    # @staticmethod
    # def precomputed_from_json(tubes, path):
    #     try:
    #         with open(path, 'r') as jsonfile:
    #             relations = json.load(jsonfile)
    #             rmap = RelationsMap(tubes)
    #             rmap.relations = relations
    #             return rmap
    #     except:
    #         raise Exception('File not found.')


    def _fill_with_irrilevant_relations(self):
        for Ta in self.tubes:
            self.relations[Ta.tag] = {}
            for Tb in self.tubes:
                self.relations[Ta.tag][Tb.tag] = None


    def _compute(self):
        n = len(self.tubes) 
        for Ta, Tb in tqdm(permutations(self.tubes, 2), total=n*(n-1)):
            if Ta == Tb: continue
            # we focus on tube A and check the intersections with Tube B. 
            ffintersec = None # first frame of intersection.
            lfintersec = None # last frame of intersection.

            for adata in Ta:
                for bdata in Tb:
                    frame = adata[4]
                    if self._frames_intersect(adata, bdata):
                        ffintersec = frame if ffintersec is None else ffintersec
                        lfintersec = frame

            # In this case, there isn't interaction.
            if lfintersec is None: continue
            # Following the paper recommendations, we 
            # set the interaction as overlapping if there 
            # are more than 5 intersecting frames. 
            delta = lfintersec - ffintersec

            if self.relations[Tb.tag][Ta.tag] is not None:
                # If Tb-Ta relation is computed as INT or OVL, we need to
                # stick with the previous type of relation. 
                prel = self.relations[Tb.tag][Ta.tag]
                self.relations[Ta.tag][Tb.tag] = Intersection(ffintersec) \
                    if type(prel) == Intersection \
                    else Overlapping(ffintersec, lfintersec)         
            else: 
                self.relations[Ta.tag][Tb.tag] = Intersection(ffintersec) \
                    if lfintersec - ffintersec < 5 \
                    else Overlapping(ffintersec, lfintersec)
              

    def _frames_intersect(self, adata, bdata):
        xa, ya, wa, ha, _ = adata
        xb, yb, wb, hb, _ = bdata
        l_ax, l_ay = xa, ya             # Top-left point of square A
        r_ax, r_ay = xa + wa, ya + ha   # Bottom-right point of square A
        l_bx, l_by = xb, yb             # Top-left point of square B
        r_bx, r_by = xb + wb, yb + hb   # Bottom-right point of square B
        # Check if one square has empty area.
        if l_ax == r_ax or l_ay == r_ay or l_bx == r_bx or l_by == r_by:
            return False
        # Check if one square stands above the other.
        if r_ay < l_by or r_by < l_ay:
            return False
        # Check if one square stands on the left of the other
        if r_ax < l_bx or r_bx < l_ax:
            return False
        # The squares overlap!
        return True
    
    
    def as_dict(self):
        return self.relations
    

    # def as_json(self, path):
    #     with open(path, 'w') as jsonfile:
    #         dcp = self.as_dict().copy()
    #         for k in dcp:

    #         json.dump(self.as_dict(), jsonfile)


    def __str__(self):
        out = ""
        for k1 in self.relations.keys():
            out += f'[{k1}]:\t'
            for k2 in self.relations.keys():
                out += f'({k2}){self.relations[k1][k2]}\t'
            out += '\n'
        return out
