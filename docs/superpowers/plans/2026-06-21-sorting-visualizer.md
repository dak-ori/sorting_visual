# 정렬 알고리즘 비교 시각화 프로그램 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Python + matplotlib(+numpy)으로 6종 정렬 알고리즘을 실시간 애니메이션으로 시각화하고, 동일 입력에 대한 성능(비교 횟수, 실행 시간)을 비교 차트로 보여주는 대학 과제용 프로그램을 만든다.

**Architecture:** 알고리즘(`algorithms.py`)은 matplotlib을 모르는 순수 제너레이터로 구현하고, 시각화(`visualizer.py`)는 알고리즘 종류를 모르는 공통 yield 인터페이스만 소비한다. 성능 비교(`metrics.py`)는 같은 알고리즘 제너레이터를 애니메이션 없이 소비해서 재사용한다. `main.py`가 이 세 모듈을 엮는다.

**Tech Stack:** Python 3, matplotlib (FuncAnimation, widgets.Slider/Button), numpy, pytest

참고 설계 문서: `docs/superpowers/specs/2026-06-21-sorting-visualizer-design.md`

## Global Constraints

- Python 3, matplotlib, numpy만 사용 (외부 의존성 추가 금지)
- 6개 정렬 알고리즘(`bubble_sort`, `selection_sort`, `insertion_sort`, `merge_sort`, `quick_sort`, `heap_sort`)은 모두 제너레이터로 구현하고, 동일한 `yield array.copy_or_list(), info_dict` 인터페이스를 따른다 (`info_dict` 키: `comparing`, `swapping`, `sorted_indices`, `comparisons`, `array_accesses`)
- `comparing`/`swapping` 값은 인덱스 튜플 또는 `None` (대부분 길이 2이지만, 병합 정렬의 병합 완료 프레임처럼 구간 전체를 한 번에 쓰는 경우 더 긴 튜플일 수 있다 — Task 5에서 구체적인 이유 설명)
- `array_accesses`는 "배열에 값을 쓴 횟수"로 통일 (swap 1회 = 2, 단일 대입 1회 = 1)
- 각 알고리즘 함수에는 동작 원리를 설명하는 한글 docstring, 핵심 분기에는 한글 인라인 주석 필수
- 모듈 분리: `algorithms.py` / `visualizer.py` / `metrics.py` / `font_utils.py` / `main.py` (역할 분리는 설계 문서 2절 참조)
- 비교 모드(`metrics.run_comparison`)는 애니메이션 없이 제너레이터를 끝까지 소비해서 측정값만 얻는다
- 비교 모드는 동일한 배열(같은 값, 같은 순서)을 6개 알고리즘에 각각 복사해서 전달해야 한다
- 한글 폰트는 OS(Windows/Darwin/Linux) 자동 감지로 설정하고, 못 찾아도 프로그램이 멈추지 않아야 한다
- 테스트는 pytest로 작성하고, matplotlib GUI 의존 코드는 `matplotlib.use("Agg")` 헤드리스 백엔드로 테스트한다

---

## Task 1: 프로젝트 스캐폴딩 & 테스트 인프라

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `pytest.ini`
- Create: `tests/__init__.py`
- Create: `tests/helpers.py`
- Test: 이 태스크 자체가 다음 태스크들이 사용할 테스트 헬퍼를 만드는 단계 (헬퍼의 동작은 Task 2에서 실제로 검증됨)

**Interfaces:**
- Produces: `tests/helpers.py`의 `drain(generator) -> list[tuple[list, dict]]`, `assert_valid_trace(frames, original) -> None` — 이후 모든 알고리즘 테스트(Task 2~7)가 이 두 함수를 사용한다.

- [ ] **Step 1: 의존성 파일 작성**

`requirements.txt`:
```
matplotlib
numpy
```

`requirements-dev.txt`:
```
-r requirements.txt
pytest
```

- [ ] **Step 2: pytest 설정 작성**

`pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
```

- [ ] **Step 3: 가상환경 준비 및 의존성 설치**

Run: `conda create -n sorting_visual python=3.11 -y && conda run -n sorting_visual pip install -r requirements-dev.txt`
Expected: matplotlib, numpy, pytest가 설치됨 (이후 모든 Run 명령은 `conda run -n sorting_visual <command>`로 실행한다)

- [ ] **Step 4: 테스트 헬퍼 작성**

`tests/__init__.py`:
```python
```

`tests/helpers.py`:
```python
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
```

- [ ] **Step 5: 커밋**

```bash
git add requirements.txt requirements-dev.txt pytest.ini tests/__init__.py tests/helpers.py
git commit -m "test: 프로젝트 스캐폴딩 및 정렬 제너레이터 테스트 헬퍼 추가"
```

---

## Task 2: 버블 정렬 (`algorithms.py` 생성 + `bubble_sort`)

**Files:**
- Create: `algorithms.py`
- Test: `tests/test_algorithms.py`

