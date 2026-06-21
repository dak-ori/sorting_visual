"""시각화 모듈(visualizer.py)을 검증한다. GUI가 없는 환경에서도 동작하도록
Agg 백엔드를 사용한다."""
import matplotlib
matplotlib.use("Agg")

import pytest

from visualizer import (
    compute_bar_colors,
    speed_to_interval,
    speed_to_frame_step,
    skip_frames,
    DEFAULT_COLOR,
    COMPARING_COLOR,
    SWAPPING_COLOR,
    SORTED_COLOR,
    MAX_SPEED,
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


def test_speed_to_frame_step_is_one_at_low_speed():
    # 기본 속도(1.0x) 이하에서는 프레임을 건너뛰지 않는다 (기존 동작 유지)
    assert speed_to_frame_step(0.25) == 1
    assert speed_to_frame_step(1.0) == 1


def test_speed_to_frame_step_increases_with_speed():
    assert speed_to_frame_step(MAX_SPEED) == round(MAX_SPEED)
    assert speed_to_frame_step(MAX_SPEED) > speed_to_frame_step(1.0)


def test_speed_to_frame_step_rejects_non_positive_speed():
    with pytest.raises(ValueError):
        speed_to_frame_step(0)


def test_skip_frames_with_step_one_yields_every_frame():
    frames = list(skip_frames(iter([1, 2, 3, 4]), step=1))
    assert frames == [1, 2, 3, 4]


def test_skip_frames_with_step_three_keeps_every_third_and_final_frame():
    # 0, 3번 인덱스가 step=3에 해당하고, 마지막 프레임(인덱스 4)은
    # step에 맞지 않아도 항상 포함되어야 한다.
    frames = list(skip_frames(iter([10, 11, 12, 13, 14]), step=3))
    assert frames == [10, 13, 14]


def test_skip_frames_does_not_duplicate_final_frame_when_aligned():
    # step=2일 때 마지막 인덱스(2)가 이미 step에 맞아 한 번만 나와야 한다.
    frames = list(skip_frames(iter([0, 1, 2]), step=2))
    assert frames == [0, 2]


def test_skip_frames_with_empty_input_yields_nothing():
    assert list(skip_frames(iter([]), step=3)) == []


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


def test_build_frame_source_skips_frames_at_high_speed():
    viz = SortVisualizer()
    viz.array_size = 30
    viz.speed = MAX_SPEED
    viz.show_sort("버블 정렬")

    skipped_count = sum(1 for _ in viz._build_frame_source())
    full_count = sum(1 for _ in metrics.ALGORITHMS["버블 정렬"](list(viz.current_array)))
    assert skipped_count < full_count


def test_build_frame_source_does_not_skip_at_default_speed():
    viz = SortVisualizer()
    viz.array_size = 30
    viz.show_sort("버블 정렬")  # 기본 속도(1.0x)

    full_count = sum(1 for _ in viz._build_frame_source())
    expected_count = sum(1 for _ in metrics.ALGORITHMS["버블 정렬"](list(viz.current_array)))
    assert full_count == expected_count


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
