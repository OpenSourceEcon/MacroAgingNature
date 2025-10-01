"""
This file generates the figures in the paper, "A Macroeconomic Approach to
Measure US Returns from Slowing Biological Aging", by Raiany Romanni, Nathanial
Hendrix, Richard W. Evans, and Jason DeBacker
"""
# Import libraries
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt

# Set paths
script_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.join(
    os.path.dirname(script_dir),
    "SimulationCode/simulation_results/MacroAgingNatureSimulations/"
)
images_dir = os.path.join(script_dir, "images")
# print("Script directory:")
# print(script_dir)
# print("")
# print("Main directory:")
# print(main_dir)
# print("")
# print("Images directory:")
# print(images_dir)

"""
-------------------------------------------------------------------------------
Create Figure 1: US population difference by year: 2025-2050
-------------------------------------------------------------------------------
"""
years1 = np.arange(2025, 2051)
T1 = len(years1)
# Read in baseline population time path from model output
(
    fert_rates_base_TP,
    mort_rates_base_TP,
    infmort_rates_base_TP,
    imm_rates_base_TP,
    pop_dist_base_TP,
    pre_pop_dist_base
) = pickle.load(open(os.path.join(main_dir, "demog_vars_baseline.pkl"), "rb"))
tot_pop_2025 = pop_dist_base_TP[0, :].sum()

tot_pop_2025_2050_base = np.zeros(T1)
tot_pop_2025_2050_base[0] = tot_pop_2025

tot_pop_2025_2050_1gen = np.zeros(T1)
tot_pop_2025_2050_1gen[0] = tot_pop_2025

tot_pop_2025_2050_2gen = np.zeros(T1)
tot_pop_2025_2050_2gen[0] = tot_pop_2025

p_base = pickle.load(
    open(os.path.join(main_dir, "baseline", "model_params.pkl"), "rb")
)
g_n_vec_base = p_base.g_n
p_1gen = pickle.load(
    open(os.path.join(main_dir, "1st_gen", "model_params.pkl"), "rb")
)
g_n_vec_1gen = p_1gen.g_n
p_2gen = pickle.load(
    open(os.path.join(main_dir, "2nd_gen", "model_params.pkl"), "rb")
)
g_n_vec_2gen = p_2gen.g_n
for t in range(1, T1):
    tot_pop_2025_2050_base[t] = (
        (1 + g_n_vec_base[t - 1]) * tot_pop_2025_2050_base[t - 1]
    )
    tot_pop_2025_2050_1gen[t] = (
        (1 + g_n_vec_1gen[t - 1]) * tot_pop_2025_2050_1gen[t - 1]
    )
    tot_pop_2025_2050_2gen[t] = (
        (1 + g_n_vec_2gen[t - 1]) * tot_pop_2025_2050_2gen[t - 1]
    )

# Put time series in millions of people
tot_pop_2025_2050_base = tot_pop_2025_2050_base / 1e6
tot_pop_2025_2050_1gen = tot_pop_2025_2050_1gen / 1e6
tot_pop_2025_2050_2gen = tot_pop_2025_2050_2gen / 1e6

fig1, ax1= plt.subplots()
ax1.plot(
    years1, tot_pop_2025_2050_1gen - tot_pop_2025_2050_base, linestyle='-',
    color='blue', linewidth=3, label='1st gen - baseline'
)
ax1.plot(
    years1, tot_pop_2025_2050_2gen - tot_pop_2025_2050_1gen, linestyle='-',
    color='green', linewidth=3, label='2nd gen - 1st gen'
)
ax1.vlines(
    x=2035, ymin=-0.2, ymax=1.2, color='black', linestyle='--',
    label="begin effective year"
)
ax1.vlines(
    x=2045, ymin=-0.2, ymax=1.2, color='black', linestyle=':',
    label="full effective year"
)
plt.grid(
    visible=True, which='major', axis='both', color='0.5', linestyle='--',
    linewidth=0.3
)
plt.ylim(-0.2, 1.2)
plt.xlabel("Year")
plt.ylabel("Population difference (millions)")
plt.legend()
plt.title("US population difference by year: 2025-2050")
plt.savefig(os.path.join(images_dir, "us_popdiff_2nd1stgen.png"))
plt.show()
