# Heatmap and dendrogram tool

TODO This is the tool used for creating heatmap and dendrogram plots in a
lexico-statistical study of Kho-Bwa languages.

## Requirements

-   Python 3
-   pip
-   the Kho-Bwa language data file (will be available in this directory once the paper is accepted for publication)

[pip][], the Python package management tool, comes bundled with Python 3.4 or
newer. If you use an older version of Python 3, or use a Python distribution
that does not include pip, then you will need to install it separately.

Note that this project uses scientific Python libraries. These libraries can be
somewhat challenging to install. The easiest and recommended way of setting up a
scientific Python environment is by installing a distribution like [Anaconda][].

[pip]: https://pip.pypa.io/en/stable/
[Anaconda]: https://docs.continuum.io/anaconda/install.html

## Installation

This project is distributed as a setuptools module.

To install the module, run the following command in the root of the project:

    pip install --editable .

This downloads and installs the necessary dependencies, and installs the
`heatmap_dendrogram` script itself.


## General usage

Having installed the script, run the following command to view usage
information:

    heatmap_dendrogram --help

The script provides two subcommands, `plot` and `simulate`.

### `plot`

`plot` produces the heatmap and dendrogram plots for a given data file (here,
`data.csv` represents the path to the spreadsheet file with the language data, by default `data/dataset_khobwa.csv`):

    heatmap_dendrogram plot data.csv

Complete usage information for `plot` can be viewed using the following command:

    heatmap_dendrogram plot --help

### `simulate`

`simulate` produces the same plots while introducing random variation. For
example, to run three simulations with a spread of 25 and binomial probability
distribution, use the following command (again assuming that `data.csv` is the
path to the data file):

    heatmap_dendrogram simulate --count=3 --spread=25 --distr=binomial data.csv

Complete usage information for `simulate` can be viewed using the following
command:

    heatmap_dendrogram simulate --help
    
## Mini tutorial to reprouce the plots in the paper
1. Have Python and pip installed on your computer.
2. Download the "kho-bwa-lexicostat" folder from Github
3. Unzip
4. Open a terminal/shell and change to it (e.g. `cd Downloads/kho-bwa-lexicostat`)
5. Install the module by typing: `pip install --editable .`
6. Make plots: `heatmap_dendrogram plot` (in the folder ‘plots’)
7. Simulate disturbed data: `heatmap_dendrogram simulate` (in the folder ‘simulations’)


    

