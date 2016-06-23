'''
***DRAFT***
Script reading from a csv spread sheet with cognacy judgements (1), computes the hamming distance/similarity matrix (2)
and creates two plots using the seaborn, pandas and numpy modules (3). Finally a simulation with slightly disturbed data
is performed (4). Runs with Python 3.
'''
#!/usr/bin/python
#Define directory of the spreadsheet and number of simulations
spreadsheet_directory = '~/Downloads/'
spreadsheet_name = 'KhoBwa_LeipzipJakarta - Data.csv'
number_of_simulations = 1       #depending on the hardware 100 simulations can take several minutes

#import modules
import time #not really necessary, just for tracking time bla
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
#import scipy
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import scipy.spatial.distance as pdist


######################################################################
#(1) Prepare spreadsheet data - convert to nxp matrix (dataframe)
'''
The data used for this analysis we had entered into a Google spreadsheet having doculects as columns and glosses and our cognacy statement as rows. Roots which we consider as cognate have the same number. Example:

______________________________________________________ 
| Gloss\Doculect|Duhumbi |Khispi |Rupa |Shergaon |...
|---------------+--------+-------+-----+---------|...
|HAND           |hut     |hut    |ʔik  |ʔik      |....
|cognacy        |1       |1      |2    |2        |....
|---------------|--------+-------+-----+---------+....
|....
|...

Where data is missing the cognacy statement is something which is not an integer 
e.g. "NA", "n.a.", "" etc.

The first step is to read the data, extract the cognacy statement, transpose to a nxp multivariate data matrix.
In our case the matrix has the dimensions 29x100, where n = 29 is the number of 
doculects, and p = 100 is the number of glosses in the adjusted Leipzig-Jakarta list. 
Looking something like the following table:

___________________________________________
|Doculect\Gloss |HAND |WATER |...|GLOSS100|
|---------------+-----+------+---+--------|
|Duhumbi        |1    |1
|Khispi         |1    |1
|Rupa           |2    |1
|Shergaon       |2    |1
|...            |.
|...            |.   
|Doculect29     |.
|___________________________________

'''
######################################################################

def make_datamatrix_from_spreadsheet(spreadsheet_dir, spreadsheet_nm):
    '''
    Takes as imput the google spreadsheet downloaded as csv. Returns a data matrix as rows.
    '''
    #import data as pandas data frame
    spreadsheet = pd.read_csv(spreadsheet_directory + spreadsheet_name)
    #read only the first 200 lines with the actual data
    spreadsheet = spreadsheet[:200]

    #the first column contains the row names
    row_names = spreadsheet.iloc[0:200:2, 1]
    #extract only the odd rows which contain the actual cognacy statement
    cognacy_matrix = spreadsheet.iloc[1:200:2, 2:32]

    #exclude an empty column between tb data and khobwa data
    cognacy_matrix.drop(cognacy_matrix.columns[[22]], axis=1, inplace=True)
    cognacy_matrix.index = row_names
    #has to be converted to numbers otherwise everything is string, and even
    #errors coerce make invalid parsing into NaN
    cognacy_matrix = cognacy_matrix.convert_objects(convert_numeric=True).T
    return cognacy_matrix

cognacy_matrix = make_datamatrix_from_spreadsheet(spreadsheet_directory, spreadsheet_name)

######################################################################
#(2) Compute distance/similarity  matrix
'''
Every row in cognacy_matrix contains integers (cognacy statement) or "NaN" (missing data). As a measure for the distance between two doculects, we implemented the Hamming metric. The Hamming metric counts the distance between two identical integers as 0 and between two not identical integers as 1. If one of the two is missing it is also counted as 0. For example if:

         | gloss1| gloss2| gloss3| gloss4|
---------+-------+-------+-------+-------|
Doculect1|     1 |      1|      1| NaN   |
Doculect2|     1 |    NaN|      2| 1     |
Doculect3|     2 |     2 |      3| 1     |

then:

d(Doculect1, Doculect2) = 1 (only gloss3 is different)
d(Doculect2, Doculect3) = 2 (gloss1 and gloss3 are different)
d(Doculect1, Doculect3) = 3 (gloss1, gloss2 and gloss3 are different)

The percentages of different glosses (Hamming distance) would be 1/4, 2/4 and 3/4 and the cognacy percentage (or similarity) between the three fictive doculects would be 75% ((1-0.25)*100), 50% and 25%. However here missing data was counted in the same way 
as non-cognate forms which is not a sensible approach (but which is done by the pre-implemented Hamming metric of pandas). It is more appropriate to ommit all pairs with missing data. The distances become 1/2, 3/3 and 2/3, and the cognacy percentages 50%, 0% and 33%. I.e. the percentage is computed on basis of the available words, and not on basis of the whole data.
'''
######################################################################

