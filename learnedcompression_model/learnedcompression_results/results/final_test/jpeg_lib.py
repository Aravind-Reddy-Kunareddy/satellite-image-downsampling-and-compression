
import io, os, sys, glob, time
import numpy as np
from PIL import Image
roots = [os.path.dirname(p) for p in glob.glob("/kaggle/input/**/protocol.json", recursive=True)]
assert len(roots) == 1, roots
os.environ["DIPCOMA_ROOT"] = roots[0]
sys.path.insert(0, roots[0] + "/code")
import dipcoma_eval as E

def jpeg_rows(path, qualities):
    xn = E.normalise(E.load_dn(path))
    q8 = E.to_uint8(xn)
    rows = []
    for q in qualities:
        nbytes, te, td = 0, 0.0, 0.0
        rec = np.empty_like(xn)
        for b in range(E.NB):
            buf = io.BytesIO()
            a = time.time(); Image.fromarray(q8[b]).save(buf, format="JPEG", quality=int(q), optimize=True); te += time.time() - a
            nbytes += buf.tell()
            buf.seek(0)
            a = time.time(); d = np.array(Image.open(buf)); td += time.time() - a
            rec[b] = E.from_uint8(d)
        pb = E.psnr_per_band(xn, rec)
        rows.append(dict(patch=os.path.basename(path), quality=int(q), bytes=nbytes, cr=E.compression_ratio(nbytes),
                         bpp=E.bpp(nbytes), bps=E.bits_per_sample(nbytes), psnr=E.psnr(xn, rec), ssim=E.ssim(xn, rec),
                         t_enc=te, t_dec=td, **{f"psnr_{b}": v for b, v in zip(E.ORDER, pb)}))
    return rows
