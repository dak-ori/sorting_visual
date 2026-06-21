# 정렬 알고리즘 비교 시각화 프로그램

Python과 matplotlib을 이용해 6종 정렬 알고리즘의 동작 과정을 실시간
막대그래프 애니메이션으로 보여주고, 동일한 입력에 대한 성능(비교 횟수,
실행 시간)을 한 장의 차트로 비교하는 프로그램입니다.

## 1. 주제 선정 이유, 설명 및 개발 방법

### 주제 선정 이유

자료구조 수업에서 정렬 알고리즘을 O(n²), O(n log n) 같은 시간복잡도
표기법으로만 배우다 보니, 알고리즘 간 실제 성능 차이가 잘 체감되지
않았습니다. 정렬이 진행되는 과정을 한 단계씩 직접 눈으로 보고 비교·교환
횟수를 실시간으로 확인할 수 있다면, 동작 원리뿐 아니라 시간복잡도 차이를
훨씬 직관적으로 이해할 수 있겠다고 생각해 이 주제를 선택했습니다. 또한
서로 다른 6가지 정렬 알고리즘을 같은 인터페이스로 구현해보면서, 같은
문제(정렬)를 푸는 여러 알고리즘의 설계 방식이 어떻게 다른지 비교해볼 수
있다는 점도 흥미로웠습니다.

### 프로그램 설명

이 프로그램은 버블/선택/삽입/병합/퀵/힙 정렬 6종을 막대그래프
애니메이션으로 시각화합니다. 비교 중인 원소는 빨강, 교환/이동 중인
원소는 초록, 정렬이 확정된 원소는 진한 파랑으로 색이 바뀌며, 화면
상단에는 비교 횟수·배열 접근 횟수·경과 시간이 실시간으로 표시됩니다.
"전체 성능 비교" 기능을 사용하면 동일한 무작위 배열을 6개 알고리즘에
똑같이 적용해 비교 횟수와 실행 시간을 막대그래프로 나란히 비교할 수
있어, O(n²)와 O(n log n)의 차이를 수치로 직접 확인할 수 있습니다.

### 개발 방법

1. **요구사항 정리 → 설계 문서 → 구현 계획 → TDD 구현** 순서로
   진행했습니다. 막연히 코드를 먼저 작성하지 않고, 화면 흐름(메뉴 →
   시각화/비교)과 모듈 책임을 먼저 문서로 정리한 뒤 구현에 들어갔습니다.
2. **모듈 분리**: 정렬 알고리즘(`algorithms.py`)은 matplotlib을 전혀
   모르고, 시각화(`visualizer.py`)는 어떤 알고리즘이 들어오는지 모르는
   구조로 설계했습니다. 모든 정렬 함수가 `yield 배열 스냅샷, info 딕셔너리`
   라는 동일한 인터페이스를 따르기 때문에, 시각화 코드를 한 번만 작성해도
   6개 알고리즘 모두에 그대로 재사용됩니다.
3. **TDD(테스트 주도 개발)**: 기능을 추가할 때마다 먼저 실패하는 pytest
   테스트를 작성하고(RED), 테스트를 통과시키는 최소 코드를 작성한 뒤(GREEN)
   다음 기능으로 넘어가는 방식을 모든 모듈에 적용했습니다. 최종적으로
   65개의 단위/통합 테스트가 작성되었습니다.
4. **개발 환경**: 의존성 충돌을 피하기 위해 Miniconda로 `sorting_visual`
   가상환경을 분리했고, matplotlib·numpy 외의 외부 의존성은 추가하지
   않았습니다.
