# 정렬 알고리즘 비교 시각화 프로그램 — 설계 문서

- 날짜: 2026-06-21
- 목적: 대학교 컴퓨터공학과 기말 대체과제 — 코드 품질과 설명력이 평가 대상

## 1. 개요

Python + matplotlib(+ numpy)으로 6종 정렬 알고리즘의 동작을 실시간 애니메이션으로
보여주고, 동일한 입력에 대한 성능(비교 횟수, 실행 시간)을 한 장의 차트로 비교하는
프로그램. 외부 의존성은 matplotlib, numpy만 사용한다.

## 2. 전체 구조

```
sorting_visual/
├── main.py            # 진입점: Figure 생성, 메뉴 화면, 모드 분기
├── algorithms.py      # 6개 정렬 알고리즘 (제너레이터로 구현)
├── visualizer.py       # SortVisualizer 클래스: 애니메이션·위젯·화면 전환
├── metrics.py          # 성능 비교 실행(run_comparison) + 요약 차트
├── font_utils.py        # OS별 한글 폰트 자동 설정
├── requirements.txt
└── README.md
```

역할 분리 기준:
- `algorithms.py`는 matplotlib을 전혀 모름 (순수 알고리즘 + 측정값 yield)
- `visualizer.py`는 어떤 알고리즘인지 모름 (공통 yield 인터페이스만 소비)
- `metrics.py`는 화면 전환을 모름 (배열과 알고리즘 목록을 받아 결과 dict만 반환)
- `main.py`가 위 세 모듈을 엮는 유일한 곳

## 3. 실행 흐름

1. `main.py` 실행 → 하나의 matplotlib Figure에 **메뉴 화면**: 알고리즘 버튼 6개(버블,
   선택, 삽입, 병합, 퀵, 힙) + "전체 성능 비교" 버튼 1개
2. 알고리즘 버튼 클릭 → 같은 Figure 안에서 **시각화 화면**으로 전환
   - 막대그래프 애니메이션(`FuncAnimation`), 상단에 비교 횟수 / array_accesses / 경과시간
     실시간 텍스트
   - `Slider`: 배열 크기(10~100), 속도(0.25x~3x)
   - `Button`: 시작/일시정지, 재시작(슬라이더 변경값 반영), 메뉴로
3. "전체 성능 비교" 클릭 → 배열 크기 슬라이더만 있는 **비교 설정 화면** → "측정 시작"
   → 6개 알고리즘을 애니메이션 없이 백그라운드로 전부 실행 → **비교 결과 화면**
   (subplot 2개: 비교 횟수 막대그래프, 실행 시간 막대그래프, 막대 위 값 라벨 표시)
4. 모든 화면에 "메뉴로" 버튼으로 1번 화면 복귀 가능

화면 전환은 새 Figure를 만들지 않고, 화면별 위젯들의 `set_visible()`을 토글하는
방식으로 구현한다 (창이 여러 개 뜨지 않도록).

## 4. 알고리즘 모듈 (`algorithms.py`)

### 4.1 공통 제너레이터 인터페이스

6개 함수(`bubble_sort`, `selection_sort`, `insertion_sort`, `merge_sort`,
`quick_sort`, `heap_sort`) 모두 동일한 형식으로 `yield`한다:

```python
yield array.copy(), {
    "comparing": (i, j),       # 비교 중인 인덱스 튜플, 없으면 None
    "swapping": (i, j),        # 교환/이동 중인 인덱스 튜플, 없으면 None
    "sorted_indices": {...},   # 정렬 확정된 인덱스 집합
    "comparisons": int,        # 누적 비교 횟수
    "array_accesses": int,     # 누적 배열 쓰기 횟수
}
```

이 인터페이스가 통일되어 있어 `visualizer.py`는 어떤 알고리즘이 들어와도 동일한
렌더링 코드로 처리할 수 있다 (알고리즘 추가 시 visualizer 수정 불필요).

### 4.2 측정 지표 정의

요구사항의 "비교 횟수, 교환/접근 횟수"를 다음으로 통일한다:

- `comparisons`: 두 원소를 비교한 횟수
- `array_accesses`: 배열에 값을 쓴(대입) 횟수
  - 버블/선택/삽입/퀵/힙 정렬의 swap 1회 = `array_accesses` 2 증가
  - 병합 정렬은 swap이 없으므로, 임시 배열 → 원본 배열로 쓰는 매 대입 1회당
    `array_accesses` 1 증가
  - 이렇게 통일하면 swap 기반 알고리즘과 병합 정렬을 같은 기준으로 비교 가능

### 4.3 시각화 색상 매핑 (visualizer가 info를 해석하는 규칙)

| 상태 | 색상 |
|---|---|
| 기본 | skyblue |
| comparing 인덱스 | 빨강 |
| swapping 인덱스 | 초록 |
| sorted_indices에 포함 | 진한 파랑 |

## 5. 시각화 모듈 (`visualizer.py`)

### 5.1 `SortVisualizer` 클래스

하나의 Figure 객체를 보유하며 화면 상태(메뉴/시각화/비교설정/비교결과)를 관리한다.
주요 메서드:

