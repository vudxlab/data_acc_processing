# Data Acquisition Processing

A modular pipeline for loading, filtering, decimating, segmenting, and visualizing vibration data from both MATLAB (`.mat`) and TDMS (`.tdms`) sources.

## Quick Start

```bash
# Install dependencies (example)
pip install -r requirements.txt  # or ensure scipy, numpy, pandas, matplotlib, nptdms are available

# Process data
python main.py --data-dir Data --output-dir processed_segments

# Visualize previously saved segments
python visualize_segments.py --base-dir processed_segments
```

## Command-line options (main.py)

- `--data-dir`: Root folder to search recursively for `.mat` and `.tdms` files (default: `Data`).
- `--output-dir`: Destination for decimated `.npy` segments and generated plots (default: `processed_segments`).
- `--skip-segments`: Disable saving decimated `.npy` segments.
- `--skip-plots`: Disable generating visualization PNGs.
- `--segment-length`: Length in seconds for saved decimated segments (default: `100`).
- `--plot-length`: Length in seconds for each plotted sub-segment (default: `50`).

## Processing flow

1. Discover `.mat` and `.tdms` files recursively under the chosen data directory.
2. Load sensor channels (`Untitled*X/Y/Z` for MATLAB files, all channels for TDMS files).
3. High-pass filter at 0.5 Hz, then decimate by a configurable factor (default: 20).
4. Split each decimated signal into fixed-length segments and save as `.npy` files under `processed_segments/<file>/<sensor>/`.
5. (Optional) Read the saved `.npy` files and generate paired PNG plots for each segment.

## Project structure

```
acc_processing/
├── __init__.py          # Package exports
├── config.py            # Pipeline configuration dataclass
├── data_io.py           # Discovery and loaders for .mat/.tdms files
├── pipeline.py          # Orchestration of loading, processing, and visualization
├── processing.py        # Filtering, decimation, segmentation, and saving
└── visualization.py     # PNG generation from saved segments

main.py                  # CLI entry point for the full pipeline
process_data.py          # Legacy wrapper pointing to the package implementation
visualize_segments.py    # CLI entry for visualization only
Data/                    # Expected input root (user-provided)
processed_segments/      # Default output directory (created at runtime)
```

## Extending the pipeline

- Add new loaders (e.g., CSV, Parquet) in `acc_processing/data_io.py` and register them in `load_data`.
- Introduce new processing steps in `acc_processing/processing.py` before the segmentation loop.
- Adjust defaults or add new runtime flags by updating `acc_processing/config.py` and `main.py`.
- Swap or augment plotting logic inside `acc_processing/visualization.py` without touching the CLI.

With the shared `PipelineConfig` and package modules, new functionality can be added without rewriting the entry-point scripts.
