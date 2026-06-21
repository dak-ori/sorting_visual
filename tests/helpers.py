"""정렬 제너레이터 테스트를 위한 공용 헬퍼 함수 모음."""


def drain(generator):
    """제너레이터를 끝까지 소비하면서 모든 (array, info) 프레임을 리스트로 모은다."""
    frames = []
    for array, info in generator:
        frames.append((list(array), dict(info)))
    return frames


def assert_valid_trace(frames, original):
    """모든 정렬 제너레이터가 지켜야 할 공통 불변조건을 검증한다.

    - 매 프레임은 정해진 키를 가진 info 딕셔너리를 동반해야 한다.
    - comparisons/array_accesses는 단조 비감소해야 한다.
    - 매 프레임의 배열은 원본과 같은 원소 구성을 유지해야 한다.
    - 마지막 프레임의 배열은 정렬되어 있어야 하고, 모든 인덱스가
      sorted_indices에 포함되어야 한다.
    """
    assert len(frames) > 0, "제너레이터가 최소 1개 프레임은 yield해야 한다"

    required_keys = {
        "comparing", "swapping", "sorted_indices",
        "comparisons", "array_accesses",
    }
    prev_comparisons = -1
    prev_accesses = -1
    for array, info in frames:
        assert required_keys.issubset(info.keys()), f"info 키 누락: {info.keys()}"
        assert info["comparisons"] >= prev_comparisons, "comparisons는 단조 비감소해야 한다"
        assert info["array_accesses"] >= prev_accesses, "array_accesses는 단조 비감소해야 한다"
        prev_comparisons = info["comparisons"]
        prev_accesses = info["array_accesses"]
        assert sorted(array) == sorted(original), "정렬 도중 원소가 사라지거나 추가되면 안 된다"

    final_array, final_info = frames[-1]
    assert final_array == sorted(original), "마지막 프레임의 배열은 정렬된 상태여야 한다"
    assert set(final_info["sorted_indices"]) == set(range(len(original))), (
        "마지막 프레임에서는 모든 인덱스가 sorted_indices에 포함되어야 한다"
    )
