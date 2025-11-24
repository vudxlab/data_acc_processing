
import os
import numpy as np
import matplotlib.pyplot as plt

def visualize_segments():
    """
    Finds all processed .npy segments, splits them, and saves visualizations as .png files.
    """
    base_dir = 'processed_segments'
    if not os.path.isdir(base_dir):
        print(f"Error: Directory '{base_dir}' not found. Please run the data processing script first.")
        return

    # Original sampling frequency and decimation factor
    fs_original = 1651
    decimation_factor = 20
    fs_decimated = fs_original / decimation_factor

    print("Starting visualization process...")

    # Use os.walk to find all .npy files
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.npy'):
                npy_path = os.path.join(root, file)
                try:
                    # Load the 100-second segment
                    segment_100s = np.load(npy_path)
                    
                    # Calculate the split point for 50s
                    # The number of points in a 50s segment
                    points_50s = int(50 * fs_decimated)
                    
                    # Ensure there's enough data to split
                    if len(segment_100s) < 2 * points_50s:
                        print(f"  - Skipping {npy_path} (not enough data for two 50s chunks)")
                        continue

                    # Split into two 50-second parts
                    part1_data = segment_100s[:points_50s]
                    part2_data = segment_100s[points_50s:2*points_50s]
                    
                    sub_segments = {'part1': part1_data, 'part2': part2_data}

                    for part_name, data_50s in sub_segments.items():
                        # Create time axis for the 50s plot
                        time_axis = np.arange(data_50s.size) / fs_decimated
                        
                        # Create the plot
                        fig, ax = plt.subplots(figsize=(12, 6))
                        ax.plot(time_axis, data_50s)
                        ax.set_title(f'Segment: {os.path.basename(npy_path)} - {part_name.capitalize()}')
                        ax.set_xlabel('Time (s)')
                        ax.set_ylabel('Amplitude')
                        ax.grid(True)
                        
                        # Save the plot
                        base_filename = os.path.splitext(npy_path)[0]
                        png_path = f"{base_filename}_{part_name}.png"
                        
                        plt.savefig(png_path)
                        plt.close(fig) # Close the figure to free up memory
                    
                    print(f"  + Visualized {npy_path}")

                except Exception as e:
                    print(f"  - Error processing {npy_path}: {e}")

    print("\nVisualization process complete.")

if __name__ == "__main__":
    visualize_segments()