5. **TDD로 잡아낸 실제 버그 2건**: 삽입 정렬과 병합 정렬은 원래 값을
   배열 밖으로 잠시 빼두는 표준적인 구현 방식을 따랐는데, 이 경우
   애니메이션 중간 프레임에서 값이 일시적으로 중복되어 보이는 문제가
   "스냅샷은 항상 원본과 같은 원소 구성을 유지해야 한다"는 테스트에서
   발견되었습니다. 인접 원소를 직접 교환하는 방식으로 바꿔 해결했습니다.
   또한 matplotlib 애니메이션이 끝까지 재생된 뒤 "메뉴로" 버튼을 누르면
   내부 상태(`event_source`)가 `None`이 되어 있어 `AttributeError`가
   발생하는 버그도 재현 테스트를 먼저 작성해 고정한 뒤 수정했습니다.
6. **형상 관리**: 기능 단위로 git 커밋을 나누어, 각 단계에서 무엇을
   왜 바꿨는지 추적할 수 있게 했습니다.

## 2. 개발 소스

### 파일 구조

| 파일 | 역할 |
|---|---|
| `main.py` | 프로그램 진입점. 한글 폰트 설정 후 시각화 클래스를 실행 |
| `algorithms.py` | 6개 정렬 알고리즘을 제너레이터로 구현 (matplotlib 의존 없음) |
| `visualizer.py` | `SortVisualizer` 클래스. 메뉴/시각화/비교 화면 전환과 애니메이션 담당 |
| `metrics.py` | 6개 알고리즘을 동일 입력으로 실행해 성능을 비교 측정 |
| `font_utils.py` | OS(Windows/Mac/Linux)별 한글 폰트 자동 감지 및 설정 |
| `tests/` | pytest 단위·통합 테스트 (총 65개) |

아래는 각 파일의 전체 소스 코드입니다.

### `main.py`

```python
"""정렬 알고리즘 비교 시각화 프로그램의 진입점.

실행: python main.py
"""
from font_utils import setup_korean_font
from visualizer import SortVisualizer


def main():
    setup_korean_font()
    visualizer = SortVisualizer()
    visualizer.run()


if __name__ == "__main__":
    main()
```

### `font_utils.py`

```python
"""OS에 맞는 한글 폰트를 자동으로 감지해서 matplotlib에 적용하는 모듈."""
import platform

import matplotlib
import matplotlib.font_manager as fm

# Linux에서 나눔고딕이 없을 때 차례로 시도해 볼 한글 폰트 키워드
_LINUX_FALLBACK_KEYWORDS = ("Nanum", "Noto Sans CJK", "Noto Sans KR", "UnDotum", "UnBatang")


def detect_korean_font():
    """현재 OS에 맞는 한글 폰트 이름을 반환한다. 찾지 못하면 None을 반환한다."""
    system = platform.system()
    if system == "Windows":
        return "Malgun Gothic"
    if system == "Darwin":
        return "AppleGothic"

    # Linux: 나눔고딕을 우선 시도하고, 없으면 설치된 폰트 중 한글 폰트로
    # 흔히 쓰이는 이름이 포함된 것을 탐색한다.
    installed = {f.name for f in fm.fontManager.ttflist}
    if "NanumGothic" in installed:
        return "NanumGothic"
    for keyword in _LINUX_FALLBACK_KEYWORDS:
        for name in installed:
            if keyword in name:
                return name
    return None


def setup_korean_font():
    """matplotlib에 한글 폰트를 적용한다.

    적합한 한글 폰트를 찾지 못하면 경고만 출력하고 기본 폰트를 유지한다
    (한글이 깨지더라도 프로그램 실행 자체는 막지 않는다).
    """
    font_name = detect_korean_font()
    if font_name is None:
        print("[경고] 한글 폰트를 찾을 수 없습니다. 그래프의 한글이 깨질 수 있습니다.")
    else:
        matplotlib.rcParams["font.family"] = font_name
    # 한글 폰트 사용 시 마이너스 기호가 깨지는 문제 방지
    matplotlib.rcParams["axes.unicode_minus"] = False
```

### `algorithms.py`

