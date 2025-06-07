# Analysis of Orientation Tuning in V1 Neurons (CRCNS.org pvc-11 Dataset)

## Project Overview

This project analyzes extracellular recordings from macaque primary visual cortex (V1) to characterize the orientation tuning properties of individual neurons. Using the publicly available `pvc-11` dataset from CRCNS.org, this script processes spike time data in response to drifting sinusoidal gratings and generates orientation tuning curves for selected neurons.

The primary goal is to demonstrate foundational skills in:
*   Loading and parsing complex neurophysiological data files (`.mat` format).
*   Extracting and processing spike train data.
*   Calculating trial-averaged firing rates in response to different stimulus conditions.
*   Visualizing neural tuning properties.
*   Working with public neuroscience datasets.

## Dataset

*   **Name:** Utah array extracellular recordings of spontaneous and visually evoked activity from anesthetized macaque primary visual cortex (V1). (CRCNS.org pvc-11)
*   **Source:** [https://crcns.org/data-sets/vc/pvc-11](https://crcns.org/data-sets/vc/pvc-11)
*   **Citation:** Kohn, A., Smith, M.A. (2016) Utah array extracellular recordings of spontaneous and visually evoked activity from anesthetized macaque primary visual cortex (V1). CRCNS.org. http://dx.doi.org/10.6080/K0NC5Z4X
    *   *Data were recorded by Matthew Smith and Adam Kohn, in the Kohn lab at the Albert Einstein College of Medicine (both data sets), and J. Anthony Movshon's lab at New York University (spontaneous data set). Tai Sing Lee (Carnegie Mellon University) provided research support and Ryan Kelly (Carnegie Mellon University) participated in the data collection and processing.*

The specific data file used for this analysis is `data_monkey1_gratings.mat` from the `spikes_gratings` portion of the dataset.

## Methods

1.  **Data Loading:** The `data_monkey1_gratings.mat` file is loaded using `scipy.io.loadmat`. The primary data structure is a MATLAB struct (loaded as a NumPy structured array) containing an `EVENTS` field.
2.  **Spike Data Extraction:** The `EVENTS` field is a 3D array of shape `(num_neurons, num_grating_conditions, num_trials)`. Each element contains a NumPy array of spike timestamps (in seconds) for a specific neuron, grating condition, and trial. For `data_monkey1_gratings.mat`, this is `(106 neurons, 12 grating conditions, 200 trials)`.
3.  **Analysis Window:** Based on insights from the accompanying MATLAB scripts and dataset documentation, spike activity is analyzed within a 1.0-second window, from 0.28 seconds to 1.28 seconds relative to the presumed start of each 1.28-second stimulus presentation.
4.  **Firing Rate Calculation:**
    *   For each selected neuron and each of the 12 grating conditions:
        *   Spikes occurring within the defined analysis window (0.28s - 1.28s) are counted for each of the 200 trials.
        *   The average spike count across these 200 trials is calculated.
        *   This average spike count is then divided by the analysis duration (1.0 second) to obtain the mean firing rate in spikes/second.
5.  **Orientation Assumption:**
    *   **CRITICAL NOTE:** The precise mapping of the 12 grating conditions (second dimension of the `EVENTS` array) to specific stimulus orientations (or directions of drift) was not explicitly found in the provided `readme.txt` files or the main PDF documentation for the `pvc-11` dataset at the time of this analysis.
    *   Therefore, for visualization purposes, it has been **assumed** that the 12 grating conditions correspond to 12 equally spaced orientations (or directions of drift) from 0 to 330 degrees, in 30-degree increments: `[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]`.
    *   This assumption allows for the generation of tuning curves, but the absolute orientation values on the x-axis should be interpreted with this caveat. Verification of the true stimulus parameters from the original publications (e.g., Cowley et al., 2016; Smith & Kohn, 2008) would be required for definitive interpretation of preferred orientations.
6.  **Plotting:** The calculated mean firing rates are plotted against the assumed stimulus orientations to generate tuning curves.

## Software and Libraries

*   Python 3
*   NumPy
*   SciPy (for loading `.mat` files)
*   Matplotlib (for plotting)
*   os (for directory and path handling)

## How to Run

1.  **Download the Dataset:**
    *   Register and download the `pvc-11` dataset from [CRCNS.org](https://crcns.org/data-sets/vc/pvc-11). You will need the `data_and_scripts.tar.gz` file.
    *   Extract the archive. The relevant file for this script is located at a path similar to `data_and_scripts/spikes_gratings/data_monkey1_gratings.mat`.
2.  **Set up Python Environment:** Ensure you have Python 3 and the required libraries installed:
    ```bash
    pip install numpy scipy matplotlib
    ```
3.  **Configure Script:**
    *   Open the Python script (e.g., `analyze_v1_tuning.py`).
    *   Modify the `mat_file_path` variable at the top of the script to point to the exact location of your `data_monkey1_gratings.mat` file.
    *   (Optional) Adjust the `neurons_to_plot_indices` list/range to select which neurons you want to analyze. By default, it analyzes a subset.
4.  **Run the Script:**
    Execute the script from your terminal:
    ```bash
    python analyze_v1_tuning.py 
    ```
    
5.  **Output:**
    *   The script will print progress information to the console.
    *   Generated tuning curve plots (PNG images) will be saved in a subfolder named `tuning_curve_plots/` created in the same directory as the script.

## Example Results

The analysis reveals a diversity of orientation tuning properties among V1 neurons. Below are a few examples (using the assumed orientation mapping):

**Neuron 0:** Exhibits complex, multimodal tuning with prominent peaks around 60, 120, and 270 degrees.
![Tuning Curve for Neuron 0](tuning_curve_plots/neuron_0_tuning_curve.png) 

**Neuron 12:** Shows very low overall firing rates but a remarkably sharp tuning peak at an assumed orientation of 30 degrees.
![Tuning Curve for Neuron 12](tuning_curve_plots/neuron_12_tuning_curve.png)

**Neuron 17:** Displays an interesting response profile with suppressed activity around 60-120 degrees and strong responses at 0-30 and 180-210 degrees.
![Tuning Curve for Neuron 17](tuning_curve_plots/neuron_17_tuning_curve.png)

**Neuron 18:** A clear example of strong tuning, with a dominant peak at 180 degrees and a secondary peak at 0 degrees.
![Tuning Curve for Neuron 18](tuning_curve_plots/neuron_18_tuning_curve.png)


