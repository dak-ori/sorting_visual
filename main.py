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