**Interfaces:**
- Consumes: `tests/helpers.py`의 `drain`, `assert_valid_trace` (Task 1)
- Produces: `algorithms.py`의 `bubble_sort(array) -> Generator[tuple[list, dict], None, None]` — Task 9(metrics)와 Task 12(visualizer)가 이 함수를 이름으로 가져다 쓴다. 이후 5개 알고리즘(Task 3~7)도 동일한 시그니처를 갖는다.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_algorithms.py`:
```python
"""6개 정렬 알고리즘 제너레이터의 정확성과 측정값을 검증한다."""
from algorithms import bubble_sort
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
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `conda run -n sorting_visual pytest tests/test_algorithms.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'algorithms'`

- [ ] **Step 3: `bubble_sort` 구현**

`algorithms.py`:
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
```

- [ ] **Step 4: 테스트 실행해서 통과 확인**

Run: `conda run -n sorting_visual pytest tests/test_algorithms.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: 커밋**

```bash
git add algorithms.py tests/test_algorithms.py
git commit -m "feat: 버블 정렬 제너레이터 구현"
```

---

## Task 3: 선택 정렬 (`selection_sort`)

**Files:**
- Modify: `algorithms.py` (append)
- Modify: `tests/test_algorithms.py` (append)

**Interfaces:**
- Consumes: `tests/helpers.py`의 `drain`, `assert_valid_trace`
- Produces: `algorithms.py`의 `selection_sort(array)` — Task 2와 동일한 시그니처

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_algorithms.py`에 추가:
```python
from algorithms import selection_sort


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
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `conda run -n sorting_visual pytest tests/test_algorithms.py -v -k selection`
Expected: FAIL with `ImportError: cannot import name 'selection_sort'`

- [ ] **Step 3: `selection_sort` 구현**

