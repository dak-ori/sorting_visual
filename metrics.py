"""6개 정렬 알고리즘의 성능(비교 횟수, 실행 시간)을 동일한 입력으로
비교 측정하는 모듈. 애니메이션 없이 알고리즘 제너레이터를 끝까지
소비해서 마지막 프레임의 측정값만 취한다."""
import time

import numpy as np

from algorithms import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    heap_sort,
)

# 시각화 화면과 비교 화면에서 공통으로 사용하는 알고리즘 이름 -> 함수 매핑
ALGORITHMS = {
    "버블 정렬": bubble_sort,
    "선택 정렬": selection_sort,
    "삽입 정렬": insertion_sort,
    "병합 정렬": merge_sort,
    "퀵 정렬": quick_sort,
    "힙 정렬": heap_sort,
}


def generate_array(size):
    """1~size 정수를 중복 없이 무작위로 섞은 배열을 생성한다."""
    return (np.random.permutation(size) + 1).tolist()


def run_comparison(array):
    """주어진 배열의 복사본을 6개 알고리즘에 동일하게 전달해서 실행하고,
    알고리즘명 -> {comparisons, array_accesses, elapsed_time(초)} 딕셔너리를
    반환한다. 입력 array는 변경하지 않는다."""
    results = {}
    for name, algorithm in ALGORITHMS.items():
        data = list(array)
        start = time.perf_counter()
        final_info = {"comparisons": 0, "array_accesses": 0}
        for _, info in algorithm(data):
            final_info = info
        elapsed = time.perf_counter() - start
        results[name] = {
            "comparisons": final_info["comparisons"],
            "array_accesses": final_info["array_accesses"],
            "elapsed_time": elapsed,
        }
    return results
