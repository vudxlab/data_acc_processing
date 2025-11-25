"""Visualization helpers for saved signal segments."""

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def visualize_segments(
    *,
    base_dir: str = "processed_segments",
    fs_original: int = 1651,
    decimation_factor: int = 20,
    plot_length_seconds: int = 50,
) -> None:
    """Visualize saved ``.npy`` segments by splitting them into sub-chunks.

    The function walks ``base_dir`` to find decimated ``.npy`` segments and
    saves ``.png`` plots for each part. It assumes that the saved segments are
    already decimated by ``decimation_factor`` from the original sampling
    frequency.
    """
    if not os.path.isdir(base_dir):
        print(f"Error: Directory '{base_dir}' not found. Please run the data processing script first.")
        return

    fs_decimated = fs_original / decimation_factor
    points_per_plot = int(plot_length_seconds * fs_decimated)

    print("Starting visualization process...")

    for npy_path in Path(base_dir).rglob("*.npy"):
        try:
            segment = np.load(npy_path)

            if len(segment) < 2 * points_per_plot:
                print(f"  - Skipping {npy_path} (not enough data for two {plot_length_seconds}s chunks)")
                continue

            sub_segments = {
                "part1": segment[:points_per_plot],
                "part2": segment[points_per_plot : 2 * points_per_plot],
            }

            for part_name, data_slice in sub_segments.items():
                time_axis = np.arange(data_slice.size) / fs_decimated
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(time_axis, data_slice)
                ax.set_title(f"Segment: {os.path.basename(npy_path)} - {part_name.capitalize()}")
                ax.set_xlabel("Time (s)")
                ax.set_ylabel("Amplitude")
                ax.grid(True)

                base_filename = os.path.splitext(npy_path)[0]
                png_path = f"{base_filename}_{part_name}.png"

                plt.savefig(png_path)
                plt.close(fig)

            print(f"  + Visualized {npy_path}")

        except Exception as exc:  # pragma: no cover - defensive logging
            print(f"  - Error processing {npy_path}: {exc}")

    print("\nVisualization process complete.")