`algorithms.py`에 추가:
```python
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

- [ ] **Step 4: 테스트 실행해서 통과 확인**

Run: `conda run -n sorting_visual pytest tests/test_algorithms.py -v -k selection`
Expected: PASS (3 passed)

- [ ] **Step 5: 커밋**

```bash
git add algorithms.py tests/test_algorithms.py
git commit -m "feat: 선택 정렬 제너레이터 구현"
```

---

## Task 4: 삽입 정렬 (`insertion_sort`)

**Files:**
- Modify: `algorithms.py` (append)
- Modify: `tests/test_algorithms.py` (append)

**Interfaces:**
- Consumes: `tests/helpers.py`의 `drain`, `assert_valid_trace`
- Produces: `algorithms.py`의 `insertion_sort(array)` — Task 2와 동일한 시그니처

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_algorithms.py`에 추가:
```python
from algorithms import insertion_sort


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
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `conda run -n sorting_visual pytest tests/test_algorithms.py -v -k insertion`
Expected: FAIL with `ImportError: cannot import name 'insertion_sort'`

- [ ] **Step 3: `insertion_sort` 구현**

`algorithms.py`에 추가:
```python
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
```

**구현 중 발견된 버그 수정:** 원래 계획은 `key`를 배열 밖 변수로 빼내는
표준 삽입 정렬 방식이었으나, 이 경우 `key`가 빠진 자리에 인접 값이
복제되어 중간 스냅샷이 일시적으로 원본과 다른 원소 구성을 갖게 되어
`assert_valid_trace`의 "원소 보존" 불변조건을 깨뜨렸다. 모든 이동을
실제 교환(swap)으로 수행하는 방식으로 수정해 항상 유효한 순열을
유지하도록 했다 (시간복잡도와 동작 특성은 동일).

- [ ] **Step 4: 테스트 실행해서 통과 확인**

Run: `conda run -n sorting_visual pytest tests/test_algorithms.py -v -k insertion`
Expected: PASS (4 passed)

- [ ] **Step 5: 커밋**

```bash
git add algorithms.py tests/test_algorithms.py
git commit -m "feat: 삽입 정렬 제너레이터 구현"
```

---

## Task 5: 병합 정렬 (`merge_sort`)

**Files:**
- Modify: `algorithms.py` (append)
- Modify: `tests/test_algorithms.py` (append)

**Interfaces:**
- Consumes: `tests/helpers.py`의 `drain`, `assert_valid_trace`
- Produces: `algorithms.py`의 `merge_sort(array)` — Task 2와 동일한 시그니처. 단, 분할정복 특성상 중간 프레임에서는 `sorted_indices`가 항상 빈 집합이고, 마지막 프레임에서만 전체 인덱스가 채워진다 (다른 알고리즘과의 차이점, Task 12에서 시각화할 때 참고).

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_algorithms.py`에 추가:
```python
from algorithms import merge_sort


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
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `conda run -n sorting_visual pytest tests/test_algorithms.py -v -k merge`
Expected: FAIL with `ImportError: cannot import name 'merge_sort'`

- [ ] **Step 3: `merge_sort` 구현**

`algorithms.py`에 추가:
```python
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
```

**구현 중 발견된 버그 수정:** 원래 계획은 병합 결과를 한 칸씩 `arr`에
되돌려 쓰면서 매번 yield하는 방식이었으나, 이 경우 아직 옮기지 않은
원본 값과 막 옮겨놓은 새 값이 같은 자리에 겹쳐 보이는(중복되는) 시점이
생겨 `assert_valid_trace`의 "원소 보존" 불변조건을 깨뜨렸다 (Task 4의
삽입 정렬과 같은 종류의 문제). 병합이 끝난 뒤 구간 전체를 한 번에
반영하는 단일 프레임으로 바꿔 수정했다. 이로 인해 `swapping` 필드가
2개를 넘는 인덱스를 담을 수 있게 되어 Global Constraints를 갱신했다.

- [ ] **Step 4: 테스트 실행해서 통과 확인**

Run: `conda run -n sorting_visual pytest tests/test_algorithms.py -v -k merge`
Expected: PASS (4 passed)

- [ ] **Step 5: 커밋**

```bash
git add algorithms.py tests/test_algorithms.py
git commit -m "feat: 병합 정렬 제너레이터 구현"
```

---

## Task 6: 퀵 정렬 (`quick_sort`)

**Files:**
- Modify: `algorithms.py` (append)
- Modify: `tests/test_algorithms.py` (append)

**Interfaces:**
- Consumes: `tests/helpers.py`의 `drain`, `assert_valid_trace`
- Produces: `algorithms.py`의 `quick_sort(array)` — Task 2와 동일한 시그니처

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_algorithms.py`에 추가:
```python
from algorithms import quick_sort


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
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `conda run -n sorting_visual pytest tests/test_algorithms.py -v -k quick`
Expected: FAIL with `ImportError: cannot import name 'quick_sort'`

- [ ] **Step 3: `quick_sort` 구현**

`algorithms.py`에 추가:
```python
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
```

- [ ] **Step 4: 테스트 실행해서 통과 확인**

Run: `conda run -n sorting_visual pytest tests/test_algorithms.py -v -k quick`
Expected: PASS (4 passed)

- [ ] **Step 5: 커밋**

```bash
git add algorithms.py tests/test_algorithms.py
git commit -m "feat: 퀵 정렬 제너레이터 구현"
```

---

## Task 7: 힙 정렬 (`heap_sort`)

**Files:**
- Modify: `algorithms.py` (append)
- Modify: `tests/test_algorithms.py` (append)

**Interfaces:**
- Consumes: `tests/helpers.py`의 `drain`, `assert_valid_trace`
- Produces: `algorithms.py`의 `heap_sort(array)` — Task 2와 동일한 시그니처. 이로써 `algorithms.py`의 6개 알고리즘이 모두 완성된다 (Task 9, 12가 이 6개를 모두 참조함).

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_algorithms.py`에 추가:
```python
from algorithms import heap_sort


def test_heap_sort_sorts_and_tracks_metrics():
    original = [5, 2, 4, 1, 3]
    frames = drain(heap_sort(original))
    assert_valid_trace(frames, original)
    assert frames[-1][1]["comparisons"] > 0


def test_heap_sort_empty_array():
    frames = drain(heap_sort([]))
    assert_valid_trace(frames, [])


def test_heap_sort_single_element():
    frames = drain(heap_sort([42]))
    assert_valid_trace(frames, [42])


def test_heap_sort_two_elements():
    frames = drain(heap_sort([2, 1]))
    assert_valid_trace(frames, [2, 1])
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `conda run -n sorting_visual pytest tests/test_algorithms.py -v -k heap`
Expected: FAIL with `ImportError: cannot import name 'heap_sort'`

- [ ] **Step 3: `heap_sort` 구현**

`algorithms.py`에 추가:
```python
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
```

- [ ] **Step 4: 테스트 실행해서 통과 확인**

Run: `conda run -n sorting_visual pytest tests/test_algorithms.py -v -k heap`
Expected: PASS (4 passed)

- [ ] **Step 5: 전체 알고리즘 테스트 한 번에 실행해서 회귀 확인**

Run: `conda run -n sorting_visual pytest tests/test_algorithms.py -v`
Expected: PASS (모든 테스트, 총 23개 통과)

- [ ] **Step 6: 커밋**

```bash
git add algorithms.py tests/test_algorithms.py
git commit -m "feat: 힙 정렬 제너레이터 구현"
```

---

## Task 8: 한글 폰트 자동 설정 (`font_utils.py`)

**Files:**
- Create: `font_utils.py`
- Test: `tests/test_font_utils.py`

**Interfaces:**
- Produces: `font_utils.py`의 `detect_korean_font() -> str | None`, `setup_korean_font() -> None` — Task 14(`main.py`)가 시작 시 `setup_korean_font()`를 호출한다.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_font_utils.py`:
```python
"""OS별 한글 폰트 자동 감지 로직을 검증한다."""
import font_utils


def test_detect_korean_font_on_windows(monkeypatch):
    monkeypatch.setattr(font_utils.platform, "system", lambda: "Windows")
    assert font_utils.detect_korean_font() == "Malgun Gothic"


def test_detect_korean_font_on_macos(monkeypatch):
    monkeypatch.setattr(font_utils.platform, "system", lambda: "Darwin")
    assert font_utils.detect_korean_font() == "AppleGothic"


def test_detect_korean_font_on_linux_with_nanumgothic_installed(monkeypatch):
    monkeypatch.setattr(font_utils.platform, "system", lambda: "Linux")
    fake_font = type("FakeFont", (), {"name": "NanumGothic"})()
    monkeypatch.setattr(
        font_utils.fm.fontManager, "ttflist", [fake_font],
    )
    assert font_utils.detect_korean_font() == "NanumGothic"


def test_detect_korean_font_on_linux_without_any_korean_font(monkeypatch):
    monkeypatch.setattr(font_utils.platform, "system", lambda: "Linux")
    fake_font = type("FakeFont", (), {"name": "DejaVu Sans"})()
    monkeypatch.setattr(
        font_utils.fm.fontManager, "ttflist", [fake_font],
    )
    assert font_utils.detect_korean_font() is None


def test_setup_korean_font_does_not_raise_when_font_missing(monkeypatch):
    monkeypatch.setattr(font_utils, "detect_korean_font", lambda: None)
    font_utils.setup_korean_font()  # 예외 없이 끝나야 한다 (경고만 출력)
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `conda run -n sorting_visual pytest tests/test_font_utils.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'font_utils'`

- [ ] **Step 3: `font_utils.py` 구현**

`font_utils.py`:
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

- [ ] **Step 4: 테스트 실행해서 통과 확인**

Run: `conda run -n sorting_visual pytest tests/test_font_utils.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: 커밋**

