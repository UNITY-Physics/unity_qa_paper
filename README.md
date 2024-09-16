# UNITY QA Paper

Contains code to reproduce results for the UNITY QA Paper (in preparation). Original source data is not shared, but compiled results in form of .csv files are shared in here.

The results in here were produced using the [`ghost`](https://github.com/UNITY-Physics/GHOST) framework, but this is not required to reproduce most of the figures and stats in the paper. The [`ghost`](https://github.com/UNITY-Physics/GHOST) repository contains examples of how to run the type of analysis used in the paper.

## Python dependencies

Example of how to set up python environment with conda

```sh
conda create --name qa_paper python=3.9
conda activate qa_paper
python3 -m pip install -r requirements.txt
python3 -m ipykernel install --user --name=qa_paper
```

The `PSNR` notebook also requires the `ghost` repository to be installed with the `Caliber137` model downloaded.

## Organisation

```txt
├── data (csv data for stats)
├── nnUNet (related to the nnUNet fiducial segmentation)
├── notebooks (Code to generate results)
└── results (Output folder for results)
    └── figures (Paper figures)
```

## Notebooks to reproduce figures from paper

- [`site_overview.ipynb`](notebooks/site_overview.ipynb): Overview of all the scans from the sites. Supplemental materials figure S1 and S2.
- [`relaxivity_plots.ipynb`](notebooks/relaxivity_plots.ipynb): Analysis of T1 and T2 relaxation in the phantom. Paper figure 5.
- [`PSNR.ipynb`](notebooks/PSNR.ipynb): Analysis of temperature and Larmor frequency as well as the PSNR and SSIM analysis. Paper figures 6 and 7. Also simulation of PSNR, SSIM and SNR figure S4.
- [`contrast.ipynb`](notebooks/contrast.ipynb): Analysis of image contrast. Paper figure 8.
- [`distortions_2D.ipynb`](notebooks/distortions_2D.ipynb): Analysis of in-plane distortions. Paper figure 9 and 10.
- [`longitudinal.ipynb`](notebooks/longitudinal.ipynb): Longitudinal analysis from one site. Paper figure 11.
- [`nnUNet_reproducibility.ipynb`](notebooks/nnUNet_reproducibility.ipynb): Reproducibility analysis of the fiducial segmentation with nnUNet. Supplemental materials figure S5.

Two additional python files are included with various functions required by the notebooks

- `dataframe_help.py`: General functions to process the stats data frames.
- `stats_help.py`: Specialized stats functions.
