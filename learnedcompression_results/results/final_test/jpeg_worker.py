
import sys, json, glob
import pandas as pd
from jpeg_lib import jpeg_rows
paths_file, out_csv, part, nparts = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
J = pd.read_csv(glob.glob("/kaggle/input/**/results/jpeg_val.csv", recursive=True)[0])
quals = sorted(J.quality.unique())
paths = json.load(open(paths_file))
rows, done = [], 0
for i, p in enumerate(paths):
    if i % nparts != part: continue
    rows += jpeg_rows(p, quals); done += 1
    if done % 10 == 0: print(f"jpeg part {part}: {done} patches done", flush=True)
pd.DataFrame(rows).to_csv(out_csv, index=False)
print(f"jpeg part {part}: finished", flush=True)