```python
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


def quick_sort(array):
    """퀵 정렬 (Lomuto partition, 마지막 원소를 피벗으로 사용).

    피벗을 하나 골라 피벗보다 작은 값은 왼쪽, 큰 값은 오른쪽으로
    나누는 분할(partition)을 수행한 뒤, 분할된 양쪽 구간을 재귀적으로
    정렬한다. 분할이 끝나면 피벗은 항상 자기 자리에 확정되므로 그
    인덱스를 즉시 sorted_indices에 추가한다. 평균적으로 양쪽을 절반씩
    나누어 O(n log n)이지만, 이미 정렬되었거나 역순인 배열에서는 매번
    한쪽 구간이 비어버려 O(n^2)까지 느려질 수 있다.

    시간복잡도: 평균 O(n log n), 최악 O(n^2)
    공간복잡도: O(log n) (재귀 호출 스택, 평균적인 경우)
    안정 정렬: 아니오
    """
    arr = list(array)
    n = len(arr)
    state = {"comparisons": 0, "array_accesses": 0}
    sorted_indices = set()

    def make_info(comparing=None, swapping=None):
        return {
            "comparing": comparing,
            "swapping": swapping,
            "sorted_indices": set(sorted_indices),
            "comparisons": state["comparisons"],
            "array_accesses": state["array_accesses"],
        }

    def partition(low, high):
        # arr[high]를 피벗으로 삼아, 피벗보다 작은 값들을 앞쪽
        # (store_idx 이전)으로 모은다. 피벗의 최종 위치를 반환한다.
        pivot = arr[high]
        store_idx = low
        for i in range(low, high):
            state["comparisons"] += 1
            yield list(arr), make_info(comparing=(i, high))
            if arr[i] < pivot:
                if i != store_idx:
                    arr[i], arr[store_idx] = arr[store_idx], arr[i]
                    state["array_accesses"] += 2
                    yield list(arr), make_info(swapping=(i, store_idx))
                store_idx += 1
        if store_idx != high:
            arr[store_idx], arr[high] = arr[high], arr[store_idx]
            state["array_accesses"] += 2
            yield list(arr), make_info(swapping=(store_idx, high))
        sorted_indices.add(store_idx)
        return store_idx

    def quick_sort_recursive(low, high):
        if low >= high:
            if low == high:
                sorted_indices.add(low)
            return
        pivot_idx = yield from partition(low, high)
        yield from quick_sort_recursive(low, pivot_idx - 1)
        yield from quick_sort_recursive(pivot_idx + 1, high)

    if n == 0:
        yield list(arr), make_info()
        return

    yield from quick_sort_recursive(0, n - 1)

    sorted_indices.update(range(n))
    yield list(arr), make_info()


def heap_sort(array):
    """힙 정렬.

    배열 전체를 최대 힙(부모가 항상 자식보다 큰 이진 트리)으로 만든 뒤,
    힙의 루트(=배열의 최댓값)를 배열 맨 끝과 교환해서 정렬 확정시키고,
    힙의 크기를 1 줄여서 같은 과정을 반복한다. 힙을 만드는 과정과
    원소 하나를 제거한 뒤 힙 속성을 복구하는 과정(heapify, sift-down)이
    모두 O(log n)이고, 이를 n번 반복하므로 입력 상태와 무관하게 항상
    O(n log n)이다.

    시간복잡도: 최선/평균/최악 O(n log n)
    공간복잡도: O(1) (배열 내부에서 힙을 구성, 추가 배열 불필요)
    안정 정렬: 아니오
    """
    arr = list(array)
    n = len(arr)
    state = {"comparisons": 0, "array_accesses": 0}
    sorted_indices = set()

    def make_info(comparing=None, swapping=None):
        return {
            "comparing": comparing,
            "swapping": swapping,
            "sorted_indices": set(sorted_indices),
            "comparisons": state["comparisons"],
            "array_accesses": state["array_accesses"],
        }

    def heapify(heap_size, root):
        # root를 기준으로 두 자식 중 더 큰 값을 찾아, root보다 크면
        # 자리를 바꾸고(sift-down) 그 아래에서 같은 과정을 재귀로 반복한다.
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2

        if left < heap_size:
            state["comparisons"] += 1
            yield list(arr), make_info(comparing=(left, largest))
            if arr[left] > arr[largest]:
                largest = left
        if right < heap_size:
            state["comparisons"] += 1
            yield list(arr), make_info(comparing=(right, largest))
            if arr[right] > arr[largest]:
                largest = right

        if largest != root:
            arr[root], arr[largest] = arr[largest], arr[root]
            state["array_accesses"] += 2
            yield list(arr), make_info(swapping=(root, largest))
            yield from heapify(heap_size, largest)

    if n == 0:
        yield list(arr), make_info()
        return

    # 1단계: 배열 전체를 최대 힙으로 구성한다 (마지막 내부 노드부터 거꾸로)
    for root in range(n // 2 - 1, -1, -1):
        yield from heapify(n, root)

    # 2단계: 루트(최댓값)를 맨 끝으로 보내고 힙 크기를 줄여가며 반복한다
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        state["array_accesses"] += 2
        yield list(arr), make_info(swapping=(0, end))
        sorted_indices.add(end)
        yield from heapify(end, 0)

    sorted_indices.add(0)
    yield list(arr), make_info()


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
```

