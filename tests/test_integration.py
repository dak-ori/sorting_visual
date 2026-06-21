"""화면 전환 전체 흐름(메뉴 -> 시각화 -> 비교)이 예외 없이 동작하는지
확인하는 헤드리스 통합 스모크 테스트."""
import matplotlib
matplotlib.use("Agg")

import metrics
from visualizer import SortVisualizer


def test_every_algorithm_can_be_visualized_and_return_to_menu():
    for name in metrics.ALGORITHMS:
        viz = SortVisualizer()
        viz.array_size = 12
        viz.show_sort(name)

        # 알고리즘이 실제로 최소 한 프레임을 생성하고, _animate가
        # 예외 없이 그 프레임을 처리할 수 있는지 확인한다.
        frame = next(iter(metrics.ALGORITHMS[name](list(viz.current_array))))
        viz._animate(frame)

        viz.show_menu()
        assert len(viz.fig.axes) == len(metrics.ALGORITHMS) + 1


def test_compare_mode_full_flow_from_menu_to_result():
    viz = SortVisualizer()
    viz.show_menu()
    viz.show_compare_setup()
    viz.compare_size_slider.set_val(10)
    viz._run_compare()

    bar_axes = [ax for ax in viz.fig.axes if ax.patches]
    assert len(bar_axes) == 2
    for ax in bar_axes:
        assert len(ax.patches) == len(metrics.ALGORITHMS)
