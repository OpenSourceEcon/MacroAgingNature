"""
This file generates the figures in the paper, "A Macroeconomic Approach to
Measure US Returns from Slowing Biological Aging", by Raiany Romanni, Nathaniel
Hendrix, Richard W. Evans, and Jason DeBacker
"""
# Import libraries
import os
import pickle
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ogcore.demographics import get_pop
from ogcore.utils import shift_bio_clock

# Set paths
script_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.join(script_dir, "simulation_results")
images_dir = os.path.join(
    os.path.dirname(script_dir), "ResultsInPaper", "figures"
)

"""
-------------------------------------------------------------------------------
Create Figure 1: US population difference by year: 2026-2050
-------------------------------------------------------------------------------
"""
end_year = 2050
p_base = pickle.load(
    open(os.path.join(main_dir, "baseline", "model_params.pkl"), "rb")
)
years1 = np.arange(p_base.start_year, end_year + 1)
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
# Create time series for basline population from 2025 to 2050
base_pop_full_path, _ = get_pop(
    E=20,
    S=80,
    min_age=0,
    max_age=99,
    infer_pop=True,
    fert_rates=fert_rates_base_TP,
    mort_rates=mort_rates_base_TP,
    infmort_rates=infmort_rates_base_TP,
    imm_rates=imm_rates_base_TP,
    initial_pop=pop_dist_base_TP[0, :],
    pre_pop_dist=pre_pop_dist_base,
    start_year=p_base.start_year,
    end_year=end_year,
    download_path=None,
)
tot_pop_2025_2050_base = base_pop_full_path.sum(axis=1)

# Get total population time series from 2025 to 2050 for 1st-gen and 2nd-gen
# scenarios
tot_pop_2025_2050_1gen = pd.read_csv(
    os.path.join(
        main_dir, "1st_gen", "demographic_data", "population_distribution.csv"
    ), header=None
).sum(axis=1).to_numpy()[:T1]

tot_pop_2025_2050_2gen = pd.read_csv(
    os.path.join(
        main_dir, "2nd_gen", "demographic_data", "population_distribution.csv"
    ), header=None
).sum(axis=1).to_numpy()[:T1]

print(
    f"FIG 1: 1st-gen population change relative to baseline in 2050 " +
    f"is {tot_pop_2025_2050_1gen[-1] - tot_pop_2025_2050_base[-1]:,.0f}."
)
print(
    f"FIG 1: 2nd-gen population change relative to baseline in 2050 " +
    f"is {tot_pop_2025_2050_2gen[-1] - tot_pop_2025_2050_base[-1]:,.0f}."
)

fig1, ax1 = plt.subplots()
ax1.plot(
    years1, (tot_pop_2025_2050_1gen - tot_pop_2025_2050_base)/1e6,
    linestyle='-', linewidth=3, color='blue', marker='^',
    markeredgecolor='black', label='1st gen minus baseline'
)
ax1.vlines(
    x=2030, ymin=-0.1, ymax=1.5, color='blue', linestyle=':',
    # label="2030 begin effective year, 1st gen"
)
ax1.vlines(
    x=2034.85, ymin=-0.1, ymax=1.5, color='blue', linestyle='--',
    # label="2035 full effective year, 1st gen"
)
ax1.plot(
    years1, (tot_pop_2025_2050_2gen - tot_pop_2025_2050_base)/1e6,
    linestyle='-', linewidth=3, color='green', marker='o',
    markeredgecolor='black', label='2nd gen minus baseline'
)
ax1.vlines(
    x=2035.15, ymin=-0.1, ymax=1.5, color='green', linestyle=':',
    # label="2035 begin effective year, 2nd gen"
)
ax1.vlines(
    x=2045, ymin=-0.1, ymax=1.5, color='green', linestyle='--',
    # label="2045 full effective year, 2nd gen"
)
plt.grid(
    visible=True, which='major', axis='both', color='0.5', linestyle='--',
    linewidth=0.3
)
plt.ylim(-0.1, 1.2)
plt.xlabel("Year")
plt.ylabel("Population difference (millions)")
plt.legend()
plt.title("Figure 1. US population difference by year: 2026-2050")
plt.savefig(os.path.join(images_dir, "fig1_us_popdiff_2nd1stgen.png"))
plt.show()

