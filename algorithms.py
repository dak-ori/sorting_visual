"""6종 정렬 알고리즘을 제너레이터로 구현한 모듈.

모든 함수는 동일한 인터페이스를 따른다:
    yield 현재 배열 스냅샷(list), info 딕셔너리

info 딕셔너리 키:
    comparing      : 비교 중인 인덱스 튜플(보통 길이 2) 또는 None
    swapping       : 교환/이동/일괄 쓰기 중인 인덱스 튜플 또는 None
                     (대부분 길이 2의 swap이지만, 병합 정렬의 병합
                     완료 프레임처럼 구간 전체를 한 번에 쓰는 경우
                     더 긴 인덱스 튜플일 수 있다)
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


def insertion_sort(array):
    """삽입 정렬 (인접 교환 방식).

    앞쪽부터 "정렬된 부분"을 유지하면서, 그 다음 원소를 정렬된 부분의
    알맞은 위치까지 바로 앞 원소와 인접 교환(swap)을 반복해 끼워 넣는다.
    원소를 배열 밖으로 잠시 빼내는 대신 항상 교환으로만 이동시키므로,
    중간 과정의 모든 스냅샷이 원본과 같은 원소 구성을 유지한다(시각화에
    유리함). 이미 정렬에 가까운 배열일수록 비교/교환 횟수가 급격히
    줄어드는 것이 특징이다(최선 O(n)).

    시간복잡도: 최선 O(n), 평균/최악 O(n^2)
    공간복잡도: O(1)
    안정 정렬: 예
    """
    arr = list(array)
    n = len(arr)
    comparisons = 0
    array_accesses = 0

    if n > 0:
        yield list(arr), {
            "comparing": None, "swapping": None,
            "sorted_indices": {0}, "comparisons": 0, "array_accesses": 0,
        }

    for i in range(1, n):
        j = i
        while j > 0:
            comparisons += 1
            yield list(arr), {
                "comparing": (j - 1, j), "swapping": None,
                "sorted_indices": set(range(i)),
                "comparisons": comparisons, "array_accesses": array_accesses,
            }
            if arr[j - 1] > arr[j]:
                arr[j - 1], arr[j] = arr[j], arr[j - 1]
                array_accesses += 2
                yield list(arr), {
                    "comparing": None, "swapping": (j - 1, j),
                    "sorted_indices": set(range(i)),
                    "comparisons": comparisons, "array_accesses": array_accesses,
                }
                j -= 1
            else:
                break

    yield list(arr), {
        "comparing": None, "swapping": None,
        "sorted_indices": set(range(n)),
        "comparisons": comparisons, "array_accesses": array_accesses,
    }


def merge_sort(array):
    """병합 정렬.

    배열을 반으로 쪼개는(분할) 과정을 재귀로 반복해 더 이상 쪼갤 수 없는
    크기 1 구간까지 내려간 뒤, 정렬된 두 구간을 합치는(병합) 과정을
    거꾸로 거쳐 올라온다. 분할정복 특성상 같은 인덱스가 여러 레벨에서
    반복적으로 덮어써지므로, 다른 알고리즘과 달리 "정렬 확정 영역"이
    점진적으로 늘어나지 않고 최상위 병합이 끝나는 순간 한 번에 확정된다.
    항상 O(n log n)을 보장하지만 병합 과정에서 임시 리스트가 필요하다.

    시간복잡도: 최선/평균/최악 O(n log n)
    공간복잡도: O(n) (병합용 임시 리스트)
    안정 정렬: 예
    """
    arr = list(array)
    n = len(arr)
    state = {"comparisons": 0, "array_accesses": 0}

    def make_info(comparing=None, swapping=None, sorted_indices=()):
        return {
            "comparing": comparing,
            "swapping": swapping,
            "sorted_indices": set(sorted_indices),
            "comparisons": state["comparisons"],
            "array_accesses": state["array_accesses"],
        }

    def merge(left, mid, right):
        # 정렬된 두 구간 [left, mid]와 [mid+1, right]를 하나의 정렬된
        # 구간으로 합친다. 비교 단계에서는 원본 값을 그대로 보여주고,
        # 병합이 끝나면 갱신된 구간 전체를 한 프레임으로 보여준다. (한
        # 칸씩 되돌려 쓰는 중간 과정을 그대로 yield하면, 아직 옮기지
        # 않은 원본 값과 새로 옮긴 값이 같은 자리에 겹쳐 보이는 시점이
        # 생겨 "스냅샷은 항상 원본과 같은 원소 구성을 유지해야 한다"는
        # 불변조건이 깨진다.)
        merged = []
        i, j = left, mid + 1
        while i <= mid and j <= right:
            state["comparisons"] += 1
            yield list(arr), make_info(comparing=(i, j))
            if arr[i] <= arr[j]:
                merged.append(arr[i])
                i += 1
            else:
                merged.append(arr[j])
                j += 1
        # 한쪽이 먼저 끝나면 남은 쪽은 비교 없이 그대로 이어붙인다
        while i <= mid:
            merged.append(arr[i])
            i += 1
        while j <= right:
            merged.append(arr[j])
            j += 1

        for offset, value in enumerate(merged):
            arr[left + offset] = value
        state["array_accesses"] += len(merged)
        yield list(arr), make_info(swapping=tuple(range(left, right + 1)))

    def sort_range(left, right):
        # [left, right] 구간을 분할정복으로 정렬한다.
        if left >= right:
            return
        mid = (left + right) // 2
        yield from sort_range(left, mid)
        yield from sort_range(mid + 1, right)
        yield from merge(left, mid, right)

    if n == 0:
        yield list(arr), make_info()
        return

    yield from sort_range(0, n - 1)

    yield list(arr), make_info(sorted_indices=range(n))


def selection_sort(array):
    """선택 정렬.

    정렬되지 않은 영역 전체를 훑어 최솟값의 인덱스를 찾고, 그 값을
    정렬되지 않은 영역의 맨 앞으로 보내는 과정을 반복한다. 매 패스마다
    정렬 확정 영역이 앞에서부터 늘어난다. 비교 횟수는 입력 상태와
    무관하게 항상 일정하지만(O(n^2)), 교환은 패스당 최대 1번만 일어나
    버블 정렬보다 array_accesses가 훨씬 적다.

    시간복잡도: 최선/평균/최악 O(n^2)
    공간복잡도: O(1)
    안정 정렬: 아니오 (최솟값을 멀리서 가져와 끼워넣으면서 순서가 바뀔 수 있음)
    """
    arr = list(array)
    n = len(arr)
    comparisons = 0
    array_accesses = 0
    sorted_indices = set()

    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            yield list(arr), {
                "comparing": (min_idx, j), "swapping": None,
                "sorted_indices": set(sorted_indices),
                "comparisons": comparisons, "array_accesses": array_accesses,
            }
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            array_accesses += 2
            yield list(arr), {
                "comparing": None, "swapping": (i, min_idx),
                "sorted_indices": set(sorted_indices),
                "comparisons": comparisons, "array_accesses": array_accesses,
            }
        sorted_indices.add(i)

    yield list(arr), {
        "comparing": None, "swapping": None,
        "sorted_indices": set(sorted_indices),
        "comparisons": comparisons, "array_accesses": array_accesses,
    }
