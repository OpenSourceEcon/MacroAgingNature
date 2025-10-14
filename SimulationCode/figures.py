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
# plt.show()
plt.close()

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
plt.xlabel(r"Age $s$ (years)")
plt.ylim(-0.05, 1.08)
plt.ylabel("Cumulative survival rate")
# Create custom ytick labels as percentages
yticks = np.arange(0, 1.1, 0.2)
plt.yticks(yticks, [f"{int(y*100)}%" for y in yticks])
plt.legend()
plt.title("Figure 2A. US survival rates by age: 2026")
plt.savefig(os.path.join(images_dir, "fig2a_us_survrates_2026.png"))
# plt.show()
plt.close()

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
plt.xlabel(r"Age $s$ (years)")
plt.ylim(-0.003, 0.057)
plt.ylabel(r"Fertility rate $f_s$")
# Create custom ytick labels as percentages
yticks = np.arange(0, 0.06, 0.01)
plt.yticks(yticks, [f"{int(y*100)}%" for y in yticks])
plt.legend()
plt.title("Figure 2B. US fertility rates by age: 2026")
plt.savefig(os.path.join(images_dir, "fig2b_us_fertrates_2026.png"))
# plt.show()
plt.close()

"""
-------------------------------------------------------------------------------
Create Figure 3: Lifecycle profiles of U.S. hourly earnings: baseline versus
simulated 5-year shift in productivity rates by age
-------------------------------------------------------------------------------
"""
ages3 = np.arange(p_base.E + 1, 101)
# BLS Aug. 2025(p) https://www.bls.gov/news.release/empsit.t19.htm
us_avg_hrly_earn = 36.53
e_base = p_base.e[0, :, :]
avg_e_base = (
    e_base * np.tile(p_base.lambdas.reshape(1, p_base.J), (p_base.S, 1))
).sum(axis=1)
avg_hrly_earn = avg_e_base * us_avg_hrly_earn
avg_hrly_earn_shift = avg_hrly_earn.copy()
avg_hrly_earn_shift[39:] = avg_hrly_earn_shift[38:-1]

fig3, ax3 = plt.subplots()
ax3.plot(
    ages3[:60], avg_hrly_earn[:60], linestyle='-', linewidth=1, color='blue',
    label='Baseline, from data'
)
ax3.plot(
    ages3[59:], avg_hrly_earn[59:], linestyle='--', linewidth=1, color='blue',
    label='Baseline, extrapolated (scarce data)'
)
ax3.plot(
    ages3, avg_hrly_earn_shift, linestyle=':', linewidth=1, color='green',
    label='Reform, one-year shift (age ≥ 40)'
)
plt.grid(
    visible=True, which='major', axis='both', color='0.5', linestyle='--',
    linewidth=0.3
)
plt.xlim(19, 102)
plt.xticks(np.arange(20, 101, 10))
plt.xlabel(r"Age $s$ (years)")
plt.ylim(11, 54)
plt.ylabel(r"Avg. hourly earnings (\$)")
plt.legend()
plt.title(
    "Figure 3. Lifecycle profiles of U.S. hourly earnings: \n baseline " +
    "versus simulated 1-year shift in productivity rates by age")
plt.savefig(os.path.join(images_dir, "fig3_abil_by_age.png"))
# plt.show()
plt.close()

