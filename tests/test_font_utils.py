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
