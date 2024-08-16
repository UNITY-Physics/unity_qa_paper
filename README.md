# UNITY QA Paper

Contains code to reproduce results for the UNITY QA Paper (in preparation). Original source data is not shared, but compiled results in form of .csv files are shared in here. 

The results in here were produced using the [`ghost`](https://github.com/UNITY-Physics/GHOST) framework, but this is not required to reproduce the figures and stats in the paper. The [`ghost`](https://github.com/UNITY-Physics/GHOST) repository contains examples of how to run the type of analysis used in the paper.

## Python dependencies

Example of how to set up python environment with conda
```sh
conda create --name qa_paper python=3.9
conda activate qa_paper
python3 -m pip install -r requirements.txt
python3 -m ipykernel install --user --name=qa_paper
```


## Organisation

```
├── data (csv data for stats)
├── nnUNet (related to the nnUNet fiducial segmentation)
├── python (Code to generate results)
└── results (Output folder for results)
    └── figures (Paper figures)
```

## Reroduce figures from paper

This will go through section by section how results were produced.

### Relaxometry

