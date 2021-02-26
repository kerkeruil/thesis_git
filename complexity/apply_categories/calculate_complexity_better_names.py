import numpy as np
import ast
import sys

import matplotlib.pyplot as plt

# Get class from one directory above
sys.path.append("..")

from tools import Tools


def read_in_partitions(path_to_file):
    usefull_members = np.array([9,10,11,12,13,14,15,16,17,18,19,20,21,22,31,32,33,34,43,44,45,46,47,48,49,50,
                        51,52,53,54,55,56,65,66,67,68,69,70,71,72,73,74,75,76,77,78,87,88,89,90,99,100,
                        101,102,103,104,105,106,107,108,109,110,111,112])

    file = open(path_to_file, "r")
    partitions = []
    for line in file:
        # First element is frequency of partition
        line = np.array(line.split())
        # Select columns of usefull members
        members = line[usefull_members]
        partitions.append(members)
    file.close()
    return np.array(partitions)


def read_in_categories(path_to_file):
    file = open(path_to_file, "r")
    matrices, matrix = [], []
    for line in file:
        line = line.split(',')
        # Remove \n at the end of the last element.
        line[-1] = line[-1][:1]
        if line == [" "]:
            matrices.append(np.array(matrix, dtype=int))
            matrix =[]
        else:
            matrix.append(line)
    file.close()
    return matrices


def read_in_names(path_to_file):
    file = open(path_to_file, "r")
    names = []
    for line in file:
        line = list(ast.literal_eval(line))
        names.append(line)
    file.close()
    return names
    

def get_ego_relatives_from_list(categories):
    """
    Returns a list of all the ego relative extensions of given list of categories.
    """
    egos = []
    for c in categories:
        egos.append(get_ego_relatives_from_matrix(c))
    return np.array(egos)

        
def get_ego_relatives_from_matrix(matrix):
    """
    Extract the ego relative extension from a matrix.
    Different from the one in tools because it does not store the relations of
    the male tree members towards Alice and the relations between Alice and Bob
    """
    n = len(matrix.transpose())
    firsthalf  = np.arange(0,(n-2)/2, dtype=int)
    secondhalf = np.arange((firsthalf[-1]+1),n-2, dtype=int)
    exm2a = matrix[:,n-2][firsthalf]
    exm2b = matrix[:,n-1][secondhalf]
    return np.concatenate((exm2a, exm2b))


def get_unique_terms_as_ego(partition):
    """
    Returns a numpy array of all the unique terms in a partition as ego-relative extentions.
    This makes finding intensions by matching the terms a lot easier. 
    """
    uniques = np.unique(partition)
    n = len(partition)
    egos = []
    for u in uniques:
        zeros = np.zeros(n)
        indices = np.where(partition==u)
        # Rereate the ego relative extension by setting al indices that contain
        # the term to 1. 
        np.put(zeros, indices, 1)
        egos.append(zeros.astype(dtype=int))
    return np.array(egos)


def get_dict_with_intension(unique_terms, ego_of_categories, names_of_categories):
    """
    Returns a dictionary of intensions with as key the index of the term and as a value a list
    of the corresponding intensions.
    """
    d = dict()
    for i, ego_term in enumerate(unique_terms):
        # Get indices of categories that match the partition.
        inds = np.where((ego_term == ego_of_categories).all(axis=1))[0]

        # No intensions are found that match the term.
        if inds.size == 0:
            intensions = ([-1], 1)
        else:
            intensions = ([names_of_categories[ind] for ind in inds], inds.size)
        # Save index of term in list of unique terms as key. The ego of the term is a np.array which is unhashable so
        # this was the quickest solution I could come up with. There is probably something better.
        d[i] = intensions
    return d


def flatten(x):
    """
    Small function to flatten a normal list which apparantly doesn't exist already in python.
    """
    if isinstance(x, list):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]

def add_definition(intension, definitions):
    """
    Add definition to given list of definition if not in their already.
    """
    dup = False
    for defi in definitions:
        if defi == intension:
            dup = True
            break 
    if not dup:
        definitions.append(intension)
    return definitions


def deconstruct(intensions, definitions):
    """
    Uses recursion to append every intension in given list of intensions to definition.
    Example: the intension [[[12, 22], [23, 12]], [[22, 22]]] will result in 
    a the list of defintions: [[[12, 22], [23, 12]], [12, 22], [23, 12], [22, 22]]].
    """
    if isinstance(intensions, int):
        return definitions

    definitions = add_definition(intensions, definitions)

    tmp = flatten(intensions)
    if len(tmp) > 3:
        for s_int in intensions:
            # Check if intension already defined.
            definitions = add_definition(s_int, definitions)

            # Flatten the list.
            tmp = flatten(s_int)
            if len(tmp) > 3:
                definitions = deconstruct(s_int, definitions)
    return definitions


def find_minimal_complexiy(unique_terms, dict_with_intensions, definitions=[], score=None):
    """
    """
    end_node = True
    for term in range(len(unique_terms)):
        intensions = dict_with_intensions[term]
        if score != None and len(definitions) > score:
            return score
        if intensions[-1] > 1:
            # Because there are more intensions to try.
            end_node = False
            for s_int in intensions[0]:
                tmp_definitions = deconstruct(s_int, definitions.copy())
                tmp_dict = dict_with_intensions.copy()
                tmp_dict[term] = (s_int, 1)
                score = find_minimal_complexiy(unique_terms, tmp_dict, tmp_definitions, score)
        else:
            # Which is now just 1 intension despite the name. 
            if intensions[0] not in definitions:
                definitions = deconstruct(intensions[0][0], definitions)

    if end_node == True:
        score = len(definitions)
    return score


def main():
    ts = Tools()
    partitions = read_in_partitions("partitions/rwpartitions.txt")
    categories = read_in_categories("categories/bn_matrix_depth_3")
    names_of_categories = read_in_names("categories/bn_names_depth_3")
    egos_of_categories = get_ego_relatives_from_list(categories)

    scores = []
    n = len(partitions)
    count = 0
    max_configurations = 10000
    word_count = []
    for par in partitions:
        count+=1
        if count % 10 == 0: # To let the person running know how far the matching is.
            print("currently at partition {} of the {}".format(count, n))
        unique_terms = get_unique_terms_as_ego(par)
        dict_with_intensions = get_dict_with_intension(unique_terms, egos_of_categories, names_of_categories)
        score = find_minimal_complexiy(unique_terms, dict_with_intensions, max_configurations)
        scores.append(score)
        word_count.append(len(unique_terms))

    # Store data to file.
    with open("results/complexity_scores.txt", "w") as file:
        for s in scores:
            file.write(str(s) + "\n")
    print("Wrote scores to file complexity_scores.txt in the results directory.")

    plt.scatter(word_count, scores, c='none', edgecolor="blue")
    plt.xlabel("wod")
    plt.ylabel("compl cost")
    plt.title("Informativeness against Complexity")
    plt.show()
if __name__ == "__main__":
    main()
    