```bash
git add font_utils.py tests/test_font_utils.py
git commit -m "feat: OS별 한글 폰트 자동 감지 및 설정 구현"
```

---

## Task 9: 성능 비교 모듈 (`metrics.py`)

**Files:**
- Create: `metrics.py`
- Test: `tests/test_metrics.py`

**Interfaces:**
- Consumes: `algorithms.py`의 6개 정렬 함수 (Task 2~7)
- Produces: `metrics.py`의 `ALGORITHMS: dict[str, callable]`, `generate_array(size: int) -> list[int]`, `run_comparison(array: list[int]) -> dict[str, dict]` — Task 13(visualizer 비교 화면)과 Task 14(`main.py`)가 이 세 개를 그대로 가져다 쓴다. `run_comparison`의 반환값 형태: `{"버블 정렬": {"comparisons": int, "array_accesses": int, "elapsed_time": float}, ...}` (`elapsed_time` 단위는 초).

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_metrics.py`:
```python
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
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `conda run -n sorting_visual pytest tests/test_metrics.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'metrics'`

- [ ] **Step 3: `metrics.py` 구현**

`metrics.py`:
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

- [ ] **Step 4: 테스트 실행해서 통과 확인**

Run: `conda run -n sorting_visual pytest tests/test_metrics.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: 커밋**

```bash
git add metrics.py tests/test_metrics.py
git commit -m "feat: 알고리즘 성능 비교 모듈(metrics.py) 구현"
```

---

## Task 10: 시각화 순수 헬퍼 함수 (`visualizer.py` 생성)

**Files:**
- Create: `visualizer.py`
- Test: `tests/test_visualizer.py`

**Interfaces:**
- Produces: `visualizer.py`의 `compute_bar_colors(n, info) -> list[str]`, `speed_to_interval(speed) -> float`, 색상 상수(`DEFAULT_COLOR`, `COMPARING_COLOR`, `SWAPPING_COLOR`, `SORTED_COLOR`), 화면 설정 상수(`MIN_SIZE`, `MAX_SIZE`, `DEFAULT_SIZE`, `MIN_SPEED`, `MAX_SPEED`, `DEFAULT_SPEED`) — Task 11~13의 `SortVisualizer` 클래스가 이 상수와 함수를 그대로 사용한다.

matplotlib GUI 위젯이 필요 없는 순수 함수만 다루므로 헤드리스 환경에서도 안전하게 테스트할 수 있다.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_visualizer.py`:
```python
"""시각화 모듈(visualizer.py)을 검증한다. GUI가 없는 환경에서도 동작하도록
Agg 백엔드를 사용한다."""
import matplotlib
matplotlib.use("Agg")

import pytest

from visualizer import (
    compute_bar_colors,
    speed_to_interval,
    DEFAULT_COLOR,
    COMPARING_COLOR,
    SWAPPING_COLOR,
    SORTED_COLOR,
)


def test_compute_bar_colors_default():
    info = {"comparing": None, "swapping": None, "sorted_indices": set()}
    assert compute_bar_colors(5, info) == [DEFAULT_COLOR] * 5


def test_compute_bar_colors_marks_comparing_indices():
    info = {"comparing": (1, 3), "swapping": None, "sorted_indices": set()}
    colors = compute_bar_colors(5, info)
    assert colors[1] == COMPARING_COLOR
    assert colors[3] == COMPARING_COLOR
    assert colors[0] == DEFAULT_COLOR


def test_compute_bar_colors_swapping_overrides_comparing():
    info = {"comparing": (1, 2), "swapping": (2,), "sorted_indices": set()}
    colors = compute_bar_colors(5, info)
    assert colors[2] == SWAPPING_COLOR


def test_compute_bar_colors_marks_sorted_indices():
    info = {"comparing": None, "swapping": None, "sorted_indices": {0, 1, 2}}
    colors = compute_bar_colors(5, info)
    assert colors[0] == SORTED_COLOR
    assert colors[2] == SORTED_COLOR
    assert colors[3] == DEFAULT_COLOR


def test_speed_to_interval_higher_speed_means_shorter_interval():
    assert speed_to_interval(2.0) < speed_to_interval(1.0) < speed_to_interval(0.5)


def test_speed_to_interval_rejects_non_positive_speed():
    with pytest.raises(ValueError):
        speed_to_interval(0)
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `conda run -n sorting_visual pytest tests/test_visualizer.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'visualizer'`

- [ ] **Step 3: 순수 헬퍼 함수 구현**

`visualizer.py`:
```python
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
```

- [ ] **Step 4: 테스트 실행해서 통과 확인**

Run: `conda run -n sorting_visual pytest tests/test_visualizer.py -v`
Expected: PASS (6 passed)

- [ ] **Step 5: 커밋**

```bash
git add visualizer.py tests/test_visualizer.py
git commit -m "feat: 시각화 색상/속도 순수 헬퍼 함수 구현"
```

---

## Task 11: `SortVisualizer` 클래스 — 메뉴 화면

**Files:**
- Modify: `visualizer.py` (append imports + class)
- Modify: `tests/test_visualizer.py` (append)

**Interfaces:**
- Consumes: `metrics.ALGORITHMS` (Task 9)
- Produces: `visualizer.py`의 `SortVisualizer` 클래스 — `__init__()`, `run()`, `show_menu()`, 내부 헬퍼 `_clear_figure()`. Task 12~13이 이 클래스에 메서드를 계속 추가한다.

화면 전환은 새 Figure를 띄우지 않고, 같은 `self.fig`를 `fig.clear()`로 비운 뒤 해당 화면의 위젯을 새로 그리는 방식으로 구현한다 (창이 여러 개 뜨지 않도록 하는 설계 의도를 유지하면서, `set_visible` 토글보다 단순하고 안전하게 구현하기 위함 — 숨겨진 Axes의 버튼이 클릭 이벤트를 계속 받는 matplotlib의 알려진 동작을 피할 수 있다).

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_visualizer.py`에 추가:
```python
from visualizer import SortVisualizer
import metrics


def test_show_menu_creates_one_button_per_algorithm_plus_compare_button():
    viz = SortVisualizer()
    viz.show_menu()
    # 6개 알고리즘 버튼 + "전체 성능 비교" 버튼 1개 = 7개 Axes
    assert len(viz.fig.axes) == len(metrics.ALGORITHMS) + 1


def test_show_menu_button_labels_include_all_algorithm_names():
    viz = SortVisualizer()
    viz.show_menu()
    labels = {button.label.get_text() for button in viz._widgets}
    assert set(metrics.ALGORITHMS.keys()).issubset(labels)
    assert "전체 성능 비교" in labels


def test_clear_figure_resets_widgets_list():
    viz = SortVisualizer()
    viz.show_menu()
    assert len(viz._widgets) > 0
    viz._clear_figure()
    assert viz._widgets == []
    assert viz.fig.axes == []
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `conda run -n sorting_visual pytest tests/test_visualizer.py -v -k SortVisualizer or menu or clear_figure`
Expected: FAIL with `ImportError: cannot import name 'SortVisualizer'`

- [ ] **Step 3: `SortVisualizer` 클래스(메뉴 화면) 구현**

`visualizer.py` 맨 위 import 블록에 추가:
```python
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import metrics
```

`visualizer.py` 맨 아래에 추가:
```python
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
```

- [ ] **Step 4: 테스트 실행해서 통과 확인**

Run: `conda run -n sorting_visual pytest tests/test_visualizer.py -v`
Expected: PASS (9 passed)

- [ ] **Step 5: 커밋**

```bash
git add visualizer.py tests/test_visualizer.py
git commit -m "feat: SortVisualizer 메뉴 화면 구현"
```

---

## Task 12: `SortVisualizer` 클래스 — 시각화 화면 (애니메이션)

**Files:**
- Modify: `visualizer.py` (append imports + methods)
- Modify: `tests/test_visualizer.py` (append)

**Interfaces:**
- Consumes: `metrics.ALGORITHMS` (Task 9), `compute_bar_colors`/`speed_to_interval` (Task 10), `show_menu`/`_clear_figure` (Task 11)
- Produces: `SortVisualizer.show_sort(algorithm_name)`, `_setup_sort_screen()`, `_animate(frame)`, `_update_info_text(info, elapsed)`, `_restart_sort()`, `_toggle_pause()` — Task 14(`main.py`)가 `show_sort`를 호출하고, Task 16(수동 검증)에서 전체 동작을 확인한다.

`_animate`와 `_update_info_text`는 GUI 이벤트 루프 없이도 직접 호출해서 테스트할 수 있도록 작은 단위로 분리한다 (matplotlib `FuncAnimation`이 실제로 프레임을 자동 진행하는 동작 자체는 matplotlib이 보장하는 영역이므로 별도로 테스트하지 않는다).

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_visualizer.py`에 추가:
```python
import matplotlib


def test_show_sort_creates_one_bar_per_array_element():
    viz = SortVisualizer()
    viz.array_size = 8
    viz.show_sort("버블 정렬")
    assert len(viz.bars) == 8
    assert viz.ax_bars.get_title() == "버블 정렬"


def test_animate_updates_bar_heights_and_colors():
    viz = SortVisualizer()
    viz.array_size = 5
    viz.show_sort("버블 정렬")
    frame = (
        [10, 20, 30, 40, 50],
        {
            "comparing": (0, 1), "swapping": None, "sorted_indices": set(),
            "comparisons": 3, "array_accesses": 1,
        },
    )
    viz._animate(frame)
    heights = [bar.get_height() for bar in viz.bars]
    assert heights == [10, 20, 30, 40, 50]
    assert viz.bars[0].get_facecolor() == matplotlib.colors.to_rgba("red")


def test_update_info_text_includes_comparisons_and_accesses():
    viz = SortVisualizer()
    viz.array_size = 5
    viz.show_sort("버블 정렬")
    viz._update_info_text({"comparisons": 7, "array_accesses": 3}, 1.23)
    text = viz.info_text.get_text()
    assert "7" in text
    assert "3" in text


def test_restart_sort_applies_new_slider_values():
    viz = SortVisualizer()
    viz.show_sort("버블 정렬")
    viz.size_slider.set_val(20)
    viz.speed_slider.set_val(2.0)
    viz._restart_sort()
    assert viz.array_size == 20
    assert viz.speed == 2.0
    assert len(viz.bars) == 20


def test_toggle_pause_changes_button_label():
    viz = SortVisualizer()
    viz.show_sort("버블 정렬")
    assert viz.pause_button.label.get_text() == "일시정지"
    viz._toggle_pause()
    assert viz.pause_button.label.get_text() == "계속"
    viz._toggle_pause()
    assert viz.pause_button.label.get_text() == "일시정지"


def test_show_menu_after_sort_returns_to_menu_screen():
    viz = SortVisualizer()
    viz.show_sort("버블 정렬")
    viz.show_menu()
    assert len(viz.fig.axes) == len(metrics.ALGORITHMS) + 1
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `conda run -n sorting_visual pytest tests/test_visualizer.py -v -k "show_sort or animate or restart or toggle_pause"`
Expected: FAIL with `AttributeError: 'SortVisualizer' object has no attribute 'show_sort'`

- [ ] **Step 3: 시각화 화면 구현**

`visualizer.py` import 블록에 추가:
```python
import time

