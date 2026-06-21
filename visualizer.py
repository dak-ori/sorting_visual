"""정렬 알고리즘 애니메이션과 성능 비교 화면을 matplotlib으로 그리는 모듈.

색상 규칙:
    기본            : DEFAULT_COLOR (연한 파랑)
    비교 중인 원소   : COMPARING_COLOR (빨강)
    교환/이동 중인 원소 : SWAPPING_COLOR (초록)
    정렬 완료된 원소 : SORTED_COLOR (진한 파랑)
"""
import time

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider

import metrics

DEFAULT_COLOR = "skyblue"
COMPARING_COLOR = "red"
SWAPPING_COLOR = "green"
SORTED_COLOR = "navy"

BASE_INTERVAL_MS = 200  # 속도 1.0x일 때 애니메이션 프레임 간 간격(ms)

MIN_SIZE, MAX_SIZE, DEFAULT_SIZE = 10, 100, 50
MIN_SPEED, MAX_SPEED, DEFAULT_SPEED = 0.25, 3.0, 1.0


def compute_bar_colors(n, info):
    """info 딕셔너리(comparing/swapping/sorted_indices)를 받아 n개 막대의
    색상 리스트를 계산한다. matplotlib에 의존하지 않는 순수 함수라서
    GUI 없이도 단위 테스트가 가능하다.

    적용 순서: 기본값 -> 정렬 완료 -> 비교 중 -> 교환/이동 중
    (현재 진행 중인 동작이 가장 눈에 잘 보이도록 마지막에 덮어쓴다)
    """
    colors = [DEFAULT_COLOR] * n
    for idx in info.get("sorted_indices") or ():
        colors[idx] = SORTED_COLOR
    for idx in info.get("comparing") or ():
        colors[idx] = COMPARING_COLOR
    for idx in info.get("swapping") or ():
        colors[idx] = SWAPPING_COLOR
    return colors


def speed_to_interval(speed):
    """속도 배수(0.25x~3x)를 matplotlib FuncAnimation의 interval(ms)로
    변환한다. 속도가 빠를수록 프레임 간 간격은 짧아진다."""
    if speed <= 0:
        raise ValueError("speed는 0보다 커야 합니다")
    return BASE_INTERVAL_MS / speed


