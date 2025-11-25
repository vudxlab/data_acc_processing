from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.io
from nptdms import TdmsFile
from scipy.signal import butter, decimate, lfilter


FS = 1651
DECIMATION_FACTOR = 20


def discover_data_files(data_dir: str = "Data") -> List[Path]:
    """Recursively find .mat and .tdms files under ``data_dir``.

    Parameters
    ----------
    data_dir: str
        Root directory to search.

    Returns
    -------
    List[Path]
        Sorted list of discovered files.
    """
    root = Path(data_dir)
    mat_files = list(root.rglob("*.mat"))
    tdms_files = list(root.rglob("*.tdms"))
    return sorted(mat_files + tdms_files)


def load_data_from_mat_file(file_path: Path) -> Tuple[Optional[np.ndarray], Optional[List[str]]]:
    """Load data and sensor labels from a MATLAB ``.mat`` file.

    The loader searches for keys that start with ``Untitled`` and end with
    ``X``, ``Y`` or ``Z``. Each matched entry is expected to be a struct with a
    ``Data`` field containing numerical values.
    """
    try:
        mat_data = scipy.io.loadmat(file_path)
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"Error loading file {file_path}: {exc}")
        return None, None

    keys_to_extract = [
        key
        for key in mat_data.keys()
        if key.startswith("Untitled") and (key.endswith("X") or key.endswith("Y") or key.endswith("Z"))
    ]

    if not keys_to_extract:
        print(f"Warning: No 'Untitled...[X,Y,Z]' keys found in {file_path}.")
        return None, None

    extracted_arrays: List[np.ndarray] = []
    sensor_labels: List[str] = []

    for key in keys_to_extract:
        value = mat_data.get(key)
        if isinstance(value, np.ndarray) and value.shape == (1, 1):
            raw_value = value[0, 0]
            if isinstance(raw_value, np.void) and "Data" in raw_value.dtype.names:
                numerical_array = raw_value["Data"]
                if isinstance(numerical_array, np.ndarray) and numerical_array.ndim >= 1:
                    extracted_arrays.append(numerical_array.flatten())
                    sensor_labels.append(key)

    if not extracted_arrays:
        print(f"Warning: Found matching keys in {file_path}, but could not extract valid numerical data.")
        return None, None

    first_len = len(extracted_arrays[0])
    if not all(len(arr) == first_len for arr in extracted_arrays):
        print(f"Warning: Sensor data arrays in {file_path} have inconsistent lengths. Skipping.")
        return None, None

    return np.column_stack(extracted_arrays), sensor_labels


def load_data_from_tdms_file(file_path: Path) -> Tuple[Optional[np.ndarray], Optional[List[str]]]:
    """Load data and channel labels from a TDMS file."""
    try:
        tdms_file = TdmsFile.read(file_path)
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"Error loading file {file_path}: {exc}")
        return None, None

    channel_data: List[np.ndarray] = []
    channel_names: List[str] = []

    for group in tdms_file.groups():
        for channel in group.channels():
            data = channel[:]
            if data is None:
                continue
            numeric_data = np.asarray(data).flatten()
            if numeric_data.size == 0:
                continue
            channel_data.append(numeric_data)
            channel_names.append(f"{group.name}_{channel.name}" if group.name else channel.name)

    if not channel_data:
        print(f"Warning: No channel data found in {file_path}.")
        return None, None

    min_len = min(len(arr) for arr in channel_data)
    aligned_data = [arr[:min_len] for arr in channel_data]
    return np.column_stack(aligned_data), channel_names


def load_data(file_path: Path) -> Tuple[Optional[np.ndarray], Optional[List[str]]]:
    """Dispatch data loading based on file extension."""
    suffix = file_path.suffix.lower()
    if suffix == ".mat":
        return load_data_from_mat_file(file_path)
    if suffix == ".tdms":
        return load_data_from_tdms_file(file_path)

    print(f"Unsupported file type: {file_path}")
    return None, None


def _filter_and_decimate(series: Sequence[float], fs: int = FS, decimation_factor: int = DECIMATION_FACTOR) -> np.ndarray:
    """Apply a high-pass Butterworth filter and decimate the series."""
    b, a = butter(4, 0.5, "high", fs=fs)
    filtered_data = lfilter(b, a, series)
    return decimate(filtered_data, decimation_factor, ftype="fir")


def _segment_array(data: np.ndarray, segment_length_points: int) -> List[np.ndarray]:
    """Split ``data`` into contiguous segments of ``segment_length_points``."""
    if segment_length_points <= 0:
        return []
    num_segments = len(data) // segment_length_points
    return [data[i * segment_length_points : (i + 1) * segment_length_points] for i in range(num_segments)]


