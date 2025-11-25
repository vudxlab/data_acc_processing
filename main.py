import argparse

from acc_processing.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process vibration data files under the Data directory.")
    parser.add_argument("--data-dir", default="Data", help="Root directory containing .mat/.tdms files (default: Data)")
    parser.add_argument(
        "--output-dir",
        default="processed_segments",
        help="Directory for saved decimated .npy segments and plots (default: processed_segments)",
    )
    parser.add_argument("--skip-segments", action="store_true", help="Skip saving decimated .npy segments")
    parser.add_argument("--skip-plots", action="store_true", help="Skip saving visualization PNGs")
    parser.add_argument("--segment-length", type=int, default=100, help="Segment length in seconds for saved .npy files")
    parser.add_argument("--plot-length", type=int, default=50, help="Segment length in seconds for plot PNGs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_pipeline(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        save_segments=not args.skip_segments,
        save_plots=not args.skip_plots,
        segment_length_seconds=args.segment_length,
        plot_segment_seconds=args.plot_length,
    )


if __name__ == "__main__":
    main()