from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
```

`SortVisualizer` 클래스에 메서드 추가:
```python
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

        generator = metrics.ALGORITHMS[self._algorithm_name](self.current_array)
        self._animation = FuncAnimation(
            self.fig,
            self._animate,
            frames=generator,
            interval=speed_to_interval(self.speed),
            repeat=False,
            cache_frame_data=False,
        )
        self.fig.canvas.draw_idle()

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
        if self._paused:
            self._animation.event_source.start()
        else:
            self._animation.event_source.stop()
        self._paused = not self._paused
        self.pause_button.label.set_text("계속" if self._paused else "일시정지")
```

- [ ] **Step 4: 테스트 실행해서 통과 확인**

Run: `conda run -n sorting_visual pytest tests/test_visualizer.py -v`
Expected: PASS (15 passed)

- [ ] **Step 5: 커밋**

```bash
git add visualizer.py tests/test_visualizer.py
git commit -m "feat: SortVisualizer 시각화 애니메이션 화면 구현"
```

---

## Task 13: `SortVisualizer` 클래스 — 비교 설정/결과 화면

**Files:**
- Modify: `visualizer.py` (append methods)
- Modify: `tests/test_visualizer.py` (append)

**Interfaces:**
- Consumes: `metrics.generate_array`, `metrics.run_comparison` (Task 9), `show_menu`/`_clear_figure` (Task 11)
- Produces: `SortVisualizer.show_compare_setup()`, `_run_compare()`, `show_compare_result(result)` — Task 14(`main.py`)는 이 화면 전환 흐름을 직접 호출하지 않지만(메뉴 버튼 클릭으로 진입), Task 16(수동 검증)에서 전체 동작을 확인한다. 이로써 `SortVisualizer`의 모든 화면(메뉴/시각화/비교)이 완성된다.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_visualizer.py`에 추가:
```python
def test_show_compare_setup_creates_slider_and_two_buttons():
    viz = SortVisualizer()
    viz.show_compare_setup()
    # 배열 크기 슬라이더 1개 + 측정 시작 버튼 + 메뉴로 버튼 = 3개 Axes
    assert len(viz.fig.axes) == 3


def test_show_compare_result_creates_two_subplots_with_six_bars_each():
    viz = SortVisualizer()
    fake_result = {
        name: {"comparisons": 100, "array_accesses": 50, "elapsed_time": 0.01}
        for name in metrics.ALGORITHMS
    }
    viz.show_compare_result(fake_result)
    bar_axes = [ax for ax in viz.fig.axes if ax.patches]
    assert len(bar_axes) == 2
    for ax in bar_axes:
        assert len(ax.patches) == 6


def test_run_compare_uses_slider_value_as_array_size(monkeypatch):
    viz = SortVisualizer()
    viz.show_compare_setup()
    viz.compare_size_slider.set_val(15)

    captured = {}

    def fake_run_comparison(array):
        captured["size"] = len(array)
        return {
            name: {"comparisons": 1, "array_accesses": 1, "elapsed_time": 0.0}
            for name in metrics.ALGORITHMS
        }

    monkeypatch.setattr(metrics, "run_comparison", fake_run_comparison)
    viz._run_compare()
    assert captured["size"] == 15
    assert viz.array_size == 15
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `conda run -n sorting_visual pytest tests/test_visualizer.py -v -k compare`
Expected: FAIL with `AttributeError: 'SortVisualizer' object has no attribute 'show_compare_setup'`

- [ ] **Step 3: 비교 화면 구현**

`SortVisualizer` 클래스에 메서드 추가:
```python
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