- `show_menu()`: 메뉴 화면 위젯만 visible로 전환
- `show_sort(algo_name)`: 시각화 화면 전환, 선택된 알고리즘의 제너레이터를
  `FuncAnimation`에 연결
- `show_compare_setup()`: 비교 설정 화면 전환
- `show_compare_result(result)`: `metrics.run_comparison()` 결과를 받아 subplot 2개로
  렌더링

### 5.2 시각화 화면 상세

- 메인 막대그래프 + `ax.text()`로 매 프레임 갱신되는 상단 카운터
  (비교 횟수, array_accesses, 경과 시간(`time.perf_counter()` 기준))
- 슬라이더 변경은 애니메이션 진행 중 즉시 반영하지 않고, "재시작" 버튼을 눌렀을 때
  새 배열 크기/속도로 다시 시작한다 (matplotlib `FuncAnimation`의 interval을 진행 중
  실시간으로 바꾸는 것은 불안정하므로, 재시작 방식이 더 안전하고 명확함)
- 속도 슬라이더는 `FuncAnimation`의 `interval`(ms) 또는 프레임 스킵 수에 매핑

### 5.3 비교 결과 화면 상세

- subplot 2개를 가로로 배치: (1) 알고리즘별 비교 횟수 막대그래프, (2) 알고리즘별
  실행 시간(ms) 막대그래프
- 각 막대 위에 정확한 값을 텍스트로 표시 (O(n²) vs O(n log n) 격차를 숫자로도 확인)
- x축은 6개 알고리즘 이름(한글)

## 6. 성능 비교 모듈 (`metrics.py`)

```python
def run_comparison(size: int) -> dict:
    """동일한 무작위 배열을 6개 알고리즘에 각각 복사해서 실행하고,
    알고리즘명 -> {comparisons, array_accesses, elapsed_time} 딕셔너리를 반환.
    elapsed_time 단위는 초(float, time.perf_counter 기준)이며,
    5.3절 차트에 표시할 때 ms로 환산한다."""
```

- 입력 배열은 `numpy.random.permutation(size) + 1`로 1~size 중복 없는 무작위 배열을
  1회 생성하고, 각 알고리즘에 `array.copy()`로 동일하게 전달 (공정한 비교 보장)
  
**구현 노트:** `algorithms.py`의 제너레이터는 시각화 모드와 동일한 함수를 그대로
재사용하되, `run_comparison`에서는 제너레이터를 끝까지 소비(`for _ in generator: pass`)
하면서 애니메이션 렌더링 없이 마지막 yield의 `comparisons`/`array_accesses`만 취하고,
실행 시간은 소비 시작~종료까지 `time.perf_counter()`로 측정한다. 이를 통해 알고리즘
구현이 시각화용과 비교용으로 중복되지 않는다.

## 7. 한글 폰트 처리 (`font_utils.py`)

```python
def setup_korean_font():
    """platform.system()으로 OS를 감지해 적절한 한글 폰트를 matplotlib에 적용."""
```

- Windows → `Malgun Gothic`
- macOS (Darwin) → `AppleGothic`
- Linux → `NanumGothic` 우선 시도, 시스템에 설치되어 있지 않으면
  `matplotlib.font_manager`로 사용 가능한 한글 폰트를 탐색해서 첫 번째로 발견된 것을
  사용. 끝까지 못 찾으면 경고 메시지만 출력하고 기본 폰트 유지(프로그램 동작은
  막지 않음)
- `plt.rcParams['axes.unicode_minus'] = False`로 마이너스 기호 깨짐 방지

## 8. 산출물

### 8.1 `requirements.txt`

```
matplotlib
numpy
```

### 8.2 `README.md` 구성

1. 프로그램 개요 + 스크린샷 자리 (`![demo](docs/screenshot.png)` placeholder)
2. 실행 방법 (`pip install -r requirements.txt` → `python main.py`)
3. 알고리즘별 시간복잡도(최선/평균/최악)·공간복잡도·안정성 여부 표
4. 사용법 (메뉴 화면 캡처 자리 placeholder + 조작법 설명)

### 8.3 코드 주석 규칙

- 각 알고리즘 함수 상단에 동작 원리를 설명하는 한글 docstring
- 핵심 분기(퀵정렬 피벗 선택, 병합 정렬 분할정복 경계, 힙 정렬 heapify 등)에
  한글 인라인 주석

## 9. 테스트 데이터 생성

- `numpy.random.permutation(size) + 1`로 1~size 정수를 중복 없이 무작위 섞어서 생성
- 시각화 모드: 알고리즘 선택/재시작 시마다 새로 생성
- 비교 모드: 한 번 생성한 배열을 6개 알고리즘 모두에 동일하게 복사 전달 (같은 입력
  보장)

## 10. 범위 외 (Out of scope)

- 정렬 외 알고리즘(탐색 등) 시각화
- 다중 윈도우/탭 동시 비교
- 애니메이션 진행 중 실시간 슬라이더 반영 (재시작 시에만 반영)
- 사용자 직접 배열 입력 (무작위 생성만 지원)
