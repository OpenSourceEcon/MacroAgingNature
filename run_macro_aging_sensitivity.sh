#!/bin/bash
# set the job name
#SBATCH --job-name=nature-aging-sensitivity

# set file to send output to
#SBATCH --output=nature-aging-sensitivity-%j.out
#SBATCH --error=nature-aging-sensitivity-%j.err

# set partition
#SBATCH -p defq  # partition name

# Set time
#SBATCH --time=48:00:00  # 48 hours is the max

# Set resources
#SBATCH --ntasks=5  # total number of tasks across all nodes
#SBATCH --cpus-per-task=1 # cpu-cores per task
#SBATCH --nodes=1  # total number of nodes
#SBATCH --mem=64G  # total memory per node (4 GB per cpu-core is default)

# Add account info
#SBATCH --account=rc_general

###########Load modules and enter code below

module load python3/anaconda/

# Initialize conda for this shell session
eval "$(conda shell.bash hook)"

# Create and activate Conda environment
# conda env remove -n macro-aging-env
# conda env create -f environment.yml
conda activate macro-aging-env

# Run simulations
cd SimulationCode
python simulation.py hi_low_parameterizations.json

# process results and save to CSV
python process_results.py "simulation_results/SensitivitySimulations" hi_low_parameterizations.json "../Results/macro_aging_sensitivity_results.csv"