- [ ] **Step 4: 테스트 실행해서 통과 확인**

Run: `conda run -n sorting_visual pytest tests/test_visualizer.py -v`
Expected: PASS (18 passed)

- [ ] **Step 5: 전체 테스트 스위트 회귀 확인**

Run: `conda run -n sorting_visual pytest -v`
Expected: PASS (모든 모듈의 테스트 통과, 약 51개 — 알고리즘 23 + font_utils 5 + metrics 5 + visualizer 18)

- [ ] **Step 6: 커밋**

```bash
git add visualizer.py tests/test_visualizer.py
git commit -m "feat: SortVisualizer 성능 비교 설정/결과 화면 구현"
```

---

## Task 14: 진입점 (`main.py`)

**Files:**
- Create: `main.py`
- Test: `tests/test_main.py`

**Interfaces:**
- Consumes: `font_utils.setup_korean_font` (Task 8), `visualizer.SortVisualizer` (Task 11~13)
- Produces: `main.py`의 `main()` — 프로그램의 유일한 진입점. 이로써 설계 문서의 모든 모듈(`algorithms`, `font_utils`, `metrics`, `visualizer`, `main`)이 연결된다.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_main.py`:
```python
"""진입점(main.py)이 한글 폰트 설정과 SortVisualizer 실행을 순서대로
호출하는지 검증한다."""
import matplotlib
matplotlib.use("Agg")

