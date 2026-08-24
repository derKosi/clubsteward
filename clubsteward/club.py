"""ClubSteward club CLI — manage multiple clubs, white-labeled.

Usage:
  uv run python -m clubsteward.club list
  uv run python -m clubsteward.club new <id> --name "Mein Verein e.V." [--tagline "..."] [--color "#15803d"]
  uv run python -m clubsteward.club run <id>          # nightly pipeline for that club
  uv run python -m clubsteward.club decide <id>       # decision queue for that club
  uv run python -m clubsteward.club status <id>       # inbox/outbox/decisions/register overview
  uv run python -m clubsteward.club reset <id>        # restore corpus into inbox
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLUBS = ROOT / "clubs"

C_TITLE, C_GREEN, C_DIM, R = "\033[1;96m", "\033[92m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    C_TITLE = C_GREEN = C_DIM = R = ""


def club_dirs() -> list[Path]:
    if not CLUBS.exists():
        return []
    return sorted(d for d in CLUBS.iterdir() if d.is_dir() and (d / "policy.yaml").exists())


def load_brand(club_dir: Path) -> dict:
    import yaml
    p = club_dir / "brand.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def cmd_list(_args=None) -> int:
    dirs = club_dirs()
    if not dirs:
        print("No clubs yet. Create one:  uv run python -m clubsteward.club new <id> --name '...' ")
        return 0
    print(f"{C_TITLE}Clubs ({len(dirs)}):{R}")
    for d in dirs:
        b = load_brand(d)
        name = b.get("name", d.name)
        tagline = b.get("tagline", "")
        color = (b.get("colors") or {}).get("primary", "")
        n_inbox = len(list((d / "inbox").glob("*.eml"))) if (d / "inbox").exists() else 0
        n_dec = len(list((d / "decisions").glob("*.json"))) if (d / "decisions").exists() else 0
        n_out = len(list((d / "outbox").glob("*.eml"))) if (d / "outbox").exists() else 0
        print(f"  {C_GREEN}{d.name:16}{R} {name}")
        if tagline:
            print(f"  {'':16} {C_DIM}{tagline}{R}")
        print(f"  {'':16} {C_DIM}inbox={n_inbox} decisions={n_dec} drafts={n_out} color={color or '-'}{R}")
    return 0


def cmd_new(args) -> int:
    club_id = args.id.lower().strip()
    if not club_id.replace("-", "").isalnum():
        print("Club id must be alphanumeric/dashes")
        return 2
    d = CLUBS / club_id
    if d.exists():
        print(f"Club '{club_id}' already exists")
        return 2
    template = CLUBS / args.template if args.template else None
    if template and template.exists():
        shutil.copytree(template, d)
        # fresh runtime state
        for sub in ("inbox", "outbox", "decisions", "processed", "sessions"):
            shutil.rmtree(d / sub, ignore_errors=True)
            (d / sub).mkdir(parents=True)
            (d / sub / ".gitkeep").touch()
    else:
        for sub in ("corpus", "inbox", "outbox", "decisions", "processed", "sessions"):
            (d / sub).mkdir(parents=True)
            (d / sub / ".gitkeep").touch()
        (d / "policy.yaml").write_text(TEMPLATE_POLICY.format(club_name=args.name, signature=args.name), encoding="utf-8")
        (d / "corpus" / "register.csv").write_text(TEMPLATE_REGISTER, encoding="utf-8")
    # brand.yaml (new or overwritten fields)
    import yaml
    brand_p = d / "brand.yaml"
    brand = load_brand(d) if brand_p.exists() else {}
    brand.update({"name": args.name, "tagline": args.tagline or brand.get("tagline", ""), "locale": args.locale})
    if args.color:
        brand.setdefault("colors", {})
        brand["colors"]["primary"] = args.color
    brand_p.write_text(yaml.safe_dump(brand, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"{C_GREEN}Club created:{R} {club_id}")
    print(f"  dir:    {d}")
    print(f"  brand:  {args.name}" + (f" — {args.tagline}" if args.tagline else ""))
    print(f"  next:   put sample mails in {d}/corpus, edit {d}/policy.yaml")
    print(f"  run:    uv run python -m clubsteward.club run {club_id}")
    return 0


def cmd_run(args) -> int:
    from .pipeline import run
    return run(club=args.id)


def cmd_decide(args) -> int:
    from .decide import run
    return run(assume=args.assume, club=args.id)


def cmd_status(args) -> int:
    d = CLUBS / args.id
    if not d.exists():
        print(f"Unknown club '{args.id}' — see: club list")
        return 2
    b = load_brand(d)
    print(f"{C_TITLE}=== {b.get('name', args.id)} ==={R}")
    if b.get("tagline"):
        print(f"{C_DIM}{b['tagline']}{R}")
    for sub, label in (("inbox", "📥 Inbox"), ("decisions", "⚖️  Entscheidungen"), ("outbox", "📤 Outbox (Entwürfe)"), ("processed", "✅ Erledigt")):
        p = d / sub
        n = len([f for f in p.iterdir() if f.suffix in (".eml", ".json")]) if p.exists() else 0
        print(f"  {label}: {n}")
    reg = d / "register.csv"
    if reg.exists():
        lines = reg.read_text(encoding="utf-8").strip().splitlines()
        print(f"  👥 Mitglieder: {max(0, len(lines) - 1)}")
    return 0


def cmd_reset(args) -> int:
    d = CLUBS / args.id
    corpus = d / "corpus"
    if not corpus.exists():
        print(f"Club '{args.id}' has no corpus/ to reset from")
        return 2
    for sub in ("inbox", "outbox", "decisions", "processed", "sessions"):
        shutil.rmtree(d / sub, ignore_errors=True)
        (d / sub).mkdir(parents=True)
        (d / sub / ".gitkeep").touch()
    for f in sorted(corpus.glob("*.eml")):
        shutil.copy(f, d / "inbox" / f.name)
    reg = corpus / "register.csv"
    if reg.exists():
        shutil.copy(reg, d / "register.csv")
    pol = corpus / "policy.yaml"
    if pol.exists():
        shutil.copy(pol, d / "policy.yaml")
    log = d / "activity.log"
    if log.exists():
        log.unlink()
    print(f"{C_GREEN}Reset:{R} {args.id} — inbox={len(list((d/'inbox').glob('*.eml')))} mails, frisches Register")
    return 0


TEMPLATE_POLICY = """# ClubSteward-Policy — hier regelt der Vorstand, was der Agent allein darf.
club_name: {club_name}
season: "2026"
fees:
  jahresbeitrag: 60.0
