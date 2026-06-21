"""정렬 알고리즘 애니메이션과 성능 비교 화면을 matplotlib으로 그리는 모듈.

색상 규칙:
    기본            : DEFAULT_COLOR (연한 파랑)
    비교 중인 원소   : COMPARING_COLOR (빨강)
    교환/이동 중인 원소 : SWAPPING_COLOR (초록)
    정렬 완료된 원소 : SORTED_COLOR (진한 파랑)
"""
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

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
