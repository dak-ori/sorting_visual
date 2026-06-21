"""시각화 모듈(visualizer.py)을 검증한다. GUI가 없는 환경에서도 동작하도록
Agg 백엔드를 사용한다."""
import matplotlib
matplotlib.use("Agg")

import pytest

from visualizer import (
    compute_bar_colors,
    speed_to_interval,
    DEFAULT_COLOR,
    COMPARING_COLOR,
    SWAPPING_COLOR,
    SORTED_COLOR,
)


def test_compute_bar_colors_default():
    info = {"comparing": None, "swapping": None, "sorted_indices": set()}
    assert compute_bar_colors(5, info) == [DEFAULT_COLOR] * 5


def test_compute_bar_colors_marks_comparing_indices():
    info = {"comparing": (1, 3), "swapping": None, "sorted_indices": set()}
    colors = compute_bar_colors(5, info)
    assert colors[1] == COMPARING_COLOR
    assert colors[3] == COMPARING_COLOR
    assert colors[0] == DEFAULT_COLOR


def test_compute_bar_colors_swapping_overrides_comparing():
    info = {"comparing": (1, 2), "swapping": (2,), "sorted_indices": set()}
    colors = compute_bar_colors(5, info)
    assert colors[2] == SWAPPING_COLOR


def test_compute_bar_colors_marks_sorted_indices():
    info = {"comparing": None, "swapping": None, "sorted_indices": {0, 1, 2}}
    colors = compute_bar_colors(5, info)
    assert colors[0] == SORTED_COLOR
    assert colors[2] == SORTED_COLOR
    assert colors[3] == DEFAULT_COLOR


def test_speed_to_interval_higher_speed_means_shorter_interval():
    assert speed_to_interval(2.0) < speed_to_interval(1.0) < speed_to_interval(0.5)


def test_speed_to_interval_rejects_non_positive_speed():
    with pytest.raises(ValueError):
        speed_to_interval(0)
