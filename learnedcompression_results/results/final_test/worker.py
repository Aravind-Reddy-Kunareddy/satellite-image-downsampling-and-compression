
import os, sys, glob, time, json, gc
gpu, tasks_file, OUT, paths_file = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
os.environ["CUDA_VISIBLE_DEVICES"] = gpu
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"          # needed for deterministic GPU matrix products
hits = [os.path.dirname(p) for p in glob.glob("/kaggle/input/**/protocol.json", recursive=True)]
assert len(hits) == 1, hits
ROOT = hits[0]
os.environ["DIPCOMA_ROOT"] = ROOT
sys.dont_write_bytecode = True
sys.path.insert(0, ROOT + "/code")
import numpy as np, pandas as pd, torch
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
torch.use_deterministic_algorithms(True, warn_only=True)
import dipcoma_eval as E
import dipcoma_learned as L
L.DST = E.DATA
val_p = json.load(open(paths_file))
sync = torch.cuda.synchronize
for t in json.load(open(tasks_file))[gpu]:
    tag, mode = t["tag"], t["mode"]
    if os.path.exists(f"{OUT}/summary_{tag}.json"):
        print(f"{tag}: already done, skipping", flush=True); continue
    t0 = time.time()
    model = L.make_model(13 if mode == "merged" else 1, N=t["N"], M=t["M"]).to("cuda")
    ck = L.load_ckpt(t["ckpt"], model)
    model.eval(); model.update(force=True)
    nparams = sum(p.numel() for p in model.parameters())
    def inputs_of(xn):
        x = torch.from_numpy(xn).to("cuda")
        return [x[None]] if mode == "merged" else [x[b:b + 1][None] for b in range(13)]
    def real(xn):                                          # real compress and decompress
        nbytes, rec, te, td = 0, [], 0.0, 0.0
        for inp in inputs_of(xn):
            sync(); a = time.time(); comp = model.compress(inp); sync(); te += time.time() - a
            nbytes += sum(len(q) for qq in comp["strings"] for q in qq)
            sync(); a = time.time(); d = model.decompress(comp["strings"], comp["shape"]); sync(); td += time.time() - a
            rec.append(d["x_hat"][0])
        return nbytes, torch.cat(rec, dim=0).cpu().numpy(), te, td
    def ideal(xn):                                         # error-free reconstruction, for the consistency check
        rec = [model(inp)["x_hat"][0].clamp(0, 1) for inp in inputs_of(xn)]
        return torch.cat(rec, dim=0).cpu().numpy()
    rows = []
    with torch.no_grad():
        real(E.normalise(E.load_dn(val_p[0])))             # untimed warm-up
        for p in val_p:
            xn = E.normalise(E.load_dn(p))
            nbytes, xr, te, td = real(xn)
            xi = ideal(xn)
            pb = E.psnr_per_band(xn, xr)
            rows.append(dict(patch=os.path.basename(p), bytes=nbytes, psnr=E.psnr(xn, xr), ssim=E.ssim(xn, xr),
                             psnr_ideal=E.psnr(xn, xi), finite=bool(np.isfinite(xr).all()), t_enc=te, t_dec=td,
                             **{b: v for b, v in zip(E.ORDER, pb)}))
    df = pd.DataFrame(rows); df.to_csv(f"{OUT}/final_{tag}.csv", index=False)
    mism = (df.psnr - df.psnr_ideal).abs()
    s = dict(tag=tag, mode=mode, lam=ck["lmbda"], params=nparams, n=len(df),
             bytes_mean=float(df.bytes.mean()), bpp=float(E.bpp(df.bytes.mean())), CR=float(E.compression_ratio(df.bytes.mean())),
             psnr=float(df.psnr.mean()), ssim=float(df.ssim.mean()), psnr_ideal=float(df.psnr_ideal.mean()),
             n_nonfinite=int((~df.finite).sum() + df.psnr.isna().sum()),
             n_mismatch=int(((mism > 0.05) | mism.isna()).sum()),
             max_mismatch=float(np.nanmax(mism)) if mism.notna().any() else float("nan"),
             perband=[float(df[b].mean()) for b in E.ORDER])
    json.dump(s, open(f"{OUT}/summary_{tag}.json", "w"))
    print(f"{tag}: done in {time.time() - t0:.0f} s | bpp {s['bpp']:.3f} | PSNR {s['psnr']:.2f} dB | mismatches {s['n_mismatch']}", flush=True)
    del model; gc.collect(); torch.cuda.empty_cache()
