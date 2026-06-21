"""6개 정렬 알고리즘 제너레이터의 정확성과 측정값을 검증한다."""
from algorithms import bubble_sort, selection_sort
from tests.helpers import drain, assert_valid_trace


def test_bubble_sort_sorts_and_tracks_metrics():
    original = [5, 2, 4, 1, 3]
    frames = drain(bubble_sort(original))
    assert_valid_trace(frames, original)
    # 버블 정렬은 인접 비교만 하므로 최소 1회 이상 비교가 발생해야 한다
    assert frames[-1][1]["comparisons"] > 0


def test_bubble_sort_empty_array():
    frames = drain(bubble_sort([]))
    assert_valid_trace(frames, [])


def test_bubble_sort_single_element():
    frames = drain(bubble_sort([42]))
    assert_valid_trace(frames, [42])


def test_bubble_sort_already_sorted_has_fewer_swaps_than_reversed():
    sorted_input = [1, 2, 3, 4, 5]
    reversed_input = [5, 4, 3, 2, 1]
    sorted_frames = drain(bubble_sort(sorted_input))
    reversed_frames = drain(bubble_sort(reversed_input))
    assert sorted_frames[-1][1]["array_accesses"] < reversed_frames[-1][1]["array_accesses"]


def test_selection_sort_sorts_and_tracks_metrics():
    original = [5, 2, 4, 1, 3]
    frames = drain(selection_sort(original))
    assert_valid_trace(frames, original)
    assert frames[-1][1]["comparisons"] > 0


def test_selection_sort_empty_array():
    frames = drain(selection_sort([]))
    assert_valid_trace(frames, [])


def test_selection_sort_single_element():
    frames = drain(selection_sort([42]))
    assert_valid_trace(frames, [42])
