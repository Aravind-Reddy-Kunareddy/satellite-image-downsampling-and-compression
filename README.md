Comparative Study of Seven Spectral-Dimensionality Reduction and Compression Models for Sentinel-2 Multispectral Imagery
A comparative research project evaluating seven approaches for reducing
the storage and transmission burden of 13-band Sentinel-2 multispectral
imagery while preserving reconstruction quality.
GitHub repository description
Comparative evaluation of seven spectral band-selection,
dimensionality-reduction, and learned-compression methods for 13-band
Sentinel-2 imagery, analyzing reconstruction fidelity, bitrate,
compression ratio, runtime, and cross-region generalization.

Overview
Multispectral Earth-observation imagery contains valuable information
across multiple spectral bands, but storing and transmitting every band
at full precision can be expensive. This project studies seven
complementary approaches to reducing the spectral representation or
compressing the imagery.

The work consolidates the methods, ablation experiments, and
quantitative results into a single comparative research study. The
approaches are evaluated using reconstruction quality, rate/compression,
and computational-cost measures.
Important: These are seven distinct methods, not one fused model
or a single sequential pipeline. Their rate measurements are not
always directly interchangeable: selected-band payload ratios,
JPEG/JPEG2000 bitrates, PCA latent rates, and entropy-coded learned
bitstreams represent different coding setups.

Models evaluated
                        \# Model                 Core idea

                         1 **Search Model        Formulates band
                           (ACOMA)**             selection as a
                                                 combinatorial
                                                 optimization problem
                                                 and compares exhaustive
                                                 search, genetic
                                                 algorithm (GA), binary
                                                 particle swarm
                                                 optimization (BPSO),
                                                 hybrid GA--BPSO, and
                                                 random search.

                         2 **Hybrid Model**      Combines K-means
                                                 grouping, statistical
                                                 band ranking, and
                                                 GA/BPSO optimization,
                                                 with reconstruction of
                                                 omitted bands.

                         3 **PCA / Quantized     Applies principal
                           PCA**                 component analysis to
                                                 decorrelate and reduce
                                                 spectral
                                                 dimensionality;
                                                 quantized PCA stores
                                                 component scores at
                                                 reduced precision.

                         4 **Ranking-Based       Selects original bands
                           Model**               using variance-based
                                                 and
                                                 Shannon-entropy-based
                                                 ranking criteria.

                         5 **Clustering-Based    Groups spectral-band
                           Model**               profiles using
                                                 K-means++ or Ward
                                                 hierarchical clustering
                                                 and selects
                                                 representative original
                                                 bands.

                         6 **Deep Learning       Uses a compact linear
                           Model**               autoencoder to estimate
                                                 band importance,
                                                 followed by
                                                 selected-band coding
                                                 and regression-based
                                                 reconstruction.

                         7 **Learned Compression Uses a learned
                           Model**               variational autoencoder
                                                 with a scale
                                                 hyperprior; compares
                                                 joint multispectral
                                                 (merged) and shared
                                                 per-channel (split)
                                                 compression.

Dataset and experimental setting
The experiments use the DIPCOMA Sentinel-2 multispectral dataset. The
common image representation contains:
- 13 spectral bands
- 512 × 512 pixel patches
- Unsigned 16-bit source imagery in the band-selection experiments
- Geographically separated evaluation regions, including Everest,
  Great Barrier Reef, Lagos, Northern Sweden, Po Valley, and Rub' al
  Khali
Several reports use a common split of 957 training patches, 165
validation patches, and 396 independent test patches. Not every model
uses precisely the same sampling protocol or subset of the data; the
paper documents those differences rather than assuming a perfectly
identical setup.
Dataset downloads
- Training and validation dataset: DIPCOMA Train/Validation ---
  Kaggle
- Test dataset: DIPCOMA Test ---
  Kaggle
Please follow the dataset provider's terms and instructions when
downloading or redistributing the data.
Evaluation criteria
The project reports a combination of image-quality, spectral-fidelity,
compression, and computational metrics:
  Metric                              Purpose
  PSNR                            Measures pixel-level reconstruction
fidelity in decibels. Higher is
generally better.

  SSIM                            Measures structural similarity
between original and reconstructed
imagery. Higher is better.

  SAM                             Spectral Angle Mapper; measures
angular difference between spectral
vectors. Lower is better.

  MAE                             Mean absolute reconstruction error.
Lower is better.

  MRE                             Mean relative error. Lower is
better.

  BPP                             Bits per pixel; measures encoded
rate. Lower means fewer bits per
pixel.

  CR                              Compression ratio, as defined by
