# MacroAgingNature
Data and code for article: "A GDP Approach to Measure Returns on Investment in Aging Biology"

# Instructions to reproduce results
0. Install the Anaconda distribution of Python (https://www.anaconda.com/download).
1. Clone the repository.
2. Create a conda environment with the required packages:
   ```bash
   conda env create -f environment.yml
   ```
3. Run the bash script to reproduce the results:
   ```bash
   bash run_macro_aging.sh
    ```
4. All results will be saved in the `ResultsInPaper/macro_aging_results.csv` file and `ResultsInPaper/macro_aging_sensitivity_results.csv`. Individual figures from the paper will be saved in the `ResultsInPaper/figures/` directory.
