import os
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np

def toFloat(arr:[])->[]:
    return [float(strnum) for strnum in arr]

SEQ_FILE = "graphTimings\\seq.txt"
PAR_FILE1 = "graphTimings\\par1.txt"
PAR_FILE2 = "graphTimings\\par2.txt"

seq_coarse = []
seq_file = []
with open(SEQ_FILE) as output_file:
    output_str = output_file.readlines()[0].strip()
    seq_coarse = output_str.split(";")[0].split(" ")
    seq_fine = output_str.split(";")[1].split(" ")

seq_coarse = toFloat(seq_coarse)
seq_fine = toFloat(seq_fine)

par1_coarse = []
par1_fine = []
x = []
with open(PAR_FILE1) as output_file:
    output_str = output_file.readlines()
    coarse_str = output_str[0]
    fine_str = output_str[1]
    coarse_arr = coarse_str.split(";")
    fine_arr = fine_str.split(";")
    
    for item in coarse_arr[:len(coarse_arr)-1]:
        item = eval(item.split(":")[-1])
        item = toFloat(item)
        par1_coarse.append(item)

    for item in fine_arr[:len(fine_arr)-1]:
        temp_item = eval(item.split(":")[-1])
        x.append(item.split(":")[0])
        temp_item = toFloat(temp_item)
        par1_fine.append(temp_item)

par2_coarse = []
par2_fine = []
with open(PAR_FILE2) as output_file:
    output_str = output_file.readlines()
    coarse_str = output_str[0]
    fine_str = output_str[1]
    coarse_arr = coarse_str.split(";")
    fine_arr = fine_str.split(";")

    for item in coarse_arr[:len(coarse_arr)-1]:
        item = eval(item.split(":")[-1])
        item = toFloat(item)
        par2_coarse.append(item)

    for item in fine_arr[:len(fine_arr)-1]:
        item = eval(item.split(":")[-1])
        item = toFloat(item)
        par2_fine.append(item)

np_par1_coarse = np.array(par1_coarse).T
np_par1_fine = np.array(par1_fine).T
np_par2_coarse = np.array(par2_coarse).T
np_par2_fine = np.array(par2_fine).T
seq_coarse = np.array(seq_coarse)
seq_coarse = seq_coarse[:, np.newaxis]
seq_fine = np.array(seq_fine)
seq_fine = seq_fine[:, np.newaxis]
par1_coarse_speedup = seq_coarse / np_par1_coarse
par1_fine_speedup = seq_fine / np_par1_fine
par2_coarse_speedup = seq_coarse / np_par2_coarse
par2_fine_speedup = seq_fine / np_par2_fine

par1_coarse_speedup = np.mean(par1_coarse_speedup, axis = 1)
par1_fine_speedup = np.mean(par1_fine_speedup, axis = 1)

sns.lineplot(x=x, y=1, label = "sequential", linestyle = '--')
sns.lineplot(x=x, y=par1_coarse_speedup[0], label = "goroutine-per-bst", linestyle='--')
sns.lineplot(x=x, y=par2_coarse_speedup[0])

plt.title("Hashtime Speedup vs Number of Hash Workers(coarse.txt)")
plt.ylabel("Speedup (Seq/Par)")
plt.xlabel("Number of Hash Workers")
plt.grid(visible=True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.savefig('graphs/hash_speedup_coarse.png')

plt.clf()

sns.lineplot(x=x, y=1, label = "sequential", linestyle = '--')
sns.lineplot(x=x, y=par1_coarse_speedup[1], label = "goroutine-per-bst", linestyle='--')
sns.lineplot(x=x, y=par2_coarse_speedup[1])
plt.title("HashGroupTime Speedup\n vs Number of HashWorkers and DataWorkers(coarse.txt)")
plt.ylabel("Speedup (Seq/Par)")
plt.xlabel("Number of Hash Workers and Data Workers(HashWorkers = DataWorkers)")
plt.grid(visible=True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.savefig('graphs/hashGroup_speedup_coarse.png')

plt.clf()

sns.lineplot(x=x, y=1, label = "sequential", linestyle = '--')
sns.lineplot(x=x, y=par1_coarse_speedup[2], label = "goroutine-per-bst", linestyle='--')
sns.lineplot(x=x, y=par2_coarse_speedup[2])
plt.title("Compare Speedup vs Number of Compare Workers(coarse.txt)")
plt.ylabel("Speedup (Seq/Par)")
plt.xlabel("Number of Compare Workers")
plt.grid(visible=True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.savefig('graphs/compare_speedup_coarse.png')

plt.clf()

sns.lineplot(x=x, y=1, label = "sequential", linestyle = '--')
sns.lineplot(x=x, y=par1_fine_speedup[0], label = "goroutine-per-bst", linestyle='--')
sns.lineplot(x=x, y=par2_fine_speedup[0])
plt.title("Hashtime Speedup vs Number of Hash Workers(fine.txt)")
plt.ylabel("Speedup (Seq/Par)")
plt.xlabel("Number of Hash Workers")
plt.grid(visible=True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.savefig('graphs/hash_speedup_fine.png')

plt.clf()

sns.lineplot(x=x, y=1, label = "sequential", linestyle = '--')
sns.lineplot(x=x, y=par1_fine_speedup[1], label = "goroutine-per-bst", linestyle='--')
sns.lineplot(x=x, y=par2_fine_speedup[1])
plt.title("HashGroupTime Speedup\n vs Number of HashWorkers and DataWorkers(fine.txt)")
plt.ylabel("Speedup (Seq/Par)")
plt.xlabel("Number of Hash Workers and Data Workers(HashWorkers = DataWorkers)")
plt.grid(visible=True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.savefig('graphs/hashGroup_speedup_fine.png')


