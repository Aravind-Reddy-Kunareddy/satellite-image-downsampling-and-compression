# DIPCOMA hybrid band-selection and compression report

## Protocol
- Train/validation dataset root: `/kaggle/input/datasets/krrishshandilya/dipcoma-trainval/dataset`
- Independent test dataset root: `/kaggle/input/datasets/krrishshandilya/dipcoma-test/test`
- Train fit/search patches: 120 / 60
- Validation patches: 36
- Final evaluation patches: 120
- Official test patches: 120
- Spectral bands: 13; retained bands: 6
- Candidate pool from group→rank stage: [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12]
- Frozen validation winner: **KMeans_group**, bands `[1, 3, 6, 9, 10, 11]`

## Final evaluation results
- Evaluation set: Independent official held-out test dataset: dipcoma-test
- Official test patches available: 120
| method            |   k |    psnr |     ssim |   sam_deg |      mae |       mre |      cr |      bpp |   redundancy |    enc_s |    dec_s |   regression_parameters |   peak_traced_memory_MiB |
|:------------------|----:|--------:|---------:|----------:|---------:|----------:|--------:|---------:|-------------:|---------:|---------:|------------------------:|-------------------------:|
| KMeans_group      |   6 | 56.322  | 0.997862 |   1.81173 |  65.3464 | 0.0213136 | 19.9889 | 0.804991 |     0.45144  | 0.330298 | 0.104941 |                      49 |                  143.295 |
| Hybrid_BPSO       |   6 | 55.9283 | 0.997788 |   1.88578 |  69.1634 | 0.0227723 | 19.9874 | 0.80505  |     0.448064 | 0.326463 | 0.105009 |                      49 |                  143.29  |
| Hybrid_GA         |   6 | 55.7628 | 0.998029 |   1.85362 |  67.5265 | 0.0212596 | 20.3685 | 0.793994 |     0.429897 | 0.294488 | 0.104952 |                      49 |                  143.226 |
| Hybrid_group_rank |   6 | 55.321  | 0.99771  |   2.00236 |  75.4359 | 0.0241374 | 19.9893 | 0.804978 |     0.46826  | 0.331816 | 0.104828 |                      49 |                  143.289 |
| Variance_rank     |   6 | 51.7356 | 0.994678 |   3.21454 | 118.168  | 0.0434655 | 17.3691 | 0.921175 |     0.733063 | 0.431272 | 0.114981 |                      49 |                  143.27  |
| Entropy_rank      |   6 | 48.9978 | 0.991116 |   4.14714 | 159.425  | 0.0613216 | 17.3687 | 0.921196 |     0.744374 | 0.429205 | 0.115283 |                      49 |                  143.285 |

## Metric conventions
- CR = original 16-bit cube bits / actual JPEG2000 selected-band bitstream bits.
- bpp = compressed bits / (H × W × 13), i.e. per-pixel-per-original-band; bits per spatial pixel is separately available in CSV.
- PSNR uses fixed MAX=65535; SSIM is 2-D per band averaged over 13 bands.
- SAM is mean per-pixel spectral angle in degrees; MAE and MRE are full-cube metrics.
- Redundancy is mean absolute Pearson correlation among selected bands.
- OA, AA, κ: OA / AA / Cohen's kappa: N/A — this DIPCOMA patch pipeline did not discover aligned pixel-level ground-truth class masks. Do not infer classes from region names.
- Encoding/decoding times are measured for selected bands; regression parameter count is reported separately.
- `model_size_bytes` is cumulative encoded bitstream bytes over evaluated patches, not a trained neural model size.
- Peak memory is Python tracemalloc peak for evaluation; it does not include all native-library allocations.

## Interpretation and limitations
The proposed hybrid first groups correlated band profiles, ranks candidates within each group using variance/entropy, then searches a reduced candidate pool with a rate-aware objective. This is an engineering implementation inspired by the group-then-rank hybrid in Vaddi et al. (2024), Algorithm 2, and the rate-aware objective in the supplied Sentinel-2 project note. It is not a reproduction of an exact published algorithm.

Validation-selection regions choose the reported winner; final evaluation uses a region-disjoint set. The final results are computed on the separately attached `dipcoma-test` dataset, which is not used for fitting, search, or validation-based winner selection. This is a one-run benchmark, not evidence of statistical significance. For publication, repeat with multiple seeds and report confidence intervals, run a fair identical classifier when valid labels are available, compare more codecs/baselines, and verify dataset acquisition-month metadata against the source files.