def process_loaded_data(
    data_array: np.ndarray,
    sensor_labels: Sequence[str],
    file_basename: str,
    *,
    output_dir: str = "processed_segments",
    fs: int = FS,
    decimation_factor: int = DECIMATION_FACTOR,
    segment_length_seconds: int = 100,
) -> None:
    """Filter, decimate, and segment data before saving as ``.npy`` files."""
    df = pd.DataFrame(data_array, columns=sensor_labels)

    print(f"\nProcessing {file_basename} with {len(sensor_labels)} sensors...")

    decimated_fs = fs / decimation_factor
    segment_length_points = int(segment_length_seconds * decimated_fs)

    for sensor_col in df.columns:
        print(f"  Processing {sensor_col}...")
        decimated_data = _filter_and_decimate(df[sensor_col], fs=fs, decimation_factor=decimation_factor)
        segments = _segment_array(decimated_data, segment_length_points)

        if not segments:
            print(f"    Not enough data to create a {segment_length_seconds}-second segment.")
            continue

        sensor_dir = Path(output_dir) / file_basename / sensor_col
        sensor_dir.mkdir(parents=True, exist_ok=True)

        for idx, segment in enumerate(segments, start=1):
            np.save(sensor_dir / f"segment_{idx}.npy", segment)

        print(f"    Saved {len(segments)} segments to '{sensor_dir}'")


def visualize_loaded_data(
    data_array: np.ndarray,
    sensor_labels: Sequence[str],
    file_basename: str,
    *,
    output_dir: str = "results",
    fs: int = FS,
    decimation_factor: int = DECIMATION_FACTOR,
    segment_length_seconds: int = 50,
) -> None:
    """Filter, decimate, and visualize sensor data as PNG files."""
    df = pd.DataFrame(data_array, columns=sensor_labels)

    print(f"\nVisualizing {file_basename} with {len(sensor_labels)} sensors...")

    decimated_fs = fs / decimation_factor
    segment_length_points = int(segment_length_seconds * decimated_fs)

    for sensor_col in df.columns:
        print(f"  Plotting {sensor_col}...")
        decimated_data = _filter_and_decimate(df[sensor_col], fs=fs, decimation_factor=decimation_factor)
        segments = _segment_array(decimated_data, segment_length_points)

        if not segments:
            print(f"    Not enough data to create a {segment_length_seconds}-second segment.")
            continue

        sensor_dir = Path(output_dir) / file_basename / sensor_col
        sensor_dir.mkdir(parents=True, exist_ok=True)

        for idx, segment in enumerate(segments, start=1):
            time_axis = np.arange(segment.size) / decimated_fs
            fig, ax = plt.subplots(figsize=(15, 4))
            ax.plot(time_axis, segment)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Amplitude")
            ax.grid(True)

            png_path = sensor_dir / f"chunk_{idx}.png"
            plt.savefig(png_path)
            plt.close(fig)

        print(f"    Saved {len(segments)} plot(s) to '{sensor_dir}'")


def run_pipeline(
    data_dir: str = "Data",
    *,
    save_segments: bool = True,
    save_plots: bool = True,
    segment_length_seconds: int = 100,
    plot_segment_seconds: int = 50,
    fs: int = FS,
    decimation_factor: int = DECIMATION_FACTOR,
) -> None:
    """Discover data files and run processing/visualization steps."""
    data_files = discover_data_files(data_dir)
    if not data_files:
        print(f"No data files found under '{data_dir}'.")
        return

    for file_path in data_files:
        print(f"--- Starting file: {file_path} ---")
        data_array, sensor_labels = load_data(file_path)

        if data_array is None or sensor_labels is None:
            print(f"Skipping processing for {file_path} due to loading errors.")
            continue

        file_basename = file_path.stem

        if save_segments:
            process_loaded_data(
                data_array,
                sensor_labels,
                file_basename,
                output_dir="processed_segments",
                fs=fs,
                decimation_factor=decimation_factor,
                segment_length_seconds=segment_length_seconds,
            )

        if save_plots:
            visualize_loaded_data(
                data_array,
                sensor_labels,
                file_basename,
                output_dir="results",
                fs=fs,
                decimation_factor=decimation_factor,
                segment_length_seconds=plot_segment_seconds,
            )

    print("\n--- All files processed. ---")


def main() -> None:
    run_pipeline()


if __name__ == "__main__":
    main()
