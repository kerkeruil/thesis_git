import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt


class informativeness(object):
	def __init__(self, plot=True):
		"""
		Initialize the values for the class and computes the communicative cost for each language.

		The columns english and german aren't necesarry but form by using formula's the average column in the xls file which meant that
		removing them also removed to average file, this was the fastest way. And who knows... maybe using the only 
		the english or german probabilities yields better results and we can test that now. 
		"""
		self.filename = "rwpartitions.txt"
		self.probs = pd.read_csv("need_probs.csv")
		self.probs.columns = ["category",
								"english",
								"german", 
								"average"]
		self.female, self.male, self.word_count, self.female_tree, self.male_tree = [], [], [], [], []

		# Put all members that have a probility in the self.male of self.female list.
		self.get_useful_partitions()

		# Fill tree lists with members of the family tree in the same order as the partitions.
		self.get_family_tree()

		print("For female tree")
		f_cost = np.array(self.calculate_communication_cost(self.female, self.female_tree))
		print("For male tree")
		m_cost = np.array(self.calculate_communication_cost(self.male, self.male_tree))

		tot_cost = (f_cost + m_cost)/2
		self.store_data("communicative_cost.txt", tot_cost)

		# Doesn't plot based on the stored data (yet).
		if plot == True:
			print(len(self.word_count))
			print(len(tot_cost))
			self.plot_data(self.word_count, tot_cost, ["Word count", "Communicative Cost"], "Communicative cost against Word Count")


	def calculate_communication_cost(self, partitions, tree):
		"""
		Calculates the communicative cost of a given partion. Assumes that the partition is female of male.

		Instead of calculating the addition cost (c) for each member and then looping over the familiy again 
		to multiply it with the need probability (p_i). It multiplies it immediatly so that p_i doesn't have to 
		be stored ore called twice.
		"""
		comm_cost_tmp = []
		count = 0
		n = len(partitions)
		for partition in partitions:
			count +=1
			if (count % 50) == 0:
				print("Now handeling partition {} of the {}".format(str(count), n))
			individual_communicative_cost = []
			for code, category in zip(partition, tree):
				p_i = self.get_probability(category)
				p_j = self.make_p_j(partition, code, tree)
				individual_communicative_cost.append(-math.log2(p_i/p_j))
			comm_cost_tmp.append(sum(individual_communicative_cost))

		return np.array(comm_cost_tmp)


	def make_p_j(self, partition, code, tree):
		# Gives a tuple of indices with the same code.
		indices = np.where(partition == code)[0]
		# Loop over indices and get all the probabilites of the categories found. Add those together 
		# to get p_j.
		return sum([self.get_probability(tree[i]) for i in indices])
			


	def get_probability(self, category):
		return self.probs.loc[self.probs["category"] == category, "average"].values[0]

	def get_useful_partitions(self): 
		"""
		Filters the members of the family tree that don't have a probability.

		(The first integer in a partition is the frequency but that starts at zero and the members are counted from one.)
		"""
		categories_with_probability_female = np.array([*range(9, 23), *range(31, 35), 47, 48, *range(53, 57)])
		categories_with_probability_male = np.array([*range(65, 79), *range(87, 91), *range(99, 113)])
		
		with open(self.filename, 'r') as f:
			for line in f:
				line = np.array(line.split())
				f_partition = line[categories_with_probability_female]
				m_partition = line[categories_with_probability_male]
				self.female.append(f_partition)
				self.male.append(m_partition)
				tmp_count = (len(set(f_partition)) + len(set(m_partition)))/2
				self.word_count.append(tmp_count)


	def get_family_tree(self):
		"""
		Returns a list with the familiymembers in the order of the partitions. 
		Brothers and sisters have each a younger and an elder variant which is why they 
		are doubled.  
		"""
		aunt = 2*["aunt"]
		uncle = 2*["uncle"]
		brother = 2*["brother"]
		sister = 2*["sister"]
		nn = ["niece", "nephew"]
		grandkids = ["granddaughter", "grandson"]

		self.female_tree = ["grandmother", "grandfather", "grandmother", "grandfather",
										*aunt, "mother", *uncle, *aunt, "father", *uncle,
														*sister, *brother,
														"daughter", "son", 
													*grandkids, *grandkids]

		self.male_tree = ["grandmother", "grandfather", "grandmother", "grandfather",
										*aunt, "mother", *uncle, *aunt, "father", *uncle,
														*sister, *brother,
													*nn, *nn, "daughter", "son", *nn, *nn, 
														*grandkids, *grandkids]
													


	def store_data(self, location, data):
		"""
		Store data in given location. Works for txt files. 
		"""
		with open(location, "w") as file:
			# np.set_printoptions(linewidth=np.inf)
			for e in data:
				file.write(str(e) + "\n")


	def plot_data(self, x, y, labels, title):
		"""
		Plot the data
		"""
		plt.scatter(x, y, c='none', edgecolor="blue");
		plt.xlabel(labels[0]);
		plt.ylabel(labels[1]);
		plt.title(title);
		plt.show()


test = informativeness()
# print(test)