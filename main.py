
import os
import scipy.io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, decimate

def load_data_from_mat_file(file_path):
    """
    Loads data from a single MATLAB .mat file.
    Extracts data from keys ending in 'X', 'Y', or 'Z'.
    """
    try:
        mat_data = scipy.io.loadmat(file_path)
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

    # Find all keys with the specified patterns
    keys_to_extract = [key for key in mat_data.keys() 
                       if key.startswith("Untitled") and (key.endswith("X") or key.endswith("Y") or key.endswith("Z"))]

    if not keys_to_extract:
        print(f"Warning: No 'Untitled...[X,Y,Z]' keys found in {file_path}.")
        return None, None

    extracted_arrays = []
    valid_keys = []
    for key in keys_to_extract:
        if (isinstance(mat_data[key], np.ndarray) and mat_data[key].shape == (1, 1)):
            raw_value = mat_data[key][0, 0]
            if isinstance(raw_value, np.void) and 'Data' in raw_value.dtype.names:
                numerical_array = raw_value['Data']
                if isinstance(numerical_array, np.ndarray) and numerical_array.ndim >= 1:
                    extracted_arrays.append(numerical_array.flatten())
                    valid_keys.append(key)

    if not extracted_arrays:
        print(f"Warning: Found matching keys in {file_path}, but could not extract valid numerical data.")
        return None, None

    # Ensure all arrays have the same length
    first_len = len(extracted_arrays[0])
    if not all(len(arr) == first_len for arr in extracted_arrays):
        print(f"Warning: Sensor data arrays in {file_path} have inconsistent lengths. Skipping.")
        return None, None

    return np.column_stack(extracted_arrays), valid_keys

def main():
    """
    Main function to load, process, and visualize the data in a single pipeline.
    """
    mat_files = [
        'Data/SETUP1.mat', 'Data/SETUP2.mat', 'Data/SETUP3.mat',
        'Data/SETUP4.mat', 'Data/SETUP5.mat', 'Data/SETUP6.mat',
        'Data/setup7.mat', 'Data/setup8.mat', 'Data/setup9.mat', 'Data/setup10.mat'
    ]
    
    output_base_dir = 'results'
    os.makedirs(output_base_dir, exist_ok=True)

    # Processing parameters
    fs = 1651
    decimation_factor = 20
    decimated_fs = fs / decimation_factor
    segment_length_seconds = 50
    segment_length_points = int(segment_length_seconds * decimated_fs)

    if segment_length_points == 0:
        print("Error: Segment length is 0 points. Check sampling and decimation rates.")
        return

    for file_path in mat_files:
        print(f"--- Starting file: {file_path} ---")
        
        data_array, sensor_keys = load_data_from_mat_file(file_path)
        
        if data_array is None:
            print(f"Skipping processing for {file_path} due to loading errors.")
            continue

        file_basename = os.path.splitext(os.path.basename(file_path))[0]
        df = pd.DataFrame(data_array, columns=sensor_keys)
        
        print(f"Processing {file_basename} with {len(sensor_keys)} sensors...")

        # Process each sensor column
        for sensor_col in df.columns:
            print(f"  Processing {sensor_col}...")
            
            # Filter
            b, a = butter(4, 0.5, 'high', fs=fs)
            filtered_data = lfilter(b, a, df[sensor_col])
            
            # Decimate
            decimated_data = decimate(filtered_data, decimation_factor, ftype='fir')
            
            # Segment and Visualize
            num_segments = len(decimated_data) // segment_length_points
            if num_segments == 0:
                print(f"    Not enough data to create a single 50-second segment.")
                continue

            # Create output directory for this sensor
            sensor_dir = os.path.join(output_base_dir, file_basename, sensor_col)
            os.makedirs(sensor_dir, exist_ok=True)
            
            for i in range(num_segments):
                start = i * segment_length_points
                end = start + segment_length_points
                segment_50s = decimated_data[start:end]

                # Create time axis for the 50s plot
                time_axis = np.arange(segment_50s.size) / decimated_fs
                
                # Create the plot with specified aspect ratio and no title
                fig, ax = plt.subplots(figsize=(15, 4)) # 5:1 aspect ratio
                ax.plot(time_axis, segment_50s)
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Amplitude')
                ax.grid(True)
                
                # Save the plot directly
                png_path = os.path.join(sensor_dir, f'chunk_{i+1}.png')
                plt.savefig(png_path)
                plt.close(fig) # Close the figure to free up memory

            print(f"    Saved {num_segments} plot(s) to '{sensor_dir}'")

    print("\n--- All files processed. ---")


if __name__ == "__main__":
    main()
