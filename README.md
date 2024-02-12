# Network MCS
The Network MCS module uses the Jaccard Index with Maximum Common Subgraph to generate a similarity score between IE models in the PBSHM network. This module works within the [PBSHM Core](https://github.com/dynamics-research-group/pbshm-flask-core) software stack.

Within this module, you can select any IE models that are loaded into your PBSHM database (given that they meet the specification outlined in [PBSHM Schema](https://github.com/dynamics-research-group/pbshm-schema)) and generate a similarity matrix (1 = similar, 0 = dissimilar) for the selected models.

This module was originally authored by [Dr Julian Gosliga](https://github.com/jgosliga) and has then since been maintained and updated to work with the [PBSHM Core](https://github.com/dynamics-research-group/pbshm-flask-core).

## Installation
Install the package via pip:
```
pip install pbshm-network-mcs
```

## Setup
Firstly, configure the PBSHM Core by following the [outlined guide](https://github.com/dynamics-research-group/pbshm-flask-core#setup)

## Running
The application is run via the standard Flask command:
```
flask run
```