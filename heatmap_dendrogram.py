"""
This script performs the computations for the paper "Sub-grouping Kho-Bwa based on 
shared core vocabulary" by Ismael Lieberherr and Timotheus A. Bodt to appear end 
of 2017 in Himalayan Linguistics 16.2. 
***
Script...
(1) reads from a csv spread sheet with cognacy judgements
(2) computes the hamming distance/similarity matrix
(3) creates two plots using the seaborn, pandas and numpy modules
(4) performs simulations with slightly disturbed data.
Runs with Python 3.
"""
# import scientific modules
import time 
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# import scipy
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import scipy.spatial.distance as pdist
import click
click.disable_unicode_literals_warning = True

######################################################################
# (1) Prepare spreadsheet data - convert to nxp matrix (dataframe)
"""
The data used for this analysis we had entered into a Google spreadsheet having
language as columns and glosses and our cognacy statement as rows. Roots which
we consider as cognate have the same number. Example:

________________________________________________________
|Language\Concept  |HAND |cognacy |ASH  |cognacy   |big 
|------------------+-----+--------+-----+----------+-----
|Duhumbi           |hut  |       1|     |         1|
|Khispi            |hut  |       1|  
|Rupa              |ʔik  |       2|
|Shergaon          |ʔik  |       2|
|....              
|...
|#Comment1 
|#Comment2

The table may contain empty rows for visually grouping languages when 
entering the data.

The table may contain  comment rows in any place, which are excluded 
from the analysis. The name of a comment row has to start with a hash "#" 
(like in python).

Where data is missing the cognacy statement is something which is not an
integer e.g. "NA", "n.a.", "" etc.

The first step is to read the data, extract the cognacy statement, to
a nxp multivariate data matrix. In our case the matrix has the dimensions
29x100, where n = 29 is the number of languages, and p = 100 is the number of
glosses in the adjusted Leipzig-Jakarta list. Looking something like the
following table:

___________________________________________
|Language\Gloss |HAND |WATER |...|GLOSS100|
|---------------+-----+------+---+--------|
|Duhumbi        |1    |1
|Khispi         |1    |1
|Rupa           |2    |1
|Shergaon       |2    |1
|...            |.
|...            |.
|Language29     |.
|___________________________________


"""
######################################################################


def make_datamatrix_from_spreadsheet(infile):
    """
    Takes as imput the google spreadsheet downloaded as csv. Returns a data
    matrix.
    """
    # import data as pandas data frame
    spreadsheet = pd.read_csv(infile, comment='#', sep=',').dropna(how='all')
    # drop empty rows and columns
    #spreadsheet = spreadsheet.dropna(axis=0, how='all')
    #spreadsheet = spreadsheet.dropna(axis=1, how='all')
    # the first column contains the row names
    row_names = spreadsheet.iloc[:, 0]
    concepts = spreadsheet.columns[1::2]
    col_names = concepts
    # extract only the odd colums which contain the actual cognacy judgement
    cognacy_matrix = spreadsheet.iloc[:, 2::2]
    # exclude an empty column between tb data and khobwa data
    cognacy_matrix.index = row_names
    cognacy_matrix.columns = col_names
    # Has to be converted to numbers otherwise everything is string, and even
    # errors coerce make invalid parsing into NaN
    cognacy_matrix = cognacy_matrix.apply(pd.to_numeric, errors='coerce')
    return cognacy_matrix

#infile = 'data/dataset_khobwa.csv'

#bla = make_datamatrix_from_spreadsheet(infile)


######################################################################
# (2) Compute distance/similarity  matrix
"""
Every row in cognacy_matrix contains integers (cognacy statement) or "NaN"
(missing data). As a measure for the distance between two languages, we
implemented the Hamming metric. The Hamming metric counts the distance between
two identical integers as 0 and between two not identical integers as 1. If one
of the two is missing, it is also counted as 0. For example if:

         | concept1| concept2| concept3| concept4|
---------+---------+---------+---------+---------|
Language1|       1 |       1 |       1 |     NaN |
Language2|       1 |     NaN |       2 |       1 | 
Language3|       2 |       2 |       3 |       1 |

then:

d(Language1, Language2) = 1 (only gloss3 is different)
d(Language2, Language3) = 2 (gloss1 and gloss3 are different)
d(Language1, Language3) = 3 (gloss1, gloss2 and gloss3 are different)

The percentages of different glosses (Hamming distance) would be 1/4, 2/4 and
3/4 and the cognacy percentage (or similarity) between the three fictive
languages would be 75% ((1-0.25)*100), 50% and 25%. However here missing data
was counted in the same way as non-cognate forms which is not a sensible
approach (but which is done by the pre-implemented Hamming metric of pandas).
It is more appropriate to ommit all pairs with missing data. The distances
become 1/2, 3/3 and 2/3, and the cognacy percentages 50%, 0% and 33%. I.e. the
percentage is computed on basis of the available words, and not on basis of the
whole data.
"""
######################################################################