import main as main_module


def test_main_sets_up_font_before_running_visualizer(monkeypatch):
    calls = []
    monkeypatch.setattr(main_module, "setup_korean_font", lambda: calls.append("font"))
    monkeypatch.setattr(main_module.SortVisualizer, "run", lambda self: calls.append("run"))

    main_module.main()

    assert calls == ["font", "run"]
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `conda run -n sorting_visual pytest tests/test_main.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'main'`

- [ ] **Step 3: `main.py` 구현**

`main.py`:
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

- [ ] **Step 4: 테스트 실행해서 통과 확인**

Run: `conda run -n sorting_visual pytest tests/test_main.py -v`
Expected: PASS (1 passed)

- [ ] **Step 5: 커밋**

```bash
git add main.py tests/test_main.py
git commit -m "feat: 프로그램 진입점(main.py) 구현"
```

---

## Task 15: 통합 스모크 테스트

**Files:**
- Create: `tests/test_integration.py`

**Interfaces:**
- Consumes: `metrics.ALGORITHMS` (Task 9), `visualizer.SortVisualizer` (Task 11~13)
- Produces: 헤드리스(Agg) 환경에서 메뉴 → 6개 알고리즘 시각화 → 비교 모드 전체 흐름이 예외 없이 동작함을 보장하는 회귀 테스트. 디스플레이가 없는 환경(CI, 이 작업 환경)에서도 "전체 화면 전환이 깨지지 않는다"를 검증할 수 있는 안전망 역할을 한다.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_integration.py`:
```python
"""화면 전환 전체 흐름(메뉴 -> 시각화 -> 비교)이 예외 없이 동작하는지
확인하는 헤드리스 통합 스모크 테스트."""
import matplotlib
matplotlib.use("Agg")

