"""Legacy wrappers that forward to the modular processing package."""

from acc_processing.config import PipelineConfig
from acc_processing.data_io import discover_data_files, load_data, load_data_from_mat_file, load_data_from_tdms_file
from acc_processing.pipeline import run_pipeline
from acc_processing.processing import process_loaded_data
from acc_processing.visualization import visualize_segments

__all__ = [
    "PipelineConfig",
    "discover_data_files",
    "load_data_from_mat_file",
    "load_data_from_tdms_file",
    "load_data",
    "process_loaded_data",
    "run_pipeline",
    "visualize_segments",
]


if __name__ == "__main__":
    run_pipeline()
