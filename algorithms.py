"""6종 정렬 알고리즘을 제너레이터로 구현한 모듈.

모든 함수는 동일한 인터페이스를 따른다:
    yield 현재 배열 스냅샷(list), info 딕셔너리

info 딕셔너리 키:
    comparing      : 비교 중인 인덱스 튜플(길이 1~2) 또는 None
    swapping       : 교환/이동 중인 인덱스 튜플(길이 1~2) 또는 None
    sorted_indices : 정렬이 확정된 인덱스 집합(set)
    comparisons    : 누적 비교 횟수
    array_accesses : 누적 배열 쓰기(대입) 횟수
"""


def bubble_sort(array):
    """버블 정렬.

    인접한 두 원소를 비교해 더 큰 값을 뒤로 보내는 과정을 배열 끝까지
    반복한다. 한 번 순회(패스)할 때마다 가장 큰 값이 뒤쪽으로 확정되므로,
    매 패스가 끝날 때마다 정렬 확정 영역이 뒤에서부터 늘어난다.
    한 패스 동안 교환이 한 번도 없었다면 이미 정렬된 것이므로 조기 종료한다.

    시간복잡도: 최선 O(n) (조기 종료), 평균/최악 O(n^2)
    공간복잡도: O(1)
    안정 정렬: 예
    """
    arr = list(array)
    n = len(arr)
    comparisons = 0
    array_accesses = 0
    sorted_indices = set()

    if n == 0:
        yield list(arr), {
            "comparing": None, "swapping": None,
            "sorted_indices": set(), "comparisons": 0, "array_accesses": 0,
        }
        return

    for i in range(n - 1, 0, -1):
        swapped = False
        for j in range(i):
            comparisons += 1
            yield list(arr), {
                "comparing": (j, j + 1), "swapping": None,
                "sorted_indices": set(sorted_indices),
                "comparisons": comparisons, "array_accesses": array_accesses,
            }
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                array_accesses += 2
                swapped = True
                yield list(arr), {
                    "comparing": None, "swapping": (j, j + 1),
                    "sorted_indices": set(sorted_indices),
                    "comparisons": comparisons, "array_accesses": array_accesses,
                }
        sorted_indices.add(i)
        if not swapped:
            break

    sorted_indices.update(range(n))
    yield list(arr), {
        "comparing": None, "swapping": None,
        "sorted_indices": set(sorted_indices),
        "comparisons": comparisons, "array_accesses": array_accesses,
    }
