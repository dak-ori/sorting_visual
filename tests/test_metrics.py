"""성능 비교 모듈(metrics.py)을 검증한다."""
import metrics


def test_algorithms_dict_has_six_entries():
    assert len(metrics.ALGORITHMS) == 6


def test_generate_array_has_no_duplicates_and_correct_size():
    array = metrics.generate_array(20)
    assert len(array) == 20
    assert len(set(array)) == 20
    assert set(array) == set(range(1, 21))


def test_run_comparison_returns_entry_per_algorithm():
    result = metrics.run_comparison([3, 1, 2])
    assert set(result.keys()) == set(metrics.ALGORITHMS.keys())
    for entry in result.values():
        assert set(entry.keys()) == {"comparisons", "array_accesses", "elapsed_time"}
        assert entry["comparisons"] > 0
        assert entry["elapsed_time"] >= 0


def test_run_comparison_does_not_mutate_input_array():
    original = [3, 1, 2]
    metrics.run_comparison(original)
    assert original == [3, 1, 2]


def test_run_comparison_uses_identical_input_for_every_algorithm():
    # 모든 알고리즘이 정확히 같은 배열을 정렬했는지는 직접 확인할 수
    # 없지만(이미 소비된 제너레이터), 정렬 알고리즘이 모두 정확하다면
    # (Task 2~7에서 검증됨) 같은 입력에 대한 비교 횟수는 알고리즘별로
    # 결정적(deterministic)이어야 한다 -> 같은 입력으로 두 번 돌리면
    # 알고리즘별 비교 횟수가 완전히 같아야 한다.
    array = [5, 3, 4, 1, 2]
    result_a = metrics.run_comparison(array)
    result_b = metrics.run_comparison(array)
    for name in metrics.ALGORITHMS:
        assert result_a[name]["comparisons"] == result_b[name]["comparisons"]
        assert result_a[name]["array_accesses"] == result_b[name]["array_accesses"]
