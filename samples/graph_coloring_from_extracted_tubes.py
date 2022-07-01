import pandas as pd

from pcgvs.extraction import Tube
from pcgvs.aggregation import solve


columns = ['frame', 'tag', 'x', 'y', 'w', 'h' ]
with open('../notebooks/data/video-2-raw.txt') as output:
    rawdata = [ line.strip().split(' ')[:6] for line in output.readlines() ]
    df = pd.DataFrame(rawdata, columns=columns)
    df = df.astype('int')

tubes = []

for tag in df.tag.unique():
    ob_df = df[df['tag'] == tag]
    if (len(ob_df) < 10): continue # remove shadows
    ob_df = ob_df.sort_values(by='frame')
    sframe = ob_df.frame.min()
    eframe = ob_df.frame.max()
    tube = Tube(tag, sframe, eframe)
    tubes.append(tube)
    for _, r in ob_df.iterrows():
        tube.next_bounding_box(r['x'], r['y'], r['w'], r['h'])

st = solve(tubes)
print(st)