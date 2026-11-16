
import os, sys, glob, json
import numpy as np, pandas as pd
OUT, MODE = sys.argv[1], sys.argv[2]
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60)
ORDER = ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B10", "B11", "B12"]
checks = []
def check(name, ok, info=""):
    checks.append(bool(ok)); print(("PASS" if ok else "FAIL"), "-", name, info)
tasks = json.load(open(f"{OUT}/tasks.json"))
tags = [t["tag"] for g in tasks.values() for t in g]
n_expected = len(json.load(open(f"{OUT}/paths.json")))
VAL = json.load(open(f"{OUT}/val_ref.json"))
S = [json.load(open(f"{OUT}/summary_{t}.json")) for t in tags if os.path.exists(f"{OUT}/summary_{t}.json")]
check("all models evaluated", len(S) == len(tags), f"{len(S)}/{len(tags)}")
fam = lambda s: 0 if s["tag"].startswith("merged") else (1 if s["tag"].startswith("wide") else 2)
S.sort(key=lambda s: (fam(s), s["lam"], s["tag"].endswith("_s1")))
check("every model decoded every patch", all(s["n"] == n_expected for s in S), f"({n_expected} patches)")
check("no decode produced non-finite values", sum(s["n_nonfinite"] for s in S) == 0, f"({sum(s['n_nonfinite'] for s in S)} patches)")
check("every decoded patch matches the error-free PSNR within 0.05 dB", sum(s["n_mismatch"] for s in S) == 0,
      f"({sum(s['n_mismatch'] for s in S)} patches differ; largest {max(s['max_mismatch'] for s in S):.3f} dB)")

parts = sorted(glob.glob(f"{OUT}/jpeg_part*.csv"))
J = pd.concat([pd.read_csv(p) for p in parts]) if parts else pd.DataFrame()
okj = len(J) > 0 and J.patch.nunique() == n_expected and J.groupby("quality").patch.nunique().min() == n_expected
check("JPEG results complete for every patch and quality", okj)
pbc = [f"psnr_{b}" for b in ORDER]
Jq = J.groupby("quality").agg(bpp=("bpp", "mean"), psnr=("psnr", "mean"), ssim=("ssim", "mean"), **{c: (c, "mean") for c in pbc}).reset_index().sort_values("bpp")
Jq["val_psnr"] = Jq.quality.map({1: 27.43, 10: 33.98, 20: 36.68, 30: 38.09, 50: 39.76, 70: 41.23, 85: 43.51, 95: 47.86})
print("\nJPEG on these patches (mean over patches; val_psnr = value on the validation patches):")
print(Jq[["quality", "bpp", "psnr", "ssim", "val_psnr"]].round(3).to_string(index=False))
Ju = Jq.drop_duplicates(subset="bpp")
def jint(b, col):
    if b < Ju.bpp.min() or b > Ju.bpp.max(): return np.nan
    return float(np.interp(np.log(b), np.log(Ju.bpp.values), Ju[col].values))

t1 = pd.DataFrame([dict(model=s["tag"], params_M=s["params"] / 1e6, bpp=s["bpp"], CR=s["CR"], PSNR=s["psnr"], SSIM=s["ssim"]) for s in S])
print(f"\nTable 1: results on the {MODE.upper()} patches, real deterministic decoding:")
print(t1.round({"params_M": 2, "bpp": 3, "CR": 0, "PSNR": 2, "SSIM": 3}).to_string(index=False))
t2 = pd.DataFrame([dict(model=s["tag"], bpp=s["bpp"], PSNR=s["psnr"], JPEG_PSNR=jint(s["bpp"], "psnr"), SSIM=s["ssim"], JPEG_SSIM=jint(s["bpp"], "ssim")) for s in S])
t2["dPSNR"], t2["dSSIM"] = t2.PSNR - t2.JPEG_PSNR, t2.SSIM - t2.JPEG_SSIM
print("\nTable 2: against JPEG at the same bpp (JPEG interpolated in log bpp; nan = outside JPEG's range):")
print(t2.round({"bpp": 3, "PSNR": 2, "JPEG_PSNR": 2, "dPSNR": 2, "SSIM": 3, "JPEG_SSIM": 3, "dSSIM": 3}).to_string(index=False))
t3 = pd.DataFrame([[s["tag"]] + s["perband"] for s in S], columns=["model"] + ORDER)
print("\nTable 3: mean PSNR (dB) per band:")
print(t3.round(1).to_string(index=False))
t4 = pd.DataFrame([[s["tag"]] + [s["perband"][i] - jint(s["bpp"], f"psnr_{b}") for i, b in enumerate(ORDER)] for s in S], columns=["model"] + ORDER)
print("\nTable 4: per-band PSNR minus JPEG per-band PSNR at the same bpp (dB, positive = learned codec better):")
print(t4.round(1).to_string(index=False))
G = {"10m": ["B02", "B03", "B04", "B08"], "20m": ["B05", "B06", "B07", "B8A", "B11", "B12"], "60m": ["B01", "B09", "B10"]}
t5 = pd.DataFrame({"model": t4["model"], **{f"{k} bands": t4[v].mean(axis=1) for k, v in G.items()}})
print("\nTable 5: the same difference, averaged by native band resolution:")
print(t5.round(1).to_string(index=False))
if MODE == "test":
    t6 = pd.DataFrame([dict(model=s["tag"], val_bpp=VAL[s["tag"]][0], test_bpp=s["bpp"], val_PSNR=VAL[s["tag"]][1], test_PSNR=s["psnr"],
                            dPSNR=s["psnr"] - VAL[s["tag"]][1], val_SSIM=VAL[s["tag"]][2], test_SSIM=s["ssim"]) for s in S])
    print("\nTable 6: test against validation (same frozen models):")
    print(t6.round({"val_bpp": 3, "test_bpp": 3, "val_PSNR": 2, "test_PSNR": 2, "dPSNR": 2, "val_SSIM": 3, "test_SSIM": 3}).to_string(index=False))
    t6.to_csv(f"{OUT}/table6.csv", index=False)
for n, t in (("table1", t1), ("table2", t2), ("table3", t3), ("table4", t4), ("table5", t5)):
    t.to_csv(f"{OUT}/{n}.csv", index=False)
Jq.to_csv(f"{OUT}/jpeg_summary.csv", index=False)
print("\nREPORT DONE")