def hamming_similarity(data_mat):
    '''
    Function for computing the distance matrix for a set of languages
    takes as an imput an nxp data matrix (as Pandas data frame) and returns an nxn distance matrix (as Pandas data frame).
    '''
    #n number of languages
    n = data_mat.shape[0]
    #p number of items in the wordlist
    p = data_mat.shape[1]
    #create two empty matrix
    num_cog = np.zeros(shape=(n,n))
    num_comp = np.zeros(shape=(n,n))
    #
    for i in range(n):
        for j in range(n):
            #Pairwise substract rows from each other
            #In the result count the number of entries = 0 to get the number of cognates
            #Count the number of non available items to get the number of effective comparisons
            #using INT - NaN = NaN (e.g. 3 - NaN = NaN)
            #e.g. [1, 2, NaN] - [1, 1, 1] = [0, 1, NaN] i.e. 1 cognate and two comparisons
            #pairwise comparisons of languages:
            lang_comp = data_mat.iloc[i,:] - data_mat.iloc[j,:]
            #number of items available:
            num_comp[i,j] = p - lang_comp.isnull().sum()
            #number of items with value 0:
            num_cog[i,j] = lang_comp[lang_comp == 0].count()
    #the hamming similarity matrix
    similarity_matrix = pd.DataFrame(num_cog/num_comp, index=data_mat.index, columns=data_mat.index)
    return similarity_matrix

#this is a matrix with pairwise cognates
pairwise_cognacy = hamming_similarity(cognacy_matrix)*100


######################################################################
#(3) Perform cluster analysis and plot data
'''
Hierarchical clusteranalysis with unrounded similarity  matrix. The preimplemented scipy algorithm was used, which is explained in the paper.
'''
######################################################################

def plot_heatmap_with_dendrogram(similarity_matrix, plot_name):
    '''
    Makes a plot of heatmap and dendrogram. Arguments are a similarity matrix (as Pandas data frame) and the name of the plot. 
    '''
    #the distance matrix has to be condensed first
    cond_dist_matrix = pdist.squareform(100 - similarity_matrix)
    #linkage makes the whole mathematics
    Z = linkage(cond_dist_matrix, 'average')
    #uncomment the print statement to see the linkage matrix
    #print(Z)
    sns.set(font='sans-serif', font_scale=0.7)
    #round the figures displayed in the heatmap as to integers
    pairwise_cognacy_displayinheatmap = np.round(similarity_matrix, decimals=0).astype(int)
    #create a seaborn clustermap object
    heatncluster = sns.clustermap(pairwise_cognacy_displayinheatmap, annot=True, cmap="inferno_r", vmax=100, fmt="d", col_linkage=Z, row_linkage=Z)
    plt.setp(heatncluster.ax_heatmap.yaxis.get_majorticklabels(), rotation=0)
    plt.setp(heatncluster.ax_heatmap.xaxis.get_majorticklabels(), rotation=45)
    plt.savefig(plot_name + ".png")

#make two plots: one for the Kho-Bwa languages only, and one for all languages
plot_heatmap_with_dendrogram(pairwise_cognacy, 'tbkhobwa')
plot_heatmap_with_dendrogram(pairwise_cognacy.iloc[:21,:21],'khobwa')

######################################################################
#(4) Simulation
'''
Motivation for the simulation was the question whether and how much different data would change the dendrogram that we obtained. Would slightly different data and cognacy decisions change the overal result? For added a matrix with random values to our matrix, made a plot like in (3) and checked "manually" whether the result was different. 

'''

def create_random_matrix(distr, mean, spread, dim):
    """
    Function to create a matrix with random entries.
    distr: probability distribution (string)
    mean: are the random values centered around the actual value (mean = 0)? Or are all values generally lower/higher? (simulating more strict/more speculative cognacy decisions)
    spread: if value is 10 then the maximum value that might be added is +-10
    dim: size of the matrix list [,]
    """
    if distr == 'binomial':
        random_matrix = np.random.binomial(n=spread*2, p=0.5, size=dim)-spread + mean
        #make a symmetric random matrix (transpose, add divide by two)
        random_matrix = (random_matrix + random_matrix.T)/2
    elif distr == 'uniform':
        random_matrix = np.random.randint(-spread, high=spread, size=dim) + mean
        random_matrix = (random_matrix + random_matrix.T)/2
    return random_matrix   
    

#Kho-Bwa with random variation (looks obiously different every time produced)
def simulate(data_set, no_sim, distr, spread, mean, out_directory, pltname):
    """
    Function to run the simulation.
    data_set: nxn data set with cognacy percentages
    no_sim: number of simulations
    distr: probability distribution
    spread: if value is 10 then the maximum value that might be added is +-10
    out_directory: where to save the plots
    pltname: plots have the name of the value of the sting in pltname, plus an integer for every simulation. E.g. simulation_1.png, simulation_2.png,...
    """
    dim = data_set.shape
    for i in range(no_sim):
        random_matrix = create_random_matrix(distr, mean, spread, dim)
        data_plus_random_matrix = data_set + random_matrix
        #cognacy percentage can not be more than 100
        data_plus_random_matrix[data_plus_random_matrix>100] = 99
        #cognacy percentage can not be less than 0
        data_plus_random_matrix[data_plus_random_matrix<0] = 0
        #diagonals still have to be 100 (cognacy percentage of a language with itself)
        data_plus_random_matrix.values[[np.arange(dim[0])]*2] = 100
        #name of plot 
        ploti = out_directory + pltname + "_" + str(i + 1)
        plot_heatmap_with_dendrogram(data_plus_random_matrix, ploti)


start_time = time.time()
simulate(pairwise_cognacy, number_of_simulations, 'uniform', 20, 0, 'simulation/', 'simulation_uni20')
print("--- %s seconds ---" % (time.time() - start_time))
