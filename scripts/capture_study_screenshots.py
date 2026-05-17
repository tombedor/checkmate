#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description="Capture browser screenshots of the hosted study UI")
    parser.add_argument("--url", default="http://127.0.0.1:8000/", help="Study UI URL")
    parser.add_argument(
        "--output-dir",
        default="output/test-artifacts",
        help="Directory for screenshots",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()

        desktop = browser.new_page(viewport={"width": 1440, "height": 1600})
        desktop.goto(args.url, wait_until="networkidle")
        desktop.screenshot(path=str(output_dir / "study-desktop.png"), full_page=True)

        mobile = browser.new_page(viewport={"width": 430, "height": 1200}, is_mobile=True)
        mobile.goto(args.url, wait_until="networkidle")
        mobile.screenshot(path=str(output_dir / "study-mobile.png"), full_page=True)

        board = browser.new_page(viewport={"width": 1440, "height": 1200})
        board.goto(args.url, wait_until="networkidle")
        board.locator("#challenge-shell").screenshot(path=str(output_dir / "study-challenge.png"))

        browser.close()

    print(f"Wrote screenshots to {output_dir}")


if __name__ == "__main__":
    main()
