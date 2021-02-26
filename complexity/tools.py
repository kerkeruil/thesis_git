import numpy as np
import sys
import pandas as pd

class Tools():
    """
    Had to write a lot op helper functions so decided to put them all in one place. 
    """
    def show_pairs(self, grid, min=0, max=999999, show=False):
        """
        Can print and return all the pairs that are in a grid.
        Note that if a max is set it will not return all the possible pairs.
        """
        itemindex = np.where(grid==1)
        indices = []
        for i,j in zip(itemindex[0][min:max], itemindex[1][min:max]):
            if grid[i][j] == 1:
                indices.append((i,j))
                if show==True:
                    print(i,j)
        return indices
                

    def save_matrix(self, matrix, path="concepts/matrix_shown.txt", mode="w"):
        """
        Writes a relational matrix of numpy arrays to given file. 
        """
        file = open(path, mode)
        for row in matrix:
            # Place comma's,remove brackets/spaces and add an enter. 
            file.write(str(list(row)).replace(" ", "")[1:-1] + "\n")

        # Print diagonal.
        file.write("\n" + str(np.diagonal(matrix)))
        file.close()


    def write_matrix_to_file(self, categories, path_matrix, path_names):
        """ 
        Writes a list of matrices to a given file. Different from save matrix because it is for lists while save_matrix 
        just prints one matrix. Yes, the can be combined but I found it more helpfull to make it different functions. 
        Naming could be better though. 
        """
        file_m = open(path_matrix, "w")
        file_n = open(path_names, "w")
        for name, matrix, _ in categories:
            for row in matrix:
                # Place comma's,remove brackets/spaces and add an enter. 
                file_m.write(str(list(row.astype(int))).replace(" ", "")[1:-1] + "\n")
            file_m.write(" \n")
            file_n.write(str(list(name)).replace(" ", "")[1:-1] + "\n")

        file_m.close()
        file_n.close()
        print("Succesfully wrote matrix to", path_matrix)
        print("Succesfully wrote names to", path_names)


    def remove_cross_tree_relations(self, matrix):
        """ 
        Remove blocks from the matrix.
            | 0-56  57-112 113 114
        ---------------------------
        0   | x x x  0 0 0  x   0   
        -   | x x x  0 0 0  x   0
        56  | x x x  0 0 0  x   0
            |
        57  | 0 0 0  x x x  0   x
        -   | 0 0 0  x x x  0   x
        112 | 0 0 0  x x x  0   x
            |
        113 | x x x  0 0 0  x   x
        114 | 0 0 0  x x x  x   x
        x = possible pair
        0 = blocked out by code

        """
        matrix[0:57, 57:113] = 0
        matrix[57:113, 0:57] = 0
        matrix[113, 57:115] = 0
        matrix[57:115, 113] = 0
        matrix[114, 0:57] = 0
        matrix[0:57, 114] = 0
        return matrix


    def filter_familymembers(self, matrix):
        """
        Returns currently only the columns with the selected family members.
        """
        usefull_members = np.array([9,10,11,12,13,14,15,16,17,18,19,20,21,22,31,32,33,34,43,44,45,46,47,48,49,50,
                        51,52,53,54,55,56,65,66,67,68,69,70,71,72,73,74,75,76,77,78,87,88,89,90,99,100,
                        101,102,103,104,105,106,107,108,109,110,111,112,113,114])
        # Select columns of usefull members
        columns = matrix[:,usefull_members]
        return columns[usefull_members]


    def extract_ego_relatives(self, matrix):
        # Get amount of columns.
        n = len(matrix.transpose())

        # Now the same procedure as Kemp.
        firsthalf  = np.arange(1,(n-2)/2, dtype=int)
        secondhalf = np.arange((firsthalf[-1]+1),n-2, dtype=int)
        ego1 = n-2
        ego2 = n-1

        exm2a = matrix[:,ego1][firsthalf]
        exm2b = matrix[:,ego2][secondhalf]
        exm2c = matrix[:,ego1][secondhalf]
        exm2d = matrix[:,ego2][firsthalf]   
        exm2e = matrix[:,ego1][np.append(ego1, ego2)]
        exm2f = matrix[:,ego2][np.append(ego1, ego2)]

        return np.concatenate((exm2a, exm2b, exm2c, exm2d, exm2e, exm2f))


    def filter_by_ego(self, categories):
        """
        Takes the ego relative extension of a matrix and compares and filters the other matrices 
        with the same extension.
        Returns a list with the full matrices. 
        """
        categories_no_duplicates = []
        count = 0
        for i in range(len(categories)):
            dup = False
            category = categories.pop(0)
            ego = self.extract_ego_relatives(category[1])
            for _, duplicate in categories:
                count+=1
                ego_dup = self.extract_ego_relatives(duplicate)
                comparisson = ego == ego_dup
                if comparisson.all():
                    dup = True
                    break

            if dup == False:
                categories_no_duplicates.append(category)

        return categories_no_duplicates


    def filter_by_score(self, categories, ego=False):
        """
        Puts the categories with the best scores in a new list. 
        By popping and removing the categories that are found, we avoid double checking.
        """

        all_names = []
        all_matrixes = []
        all_scores = []
        for name, matrix, score in categories:
            all_names.append(name)
            all_matrixes.append(matrix)
            all_scores.append(score)

        all_matrixes = np.array(all_matrixes)
        all_scores = np.array(all_scores)

        # Get list that refers to the index of the first duplicate element
        # This works slightly confusing: return_corresponds the the array of unique elements where for every element
        # there is a integerer refering to that elements original place in the given list. Apparanlty the function does 
        # not keep the original order.

        # return_inverse return a list (same size as input) that enables reconstruction of the original input. On every index
        # it refers to what element of the unique array was supposed to stand there. For example
        #  array = [a, b, c, d, d]

        #  unique_array = [a, c, b, d] --> original order is not preserved.
        #  inds = [0, 2, 1, 3]
        #  inv_inds = [0, 2, 1, 4, 4]
        if ego:
            ego_filtered_matrixes = [self.extract_ego_relatives(m) for m in all_matrixes]
            _, inds, inv_inds, counts = np.unique(ego_filtered_matrixes, return_index=True, return_inverse=True, return_counts=True, axis=0)

        else:
            _, inds, inv_inds, counts = np.unique(all_matrixes, return_index=True, return_inverse=True, return_counts=True, axis=0)
        best_categories = []
        for i, ind in enumerate(inds):
            if counts[i] > 1:
                # Return index of duplicate matrixes
                inds_dup_matrixes = np.where(inv_inds == i)
                # Extract score of duplicate matrixes
                scores = all_scores[inds_dup_matrixes]
                # Transfer other lists as well to make indexing easier
                names = [all_names[n] for n in inds_dup_matrixes[0]]
                matrixes = all_matrixes[inds_dup_matrixes]
                # Get index of lowest score
                best = np.argmin(scores)
                # Save the name, matrix and score (the full element) to best_categories.
                best_categories.append((names[best], matrixes[best], scores[best]))
            else:
                best_categories.append(categories[ind])

        return best_categories


    def pause(self):
        """
        Helper function to pause which is also not a python function weirdly enough.
        """        
        programPause = input("pause\n")


