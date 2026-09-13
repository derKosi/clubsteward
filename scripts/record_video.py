"""Record the ClubSteward demo video v2 — beat-wise Playwright clips.

Run:  uv run --env-file <env-with-key> python scripts/record_video.py [--only beat ...]

Prereqs:
  - web server on 127.0.0.1:8765 WITHOUT CLUBSTEWARD_WEB_TOKEN (app.html sends no header)
  - kg-rheinklause has decision cards (one pipeline run done beforehand)
  - maplewood-little in reset state (10 mails in inbox)

Beat order == video order; state continuity is maintained across clips:
  01-02  fresh state (hook + intro)
  03     click Reset (visible reset), then OFF-SCREEN: process 02+03 (Tanya's card)
  04     step mode: 01-signup-epipen (queued) + 04-question-pictureday (auto draft)
  05     decisions: open Tanya's card, Approve + instruct (typed), wait for execution
  06     outbox draft pairs
  07     switch to kg-rheinklause (German cards + Dohr's original mail)
  08     run night, watch log stream, stop; then OFF-SCREEN: run remaining mails
  09     register + hero "policy is data"
  10     hero + console inbox zero

After every beat the club dir is snapshotted to docs/video/clips-v2/_snapshots/
so a single beat can be re-recorded via --only (state is restored first).
Clips land in docs/video/clips-v2/<beat>.webm (1440x900, dsf 2).
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CLIPS = ROOT / "docs" / "video" / "clips-v2"
SNAPS = CLIPS / "_snapshots"
CLUB_DIR = ROOT / "clubs" / "maplewood-little"
BASE = "http://127.0.0.1:8765"

# measured v4 VO durations (s) — every clip holds at least this long (+ pad)
VO = {
    "01-hook": 24.2, "02-intro": 17.3, "03-reset": 12.3, "04-step": 30.6,
    "05-morning": 30.2, "06-outbox": 16.1, "07-anylanguage": 24.0,
    "08-runnight": 12.4, "09-built": 20.4, "10-close": 11.4,
}

api = httpx.Client(base_url=BASE, timeout=300.0)


def hold(s: float) -> None:
    time.sleep(s)


def wait_step_done(page, timeout: float = 180.0) -> None:
    """Wait for the step to finish: button goes busy first, then back to idle."""
    page.wait_for_selector("#stepBtn:has-text('processing')", timeout=20_000)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if "processing" not in (page.locator("#stepBtn").inner_text() or ""):
            return
        hold(1.0)
    raise TimeoutError("step did not finish in time")


# ---------------------------------------------------------------- beats

def b01_hook(page):
    page.goto(BASE + "/")
    page.wait_for_selector("#stats b")
    hold(4.5)
    for _ in range(6):                      # slow pan down the hero
        page.mouse.wheel(0, 180); hold(0.7)
    hold(2.5)
    page.goto(BASE + "/app?club=maplewood-little")
    page.wait_for_selector(".inbox-row")
    page.locator("#inboxCard").scroll_into_view_if_needed()
    for _ in range(7):                      # slow pan over the 10 mails
        page.mouse.wheel(0, 110); hold(0.75)
    hold(3)


def b02_intro(page):
    page.goto(BASE + "/#how")
    page.wait_for_selector("#how .card")
    hold(3)
    for _ in range(4):
        page.mouse.wheel(0, 200); hold(0.9)
    hold(2)
    page.goto(BASE + "/app?club=maplewood-little")
    page.wait_for_selector("#clubs .chip")
    hold(4)                                  # six club chips on screen


def b03_reset(page):
    page.goto(BASE + "/app?club=maplewood-little")
    page.wait_for_selector("#resetBtn")
    page.locator("#resetBtn").click()
    page.wait_for_selector("#inboxList .inbox-row")   # dialog auto-accepted below
    page.locator("#inboxCard").scroll_into_view_if_needed()
    hold(6)


def b04_step(page):
    page.goto(BASE + "/app?club=maplewood-little")
    page.wait_for_selector("#stepBtn")
    page.locator("#stepBtn").scroll_into_view_if_needed()
    hold(1.5)
    # step 1: 01-signup-epipen → medical flag → queued
    page.locator("#stepBtn").click()
    wait_step_done(page)
    hold(7)
    # step 2: 04-question-pictureday → auto draft
    page.locator("#stepBtn").click()
    wait_step_done(page)
    hold(6)


def b05_morning(page):
    page.goto(BASE + "/app?club=maplewood-little")
    page.wait_for_selector(".dec")
    page.locator("#decisions").scroll_into_view_if_needed()
    hold(3)
    tanya = page.locator(".dec", has_text="Fee help for Ava")
    tanya.scroll_into_view_if_needed()
    hold(3)
    tanya.locator(".btn-edit").click()               # ✎ Approve + instruct
    tx = tanya.locator("textarea")
    tx.wait_for(state="visible")
    tx.type("Please offer a 50% scholarship and credit her snack-shack weekends against the rest.",
             delay=55)
    hold(1)
    tanya.locator(".ins-btns .btn-app").click()      # ✓ Approve with instructions
    page.wait_for_selector("#toast.show", timeout=120_000)  # agent executes (LLM)
    hold(4)


def b06_outbox(page):
    page.goto(BASE + "/app?club=maplewood-little")
    page.wait_for_selector(".draft-pair")
    page.locator("#outbox").scroll_into_view_if_needed()
    hold(3)
    pairs = page.locator(".draft-pair")
    if pairs.count() > 1:                            # open the Tanya pair
        for i in range(pairs.count()):
            if "Fee help" in pairs.nth(i).inner_text() or "scholarship" in pairs.nth(i).inner_text():
                pairs.nth(i).locator("summary").click(); break
    hold(8)


def b07_anylanguage(page):
    page.goto(BASE + "/app?club=kg-rheinklause")
    page.wait_for_selector(".dec")
    page.locator("#decisions").scroll_into_view_if_needed()
    hold(3)
    dohr = page.locator(".dec", has_text="Beitrag")
    dohr.scroll_into_view_if_needed()
    hold(2.5)
    dohr.locator("details.mail summary").click()     # show the original German mail
    hold(12)


def b08_runnight(page):
    page.goto(BASE + "/app?club=maplewood-little")
    page.wait_for_selector("#runBtn")
    page.locator("#runlogCard").scroll_into_view_if_needed()
    hold(1.5)
    page.locator("#runBtn").click()                  # 🌙 Run night
    hold(22)                                         # log streams (2s poll)
    page.locator("#runBtn").click()                  # ⏹ Stop
    page.wait_for_selector("#toast.show", timeout=180_000)
    hold(4)


def b09_built(page):
    page.goto(BASE + "/app?club=maplewood-little")
    page.wait_for_selector("#reg tr")
    page.locator("#register").scroll_into_view_if_needed()
    hold(8)
    page.goto(BASE + "/#how")
    page.wait_for_selector("#how .card")
    page.locator("#how .card").nth(2).scroll_into_view_if_needed()  # 3 · Policy is data
    hold(9)


def b10_close(page):
    page.goto(BASE + "/")
    page.wait_for_selector("#stats b")
    hold(4)
    for _ in range(5):
        page.mouse.wheel(0, 200); hold(0.6)
    page.goto(BASE + "/app?club=maplewood-little")
    page.wait_for_selector("#inboxCard")
    page.locator("#inboxCard").scroll_into_view_if_needed()
    hold(5)                                          # "Inbox zero 🎉"


BEATS = {
    "01-hook": b01_hook, "02-intro": b02_intro, "03-reset": b03_reset,
    "04-step": b04_step, "05-morning": b05_morning, "06-outbox": b06_outbox,
    "07-anylanguage": b07_anylanguage, "08-runnight": b08_runnight,
    "09-built": b09_built, "10-close": b10_close,
}

# what runs off-screen BETWEEN beats to set up the next one's app state.
# "process:N" = process exactly N mails via the step API (sorted inbox order).
PREP = {
    # reset restores all ten mails; prep consumes 01+02+03, then "requeue_first"
    # puts 01-signup-epipen BACK into the inbox (and drops the decision card it
    # created off-screen) so beat 04 steps Danny live — and 04-question is next.
    "04-step": ["process:3", "requeue_first"],
    "10-close": ["run_rest"],   # after 08: finish remaining mails
}


def run_prep(items: list[str]) -> None:
    for it in items:
        if it.startswith("process:"):
            n = int(it.split(":")[1])
            for _ in range(n):
                r = api.post("/api/clubs/maplewood-little/process-one")
                r.raise_for_status()
                print(f"    prep: processed one mail -> {r.json().get('outcome')}")
        elif it == "requeue_first":
            # beat 04 must step 01-signup-epipen LIVE: undo its off-screen run
            # (drop the decision card, move the mail back to the inbox)
            for j in (CLUB_DIR / "decisions").glob("*.json"):
                subj = json.loads(j.read_text(encoding="utf-8")).get("subject", "")
                if subj.startswith("Registering Danny"):
                    j.unlink()
                    print("    prep: dropped off-screen Danny decision")
            src = CLUB_DIR / "processed" / "01-signup-epipen.eml"
            if not src.exists():
                # queued mails file into decisions/, auto-processed into processed/
                src = CLUB_DIR / "decisions" / "01-signup-epipen.eml"
            if src.exists():
                shutil.move(str(src), str(CLUB_DIR / "inbox" / src.name))
                print("    prep: 01-signup-epipen requeued for live step")
        elif it == "run_rest":
            api.post("/api/clubs/maplewood-little/run").raise_for_status()
            while True:
                st = api.get("/api/clubs/maplewood-little/run/status").json()
                if not st.get("running"):
                    break
                hold(3)
            print("    prep: night run finished")


def snap(beat: str) -> None:
    dst = SNAPS / beat
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(CLUB_DIR, dst)


def restore(beat: str) -> None:
    src = SNAPS / beat
    if not src.exists():
        return
    shutil.rmtree(CLUB_DIR)
    shutil.copytree(src, CLUB_DIR)


def main() -> int:
    only = sys.argv[sys.argv.index("--only") + 1:] if "--only" in sys.argv else None
    CLIPS.mkdir(parents=True, exist_ok=True)
    SNAPS.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
            record_video_dir=str(CLIPS),
            record_video_size={"width": 1440, "height": 900},
        )
        ctx.on("page", lambda p: p.on("dialog", lambda d: d.accept()))

        for name, fn in BEATS.items():
            if only and name not in only:
                continue
            if only and name in only and (SNAPS / name).exists():
                # retake: roll app state back to "after this beat's predecessors"
                prev = [b for b in BEATS if BEATS[b] and list(BEATS).index(b) < list(BEATS).index(name)]
                if prev:
                    restore(prev[-1])
                    print(f"  (state restored from snapshot '{prev[-1]}')")
            prep = PREP.get(name)
            if prep:
                print(f"  prep for {name}: {prep}")
                run_prep(prep)
            print(f"● recording {name} …", flush=True)
            page = ctx.new_page()
            page.set_default_timeout(20_000)
            t0 = time.monotonic()
            fn(page)
            need = VO[name] + 1.5 - (time.monotonic() - t0)
            if need > 0:
                hold(need)
            video = page.video
            page.close()
            src = Path(video.path())
            dst = CLIPS / f"{name}.webm"
            shutil.move(src, dst)
            print(f"  ✓ {name} -> {dst.name} ({time.monotonic() - t0:.0f}s)")
            snap(name)

        browser.close()
    print("\nAll clips in", CLIPS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
