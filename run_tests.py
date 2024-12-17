import os
from subprocess import check_output
from subprocess import STDOUT
from subprocess import CalledProcessError
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib

IMPLEMENTATION = 2
SEQ_FILE = "graphTimings\\seq.txt"
PAR_FILE1 = "graphTimings\\par1.txt"
PAR_FILE2 = "graphTimings\\par2.txt"

i= ["input/coarse.txt", "input/fine.txt"]
hash_workers = [2,4,8,16,32]
data_workers = [2,4,8,16,32]
comp_workers = [2,4,8,16,32]

fastest_coarse = [100,100,100]
fastest_fine = [100,100,100]

test_loops = 10
fastest_coarse_par = dict()
fastest_fine_par = dict()

for _ in range(test_loops):
    for worker_index in range(len(hash_workers)):
        for index, test_file in enumerate(i):
            hash_worker = hash_workers[worker_index]
            data_worker = data_workers[worker_index]
            comp_worker = comp_workers[worker_index]
            cmd = f"go run src/main.go -hash-workers={hash_worker} -data-workers={data_worker} -comp-workers={comp_worker} -input={test_file}"
            out = check_output(cmd, shell=True, stderr=STDOUT).decode("ascii")
            outarr = out.split(" ")
            hashTimeArr = outarr[1]
            hashTime = float(hashTimeArr.split("\n")[0])
            if index ==0:
                if hashTime<fastest_coarse[0]:
                    fastest_coarse[0] = hashTime
            else:
                if hashTime<fastest_fine[0]:
                    fastest_fine[0] = hashTime

            outarr = out[out.index("hashGroupTime:"):].split(" ")
            groupTimeArr = outarr[1]
            groupTime = float(groupTimeArr.split("\n")[0])
            if index==0:
                if groupTime<fastest_coarse[1]:
                    fastest_coarse[1] = groupTime
            else:
                if groupTime<fastest_fine[1]:
                    fastest_fine[1] = groupTime

            outarr = out[out.index("compareTreeTime:"):].split(" ")
            compareTimeArr = outarr[1]
            compareTime = float(compareTimeArr.split("\n")[0])
            if index ==0:
                if compareTime<fastest_coarse[2]:
                    fastest_coarse[2] = compareTime
            else:
                if compareTime<fastest_fine[2]:
                    fastest_fine[2] = compareTime
        if len(hash_workers)>1:
            if hash_workers[worker_index] in fastest_coarse_par.keys():
                coarse_arr = fastest_coarse_par[hash_workers[worker_index]]
                fine_arr = fastest_fine_par[hash_workers[worker_index]]

                for compare_index in range(len(coarse_arr)):
                    if coarse_arr[compare_index] >fastest_coarse[compare_index]:
                        coarse_arr[compare_index] = fastest_coarse[compare_index]
                    if fine_arr[compare_index]>fastest_fine[compare_index]:
                        fine_arr[compare_index] = fastest_fine[compare_index]
                
                fastest_fine_par[hash_workers[worker_index]] = fine_arr
                fastest_coarse_par[hash_workers[worker_index]] = coarse_arr
            else:
                fastest_coarse_par[hash_workers[worker_index]] = fastest_coarse
                fastest_fine_par[hash_workers[worker_index]] = fastest_fine
            fastest_coarse = [100,100,100]
            fastest_fine = [100,100,100]
    print(_)



if len(hash_workers) == 1 and len(data_workers) ==1 and len(comp_workers) ==1:
    with open(SEQ_FILE, 'w') as output_file:
        output_file.write(f"{fastest_coarse[0]} {fastest_coarse[1]} {fastest_coarse[2]};{fastest_fine[0]} {fastest_fine[1]} {fastest_fine[2]}")

if len(hash_workers)>1 and len(data_workers)>1 and len(comp_workers)>1 and IMPLEMENTATION == 1:
    with open(PAR_FILE1, 'w') as output_file:
        for worker_num in hash_workers:
            output_file.write(f"{worker_num}:{fastest_coarse_par[worker_num]};")
        output_file.write("\n")
        for worker_num in hash_workers:
            output_file.write(f"{worker_num}:{fastest_fine_par[worker_num]};")
        output_file.write("\n")


if len(hash_workers)>1 and len(data_workers)>1 and len(comp_workers)>1 and IMPLEMENTATION == 2:
    with open(PAR_FILE2, "w") as output_file:
        for worker_num in hash_workers:
            output_file.write(f"{worker_num}:{fastest_coarse_par[worker_num]};")
        output_file.write("\n")
        for worker_num in hash_workers:
            output_file.write(f"{worker_num}:{fastest_fine_par[worker_num]};")
        output_file.write("\n")


        