tone: freundlich, herzlich, knapp — auf Deutsch
reply_signature: |
  Der Vorstand, {club_name}
  (Entwurf erstellt von ClubSteward, dem Vereins-Agenten — vom Menschen freigegeben)
rules:
  - intent: signup
    decision: auto
    note: Beitritte sind Routine
    ask_if: []
  - intent: address_change
    decision: auto
    note: reine Datenpflege
  - intent: cancellation
    decision: ask
    note: der Vorstand will persönlich antworten
  - intent: hardship_waiver
    decision: ask
    note: Geld + Menschlichkeit entscheidet immer ein Mensch
  - intent: question
    decision: auto
    note: Auskünfte sind Routine
  - intent: complaint
    decision: ask
    note: Konflikte brauchen ein menschliches Wort
  - intent: spam
    decision: reject
    note: Wegwerfen
  - intent: unknown
    decision: ask
    note: nie raten
"""

TEMPLATE_REGISTER = """member_id,first_name,last_name,email,birth_year,team,fee_status,joined,notes
"""


def main() -> int:
    ap = argparse.ArgumentParser(prog="clubsteward.club", description="Manage white-labeled clubs")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="list all clubs")
    n = sub.add_parser("new", help="create a club")
    n.add_argument("id")
    n.add_argument("--name", required=True)
    n.add_argument("--tagline", default="")
    n.add_argument("--color", default="")
    n.add_argument("--locale", default="de")
    n.add_argument("--template", default="", help="copy policy/corpus from an existing club id")
    r = sub.add_parser("run", help="nightly pipeline for a club")
    r.add_argument("id")
    d = sub.add_parser("decide", help="decision queue for a club")
    d.add_argument("id")
    d.add_argument("--assume", default=None)
    s = sub.add_parser("status", help="overview for a club")
    s.add_argument("id")
    x = sub.add_parser("reset", help="reset club sandbox from corpus")
    x.add_argument("id")

    args = ap.parse_args()
    return {"list": cmd_list, "new": cmd_new, "run": cmd_run, "decide": cmd_decide, "status": cmd_status, "reset": cmd_reset}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
