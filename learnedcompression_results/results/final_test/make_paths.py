
import os, sys, glob, json
split, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
roots = [os.path.dirname(p) for p in glob.glob("/kaggle/input/**/protocol.json", recursive=True)]
assert len(roots) == 1, roots
os.environ["DIPCOMA_ROOT"] = roots[0]
sys.path.insert(0, roots[0] + "/code")
import dipcoma_eval as E
paths = E.list_patches(split)
if split == "test":
    idx = {(os.path.basename(os.path.dirname(p)), os.path.basename(p)): p for p in glob.glob("/kaggle/input/**/test/*/*.npy", recursive=True)}
    mapped, missing = [], []
    for p in paths:
        k = (os.path.basename(os.path.dirname(p)), os.path.basename(p))
        (mapped if k in idx else missing).append(idx.get(k, p))
    assert not missing, f"{len(missing)} test patches not found, e.g. {missing[:2]}"
    assert len(idx) == len(paths), (len(idx), len(paths))
    paths = mapped
if n > 0: paths = paths[:n]
json.dump(paths, open(out, "w"))
print(len(paths))
