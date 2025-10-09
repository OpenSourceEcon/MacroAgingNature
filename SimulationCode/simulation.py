# imports
# %%
import numpy as np
import pickle
import multiprocessing
import requests
from distributed import Client
import os
import json
import time
import argparse
from ogusa.calibrate import Calibration
from ogcore.parameters import Specifications
from ogcore.execute import runner
from ogcore.utils import safe_read_pickle, shift_bio_clock
from ogcore import demographics as demog


# %%
def main(simulation_json):
    # Define parameters to use for multiprocessing
    num_workers = min(multiprocessing.cpu_count(), 7)
    client = Client(n_workers=num_workers)
    print("Number of workers = ", num_workers)

    # Read simulation JSON to get parameters of simulation and paths
    # to read/save data
    with open(simulation_json) as f:
        sim_json = json.load(f)

    # Directories to save data
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    sim_dir = os.path.join(cur_dir, "simulation_results")
    base_dir = os.path.join(sim_dir, "baseline")
    # set paths for each simulation
    scenario_directories = {}
    for k, v in sim_json["scenario_params"].items():
        scenario_directories[k] = os.path.join(sim_dir, v["directory"])
    # Create directories if they don't exist
    if not os.path.exists(sim_dir):
        os.makedirs(sim_dir)
    for scenario in scenario_directories.values():
        if not os.path.exists(scenario):
            os.makedirs(scenario)

    """
    Read in OG-USA default parameters
    """
    resp = requests.get(
        "https://raw.githubusercontent.com/PSLmodels/OG-USA/master/ogusa/" +
        "ogusa_default_parameters.json"
    )
    ogusa_default_params = json.loads(resp.text)

    # update some of these defaults that will be used in all simulations
    ogusa_default_params["tax_func_type"] = "HSV"
    ogusa_default_params["tG1"] = 30
    ogusa_default_params["RC_TPI"] = 1e-04

    """
    ---------------------------------------------------------------------------
    Run baseline policy
    ---------------------------------------------------------------------------
    """
    # Set up baseline parameterization
    p = Specifications(
        baseline=True,
        num_workers=num_workers,
        baseline_dir=base_dir,
        output_base=base_dir,
    )
    p.update_specifications(ogusa_default_params)

    # Update demographics using OG-Core demographics module
    # And find baseline demographic objects not returned by get_pop_objs
    if os.path.exists(os.path.join(sim_dir, "demog_vars_baseline.pkl")):
        (
            fert_rates_baseline_TP,
            mort_rates_baseline_TP,
            infmort_rates_baseline_TP,
            imm_rates_baseline_TP,
            pop_baseline_TP,
            pre_pop_dist_baseline,
        ) = safe_read_pickle(os.path.join(sim_dir, "demog_vars_baseline.pkl"))
    else:
        fert_rates_baseline = demog.get_fert(
            start_year=p.start_year, end_year=p.start_year
        )
        pickle.dump(
            fert_rates_baseline,
            open(os.path.join(sim_dir, "fert_rates_baseline.pkl"), "wb"),
        )
        mort_rates_baseline, infmort_rates_baseline = demog.get_mort(
            start_year=p.start_year, end_year=p.start_year
        )
        pop_dist_baseline, pre_pop_baseline = demog.get_pop(
            start_year=p.start_year, end_year=p.start_year
        )
        imm_rates_baseline = demog.get_imm_rates(
            fert_rates=fert_rates_baseline,
            mort_rates=mort_rates_baseline,
            infmort_rates=infmort_rates_baseline,
            pop_dist=pop_dist_baseline,
            start_year=p.start_year,
            end_year=p.start_year,
        )
        # And extend each fof these over the full time path
        fert_rates_baseline_TP = np.append(
            fert_rates_baseline,
            np.tile(
                fert_rates_baseline[-1, :].reshape((1, p.E + p.S)),
                (p.T + p.S - 2, 1),
            ),
            axis=0,
        )
        mort_rates_baseline_TP = np.append(
            mort_rates_baseline,
            np.tile(
                mort_rates_baseline[0, :].reshape((1, p.E + p.S)),
                (p.T + p.S - 2, 1),
            ),
            axis=0,
        )
        infmort_rates_baseline_TP = np.append(
            infmort_rates_baseline[0],
            np.ones(p.T + p.S - 1) * infmort_rates_baseline[0],
        )
        imm_rates_baseline_TP = np.append(
            imm_rates_baseline,
            np.tile(
                imm_rates_baseline[0, :].reshape((1, p.E + p.S)),
                (p.T + p.S - 2, 1),
            ),
            axis=0,
        )
        pop_baseline_TP, pre_pop_dist_baseline = demog.get_pop(
            infer_pop=True,
            fert_rates=fert_rates_baseline_TP,
            mort_rates=mort_rates_baseline_TP,
            infmort_rates=infmort_rates_baseline_TP,
            imm_rates=imm_rates_baseline_TP,
            initial_pop=None,
            pre_pop_dist=None,
            start_year=p.start_year,
            end_year=p.start_year + 1,
        )

        demog_vars_baseline = (
            fert_rates_baseline_TP,
            mort_rates_baseline_TP,
            infmort_rates_baseline_TP,
            imm_rates_baseline_TP,
            pop_baseline_TP,
            pre_pop_dist_baseline,
        )
        pickle.dump(
            demog_vars_baseline,
            open(os.path.join(sim_dir, "demog_vars_baseline.pkl"), "wb"),
        )
    # Now get population objects for the model
    num_periods = 2100 - p.start_year  # 2100 is the last year WPP forecast
    demog_vars = demog.get_pop_objs(
        p.E,
        p.S,
        p.T,
        fert_rates=fert_rates_baseline_TP[:num_periods, :],
        mort_rates=mort_rates_baseline_TP[:num_periods, :],
        infmort_rates=infmort_rates_baseline_TP[:num_periods],
        imm_rates=imm_rates_baseline_TP[:num_periods, :],
        infer_pop=True,
        pop_dist=pop_baseline_TP[:2, :],
        pre_pop_dist=pre_pop_dist_baseline,
        initial_data_year=p.start_year,
        final_data_year=p.start_year + num_periods - 1,
    )
    # I was getting error that imm_rates had value less than -1.0
    # but it didn't.  So I set raise_errors=False
    p.update_specifications(demog_vars, raise_errors=False)

    # close and delete client bc cache is too large
    client.close()
    del client
    client = Client(n_workers=num_workers)

    # Run model
    start_time = time.time()
    # runner(p, time_path=True, client=client)
    print("run time = ", time.time() - start_time)

    client.close()
    del client

    """
    Run simulations specified in simulation JSON
    """

    scenario_params = sim_json["scenario_params"]

    for scenario in scenario_params.keys():
        # create new Specifications object for reform simulation
        # Timing of investment effects -- common across all scenarios
        min_age_effect_felt = scenario_params[scenario][
            "min_age_effect_felt"
        ]  # calendar age at which the investment starts to affect health/life expectancy
        initial_effect_period = scenario_params[scenario][
            "initial_effect_period"
        ]  # number of periods into the model before any effects of R&D are felt
        final_effect_period = scenario_params[scenario][
            "final_effect_period"
        ]  # number of periods into the model until full effects of R&D are felt
        p = Specifications(
            baseline=False,
            num_workers=num_workers,
            baseline_dir=base_dir,
            output_base=scenario_directories[scenario],
        )
        p.update_specifications(ogusa_default_params)
        scenario_params[scenario]["start_year"] = p.start_year
        num_years_invest = 10  # number of years of investment (assume total invested evenly over these years)
        invest_per_year = (
            scenario_params[scenario]["rd_invest"] / num_years_invest
        )  # investment per year
        base_gdp = 27940  # GDP in billions
        alpha_G = (
            p.alpha_G[:num_years_invest] + (invest_per_year / base_gdp)
        ).tolist() + [p.alpha_G[num_years_invest]]
        # update government spending for investment
        p.update_specifications({"alpha_G": alpha_G})
        # update to baseline demographics (importance for shift of rho below)
        p.update_specifications(demog_vars)

        # Updates to mortality rates, chi_n_s, e matrix, and fertility rates
        chi_n_shift = shift_bio_clock(
            p.chi_n.copy(),
            initial_effect_period=initial_effect_period,
            final_effect_period=final_effect_period,
            total_effect=scenario_params[scenario]["prod_effect"],
            min_age_effect_felt=min_age_effect_felt - p.E,
            bound_above=True,
        )
        mort_rates_shift = shift_bio_clock(
            p.rho.copy(),
            initial_effect_period=initial_effect_period,
            final_effect_period=final_effect_period,
            total_effect=scenario_params[scenario]["mort_effect"],
            min_age_effect_felt=min_age_effect_felt - p.E,
            bound_above=True,
        )
        mort_rates_adjusted = mort_rates_baseline_TP.copy()
        mort_rates_adjusted[:, p.E :] = mort_rates_shift[:-1, :]
        mort_rates_adjusted[:, -1] = 1  # make sure last period is 1

        e_shift = shift_bio_clock(
            p.e.copy(),
            initial_effect_period=initial_effect_period,
            final_effect_period=final_effect_period,
            total_effect=scenario_params[scenario]["prod_effect"],
            min_age_effect_felt=min_age_effect_felt - p.E,
            bound_below=True,
        )
        fert_rates_shift = shift_bio_clock(
            fert_rates_baseline_TP.copy(),
            initial_effect_period=initial_effect_period,
            final_effect_period=final_effect_period,
            total_effect=scenario_params[scenario]["fert_effect"],
            min_age_effect_felt=min_age_effect_felt,
            bound_below=True,
        )
        # update labor productivity related parameters
        p.chi_n = chi_n_shift.copy()
        p.e = e_shift.copy()

        # update demographic parameters for the simulation
        num_periods = 2100 - p.start_year  # 2100 is the last year WPP forecast
        if not os.path.exists(
            os.path.join(scenario_directories[scenario], "demographic_data")
        ):
            os.makedirs(
                os.path.join(
                    scenario_directories[scenario], "demographic_data"
                )
            )

        demog_vars_sim = demog.get_pop_objs(
            p.E,
            p.S,
            p.T,
            fert_rates=fert_rates_shift[:num_periods, :],
            mort_rates=mort_rates_adjusted[:num_periods, :],
            infmort_rates=infmort_rates_baseline_TP[:num_periods],
            imm_rates=imm_rates_baseline_TP[:num_periods, :],
            infer_pop=True,
            pop_dist=pop_baseline_TP[:2, :],
            pre_pop_dist=pre_pop_dist_baseline,
            initial_data_year=p.start_year,
            final_data_year=p.start_year + num_periods - 1,
            download_path=os.path.join(
                scenario_directories[scenario], "demographic_data"
            ),
        )
        p.update_specifications(demog_vars_sim)

        # Save fert rates to disk
        pickle.dump(
            fert_rates_shift,
            open(
                os.path.join(
                    scenario_directories[scenario], "fert_rates_shifted.pkl"
                ),
                "wb",
            ),
        )

        client = Client(n_workers=num_workers)
        start_time = time.time()
        print("Solving model for ", scenario)
        runner(p, time_path=True, client=client)
        print("Run time for ", scenario, " = ", time.time() - start_time)
        client.close()
        del client


if __name__ == "__main__":
    # execute only if run as a script
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "simulation_json", help="Path to JSON with simulation parameters"
    )  # positional arg
    args = parser.parse_args()
    main(args.simulation_json)