def hamming_similarity(data_mat):
    """
    Function for computing the distance matrix for a set of languages takes as
    an imput an nxp data matrix (as Pandas data frame) and returns an nxn
    distance matrix (as Pandas data frame).
    """
    # n number of languages
    n = data_mat.shape[0]
    # p number of items in the wordlist
    p = data_mat.shape[1]
    # create two empty matrix
    num_cog = np.zeros(shape=(n, n))
    num_comp = np.zeros(shape=(n, n))

    for i in range(n):
        for j in range(n):
            # Pairwise substract rows from each other
            # In the result count the number of entries = 0 to get the number
            # of cognates
            # Count the number of non available items to get the number of
            # effective comparisons
            # using INT - NaN = NaN (e.g. 3 - NaN = NaN)
            # e.g. [1, 2, NaN] - [1, 1, 1] = [0, 1, NaN] i.e. 1 cognate and two
            # comparisons
            # pairwise comparisons of languages:
            lang_comp = data_mat.iloc[i, :] - data_mat.iloc[j, :]
            # number of items available:
            num_comp[i, j] = p - lang_comp.isnull().sum()
            # number of items with value 0:
            num_cog[i, j] = lang_comp[lang_comp == 0].count()
    # the hamming similarity matrix
    similarity_matrix = pd.DataFrame(
            num_cog/num_comp, index=data_mat.index, columns=data_mat.index)
    return similarity_matrix

######################################################################
# (3) Perform cluster analysis and plot data
"""
Hierarchical clusteranalysis with unrounded similarity matrix. The
pre-implemented scipy algorithm was used, which is explained in the paper.
"""
######################################################################


def plot_heatmap_with_dendrogram(similarity_matrix, plot_name, show_link):
    """
    Makes a plot of heatmap and dendrogram. Arguments are a similarity matrix
    (as Pandas data frame) and the name of the plot.
    """
    # the distance matrix has to be condensed first
    cond_dist_matrix = pdist.squareform(100 - similarity_matrix)
    # linkage makes the whole mathematics
    Z = linkage(cond_dist_matrix, 'average')
    # uncomment the print statement to see the linkage matrix
    if show_link:
        print(Z)
    sns.set(font='sans-serif', font_scale=0.7)
    # round the figures displayed in the heatmap as to integers
    pairwise_cognacy_displayinheatmap = np.round(
            similarity_matrix, decimals=0).astype(int)
    # create a seaborn clustermap object
    heatncluster = sns.clustermap(
            pairwise_cognacy_displayinheatmap, annot=True, cmap='inferno_r',
            vmax=100, fmt='d', col_linkage=Z, row_linkage=Z)
    plt.setp(heatncluster.ax_heatmap.yaxis.get_majorticklabels(), rotation=0)
    plt.setp(heatncluster.ax_heatmap.xaxis.get_majorticklabels(), rotation=45)

    file_name = plot_name + '.png'
    click.echo('Writing ' + file_name, err=True)
    plt.savefig(file_name)

######################################################################
# (4) Simulation
"""
Motivation for the simulation was the question whether and how much different
data would change the dendrogram that we obtained. Would slightly different
data and cognacy decisions change the overal result? For added a matrix with
random values to our matrix, made a plot like in (3) and checked "manually"
whether the result was different.
"""


def create_random_matrix(distr, mean, spread, dim):
    """
    Function to create a matrix with random entries.
    distr: probability distribution (string)
    mean: are the random values centered around the actual value (mean = 0)? Or
    are all values generally lower/higher? (simulating more strict/more
    speculative cognacy decisions)
    spread: if value is 10 then the maximum value that might be added is +-10
    dim: size of the matrix list [,]
    """
    if distr == 'binomial':
        random_matrix = np.random.binomial(
                n=spread*2, p=0.5, size=dim) - spread + mean
        # make a symmetric random matrix (transpose, add divide by two)
        random_matrix = (random_matrix + random_matrix.T) / 2
    elif distr == 'uniform':
        random_matrix = np.random.randint(
                -spread, high=spread, size=dim) + mean
        random_matrix = (random_matrix + random_matrix.T) / 2
    return random_matrix