"""
-------------------------------------------------------------------------------
Create Figure 4: Evolution of the US population distribution over time: 2026-
2100
-------------------------------------------------------------------------------
"""
base_pop_full_long_path, _ = get_pop(
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
    end_year=p_base.start_year + p_base.T,
    download_path=None,
)
pop_dist_2026 = (
    base_pop_full_long_path[0, :] / base_pop_full_long_path[0, :].sum()
)
pop_dist_2065 = (
    base_pop_full_long_path[39, :] / base_pop_full_long_path[39, :].sum()
)
pop_dist_2100 = (
    base_pop_full_long_path[74, :] / base_pop_full_long_path[74, :].sum()
)
pop_dist_adj_ss = (
    base_pop_full_long_path[-1, :] / base_pop_full_long_path[-1, :].sum()
)
fig4, ax4 = plt.subplots()
ax4.plot(
    ages2a, pop_dist_2026, linestyle='-', linewidth=1, color='blue',
    label='2026 pop.'
)
ax4.plot(
    ages2a, pop_dist_2065, linestyle='--', linewidth=1, color='green',
    label='2065 pop.'
)
ax4.plot(
    ages2a, pop_dist_2100, linestyle=':', linewidth=1, color='red',
    label='2100 pop.'
)
ax4.plot(
    ages2a, pop_dist_adj_ss, linestyle='-', linewidth=1, color='black',
    label='Adj. SS pop.'
)
plt.grid(
    visible=True, which='major', axis='both', color='0.5', linestyle='--',
    linewidth=0.3
)
plt.xlim(-2, 102)
plt.xticks(np.arange(0, 101, 10))
plt.xlabel(r"Age $s$ (years)")
plt.ylim(-0.001, 0.015)
plt.ylabel(r"Percent of population ($\omega_s$)")
yticks = np.arange(0, 0.015, 0.002)
plt.yticks(yticks, [f"{np.round(y*100, 1)}%" for y in yticks])
plt.legend()
plt.title(
    "Figure 4.Evolution of the US population distribution \n over time: " +
    "2026-2100"
)
plt.savefig(os.path.join(images_dir, "fig4_pop_dist_over_time.png"))
# plt.show()
plt.close()

"""
-------------------------------------------------------------------------------
Create Figure 5: Estimated impacts of different interventions on GDP and
population, with alternative results of scenario analyses
-------------------------------------------------------------------------------
"""
# Create the data
interventions = [
    "Brain\nAging", "Ovarian\nAging", "41 Is the\nNew 40", "66 Is the\nNew 65",
    "1st Gen.,\n11% Ag 65+", "1st Gen.,\n18.5% Ag 65+",
    "2nd Gen.,\n50% Age 40+", "2nd Gen.,\n50% Age 40+\n(Fast Dev.)"
]
scenarios = ["Pessimistic", "Base", "Optimistic"]
output_vars = ["avg_diff", "NPV", "total_pop_diff_2050"]
fig5_panel_labels = [
    "Average Annual GDP Change\n2045-2064 ($billions)",
    "Net Present Value of GDP Change\nOver Decades($trillions)",
    "Increase in 2050\nPopulation (millions)"
]
fig5_xlims = [(-30, 570), (-1.8, 37), (-0.1, 2.22)]
fig5_xticks = [
    np.arange(0, 551, 100), np.arange(0, 36, 5), np.arange(0, 2.1, 0.5)
]
data5 = {
    "avg_diff": {
        "Brain\nAging": {
            "Pessimistic": 156.91, "Base": 201.29, "Optimistic": 245.89
            },
        "Ovarian\nAging": {
            "Pessimistic": 3.5, "Base": 9.1, "Optimistic": 14.6
        },
        "41 Is the\nNew 40": {
            "Pessimistic": 321.5, "Base": 408.4, "Optimistic": 496.0
        },
        "66 Is the\nNew 65": {
            "Pessimistic": 256.0, "Base": 326.4, "Optimistic": 397.4
        },
        "1st Gen.,\n11% Ag 65+": {
            "Pessimistic": 38.9, "Base": 40.4, "Optimistic": 42.3
        },
        "1st Gen.,\n18.5% Ag 65+": {
            "Pessimistic": 76.2, "Base": 78.7, "Optimistic": 81.9
        },
        "2nd Gen.,\n50% Age 40+": {
            "Pessimistic": 498.0, "Base": 505.0, "Optimistic": 513.4
        },
        "2nd Gen.,\n50% Age 40+\n(Fast Dev.)": {
            "Pessimistic": 514.7, "Base": 522.6, "Optimistic": 531.9
        }
    },
    "NPV": {
        "Brain\nAging": {
            "Pessimistic": 7.053, "Base": 8.906, "Optimistic": 18.914
            },
        "Ovarian\nAging": {
            "Pessimistic": 7.353, "Base": 9.261, "Optimistic": 11.169
        },
        "41 Is the\nNew 40": {
            "Pessimistic": 21.551, "Base": 27.102, "Optimistic": 32.693
        },
        "66 Is the\nNew 65": {
            "Pessimistic": 11.365, "Base": 14.350, "Optimistic": 17.367
        },
        "1st Gen.,\n11% Ag 65+": {
            "Pessimistic": 2.343, "Base": 2.416, "Optimistic": 2.504
        },
        "1st Gen.,\n18.5% Ag 65+": {
            "Pessimistic": 4.042, "Base": 4.160, "Optimistic": 4.308
        },
        "2nd Gen.,\n50% Age 40+": {
            "Pessimistic": 21.872, "Base": 22.239, "Optimistic": 22.674
        },
        "2nd Gen.,\n50% Age 40+\n(Fast Dev.)": {
            "Pessimistic": 22.881, "Base": 23.264, "Optimistic": 23.718
        }
    },
    "total_pop_diff_2050": {
        "Brain\nAging": {
            "Pessimistic": 0.214, "Base": 0.268, "Optimistic": 0.322
            },
        "Ovarian\nAging": {
            "Pessimistic": 0.313, "Base": 0.391, "Optimistic": 0.470
        },
        "41 Is the\nNew 40": {
            "Pessimistic": 1.375, "Base": 1.723, "Optimistic": 2.073
        },
        "66 Is the\nNew 65": {
            "Pessimistic": 0.939, "Base": 1.178, "Optimistic": 1.419
        },
        "1st Gen.,\n11% Ag 65+": {
            "Pessimistic": 0.260, "Base": 0.275, "Optimistic": 0.294
        },
        "1st Gen.,\n18.5% Ag 65+": {
            "Pessimistic": 0.435, "Base": 0.460, "Optimistic": 0.491
        },
        "2nd Gen.,\n50% Age 40+": {
            "Pessimistic": 1.050, "Base": 1.111, "Optimistic": 1.182
        },
        "2nd Gen.,\n50% Age 40+\n(Fast Dev.)": {
            "Pessimistic": 1.259, "Base": 1.332, "Optimistic": 1.418
        }
    }
}