### `metrics.py`

```python
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
```

### `visualizer.py`

```python
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
MIN_SPEED, MAX_SPEED, DEFAULT_SPEED = 0.25, 10.0, 1.0


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
    """속도 배수(0.25x~10x)를 matplotlib FuncAnimation의 interval(ms)로
    변환한다. 속도가 빠를수록 프레임 간 간격은 짧아진다."""
    if speed <= 0:
        raise ValueError("speed는 0보다 커야 합니다")
    return BASE_INTERVAL_MS / speed


def speed_to_frame_step(speed):
    """속도 배수를 "몇 프레임마다 하나씩 그릴지" 나타내는 정수로 변환한다.

    interval만 줄이면 matplotlib이 매 프레임을 실제로 다시 그리는
    시간(렌더링 오버헤드) 때문에 체감 속도가 한계에 부딪힌다. 특히
    배열 크기가 클 때 O(n^2) 알고리즘은 프레임 수가 수천 개에 달해
    interval 조절만으로는 충분히 빨라지지 않는다. 그래서 1.0x를
    넘는 속도에서는 일부 프레임을 건너뛰어(skip) 실제로 그리는
    프레임 수 자체를 줄인다 (1.0x 이하에서는 모든 프레임을 그대로
    보여줘 기존 동작을 그대로 유지한다).
    """
    if speed <= 0:
        raise ValueError("speed는 0보다 커야 합니다")
    return max(1, round(speed))


def skip_frames(frames, step):
    """frames에서 step개마다 하나씩만 골라 yield하되, 마지막 프레임은
    step에 맞지 않아도 항상 포함한다 (빠르게 재생하더라도 정렬이
    완료된 최종 상태는 반드시 보여주기 위함). matplotlib에 의존하지
    않는 순수 함수라서 GUI 없이도 단위 테스트가 가능하다."""
    last = None
    last_was_yielded = False
    for i, frame in enumerate(frames):
        last = frame
        last_was_yielded = (i % step == 0)
        if last_was_yielded:
            yield frame
    if last is not None and not last_was_yielded:
        yield last


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
        # 전환된 뒤에도 백그라운드에서 계속 갱신을 시도할 수 있다).
        # 애니메이션이 이미 끝까지 다 돌았다면(repeat=False) matplotlib이
        # event_source를 자체적으로 None으로 바꿔두므로, 멈출 대상이
        # 없는 경우를 별도로 처리한다.
        if self._animation is not None:
            if self._animation.event_source is not None:
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

        self._animation = FuncAnimation(
            self.fig,
            self._animate,
            frames=self._build_frame_source(),
            interval=speed_to_interval(self.speed),
            repeat=False,
            cache_frame_data=False,
        )
        self.fig.canvas.draw_idle()

    def _build_frame_source(self):
        # 속도가 1.0x를 넘으면 일부 프레임을 건너뛰어 큰 배열에서도
        # 체감 속도가 충분히 빨라지도록 한다.
        generator = metrics.ALGORITHMS[self._algorithm_name](self.current_array)
        step = speed_to_frame_step(self.speed)
        return skip_frames(generator, step)

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
        # 애니메이션이 이미 끝까지 다 돌았다면 event_source가 None이라
        # 멈추거나 다시 시작할 대상이 없다 (_clear_figure와 같은 이유).
        if self._animation is not None and self._animation.event_source is not None:
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
```