class SortVisualizer:
    """하나의 matplotlib Figure로 메뉴/시각화/비교 화면을 전환하며
    관리하는 클래스. 화면을 바꿀 때마다 Figure를 비우고(clear) 해당
    화면의 위젯을 새로 그린다."""

    def __init__(self):
        self.fig = plt.figure(figsize=(9, 6))
        self.array_size = DEFAULT_SIZE
        self.speed = DEFAULT_SPEED
        self._widgets = []  # 위젯 참조를 유지해서 GC로 콜백이 사라지지 않게 함
        self._animation = None

    def run(self):
        """메뉴 화면을 띄우고 matplotlib 이벤트 루프를 시작한다."""
        self.show_menu()
        plt.show()

    def _clear_figure(self):
        # 애니메이션이 돌고 있으면 먼저 멈춘다 (멈추지 않으면 화면이
        # 전환된 뒤에도 백그라운드에서 계속 갱신을 시도할 수 있다)
        if self._animation is not None:
            self._animation.event_source.stop()
            self._animation = None
        self.fig.clear()
        self._widgets = []

    def show_menu(self):
        self._clear_figure()
        self.fig.suptitle("정렬 알고리즘 비교 시각화", fontsize=14)

        names = list(metrics.ALGORITHMS.keys())
        button_height = 0.08
        gap = 0.02
        top = 0.85

        for i, name in enumerate(names):
            ax = self.fig.add_axes([0.3, top - i * (button_height + gap), 0.4, button_height])
            button = Button(ax, name)
            button.on_clicked(lambda event, n=name: self.show_sort(n))
            self._widgets.append(button)

        compare_top = top - len(names) * (button_height + gap)
        compare_ax = self.fig.add_axes([0.3, compare_top, 0.4, button_height])
        compare_button = Button(compare_ax, "전체 성능 비교")
        compare_button.on_clicked(lambda event: self.show_compare_setup())
        self._widgets.append(compare_button)

        self.fig.canvas.draw_idle()

    def show_sort(self, algorithm_name):
        self._clear_figure()
        self.current_array = metrics.generate_array(self.array_size)
        self._algorithm_name = algorithm_name
        self._paused = False
        self._setup_sort_screen()

    def _setup_sort_screen(self):
        self.ax_bars = self.fig.add_axes([0.1, 0.35, 0.8, 0.5])
        self.bars = self.ax_bars.bar(
            range(len(self.current_array)), self.current_array, color=DEFAULT_COLOR,
        )
        self.ax_bars.set_title(self._algorithm_name)
        self.ax_bars.set_xlim(-0.5, len(self.current_array) - 0.5)

        self.info_text = self.fig.text(0.1, 0.92, "", fontsize=11)
        self._start_time = time.perf_counter()
        self._update_info_text({"comparisons": 0, "array_accesses": 0}, 0.0)

        size_ax = self.fig.add_axes([0.15, 0.22, 0.3, 0.04])
        self.size_slider = Slider(
            size_ax, "배열 크기", MIN_SIZE, MAX_SIZE, valinit=self.array_size, valstep=1,
        )
        self._widgets.append(self.size_slider)

        speed_ax = self.fig.add_axes([0.55, 0.22, 0.3, 0.04])
        self.speed_slider = Slider(
            speed_ax, "속도", MIN_SPEED, MAX_SPEED, valinit=self.speed,
        )
        self._widgets.append(self.speed_slider)

        restart_ax = self.fig.add_axes([0.15, 0.1, 0.2, 0.06])
        restart_button = Button(restart_ax, "재시작")
        restart_button.on_clicked(lambda event: self._restart_sort())
        self._widgets.append(restart_button)

        pause_ax = self.fig.add_axes([0.4, 0.1, 0.2, 0.06])
        self.pause_button = Button(pause_ax, "일시정지")
        self.pause_button.on_clicked(lambda event: self._toggle_pause())
        self._widgets.append(self.pause_button)

        menu_ax = self.fig.add_axes([0.65, 0.1, 0.2, 0.06])
        menu_button = Button(menu_ax, "메뉴로")
        menu_button.on_clicked(lambda event: self.show_menu())
        self._widgets.append(menu_button)

        generator = metrics.ALGORITHMS[self._algorithm_name](self.current_array)
        self._animation = FuncAnimation(
            self.fig,
            self._animate,
            frames=generator,
            interval=speed_to_interval(self.speed),
            repeat=False,
            cache_frame_data=False,
        )
        self.fig.canvas.draw_idle()

    def _animate(self, frame):
        # FuncAnimation이 매 프레임마다 호출한다. frame은 알고리즘
        # 제너레이터가 yield한 (array, info) 튜플이다.
        array, info = frame
        for bar, height in zip(self.bars, array):
            bar.set_height(height)
        colors = compute_bar_colors(len(array), info)
        for bar, color in zip(self.bars, colors):
            bar.set_color(color)
        elapsed = time.perf_counter() - self._start_time
        self._update_info_text(info, elapsed)
        return list(self.bars) + [self.info_text]

    def _update_info_text(self, info, elapsed):
        self.info_text.set_text(
            f"비교 횟수: {info['comparisons']}   "
            f"배열 접근: {info['array_accesses']}   "
            f"경과 시간: {elapsed:.2f}s"
        )

    def _restart_sort(self):
        self.array_size = int(self.size_slider.val)
        self.speed = self.speed_slider.val
        self.show_sort(self._algorithm_name)

    def _toggle_pause(self):
        if self._paused:
            self._animation.event_source.start()
        else:
            self._animation.event_source.stop()
        self._paused = not self._paused
        self.pause_button.label.set_text("계속" if self._paused else "일시정지")

    def show_compare_setup(self):
        self._clear_figure()
        self.fig.suptitle("전체 성능 비교 - 배열 크기 설정", fontsize=14)

        size_ax = self.fig.add_axes([0.25, 0.55, 0.5, 0.06])
        self.compare_size_slider = Slider(
            size_ax, "배열 크기", MIN_SIZE, MAX_SIZE, valinit=self.array_size, valstep=1,
        )
        self._widgets.append(self.compare_size_slider)

        start_ax = self.fig.add_axes([0.35, 0.35, 0.3, 0.08])
        start_button = Button(start_ax, "측정 시작")
        start_button.on_clicked(lambda event: self._run_compare())
        self._widgets.append(start_button)

        menu_ax = self.fig.add_axes([0.35, 0.2, 0.3, 0.08])
        menu_button = Button(menu_ax, "메뉴로")
        menu_button.on_clicked(lambda event: self.show_menu())
        self._widgets.append(menu_button)

        self.fig.canvas.draw_idle()

    def _run_compare(self):
        self.array_size = int(self.compare_size_slider.val)
        array = metrics.generate_array(self.array_size)
        result = metrics.run_comparison(array)
        self.show_compare_result(result)

    def show_compare_result(self, result):
        self._clear_figure()
        self.fig.suptitle(f"성능 비교 결과 (배열 크기: {self.array_size})", fontsize=14)

        ax_comparisons = self.fig.add_axes([0.08, 0.2, 0.4, 0.6])
        ax_time = self.fig.add_axes([0.55, 0.2, 0.4, 0.6])

        names = list(result.keys())
        comparisons = [result[name]["comparisons"] for name in names]
        elapsed_ms = [result[name]["elapsed_time"] * 1000 for name in names]

        bars1 = ax_comparisons.bar(names, comparisons, color="steelblue")
        ax_comparisons.set_title("비교 횟수")
        ax_comparisons.tick_params(axis="x", rotation=30)
        for bar, value in zip(bars1, comparisons):
            ax_comparisons.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height(),
                str(value), ha="center", va="bottom",
            )

        bars2 = ax_time.bar(names, elapsed_ms, color="indianred")
        ax_time.set_title("실행 시간 (ms)")
        ax_time.tick_params(axis="x", rotation=30)
        for bar, value in zip(bars2, elapsed_ms):
            ax_time.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{value:.2f}", ha="center", va="bottom",
            )

        menu_ax = self.fig.add_axes([0.4, 0.02, 0.2, 0.06])
        menu_button = Button(menu_ax, "메뉴로")
        menu_button.on_clicked(lambda event: self.show_menu())
        self._widgets.append(menu_button)

        self.fig.canvas.draw_idle()
