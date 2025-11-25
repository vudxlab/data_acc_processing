"""Data discovery and ingestion helpers."""

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import scipy.io
from nptdms import TdmsFile


SensorData = Tuple[Optional[np.ndarray], Optional[List[str]]]


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


def load_data_from_mat_file(file_path: Path) -> SensorData:
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


def load_data_from_tdms_file(file_path: Path) -> SensorData:
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

            if np.issubdtype(numeric_data.dtype, np.datetime64):
                # Convert datetime channels to seconds from epoch to avoid dtype promotion errors
                numeric_data = numeric_data.astype("datetime64[ns]").astype(np.int64) / 1e9
            elif np.issubdtype(numeric_data.dtype, np.number):
                numeric_data = numeric_data.astype(np.float64)
            else:
                try:
                    numeric_data = numeric_data.astype(np.float64)
                except (TypeError, ValueError):
                    print(
                        f"Warning: Skipping non-numeric channel {channel.name} in {file_path} "
                        f"(dtype={numeric_data.dtype})."
                    )
                    continue

            channel_data.append(numeric_data)
            channel_names.append(f"{group.name}_{channel.name}" if group.name else channel.name)

    if not channel_data:
        print(f"Warning: No channel data found in {file_path}.")
        return None, None

    min_len = min(len(arr) for arr in channel_data)
    aligned_data = [arr[:min_len] for arr in channel_data]
    return np.column_stack(aligned_data), channel_names


def load_data(file_path: Path) -> SensorData:
    """Dispatch data loading based on file extension."""
    suffix = file_path.suffix.lower()
    if suffix == ".mat":
        return load_data_from_mat_file(file_path)
    if suffix == ".tdms":
        return load_data_from_tdms_file(file_path)

    print(f"Unsupported file type: {file_path}")
    return None, None


def ensure_output_dir(output_dir: str, file_basename: str, sensor_col: str) -> Path:
    """Create the sensor-specific output directory if needed."""
    sensor_dir = Path(output_dir) / file_basename / sensor_col
    sensor_dir.mkdir(parents=True, exist_ok=True)
    return sensor_dir
