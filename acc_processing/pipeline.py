"""High-level orchestration for loading, processing, and visualizing data."""

from pathlib import Path

from .config import PipelineConfig
from .data_io import discover_data_files, load_data
from .processing import process_loaded_data
from .visualization import visualize_segments


def run_pipeline(
    *,
    data_dir: str = "Data",
    output_dir: str = "processed_segments",
    save_plots: bool = True,
    segment_length_seconds: int = 100,
    plot_segment_seconds: int = 50,
    fs: int = 1651,
    decimation_factor: int = 20,
    config: PipelineConfig | None = None,
) -> None:
    """Discover data files and run processing/visualization steps."""

    cfg = config or PipelineConfig(
        data_dir=data_dir,
        output_dir=output_dir,
        save_plots=save_plots,
        segment_length_seconds=segment_length_seconds,
        plot_segment_seconds=plot_segment_seconds,
        fs=fs,
        decimation_factor=decimation_factor,
    )

    data_files = discover_data_files(cfg.data_dir)
    if not data_files:
        print(f"No data files found under '{cfg.data_dir}'.")
        return

    for file_path in data_files:
        _process_file(file_path, cfg)

    print("\n--- All files processed. ---")


def _process_file(file_path: Path, cfg: PipelineConfig) -> None:
    print(f"--- Starting file: {file_path} ---")
    data_array, sensor_labels = load_data(file_path)

    if data_array is None or sensor_labels is None:
        print(f"Skipping processing for {file_path} due to loading errors.")
        return

    file_basename = file_path.stem

    segments_by_sensor = process_loaded_data(
        data_array,
        sensor_labels,
        file_basename,
        fs=cfg.fs,
        decimation_factor=cfg.decimation_factor,
        segment_length_seconds=cfg.segment_length_seconds,
    )

    if cfg.save_plots:
        visualize_segments(
            segments_by_sensor,
            file_basename=file_basename,
            output_dir=cfg.output_dir,
            fs_original=cfg.fs,
            decimation_factor=cfg.decimation_factor,
            plot_length_seconds=cfg.plot_segment_seconds,
        )
