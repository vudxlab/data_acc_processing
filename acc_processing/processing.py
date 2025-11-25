"""Signal processing utilities."""

from typing import List, Sequence

import numpy as np
import pandas as pd
from scipy.signal import butter, decimate, lfilter

from .data_io import ensure_output_dir


def _filter_and_decimate(series: Sequence[float], *, fs: int, decimation_factor: int) -> np.ndarray:
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
    output_dir: str,
    fs: int,
    decimation_factor: int,
    segment_length_seconds: int,
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

        sensor_dir = ensure_output_dir(output_dir, file_basename, sensor_col)

        for idx, segment in enumerate(segments, start=1):
            np.save(sensor_dir / f"segment_{idx}.npy", segment)

        print(f"    Saved {len(segments)} segments to '{sensor_dir}'")
