
# Documentation for `main.py`

## 1. Overview

The `main.py` script is a complete pipeline designed to process time-series data from specific MATLAB (`.mat`) files. It performs the following steps for each file:
1.  **Loads** raw sensor data from keys ending in 'X', 'Y', and 'Z'.
2.  **Filters** the data to remove very low frequencies (0-0.5 Hz).
3.  **Decimates** the data to reduce the sampling rate.
4.  **Segments** the processed data into 50-second chunks.
5.  **Visualizes** each chunk as a line plot and saves it as a `.png` image.

This entire process is done in a single run, without creating intermediate files.

## 2. Dependencies

To run this script, you need a Python environment with the following libraries installed:
- `scipy`
- `numpy`
- `pandas`
- `matplotlib`

These libraries are already present in the `lstm_fcn` conda environment we have been using.

## 3. How to Run the Script

You can execute the script from your terminal. Make sure you have activated the correct conda environment first.

```bash
# 1. Activate the conda environment
conda activate lstm_fcn

# 2. Run the main.py script
python main.py
```

Upon execution, the script will process all `.mat` files listed inside it and generate the output plots in the `results` directory.

## 4. Function Explanations

### `load_data_from_mat_file(file_path)`

This is the core function for data extraction.

- **Input:** Takes the path to a single `.mat` file.
- **Process:**
    1.  It loads the `.mat` file into a Python dictionary-like object using `scipy.io.loadmat`.
    2.  It searches for all variable names (keys) in the file that start with `Untitled` and end with `X`, `Y`, or `Z`. This targets the specific sensor data channels.
    3.  For each key found, it accesses the nested data structure. Based on the file format, the actual data is located at `mat_data[key][0, 0]`.
    4.  This `[0, 0]` element is a special `numpy.void` object, which is how SciPy represents a MATLAB `struct`. The function checks if this struct contains a field named `'Data'`.
    5.  If the `'Data'` field exists, it extracts the numerical array from it. This array contains the actual time-series measurements for that sensor.
    6.  The extracted 1D arrays (one for each sensor) are then stacked together as columns to form a single 2D array.
- **Output:** Returns the 2D NumPy array (`data_array`) where each column is a different sensor, and a list of the keys (`sensor_keys`) that were successfully extracted.

### `main()`

This is the main function that controls the entire workflow.

- **Process:**
    1.  It defines a list of all `.mat` files to be processed.
    2.  It loops through each `file_path` in the list.
    3.  For each file, it calls `load_data_from_mat_file` to get the raw data.
    4.  It converts the loaded data array into a pandas DataFrame for easier column-based operations. Each column is named after the sensor key it came from (e.g., `Untitled3204Y`).
    5.  It then enters a loop to process each `sensor_col` (each column) in the DataFrame individually.
    6.  **Filtering:** It applies a high-pass Butterworth filter to remove frequencies below 0.5 Hz.
    7.  **Decimation:** It decimates the filtered signal by a factor of 20, which significantly reduces the number of data points and smooths the signal.
    8.  **Segmenting and Visualizing:** It calculates how many 50-second chunks can be created from the decimated data. It then loops, creating one chunk at a time, and immediately generates a plot for that chunk using `matplotlib`.
    9.  **Plot Customization:** Each plot is created with a `figsize` of `(15, 3)` to achieve a 5:1 aspect ratio, and no title is added, as requested.
    10. **Saving Output:** The generated plot is saved directly as a `.png` file into a structured output directory.

## 5. Output Structure

The script will create a new top-level directory named `results`. The structure of the output will be:

```
results/
├── SETUP1/
│   ├── Untitled3204Y/
│   │   ├── chunk_1.png
│   │   ├── chunk_2.png
│   │   └── ...
│   ├── Untitled3104Z/
│   │   ├── chunk_1.png
│   │   └── ...
│   └── ...
├── SETUP2/
│   ├── ...
└── ...
```

Each `.mat` file gets its own folder, and inside that, each processed sensor channel gets its own subfolder containing the `.png` image files of its data chunks.
