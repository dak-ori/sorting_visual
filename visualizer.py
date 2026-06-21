"""정렬 알고리즘 애니메이션과 성능 비교 화면을 matplotlib으로 그리는 모듈.

색상 규칙:
    기본            : DEFAULT_COLOR (연한 파랑)
    비교 중인 원소   : COMPARING_COLOR (빨강)
    교환/이동 중인 원소 : SWAPPING_COLOR (초록)
    정렬 완료된 원소 : SORTED_COLOR (진한 파랑)
"""

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
