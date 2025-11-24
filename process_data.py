
import os
import scipy.io
import numpy as np
import pandas as pd
from scipy.signal import butter, lfilter, decimate

def load_data_from_mat_file(file_path):
    """
    Loads data from a single MATLAB .mat file based on the user's provided logic.
    It extracts data from keys ending in 'Z' and returns a 2D numpy array 
    where each column is a sensor.
    """
    try:
        mat_data = scipy.io.loadmat(file_path)
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

    # Find all keys with the pattern 'Untitled...Z'
    keys_to_extract = [key for key in mat_data.keys() if key.startswith("Untitled") and key.endswith("Z")]

    if not keys_to_extract:
        print(f"Warning: No 'Untitled...Z' keys found in {file_path}.")
        return None

    extracted_arrays = []
    for key in keys_to_extract:
        # The structure is mat_data[key][0, 0] which is an np.void (struct)
        if (isinstance(mat_data[key], np.ndarray) and mat_data[key].shape == (1, 1)):
            raw_value = mat_data[key][0, 0]
            
            # Check if it's a struct (np.void) and has a 'Data' field
            if isinstance(raw_value, np.void) and 'Data' in raw_value.dtype.names:
                numerical_array = raw_value['Data']
                
                # Ensure the data is a numerical array and flatten it to 1D
                if isinstance(numerical_array, np.ndarray) and numerical_array.ndim >= 1:
                    extracted_arrays.append(numerical_array.flatten())

    if not extracted_arrays:
        print(f"Warning: Found 'Z' keys in {file_path}, but could not extract valid numerical data from the 'Data' field.")
        return None

    # Ensure all arrays have the same length before stacking
    first_len = len(extracted_arrays[0])
    if not all(len(arr) == first_len for arr in extracted_arrays):
        print(f"Warning: Sensor data arrays in {file_path} have inconsistent lengths. Skipping this file.")
        return None

    # Stack the 1D arrays as columns in a 2D array
    return np.column_stack(extracted_arrays)

def process_and_save_data(data_array, file_basename):
    """
    Filters, decimates, segments, and saves the data for a single file.
    """
    num_sensors = data_array.shape[1]
    df = pd.DataFrame(data_array, columns=[f'Sensor_{i+1}' for i in range(num_sensors)])
    
    print(f"\nProcessing {file_basename} with {num_sensors} sensors...")
    
    fs = 1651
    decimation_factor = 20
    segment_length_seconds = 100
    
    # --- Process each sensor column ---
    for sensor_col in df.columns:
        print(f"  Processing {sensor_col}...")
        
        # Filter
        b, a = butter(4, 0.5, 'high', fs=fs)
        filtered_data = lfilter(b, a, df[sensor_col])
        
        # Decimate
        decimated_data = decimate(filtered_data, decimation_factor, ftype='fir')
        decimated_fs = fs / decimation_factor
        
        # Segment
        segment_length_points = int(segment_length_seconds * decimated_fs)
        if segment_length_points == 0:
            print(f"    Segment length is 0. Skipping.")
            continue
            
        num_segments = len(decimated_data) // segment_length_points
        if num_segments == 0:
            print(f"    Not enough data to create a single 100-second segment.")
            continue
        
        segments = []
        for i in range(num_segments):
            start = i * segment_length_points
            end = start + segment_length_points
            segments.append(decimated_data[start:end])
        
        # --- Save the processed segments for this sensor ---
        output_dir = os.path.join('processed_segments', file_basename, sensor_col)
        os.makedirs(output_dir, exist_ok=True)
        for i, segment in enumerate(segments):
            np.save(os.path.join(output_dir, f'segment_{i+1}.npy'), segment)
            
        print(f"    Saved {len(segments)} segments to '{output_dir}'")

def main():
    """
    Main function to load, process, and save the data.
    """
    mat_files = [
        'Data/SETUP1.mat', 'Data/SETUP2.mat', 'Data/SETUP3.mat',
        'Data/SETUP4.mat', 'Data/SETUP5.mat', 'Data/SETUP6.mat',
        'Data/setup7.mat', 'Data/setup8.mat', 'Data/setup9.mat', 'Data/setup10.mat'
    ]
    
    for file_path in mat_files:
        print(f"--- Starting file: {file_path} ---")
        data_from_file = load_data_from_mat_file(file_path)
        
        if data_from_file is not None:
            file_basename = os.path.splitext(os.path.basename(file_path))[0]
            process_and_save_data(data_from_file, file_basename)
        else:
            print(f"Skipping processing for {file_path} due to loading errors.")

    print("\n--- All files processed. ---")


if __name__ == "__main__":
    main()