# Set up the plot
fig5, axs5 = plt.subplots(nrows=1, ncols=3, figsize=(10,7))

# Define markers for each scenario
markers = {"Pessimistic": "s", "Base": "o", "Optimistic": "^"}

for i, out_var in enumerate(output_vars):
    axs5[i].vlines(
        x=0, ymin=-1.0, ymax=8, color='black', linestyle='--'
    )
    # Plot each scenario
    for scenario in scenarios:
        x_vals = []
        y_vals = []

        for j, intervention in enumerate(interventions):
            x_vals.append(data5[out_var][intervention][scenario])
            y_vals.append(7-j)

        axs5[i].scatter(
            x_vals, y_vals, marker=markers[scenario], s=60, label=scenario,
            edgecolor='black'
        )

    # Set labels and formatting
    axs5[i].set_xlabel(fig5_panel_labels[i])
    axs5[i].set_xlim(fig5_xlims[i][0], fig5_xlims[i][1])
    axs5[i].set_xticks(fig5_xticks[i])
    axs5[i].set_ylim(-0.4, 7.3)
    axs5[i].set_ylabel("")
    if i == 0:
        axs5[i].set_yticks(range(len(interventions)))
        axs5[i].set_yticklabels(interventions[::-1])  # Reverse order

    # Add grid
    axs5[i].grid(True, alpha=0.3)
    axs5[i].set_axisbelow(True)
    if i == 1:
        # Add legend at bottom
        axs5[i].legend(
            loc='upper center', ncol=3, title="Scenario",
            bbox_to_anchor=(0.5, -0.15)
        )
# Remove y-axis labels from second and third plots
axs5[1].tick_params(axis='y', labelleft=False)
axs5[2].tick_params(axis='y', labelleft=False)

# Set font
plt.rcParams.update({'font.size': 14, 'font.family': 'Arial Narrow'})

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Adjust the horizontal space between subplots. wspace is a fraction of the
# average axis width
plt.subplots_adjust(wspace=0.1)

# Save the figure
plt.savefig(
    os.path.join(images_dir,'fig5_gdp_pop_impacts.png'),
    dpi=300, bbox_inches='tight'
)
# plt.show()
plt.close()
