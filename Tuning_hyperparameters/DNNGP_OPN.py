# DNNGP优化脚本
import os
import re
import json
import subprocess
import numpy as np
import nevergrad as ng
# The script needs to set parameters in three places, one is the #10 directory location, the second is the #21 hyperparameter search space, and the third is the #49 DNNGP native command.
# Set priorities in descending order, except for the directory, the default parameters are sufficient for most requests.
# Define directories and file paths
output_dir = r'..\Output_files'
pkl_file = r"..\Input_files\wheat599_pc95.pkl"
pkl_dir = os.path.dirname(pkl_file)
budget = 200  # Optimize the number of script iterations
alpha = 0.7  # Adjust this weight to balance the importance of mean and variance in the optimization process
beta = 0.1  # This parameter is adjusted to control the nonlinear effect of the deviation in the optimization process
cvs = 10 # K-fold cross-validation

# Obtain all tsv files in the directory where the pkl file resides
tsv_files = [f for f in os.listdir(pkl_dir) if f.endswith('.tsv')]

# Define super parameter search space (see https://github.com/facebookresearch/nevergrad)
instr = ng.p.Instrumentation(
    batch_size=ng.p.Scalar(lower=32, upper=1024).set_integer_casting(),
    lr=ng.p.Log(lower=1e-4, upper=1),
    patience=ng.p.Scalar(lower=10, upper=50).set_integer_casting(),
    dropout1=ng.p.Log(lower=0.0, upper=0.9),
    dropout2=ng.p.Log(lower=0.0, upper=0.9),
    earlystopping=ng.p.Scalar(lower=50, upper=100).set_integer_casting()
)

# Define a function to extract statistic values

def extract_statistics(output):
    statistics = re.findall(r'statistic=([-+]?[0-9]*\.?[0-9]+)', output)
    if not statistics:
        return 0.0
    statistic_values = float(statistics[0])
    return statistic_values

# Define the objective function


def objective(batch_size: int, lr: float, patience: int, dropout1: float, dropout2: float, earlystopping: int, tsv_file: str):
    accuracies = []
    print('batch:',batch_size, 'lr:', lr, 'patience:', patience, 'dropout1:', dropout1, 'dropout2:', dropout2, 'earlystopping:', earlystopping, 'tsv_file:', tsv_file)

    for part in range(1, cvs + 1):
        command = f"python ../Scripts/dnngp_runner.py --batch_size {batch_size} --epoch 10000 --lr {lr} --patience {patience} --dropout1 {dropout1} --dropout2 {dropout2} --earlystopping {earlystopping} --cv {cvs} --part {part} --snp {pkl_file} --pheno {os.path.join(pkl_dir, tsv_file)} --output {output_dir}"
        print(command)
        p = subprocess.Popen(command, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()

        # Decode output
        output_str = output.decode(errors='ignore')
        error_str = error.decode(errors='ignore')

        if error_str:
            print("Error Output:", error_str)

        accuracy = extract_statistics(output_str)
        accuracies.append(accuracy)
    print("Statistic values for all folds", accuracies)

    mean_accuracy = np.mean(accuracies) if accuracies else 0.0
    var_accuracy = np.var(accuracies) if accuracies else 0.0

# Use a weighted combination to balance the mean and variance
# Use a nonlinear transform to adjust for the effect of variance

    combined_metric = alpha * mean_accuracy - \
        (1 - alpha) * np.exp(beta * var_accuracy)
    return -combined_metric


# Record the best parameters and results for each tsv file
best_params_per_tsv = {}

for tsv_file in tsv_files:
    print(f"Optimizing for TSV file: {tsv_file}")
    # Use Nevergrad's optimizer
    optimizer = ng.optimizers.NGOpt(parametrization=instr, budget=budget)
    # Execution optimization procedure
    recommendation = optimizer.minimize(
        lambda *args, **kwargs: objective(*args, **kwargs, tsv_file=tsv_file)
    )
    # Output optimum parameter
    print(f"Best parameters for {tsv_file}:", recommendation.value)
    best_params_per_tsv[tsv_file] = recommendation.value

# Output best_params_per_tsv to a JSON file
output_json_file = os.path.join(pkl_dir, 'best_params_per_tsv.json')
with open(output_json_file, 'w') as file:
    json.dump(best_params_per_tsv, file, indent=4)
print(f"Best parameters saved to {output_json_file}")
