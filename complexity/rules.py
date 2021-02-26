import numpy as np
import sys
import copy

class Rules(object):
    # This class is based on the makecomp.m file from C. Kemp and T. Regier.
    def conjunction(self, a, b, singles=None):
        """ 
        Return members that are in set A as well as set B. Has singles boolean which means the 
        a array is passed in rather than another matrixes. Is meant for the exceptions male and female. 
        """
        if singles == "singles":
            # b.transpose() is the y variations of the rules. (A(x,y) -- A(y)).
            return np.logical_and(a, b).astype(int), np.logical_and(a, b.transpose()).astype(int)
        return np.logical_and(a, b).astype(int)


    def disjunction(self, a, b, singles=None):
        """
        Return members that are either in set A or in set B.
        """ 
        # Identity operation is to set the diagonal to 0.
        disj = np.logical_and(np.logical_or(a, b), (1-np.identity(a.shape[0]))).astype(int)
        if singles == "singles":
            disj_y = np.logical_and(np.logical_or(a, b.transpose()).astype(int), (1-np.identity(a.shape[0]))).astype(int)
            return disj, disj_y
        return disj


    def transitive(self, a, b):
        """
        C(x,y) = A(x,z) conjunction B(z,y).
        """
        return np.logical_and(a.dot(b), (1-np.identity(a.shape[0]))).astype(int)


    def inverse(self, a):
        """
        Returns the inverse of a matrix.
        """
        return a.transpose()


    def symmetric_closure(self, a):
        """
        Returns a symmetricly closed set i.e. every pair and its inverse.
        """
        return np.logical_or(a, a.transpose()).astype(int)


    def transitive_closure(self, a, close_max=12):
        """
        Return transitive closed set. Close max is to what depth the set should be closed.
        Kemp and Regier set it at 12 so that is the default now. 
        """
        n = a.shape[0]
        diag = a.diagonal()
        tmp = np.logical_or(a, np.identity(n)).astype(int)
        tmp = np.logical_and(np.linalg.matrix_power(tmp,close_max), (1 - np.identity(n)))
        return np.logical_or(tmp, diag).astype(int)
        