import metrics
from visualizer import SortVisualizer


def test_every_algorithm_can_be_visualized_and_return_to_menu():
    for name in metrics.ALGORITHMS:
        viz = SortVisualizer()
        viz.array_size = 12
        viz.show_sort(name)

        # 알고리즘이 실제로 최소 한 프레임을 생성하고, _animate가
        # 예외 없이 그 프레임을 처리할 수 있는지 확인한다.
        frame = next(iter(metrics.ALGORITHMS[name](list(viz.current_array))))
        viz._animate(frame)

        viz.show_menu()
        assert len(viz.fig.axes) == len(metrics.ALGORITHMS) + 1


def test_compare_mode_full_flow_from_menu_to_result():
    viz = SortVisualizer()
    viz.show_menu()
    viz.show_compare_setup()
    viz.compare_size_slider.set_val(10)
    viz._run_compare()

    bar_axes = [ax for ax in viz.fig.axes if ax.patches]
    assert len(bar_axes) == 2
    for ax in bar_axes:
        assert len(ax.patches) == len(metrics.ALGORITHMS)
```

- [ ] **Step 2: 테스트 실행해서 통과 확인**

Task 1~14에서 이미 모든 메서드(`show_sort`, `show_menu`, `show_compare_setup`,
`_run_compare`, `compare_size_slider` 등)가 구현되어 있으므로, 이 테스트는
추가 구현 없이 바로 통과해야 한다.

Run: `conda run -n sorting_visual pytest tests/test_integration.py -v`
Expected: PASS (2 passed)

- [ ] **Step 3: 전체 테스트 스위트 최종 회귀 확인**

Run: `conda run -n sorting_visual pytest -v`
Expected: PASS (전체 약 54개 테스트 통과 — Task 13까지의 51개 + main.py 1개 + 통합 스모크 테스트 2개, 실패/에러 0건)

- [ ] **Step 4: 커밋**

```bash
git add tests/test_integration.py
git commit -m "test: 화면 전환 전체 흐름 헤드리스 통합 스모크 테스트 추가"
```

---

## Task 16: README.md 작성 및 수동 실행 검증

**Files:**
- Modify: `README.md` (현재 `# sorting_visual` 한 줄만 있는 상태)

**Interfaces:**
- Consumes: 알고리즘 시간/공간복잡도(Task 2~7의 docstring 내용), 실행 방법(Task 14의 `main.py`)
- Produces: 과제 보고서에 바로 활용 가능한 `README.md`. 이 작업이 전체 계획의 마지막 태스크다.

- [ ] **Step 1: README.md 작성**

`README.md`:
```markdown
# 정렬 알고리즘 비교 시각화 프로그램

Python과 matplotlib을 이용해 6종 정렬 알고리즘의 동작 과정을 실시간
막대그래프 애니메이션으로 보여주고, 동일한 입력에 대한 성능(비교 횟수,
실행 시간)을 한 장의 차트로 비교하는 프로그램입니다.

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
```

- [ ] **Step 2: 디스플레이가 있는 환경에서 수동 실행 검증**

이 계획의 나머지 작업은 모두 헤드리스(Agg) 환경에서 테스트했으므로,
실제 화면이 있는 머신에서 다음을 직접 실행해 확인한다.

Run: `conda run -n sorting_visual python main.py`

확인 체크리스트:
- [ ] 메뉴 화면에 6개 알고리즘 버튼과 "전체 성능 비교" 버튼이 보인다
- [ ] 각 알고리즘 버튼을 누르면 막대그래프 애니메이션이 시작되고,
      빨강(비교)/초록(교환)/진한 파랑(완료) 색상이 올바르게 바뀐다
- [ ] 상단 텍스트의 비교 횟수/배열 접근/경과 시간이 실시간으로 갱신된다
- [ ] 배열 크기·속도 슬라이더를 바꾼 뒤 "재시작"을 누르면 새 설정이
      반영된다
- [ ] "일시정지"를 누르면 애니메이션이 멈추고, 다시 누르면 이어진다
- [ ] "메뉴로" 버튼으로 메뉴 화면에 정상적으로 돌아간다
- [ ] "전체 성능 비교" → 배열 크기 설정 → "측정 시작" 시 6개 알고리즘
      결과가 비교 횟수/실행 시간 막대그래프 두 장으로 표시된다
- [ ] 한글 텍스트(버튼 라벨, 제목, 축 이름)가 깨지지 않고 표시된다

위 체크리스트 중 하나라도 어긋나면, 해당 화면을 담당하는 Task(11~13)로
돌아가 원인을 파악하고 수정한 뒤 관련 자동화 테스트도 함께 보완한다.

- [ ] **Step 3: 커밋**

```bash
git add README.md
git commit -m "docs: README 작성 (실행 방법, 사용법, 복잡도 표)"
```