# Kho-Bwa with random variation (looks naturally different every time produced)
def simulate_random_variation(data_set, no_sim, distr, spread,
                              mean, out_directory, pltname, linkage):
    """
    Function to run the simulation.
    data_set: nxn data set with cognacy percentages
    no_sim: number of simulations
    distr: probability distribution
    spread: if value is 10 then the maximum value that might be added is +-10
    out_directory: where to save the plots
    pltname: plots have the name of the value of the sting in pltname, plus an
    integer for every simulation. E.g. simulation_1.png, simulation_2.png,...
    """
    dim = data_set.shape
    for i in range(no_sim):
        random_matrix = create_random_matrix(distr, mean, spread, dim)
        data_plus_random_matrix = data_set + random_matrix
        # cognacy percentage can not be more than 100
        data_plus_random_matrix[data_plus_random_matrix > 100] = 99
        # cognacy percentage can not be less than 0
        data_plus_random_matrix[data_plus_random_matrix < 0] = 0
        # diagonals still have to be 100 (cognacy percentage of a language with
        # itself)
        data_plus_random_matrix.values[[np.arange(dim[0])] * 2] = 100
        # name of plot
        ploti = out_directory + '/' + pltname + '_' + str(i + 1)
        plot_heatmap_with_dendrogram(data_plus_random_matrix, ploti, linkage)


def calculate_pairwise_cognacy(infile):
    cognacy_matrix = make_datamatrix_from_spreadsheet(infile)

    # this is a matrix with pairwise cognates
    return hamming_similarity(cognacy_matrix) * 100



@click.group()
def cli():
    """ Tool for plotting a comparative word list as heatmap and dendrogram.

    Input is a csv file containing rows with the language data and
    a cognacy statement, whether two lexemes are cognate or not.
    
    Input csv (with header line) containing columns with the language data and
    cognacy statement.

    Rows in the csv starting with "#" are ignored. This is for including additional
    information about the concept, the cognacy judgement etc.
  
    e.g.

    Concept  , 1SG , cognacy , HAND, cognacy,\n
    #POS     , prn ,         ,   n ,        ,\n
    Duhumbi  , ga  , 1       , hut ,       1,\n
    Khispi   , ga  , 1       , hut ,       1,\n
    Rupa     , gu  , 1       , ʔik ,       2,\n
    Shergaon , gu  , 1       , ʔik ,       2,\n
   
    
    """


@cli.command()
@click.option('--outdir', type=click.Path(exists=True), default='plots',
              help='Output directory (Default plots).')
@click.option('--plot_all', default='tbkhobwa',
              help='Name of plot of whole data (Default tbkhobwa).')
@click.option('--plot_part', default='khobwa',
              help='Name of plot of first x columns (Default khobwa).')
@click.option('--part_range', default=22,
              help='The first x columns (Default 22).')
@click.option('--linkage/--no-linkage',
              default=False, help='Show linkage matrix (Default --no-linkage)')
@click.argument('infile', type=click.Path(exists=True),
                default='data/dataset_khobwa.csv')
def plot(outdir, infile, plot_all, plot_part, part_range, linkage):
    """Create heatmap and dendrogram plots.

    Produce two heatmap and dendrogram plots for the given data, one for
    the whole data set (Kho-Bwa and TB) and one only for a subset (by default
    only Kho-Bwa).
    By default, output is written to the directory "plots" in the current
    directory.
    The names of the plots are "khobwa.png" and "tbkhobwa.png" by default.
    The linkage matrix is not shown by default.
    """
    pairwise_cognacy = calculate_pairwise_cognacy(infile)

    # make two plots: one for the Kho-Bwa languages only,
    # and one for all languages
    plot_heatmap_with_dendrogram(pairwise_cognacy,
                                 outdir + '/' + plot_all, linkage)
    plot_heatmap_with_dendrogram(pairwise_cognacy.iloc[:part_range,
                                                       :part_range],
                                 outdir + '/' + plot_part, False)


@cli.command()
@click.option('--outdir', type=click.Path(exists=True), default='simulations',
              help='Output directory (Default simulations).')
@click.option('--count', default=1, help='Number of simulations to run. Default 1.')
@click.option('--distr', type=click.Choice(['uniform', 'binomial']),
              default='uniform', help='Probability distribution.')
@click.option('--spread', default=20, help='Maximum spread around value. Default 20.')
@click.option('--mean', default=0, help='Deviation from value. Default 0.')
@click.option('--linkage/--no-linkage', default=False,
              help='Show linkage matrix (Default --no-linkage)')
@click.argument('infile', type=click.Path(exists=True),
                default='data/dataset_khobwa.csv')
def simulate(outdir, count, distr, spread, mean, infile, linkage):
    """Create plots simulating random variation.

    Produce heatmap and dendrogram plots (default: 1) for the given data, while
    introducing random variation. By default, output is written to the
    directory "simulations" in the current directory, and simulations are
    parameterized with spread 20, mean 0, and uniform probability distribution.
   
    Note that 100 simulations can take several minutes to complete.
    """
    pairwise_cognacy = calculate_pairwise_cognacy(infile)

    start_time = time.time()
    simulate_random_variation(
            pairwise_cognacy, count, distr, spread, mean, outdir,
            'simulation_{}_{}'.format(distr, spread), linkage)
    click.echo('--- {} seconds ---'.format(time.time() - start_time), err=True)
