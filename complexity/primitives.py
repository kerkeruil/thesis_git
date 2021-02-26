import numpy as np

"""
Kemp and Regier created a 3D matrix where the x and y directions represent the pairs, for example:
  |  1   2   3
--|-----------
1 |  1   0   0
  |
2 |  0   0   1  
  |
3 |  0   0   0
Says that the category has the pairs (1,1) and (2,3)

The z direction represents the categories. So the matrix (M) above could be M(0, 0, 3) = Parents 
Currently there is no 3e dimension but just a list for time mangagement. 3e Dimension can alsways be
implemented later.
"""
class Primitives(object):
	def __init__(self):
		# Grid = family_tree +1 because python counts from 0 which means that familymember 114 
		# is out of bounds. Now we can just ignore row and column 0.
		self.n = 115

		self.f_matrix, self.females = self.get_females()
		self.m_matrix, self.males = self.get_males()
		self.parents = self.get_parents()
		self.childeren = self.parents.transpose()
		self.older = self.get_older()
		self.younger = self.older.transpose()
		self.samesex = self.get_samesex()
		self.diffsex = self.get_diffsex()

		# R(x)
		# Putting the name in a list makes it later possible to convert the whole tuple to an numpy array.
		self.singles = [('11', self.f_matrix, 0), ('12',self.m_matrix, 0)]
		# R(x,y)
		self.doubles = [('21', self.parents, 0), ('22',self.childeren, 0), ('23',self.samesex, 0), ('24',self.diffsex, 0), ('25',self.older, 0), ('26',self.younger, 0)]


	def get_females(self):
		females = np.array([1,3,5,7,9,11,13,14,15,18,19,23,25,27,29,31,32,35,37,39,41,
						43,45,47,49,51,53,55,57,59,61,63,65,67,69,70,71,74,75,79,
						81,83,85,87,88,91,93,95,97,99,101,103,105,107,109,111,113]).astype(int)
		
		# Create binair array of length 115 that has a one at the location of female members. 
		# Transpose the array and paste it a 115 times in a row as columns. Slightly confusing
		# but the result is this matrix:

		"""
		   | 0 1 2 3 4
		--------------
		0  | 0 0 0 0 0
		1  | 1 1 1 1 1
		2  | 0 0 0 0 0
		3  | 1 1 1 1 1
		4  | 0 0 0 0 0

		Where all the females on the vertical axis have an array of ones. This is Female(x).
		"""

		binair_array = np.zeros(self.n)
		binair_array[females] = 1
		binair_matrix = np.array([binair_array]*self.n).transpose()
		return binair_matrix.astype(int), females


	def get_males(self):
		# Inverse of female
		males =  np.delete(np.arange(0, self.n), self.females)[1:]
		binair_matrix = np.ones((self.n, self.n)) - self.f_matrix
		binair_matrix[:,0] = 0
		binair_matrix[0] = 0
		return binair_matrix.astype(int), males


	def get_parents(self):
		parentpairs = [
				[[1,2],  [9]],
				[[3,4],  [10]],
				[[5,6],  [11]],
				[[7,8],  [12]],
				[[9,10], [13,17]],
				[[11,12],[18,22]],
				[[13],   [23,24]],
				[[14],   [25,26]],
				[[16],   [27,28]],
				[[17],   [29,30]],
				[[18],   [35,36]],
				[[19],   [37,38]],
				[[21],   [39,40]],
				[[22],   [41,42]],
				[[31],   [43,44]],
				[[32],   [45,46]],
				[[33],   [49,50]],
				[[34],   [51,52]],
				[[47],   [53,54]],
				[[48],   [55,56]]
				]

		parents_grid = np.zeros((self.n, self.n))

		# Loop over pairs, then take the parents and (if possible) range of childeren.
		# Connect each parent to all of the childeren by putting a one in the grid where 
		# they overlap.
		for parents, childeren in parentpairs:
			for parent in parents:
				if len(childeren) > 1:
					first, last = childeren
					for child in range(first, last + 1):
						parents_grid[parent][child] = 1
						parents_grid[parent+56][child+56] = 1
				else:
					parents_grid[parent][childeren[0]] = 1
					parents_grid[parent+56][childeren[0]+56] = 1

		# Put alice and bob in the grid. This can't be done earlier because the previous code
		# create a list of the range of all the childeren which doens't work here. Writing something 
		# that fits all with a lot of if statements is more choatic than this.
		alice_bob = [
					[[113],  [47,48]],
					[[15,20], [31,32,113,33,34]], 
					[[114],   [103,104]],
					[[71,76], [87,88,114,89,90]]]

		for parents, childeren in alice_bob:
			for parent in parents:
				for child in childeren:
					parents_grid[parent][child] = 1
		return parents_grid.astype(int)


	def get_older(self):
		agegroups  = [
			[*range(1,9), *range(57,65)],
			[*range(9,13), *range(65,69)],
			[14,17,19,22,70,73,75,78], # Elder child (i.e: MZe)
			[15,20,71,76], # Middle child
			[13,16,18,21,69,72,74,77], # Younger child (i.e: MZy)
			[32,34,88,90],
			[*range(23,31), 113, *range(35,43),*range(79,87),114,*range(91,99)],
			[31,33,87,89],
			[*range(43,53), *range(99,109)],
			[*range(53,57), *range(109,113)]]

		grid = np.zeros((self.n, self.n))
		for i, generation in enumerate(agegroups):
			# Stop looping if youngest generation is reached. 
			if i == len(agegroups) - 1:
				break

			template_array = np.zeros(self.n)
			younger = np.array(sum(agegroups[i+1:], []))
			# Create array of zeros with values at index of younger members.

			template_array[younger] = 1
			for member in generation:
				grid[member] = template_array
		return grid.astype(int)


	def get_samesex(self):
		"""
		Pairs every female member to every other female member
		"""
		grid = np.zeros((self.n, self.n))
		for f0 in self.females:
			for f1 in self.females:
				grid[f0][f1] = 1
		for m0 in self.males:
			for m1 in self.males:
				grid[m0][m1] = 1 

		# Remove selfrefering pairs
		grid = np.logical_and(grid, (1-np.identity(self.n)))	
		return grid.astype(int)


	def get_diffsex(self):
		"""
		Pairs every female member to every other male member and vice versa.
		"""
		grid = np.zeros((self.n, self.n))
		for f in self.females:
			for m in self.males:
				grid[m][f] = 1
		grid = grid + grid.transpose()
		grid = np.logical_and(grid, (1-np.identity(self.n)))
		return grid.astype(int)
		
prim = Primitives()