"""
-------------------------------------------------------------------------------
Create Figure 2: US survival rates and fertility rates by age
-------------------------------------------------------------------------------
"""
ages2a = np.arange(1, 101)
# Get baseline survival rates in 2026
surv_rates_base = (1 - mort_rates_base_TP[0, :]).cumprod()
# Get one-year-shift survival rates
p_1year = pickle.load(
    open(os.path.join(main_dir, "one_year_all", "model_params.pkl"), "rb")
)
# create new Specifications object for reform simulation
# Timing of investment effects -- common across all scenarios
# calendar age at which the investment starts to affect health/life expectancy
min_age_effect_felt = 40
# number of periods into the model before any effects of R&D are felt
initial_effect_period = 10
# number of periods into the model until full effects of R&D are felt
final_effect_period = 20
# Updates to mortality rates
mort_rates_shift = shift_bio_clock(
    p_1year.rho.copy(),
    initial_effect_period=initial_effect_period,
    final_effect_period=final_effect_period,
    total_effect=1.0,
    min_age_effect_felt=min_age_effect_felt - p_1year.E,
    bound_above=True,
)
mort_rates_1year = mort_rates_base_TP.copy()
mort_rates_1year[:, p_1year.E :] = mort_rates_shift[:-1, :]
mort_rates_1year[:, -1] = 1  # make sure last period is 1
surv_rates_1year = (1 - mort_rates_1year[final_effect_period + 1, :]).cumprod()
fert_rates_adjust = shift_bio_clock(
    fert_rates_base_TP.copy(),
    initial_effect_period=initial_effect_period,
    final_effect_period=final_effect_period,
    total_effect=1.0,
    min_age_effect_felt=min_age_effect_felt,
    bound_below=True,
)
fert_rates_1year = fert_rates_adjust[final_effect_period + 1, :]
fig2a, ax2a = plt.subplots()
ax2a.plot(
    ages2a, surv_rates_base, linestyle=':', linewidth=1, color='blue',
    label='Baseline'
)
ax2a.plot(
    ages2a, surv_rates_1year, linestyle='--', linewidth=1, color='green',
    label=r'One-year shift (age $\geq$ 40)'
)
plt.grid(
    visible=True, which='major', axis='both', color='0.5', linestyle='--',
    linewidth=0.3
)
plt.xticks(np.arange(0, 101, 10))
plt.xlabel(r"Age $s$ (model periods)")
plt.ylim(-0.05, 1.08)
plt.ylabel("Cumulative survival rate")
# Create custom ytick labels as percentages
yticks = np.arange(0, 1.1, 0.2)
plt.yticks(yticks, [f"{int(y*100)}%" for y in yticks])
plt.legend()
plt.title("Figure 2A. US survival rates by age: 2026")
plt.savefig(os.path.join(images_dir, "fig2a_us_survrates_2026.png"))
plt.show()

fig2b, ax2b = plt.subplots()
ax2b.plot(
    ages2a, fert_rates_base_TP[0, :], linestyle=':', linewidth=1, color='blue',
    label='Baseline'
)
ax2b.plot(
    ages2a, fert_rates_1year, linestyle='--', linewidth=1, color='green',
    label=r'One-year shift (age $\geq$ 40)'
)
plt.grid(
    visible=True, which='major', axis='both', color='0.5', linestyle='--',
    linewidth=0.3
)
plt.xlim(-2, 102)
plt.xticks(np.arange(0, 101, 10))
plt.xlabel(r"Age $s$ (model periods)")
plt.ylim(-0.003, 0.057)
plt.ylabel(r"Fertility rate $f_s$")
# Create custom ytick labels as percentages
yticks = np.arange(0, 0.06, 0.01)
plt.yticks(yticks, [f"{int(y*100)}%" for y in yticks])
plt.legend()
plt.title("Figure 2B. US fertility rates by age: 2026")
plt.savefig(os.path.join(images_dir, "fig2b_us_fertrates_2026.png"))
plt.show()

"""
-------------------------------------------------------------------------------
Create Figure 3: Lifecycle profiles of U.S. hourly earnings: baseline versus
simulated 5-year shift in productivity rates by age
-------------------------------------------------------------------------------
"""


"""
-------------------------------------------------------------------------------
Create Figure 4: Evolution of the US population distribution over time: 2024-
2104
-------------------------------------------------------------------------------
"""


"""
-------------------------------------------------------------------------------
Create Figure 5: Estimated impacts of different interventions on GDP and
population, with alternative results of scenario analyses
-------------------------------------------------------------------------------
"""
