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


from visualizer import SortVisualizer
import metrics


def test_show_menu_creates_one_button_per_algorithm_plus_compare_button():
    viz = SortVisualizer()
    viz.show_menu()
    # 6개 알고리즘 버튼 + "전체 성능 비교" 버튼 1개 = 7개 Axes
    assert len(viz.fig.axes) == len(metrics.ALGORITHMS) + 1


def test_show_menu_button_labels_include_all_algorithm_names():
    viz = SortVisualizer()
    viz.show_menu()
    labels = {button.label.get_text() for button in viz._widgets}
    assert set(metrics.ALGORITHMS.keys()).issubset(labels)
    assert "전체 성능 비교" in labels


def test_clear_figure_resets_widgets_list():
    viz = SortVisualizer()
    viz.show_menu()
    assert len(viz._widgets) > 0
    viz._clear_figure()
    assert viz._widgets == []
    assert viz.fig.axes == []
