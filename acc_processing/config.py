from dataclasses import dataclass


@dataclass(slots=True)
class PipelineConfig:
    """Configuration for the vibration data processing pipeline."""

    data_dir: str = "Data"
    output_dir: str = "processed_segments"
    save_plots: bool = True
    segment_length_seconds: int = 100
    plot_segment_seconds: int = 50
    fs: int = 1651
    decimation_factor: int = 20