the relevant experiment. Higher
generally means stronger
compression.
Runtime / memory                Measures encoding, decoding,
fitting or inference cost, and
memory requirements.
Metric definitions and exact rate conventions are retained from the
individual experiments. Comparisons should account for differences in
bit depth, codec, preprocessing, reconstruction method, and whether
model weights are included in the reported bitstream.
Key experimental observations
- Search-based selection: ACOMA and its search baselines identify
  a six-band subset that provides strong reconstruction quality under
  the reported JPEG2000 configuration. The metaheuristics approach the
  exhaustive-search optimum with substantially lower search effort.
- Hybrid selection: Grouping and optimization methods provide
  competitive reconstruction, while the preferred configuration
  depends on whether validation quality or compression-oriented
  objectives are prioritized.
- PCA: Retaining eight principal components preserves 99.9018% of
  the reported explained variance. Quantizing PCA scores reduces the
  reported bitrate substantially, with a relatively small change in
  reconstruction metrics.
- Ranking and clustering: These approaches offer comparatively
  simple band-selection strategies. Their reconstruction performance
  depends strongly on the number and identity of retained bands, as
  well as the reconstruction strategy used for omitted bands.
- Linear autoencoder: The compact model provides a learned
  band-importance signal, but its quality/compression trade-off varies
  with the number of retained bands and JPEG quality setting.
- Learned compression: The merged and split neural codecs show
  different rate--distortion and computational profiles. Some
  configurations outperform the JPEG baseline at comparable rates,
  while high-rate configurations do not consistently do so. Decode
  reliability and latency are also important considerations.
These are experiment-specific findings, not a claim that one model is
universally best. Consult the paper's tables for the exact
configurations and numerical results.
Repository structure
.
├── README.md
├── models/
│   ├── searching_based_model/
│   ├── hybrid_model/
│   ├── pca_model/
│   ├── ranking_model/
│   ├── clustering_based_model/
│   ├── deep_learning_model/
│   └── learned_compression_model/
└── requirements.txt
This is the intended high-level organization. Add only the scripts,
datasets, and outputs that are actually part of the repository. Do not
commit restricted or very large raw datasets; document the source and
acquisition instructions instead.
Reproducibility notes
For a reliable reproduction:
1. Record the dataset version, geographic split, patch sampling, and
   preprocessing configuration.
2. Keep train, validation, and test regions separate to avoid spatial
   leakage.
3. Record the exact retained band indices and whether indexing is
   zero-based or one-based.
4. Record codec settings, bit depth, quantization, and whether model
   weights are counted in the rate.
5. Report encoding and decoding time separately, and distinguish
   model-fitting time from end-to-end runtime.
6. Preserve random seeds and report variability where multiple runs are
   available.
7. Compare models only under clearly stated, compatible evaluation
   conditions.
Some experiments report raw selected-band payload ratios rather than
measured compressed bitstream ratios. Those values should not be
compared directly with entropy-coded neural compression rates or codec
BPP values.
Limitations
- The individual model experiments do not all use identical training
  samples, test subsets, or coding configurations.
- Some ablation configurations are described but do not have complete
  numerical test results.
- The PCA component-count sweep is not numerically complete for every
  proposed component count.
- Some clustering alternatives are documented without independent-test
  results.
- The ranking report PDF supplied with the source materials duplicated
  clustering-report content; ranking-specific results were therefore
  taken from the ranking experiment notebook/results rather than that
  PDF.
- The project does not provide a unified classification benchmark
  across all seven methods. No classification-accuracy claim is made.
- Results should be interpreted within each model's stated
  reconstruction and rate-measurement protocol.
References
1. R. Vaddi, P. K. B. L. N. Phaneendra, P. Manoharan, L.
   Agilandeeswari, and V. Sangeetha, "Strategies for dimensionality
   reduction in hyperspectral remote sensing: A comprehensive
   overview," The Egyptian Journal of Remote Sensing and Space
   Sciences, vol. 27, pp. 82--92, 2024.
   https://doi.org/10.1016/j.ejrs.2024.01.005
2. D. Ding, D. Zhuang, F. Xia, and X. Yang, "Hyperspectral band
   selection based on deep learning: a review," Journal of King Saud
   University Computer and Information Sciences, vol. 38, article
   356, 2026. https://doi.org/10.1007/s44443-026-00786-4
3. P. Gómez and G. Meoni, "Tackling the satellite downlink bottleneck
   with federated onboard learning of image compression," in
   Proceedings of the IEEE/CVF Conference on Computer Vision and
   Pattern Recognition Workshops, pp. 6809--6818, 2024.
Citation
If you use this consolidated experimental study, cite the paper included
in this repository and cite the original research works listed in its
References section where relevant. Add the final author names,
institutional affiliations, publication venue, and DOI if/when the work
is formally published.
License
Choose and add a license before distributing this repository. If the
repository contains third-party datasets, pretrained weights, or copied
research materials, follow their original licenses and citation
requirements.
