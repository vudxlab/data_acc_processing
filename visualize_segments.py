"""Entry point for visualizing saved segments."""

import argparse

from acc_processing.visualization import visualize_segments


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualize saved decimated segment files.")
    parser.add_argument("--base-dir", default="processed_segments", help="Directory containing saved .npy segments")
    parser.add_argument("--fs", type=int, default=1651, help="Original sampling frequency (Hz)")
    parser.add_argument("--decimation", type=int, default=20, help="Decimation factor applied during processing")
    parser.add_argument("--plot-length", type=int, default=50, help="Length in seconds for each plotted sub-segment")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    visualize_segments(
        base_dir=args.base_dir,
        fs_original=args.fs,
        decimation_factor=args.decimation,
        plot_length_seconds=args.plot_length,
    )


if __name__ == "__main__":
    main()
