"""Devpost screenshots v2 — Maplewood basis. Overwrites docs/screenshots/01..07.

Pageshots (1440x900, dsf 2) for hero/console/decisions/card/outbox;
03-step-mode and 07-runnight are frames cut from the v2 video clips
(those UI states only exist inside a live session).

Prereq: maplewood-little restored to the beat-05 snapshot state.
"""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "docs" / "screenshots"
BASE = "http://127.0.0.1:8765"


def main() -> int:
    SHOTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page = ctx.new_page()
        page.set_default_timeout(20_000)

        # 01 — hero page: H1, sub, CTAs, live stats
        page.goto(BASE + "/")
        page.wait_for_selector("#stats b")
        page.wait_for_timeout(1200)
        page.screenshot(path=str(SHOTS / "01-hero-page.png"))

        # 02 — console top: chips, KPIs, inbox with pending decisions badge
        page.goto(BASE + "/app?club=maplewood-little")
        page.wait_for_selector(".inbox-row")
        page.wait_for_timeout(800)
        page.screenshot(path=str(SHOTS / "02-console.png"))

        # 04 — decisions section with the queued cards
        page.locator("#decisions").scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        page.screenshot(path=str(SHOTS / "04-decisions.png"))

        # 05 — Danny's EpiPen card with the instruct box open (human-in-the-loop)
        danny = page.locator(".dec", has_text="Registering Danny")
        danny.scroll_into_view_if_needed()
        danny.locator(".btn-edit").click()          # ✎ Approve + instruct
        danny.locator("textarea").wait_for(state="visible")
        danny.locator("textarea").fill(
            "Confirm with Rachel: coaches will be briefed, EpiPen stays in Danny's backpack."
        )
        page.wait_for_timeout(400)
        danny.screenshot(path=str(SHOTS / "05-decision-card.png"))

        # 06 — outbox: first pair (scholarship draft) open next to the mail
        page.locator("#outbox").scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        page.screenshot(path=str(SHOTS / "06-outbox-pair.png"))

        browser.close()
    print("pageshots done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