## 스크린샷

> 아래 자리에 실행 화면 스크린샷을 추가하세요.

| 메뉴 화면 | 시각화 화면 | 성능 비교 결과 |
|---|---|---|
| ![menu](docs/screenshots/menu.png) | ![sort](docs/screenshots/sort.png) | ![compare](docs/screenshots/compare.png) |

## 실행 방법

```bash
conda create -n sorting_visual python=3.11 -y
conda activate sorting_visual
pip install -r requirements.txt
python main.py
```

## 사용법

1. 프로그램을 실행하면 메뉴 화면에서 6개 알고리즘 버튼과 "전체 성능
   비교" 버튼을 볼 수 있습니다.
2. 알고리즘 버튼을 누르면 무작위로 섞인 막대그래프가 나타나고, 정렬
   과정이 실시간으로 애니메이션됩니다.
   - 빨강: 비교 중인 원소
   - 초록: 교환/이동 중인 원소
   - 진한 파랑: 정렬이 확정된 원소
   - 화면 상단에 비교 횟수, 배열 접근 횟수, 경과 시간이 실시간으로
     표시됩니다.
   - 슬라이더로 배열 크기와 애니메이션 속도를 조절한 뒤 "재시작"을
     누르면 새 설정으로 다시 시작합니다.
   - "일시정지"/"메뉴로" 버튼으로 애니메이션을 멈추거나 메뉴로 돌아갈
     수 있습니다.
3. "전체 성능 비교"를 누르면 배열 크기를 정한 뒤 "측정 시작"으로 6개
   알고리즘을 한꺼번에(애니메이션 없이) 실행하고, 비교 횟수와 실행
   시간(ms)을 막대그래프 두 장으로 비교해서 보여줍니다.

## 알고리즘별 복잡도

| 알고리즘 | 최선 | 평균 | 최악 | 공간복잡도 | 안정 정렬 |
|---|---|---|---|---|---|
| 버블 정렬 | O(n) | O(n²) | O(n²) | O(1) | 예 |
| 선택 정렬 | O(n²) | O(n²) | O(n²) | O(1) | 아니오 |
| 삽입 정렬 | O(n) | O(n²) | O(n²) | O(1) | 예 |
| 병합 정렬 | O(n log n) | O(n log n) | O(n log n) | O(n) | 예 |
| 퀵 정렬 | O(n log n) | O(n log n) | O(n²) | O(log n) | 아니오 |
| 힙 정렬 | O(n log n) | O(n log n) | O(n log n) | O(1) | 아니오 |

"전체 성능 비교" 기능으로 배열 크기를 키워가며 실행해보면, O(n²)
알고리즘(버블/선택/삽입)의 비교 횟수와 실행 시간이 O(n log n)
알고리즘(병합/퀵/힙)보다 훨씬 빠르게 증가하는 것을 수치로 확인할 수
있습니다.

## 프로젝트 구조

```
sorting_visual/
├── main.py            # 진입점
├── algorithms.py      # 6개 정렬 알고리즘 (제너레이터)
├── visualizer.py       # 애니메이션·위젯·화면 전환 담당
├── metrics.py          # 성능 비교 실행 및 결과 집계
├── font_utils.py        # OS별 한글 폰트 자동 설정
└── tests/               # pytest 테스트
```

## 테스트

```bash
pip install -r requirements-dev.txt
pytest -v
```
