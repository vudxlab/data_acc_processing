"""Entry point for running the plotting pipeline."""

import argparse

from acc_processing.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process data files and generate visualization PNGs.")
    parser.add_argument("--data-dir", default="Data", help="Root directory containing .mat/.tdms files (default: Data)")
    parser.add_argument("--output-dir", default="processed_segments", help="Directory for generated plots")
    parser.add_argument("--segment-length", type=int, default=100, help="Segment length in seconds before plotting")
    parser.add_argument("--plot-length", type=int, default=50, help="Length in seconds for each plotted sub-segment")
    parser.add_argument("--fs", type=int, default=1651, help="Original sampling frequency (Hz)")
    parser.add_argument("--decimation", type=int, default=20, help="Decimation factor applied during processing")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_pipeline(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        save_plots=True,
        segment_length_seconds=args.segment_length,
        plot_segment_seconds=args.plot_length,
        fs=args.fs,
        decimation_factor=args.decimation,
    )


if __name__ == "__main__":
    main()
