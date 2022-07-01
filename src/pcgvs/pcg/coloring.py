import operator
import numpy as np
import networkx as nx

from pcgvs.pcg.graph import PCG


class SaturationCache:
    
    def __init__(self, pcg: PCG):
        self.pcg = pcg
        self.Sl   = {}
        self.Sapp = {}
        self.Spc  = {}
        self._init_params()
    
    def _init_params(self):
        """ Precalculate some parameters used in the metrics. 
        """
        tubes = self.pcg.tubes
        self.video_frames = max([ tube.eframe for tube in tubes ])
        self.max_length_tube = max([ tube.frame_length() for tube in tubes ])
          
    
    def _Sl(self, nodekey):
        """ Mesure the relative length (in terms of frames) of the
            tube corresponding to the node referenced by nodekey. The
            mesure is normalized using the tube with maximum length. 
        """
        if nodekey in self.Sl: return self.Sl[nodekey]
        tube  = self.pcg.nodes[nodekey].tube
        self.Sl[nodekey] = tube.frame_length() / self.max_length_tube
        return self.Sl[nodekey]
    
    
    def _Sapp(self, nodekey):
        """ Mesure the relative time of appearance of the tube 
            corresponding to the node referenced by nodekey.
        """
        if nodekey in self.Sapp: return self.Sapp[nodekey]
        tube  = self.pcg.nodes[nodekey].tube
        self.Sapp[nodekey] = (self.video_frames - tube.sframe) / self.video_frames
        return self.Sapp[nodekey]
    
    
    def _Spc(self, nodekey):
        """ <Not sure this is correct, check out the paper>
        """
        if nodekey in self.Spc: return self.Spc[nodekey]
        tube  = self.pcg.nodes[nodekey].tube
        same_mnode = len([ node for node in self.pcg.nodes.values() if node.tube.tag == tube.tag ])
        self.Spc[nodekey] =  same_mnode / len(self.pcg.nodes)
        return self.Spc[nodekey]
    
    
    def _Sd(self, nodekey):
        """ Classic saturation, but normalized. Counts the number
            of different colors in the adjacents nodes of the node
            referenced by nodekey. This one cannot be cached. 
        """
        #---------------------------------------#
        # Fix this metric! That's not the metric read in the paper. 
        #---------------------------------------#        
        nodes_weight_map = self.pcg.A[nodekey]
        adjacent_nodes = [ v for v, w in nodes_weight_map.items() if w != 0 ]
        sat = len([ k for k in adjacent_nodes if self.pcg.nodes[k].color is not None ])
        return sat / len(self.pcg.nodes)
    
    
    def saturation(self, nodekey):
        """ Calculate the saturation of the node.
        """
        return self._Sd(nodekey) \
             + self._Sl(nodekey) \
             + self._Sapp(nodekey) \
             + self._Spc(nodekey)
    
    def saturations(self, nodekeys):
        """ Calculate the saturation of all the nodes. 
        """
        return { k:self.saturation(k) for k in nodekeys }
    
#---------------------------------------#
#---------------------------------------#
#---------------------------------------#

def q_far_apart(pcg, proposed_color, nodekey, q=5):
    """ This condition imposes that all the nodes connected by an
        edge weighted 1 (intersection) to the node referenced by node-key, 
        must be at least q color far apart. 
    """
    adjacents = pcg.adjacents(nodekey)
    for key, node in adjacents:
        if pcg.A[nodekey][key] != 1: continue 
        if node.color is None: continue
        if np.abs(node.color - proposed_color) <= q:
            return False
    return True

#---------------------------------------#
#---------------------------------------#
#---------------------------------------#

def does_not_overlap(pcg: PCG, proposed_color, nodekey):
    """ See condition 2 in paper He et Al. 
    """
    if pcg.generated_by_intersection(nodekey): return True
    vi, vj, vip, vjp = pcg.identify_quatern(nodekey)
    vi, vj, vip, vjp = pcg.node(vi), pcg.node(vj), pcg.node(vip), pcg.node(vjp)
    if vip.color is None or vjp.color is None: return True
    tij = vj.frame - vi.frame
    return (proposed_color - vip.color) * (proposed_color + tij - vjp.color) > 0

#---------------------------------------#
#---------------------------------------#
#---------------------------------------#

def ssort(saturations, pcg):
    """
    """
    olist = []
    nnodes = len(saturations)
    while len(olist) < nnodes:
        max_sat = max(saturations.values())
        ties = [ nk for nk in saturations.keys() if saturations[nk] == max_sat ]
        appearings = { nk:pcg.nodes[nk].tube.sframe for nk in ties }
        winner_key = min( appearings.items(), key=operator.itemgetter(1) )[0]
        olist.append(winner_key)
        del saturations[winner_key]
    return olist

#---------------------------------------#
#---------------------------------------#
#---------------------------------------#

def color_graph(pcg: PCG, q=5):
    """
    """
    color = 1
    pcg.clean_colors()
    sc = SaturationCache(pcg)    
    
    while len(pcg.uncolored_nodes()) > 0:
        nodes_not_colored = pcg.uncolored_nodes()
        saturations = sc.saturations(nodes_not_colored)
        ordered_list = ssort(saturations, pcg)
        saturations = sc.saturations(nodes_not_colored)
        
        for nodekey in ordered_list:
            if pcg.node(nodekey).color is not None: continue
            if q_far_apart(pcg, color, nodekey, q) and does_not_overlap(pcg, color, nodekey):
                
                pcg.nodes[nodekey].color = color
                if pcg.generated_by_overlapping(nodekey):
                    oppnode = pcg.node(pcg.identify_opposite(nodekey))
                    if oppnode.color is not None: continue
                    m = 1 if nodekey[-1] == 's' else -1
                    vs, ve, _, _ = pcg.identify_quatern(nodekey)
                    delta = pcg.node(ve).frame - pcg.node(vs).frame
                    oppnode.color = color + m * delta  

        color += 1
        
#---------------------------------------#
#---------------------------------------#
#---------------------------------------#


def starting_nodes_or_intersections(pcg, tube):
    selected_nodes = []
    for key, node in pcg.nodes.items():
        if node.tube.tag != tube.tag or key[-1] == 'e': continue
        selected_nodes.append((key, node))
    return selected_nodes

#---------------------------------------#
#---------------------------------------#
#---------------------------------------#



def tubes_starting_time(pcg: PCG, q=3):

    def get_ordered_dict(_dict, keys_vocab):
        return { k: v for k, v in sorted(_dict.items(), key=lambda item: item[1]) if k in keys_vocab}

    li = {}
    for tube in pcg.tubes:
        nodes = starting_nodes_or_intersections(pcg, tube)
        optim = lambda node: node.color - (node.frame - tube.sframe)    
        li[tube.tag] = max(1, min([ optim(node) for _, node in nodes ]))

    G = nx.Graph()
    G.add_nodes_from([ tube.tag for tube in pcg.tubes ])

    edges = set()
    for k1, v1 in pcg.nodes.items():
        for k2, v2 in pcg.nodes.items():
            if pcg.A[k1][k2] == 0 or v1.tube.tag == v2.tube.tag: continue
            edges.add(( v1.tube.tag, v2.tube.tag ))
        
    G.add_edges_from(list(edges))

    starting_time = {}

    for Ck in nx.connected_components(G):
        Ck_ordered = get_ordered_dict(li, Ck).keys()    
        l1 = min([ l for tag, l in li.items() if tag in Ck ])
        for i, tag in enumerate(Ck_ordered):
            starting_time[tag] = l1 + (q * i)
            
    return starting_time