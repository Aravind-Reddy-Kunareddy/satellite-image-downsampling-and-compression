
import sys, json, glob
import pandas as pd
from jpeg_lib import jpeg_rows, E
J = pd.read_csv(glob.glob("/kaggle/input/**/results/jpeg_val.csv", recursive=True)[0])
quals = sorted(J.quality.unique())
paths = E.list_patches("val")[:6]
rows = [r for p in paths for r in jpeg_rows(p, quals)]
M = pd.DataFrame(rows).merge(J, on=["patch", "quality"], suffixes=("", "_old"))
print("RESULT " + json.dumps(dict(n=len(M), expected=len(paths) * len(quals),
      rel_bytes=float((abs(M.bytes - M.bytes_old) / M.bytes_old).max()),
      d_psnr=float(abs(M.psnr - M.psnr_old).max()), d_ssim=float(abs(M.ssim - M.ssim_old).max()))))
