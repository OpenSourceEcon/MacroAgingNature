#!/bin/bash

# Activate Conda environment
source activate macro-aging-env

# Run simulations
cd SimulationCode
python simulation.py scenarios.json

# process results and save to CSV
cd ..
mkdir -p Results
cd SimulationCode
python process_results.py "simulation_results/" scenarios.json "simulation_results/macro_aging_results.csv"
