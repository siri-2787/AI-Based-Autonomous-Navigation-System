"""
main.py
───────
Entry point.  Run:   python main.py
"""

import sys
import os

# Ensure project root is on the path so every package resolves correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import App


def main():
    print("=" * 62)
    print("  AI-Based Autonomous Navigation System")
    print("=" * 62)
    print()
    print("  Keyboard shortcuts")
    print("  ──────────────────")
    print("  ENTER     Start navigation")
    print("  SPACE     Pause / Resume")
    print("  R         Reset (new random map)")
    print("  C         Compare all algorithms")
    print("  S         Screenshot")
    print("  ESC / Q   Quit")
    print()
    print("  Mouse")
    print("  ─────")
    print("  Click grid cell    Toggle obstacle on/off")
    print()

    try:
        App().run()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
