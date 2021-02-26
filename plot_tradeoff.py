import matplotlib.pyplot as plt

def read_data(path):
    file = open(path, "r")
    data = []
    for line in file:
        print(int(line))
        data.append(line)
    file.close()
    return data


def main():
    complexity_path = "complexity/apply_categories/results/complexity_scores.txt"
    communicative_path = "communicative_cost/communicative_cost.txt"

    complexity, communicative_cost = [], []
    complexity_file = open(complexity_path, "r")
    communicative_file = open(communicative_path, "r")
    
    for comp, comm in zip(complexity_file, communicative_file):
        complexity.append(int(comp))
        communicative_cost.append(float(comm))

    complexity_file.close()
    communicative_file.close()
    plt.scatter(complexity, communicative_cost, c='none', edgecolor="blue")
    plt.xlabel("Complexity")
    plt.ylabel("Communicative cost")
    plt.title("Informativeness against Complexity")
    plt.show()

if __name__ == "__main__":
    main()
    