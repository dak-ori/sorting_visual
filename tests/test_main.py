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
