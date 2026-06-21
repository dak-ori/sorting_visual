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
