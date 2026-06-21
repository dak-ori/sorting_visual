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


def test_show_sort_creates_one_bar_per_array_element():
    viz = SortVisualizer()
    viz.array_size = 8
    viz.show_sort("버블 정렬")
    assert len(viz.bars) == 8
    assert viz.ax_bars.get_title() == "버블 정렬"


def test_animate_updates_bar_heights_and_colors():
    viz = SortVisualizer()
    viz.array_size = 5
    viz.show_sort("버블 정렬")
    frame = (
        [10, 20, 30, 40, 50],
        {
            "comparing": (0, 1), "swapping": None, "sorted_indices": set(),
            "comparisons": 3, "array_accesses": 1,
        },
    )
    viz._animate(frame)
    heights = [bar.get_height() for bar in viz.bars]
    assert heights == [10, 20, 30, 40, 50]
    assert viz.bars[0].get_facecolor() == matplotlib.colors.to_rgba("red")


def test_update_info_text_includes_comparisons_and_accesses():
    viz = SortVisualizer()
    viz.array_size = 5
    viz.show_sort("버블 정렬")
    viz._update_info_text({"comparisons": 7, "array_accesses": 3}, 1.23)
    text = viz.info_text.get_text()
    assert "7" in text
    assert "3" in text


def test_restart_sort_applies_new_slider_values():
    viz = SortVisualizer()
    viz.show_sort("버블 정렬")
    viz.size_slider.set_val(20)
    viz.speed_slider.set_val(2.0)
    viz._restart_sort()
    assert viz.array_size == 20
    assert viz.speed == 2.0
    assert len(viz.bars) == 20


def test_toggle_pause_changes_button_label():
    viz = SortVisualizer()
    viz.show_sort("버블 정렬")
    assert viz.pause_button.label.get_text() == "일시정지"
    viz._toggle_pause()
    assert viz.pause_button.label.get_text() == "계속"
    viz._toggle_pause()
    assert viz.pause_button.label.get_text() == "일시정지"


def test_show_menu_after_sort_returns_to_menu_screen():
    viz = SortVisualizer()
    viz.show_sort("버블 정렬")
    viz.show_menu()
    assert len(viz.fig.axes) == len(metrics.ALGORITHMS) + 1


def test_show_compare_setup_creates_slider_and_two_buttons():
    viz = SortVisualizer()
    viz.show_compare_setup()
    # 배열 크기 슬라이더 1개 + 측정 시작 버튼 + 메뉴로 버튼 = 3개 Axes
    assert len(viz.fig.axes) == 3


def test_show_compare_result_creates_two_subplots_with_six_bars_each():
    viz = SortVisualizer()
    fake_result = {
        name: {"comparisons": 100, "array_accesses": 50, "elapsed_time": 0.01}
        for name in metrics.ALGORITHMS
    }
    viz.show_compare_result(fake_result)
    bar_axes = [ax for ax in viz.fig.axes if ax.patches]
    assert len(bar_axes) == 2
    for ax in bar_axes:
        assert len(ax.patches) == 6


def test_run_compare_uses_slider_value_as_array_size(monkeypatch):
    viz = SortVisualizer()
    viz.show_compare_setup()
    viz.compare_size_slider.set_val(15)

    captured = {}

    def fake_run_comparison(array):
        captured["size"] = len(array)
        return {
            name: {"comparisons": 1, "array_accesses": 1, "elapsed_time": 0.0}
            for name in metrics.ALGORITHMS
        }

    monkeypatch.setattr(metrics, "run_comparison", fake_run_comparison)
    viz._run_compare()
    assert captured["size"] == 15
    assert viz.array_size == 15
