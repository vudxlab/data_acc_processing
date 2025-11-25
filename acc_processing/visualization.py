"""Visualization helpers for processed signal segments."""

from pathlib import Path
from typing import Dict, Iterable, List

import matplotlib.pyplot as plt
import numpy as np

from .data_io import ensure_output_dir


def visualize_segments(
    segments_by_sensor: Dict[str, List[np.ndarray]],
    *,
    file_basename: str,
    output_dir: str,
    fs_original: int = 1651,
    decimation_factor: int = 20,
    plot_length_seconds: int = 50,
) -> None:
    """Generate PNG plots directly from in-memory segments.

    Each segment is split into two consecutive windows of ``plot_length_seconds``
    and saved as separate plots. No intermediate ``.npy`` files are produced.
    """

    fs_decimated = fs_original / decimation_factor
    points_per_plot = int(plot_length_seconds * fs_decimated)

    if not segments_by_sensor:
        print("No segments available for visualization.")
        return

    print("Starting visualization process...")

    for sensor, segments in segments_by_sensor.items():
        sensor_dir = ensure_output_dir(output_dir, file_basename, sensor)
        _visualize_sensor_segments(
            segments,
            sensor_dir=sensor_dir,
            fs_decimated=fs_decimated,
            points_per_plot=points_per_plot,
            sensor=sensor,
        )

    print("\nVisualization process complete.")


def _visualize_sensor_segments(
    segments: Iterable[np.ndarray],
    *,
    sensor_dir: Path,
    fs_decimated: float,
    points_per_plot: int,
    sensor: str,
) -> None:
    base_font_size = plt.rcParams.get("font.size", 10) * 2

    for idx, segment in enumerate(segments, start=1):
        if len(segment) < 2 * points_per_plot:
            print(
                f"  - Skipping {sensor} segment {idx} (not enough data for two plots of {points_per_plot} samples each)"
            )
            continue

        sub_segments = {
            "part1": segment[:points_per_plot],
            "part2": segment[points_per_plot : 2 * points_per_plot],
        }

        for part_name, data_slice in sub_segments.items():
            time_axis = np.arange(data_slice.size) / fs_decimated

            with plt.rc_context({"font.size": base_font_size}):
                fig, ax = plt.subplots(figsize=(12, 4))
                ax.plot(time_axis, data_slice, linewidth=1.2)
                ax.set_xlabel("Time (s)")
                ax.set_ylabel("Amplitude")
                ax.grid(True)
                fig.subplots_adjust(left=0.06, right=0.98)

                png_path = sensor_dir / f"segment_{idx}_{part_name}.png"
                plt.savefig(png_path, dpi=150)
                plt.close(fig)

        print(f"  + Saved plots for {sensor} segment {idx} to '{sensor_dir}'")
