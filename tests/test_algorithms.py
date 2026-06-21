"""6개 정렬 알고리즘 제너레이터의 정확성과 측정값을 검증한다."""
from algorithms import bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort
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


def test_insertion_sort_sorts_and_tracks_metrics():
    original = [5, 2, 4, 1, 3]
    frames = drain(insertion_sort(original))
    assert_valid_trace(frames, original)
    assert frames[-1][1]["comparisons"] > 0


def test_insertion_sort_empty_array():
    frames = drain(insertion_sort([]))
    assert_valid_trace(frames, [])


def test_insertion_sort_single_element():
    frames = drain(insertion_sort([42]))
    assert_valid_trace(frames, [42])


def test_insertion_sort_already_sorted_has_fewer_comparisons_than_reversed():
    sorted_input = [1, 2, 3, 4, 5]
    reversed_input = [5, 4, 3, 2, 1]
    sorted_frames = drain(insertion_sort(sorted_input))
    reversed_frames = drain(insertion_sort(reversed_input))
    assert sorted_frames[-1][1]["comparisons"] < reversed_frames[-1][1]["comparisons"]


def test_merge_sort_sorts_and_tracks_metrics():
    original = [5, 2, 4, 1, 3]
    frames = drain(merge_sort(original))
    assert_valid_trace(frames, original)
    assert frames[-1][1]["comparisons"] > 0


def test_merge_sort_empty_array():
    frames = drain(merge_sort([]))
    assert_valid_trace(frames, [])


def test_merge_sort_single_element():
    frames = drain(merge_sort([42]))
    assert_valid_trace(frames, [42])


def test_merge_sort_intermediate_frames_have_empty_sorted_indices():
    # 병합 정렬은 분할정복 특성상 마지막 프레임 전까지는
    # 어떤 인덱스도 "최종 확정"되었다고 표시하지 않는다.
    frames = drain(merge_sort([5, 2, 4, 1, 3]))
    for _, info in frames[:-1]:
        assert info["sorted_indices"] == set()


def test_quick_sort_sorts_and_tracks_metrics():
    original = [5, 2, 4, 1, 3]
    frames = drain(quick_sort(original))
    assert_valid_trace(frames, original)
    assert frames[-1][1]["comparisons"] > 0


def test_quick_sort_empty_array():
    frames = drain(quick_sort([]))
    assert_valid_trace(frames, [])


def test_quick_sort_single_element():
    frames = drain(quick_sort([42]))
    assert_valid_trace(frames, [42])


def test_quick_sort_worst_case_already_sorted():
    # 마지막 원소를 피벗으로 쓰므로 이미 정렬된 입력이 최악의 경우다.
    # 그래도 결과는 정확히 정렬되어야 한다.
    original = [1, 2, 3, 4, 5]
    frames = drain(quick_sort(original))
    assert_valid_trace(frames, original)
