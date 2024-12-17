import os
from subprocess import check_output
from subprocess import STDOUT

# List to hold the file paths
file_paths1 = []
directory = "input"

# Iterate over each file in the directory
for file in os.listdir(directory):
    if file != "simple.txt":
        file_path = os.path.join(directory, file)
        # Only append if it's a file (in case there are any hidden items)
        if os.path.isfile(file_path):
            file_paths1.append(file_path)

directory = "test_output"
file_paths2 = []
for file in os.listdir(directory):
    file_path = os.path.join(directory, file)
    # Only append if it's a file (in case there are any hidden items)
    if os.path.isfile(file_path):
        file_paths2.append(file_path)

hash_workers = 16
data_workers = 16
comp_workers = 16

for index, test_file in enumerate(file_paths1):
    cmd = f"go run src/main.go -hash-workers={hash_workers} -data-workers={data_workers} -comp-workers={comp_workers} -input={test_file}"
    out = check_output(cmd, shell=True, stderr=STDOUT).decode("ascii")
    output_file_name = f"my_output\\{test_file.split("\\")[-1].split(".")[0]}_output.txt"
    
    # Write the output to the file
    with open(output_file_name, 'w') as output_file:
        output_file.write(out)

for file in file_paths1:
    
    test_output_file_name = f"test_output\\{file.split("\\")[-1].split(".")[0]}_output.txt"
    my_output_file_name = f"my_output\\{file.split("\\")[-1].split(".")[0]}_output.txt"
    
    with open(test_output_file_name) as test_output, open(my_output_file_name) as my_output:
        test_output_lines = test_output.readlines()
        my_output_lines = my_output.readlines()

        if len(test_output_lines) != len(my_output_lines):
            print(f"wrong! test case: {my_output_file_name}")
        
        my_dict_cache = dict()
        test_dict_cache = dict()

        my_dict_group_cache = []
        test_dict_group_cache = []

        for index in range(len(test_output_lines)):
            line = test_output_lines[index].strip()
            my_line = my_output_lines[index].strip()

            if "group" in line:
                test_groupno = line.split(":")[0]
                my_groupno = my_line.split(":")[0]

                test_numbers = line.split(":")[1].strip().split(" ")
                my_numbers = my_line.split(":")[1].strip().split(" ")

                my_dict_group_cache.append(set(my_numbers))
                test_dict_group_cache.append(set(test_numbers))

            elif "hashTime" not in line and "hashGroupTime" not in line and "compareTreeTime" not in line:
                test_hash = line.split(":")[0]
                my_hash = my_line.split(":")[0]

                test_numbers = line.split(":")[1].strip().split(" ")
                my_numbers = my_line.split(":")[1].strip().split(" ")

                my_dict_cache[my_hash] = set(my_numbers)
                test_dict_cache[test_hash] = set(test_numbers)

        for key, set_item in my_dict_cache.items():
            if test_dict_cache[key] != set_item:
                print(f"wrong! test case: {my_output_file_name}")
                print(f"my set: {key} - {set_item}")
                print(f"test set: {key} - {test_dict_cache[key]}")
                break

        for set_item in my_dict_group_cache:
            if set_item not in test_dict_group_cache:
                print(f"wrong! test case: {my_output_file_name}")
                print(f"my set: {key} - {set_item}")
                print(f"test set: {key} - {test_dict_group_cache[key]}")
                break

    
    