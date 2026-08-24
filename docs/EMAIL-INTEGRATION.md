# Email Integration — how a club connects its real mailbox

ClubSteward's boundary is deliberately boring: **mails in a folder, drafts in a folder.**
Everything else (IMAP/SMTP) is an adapter at the edge. Three ways to run it:

## Option A — Drag & drop (zero setup, works today)

1. Club runs `scripts/run_web.sh` → opens `http://localhost:8765/app`
2. Volunteers drag `.eml` files from Outlook/Thunderbird onto the console's
   "Drop .eml" button (Outlook: drag mail to desktop → .msg → save-as .eml,
   or use the export function; Gmail: download message → .eml)
3. "Run night" → decisions appear in the console
4. Approved drafts land in the outbox; the volunteer copy-pastes the text into
   their mail client and sends

This is what the demo shows: no credentials, no OAuth, works with every client.

## Option B — IMAP fetch + SMTP send (planned adapter, ~100 lines)

Per-club `mailbox.yaml` (never committed):

```yaml
imap:
  host: imap.gmail.com
  user: vorstand@verein.de
  password_env: CLUB_IMAP_PASSWORD   # app password; Gmail/Outlook 2FA app passwords
  folder: INBOX
  filter: "UNSEEN"
smtp:
  host: smtp.gmail.com
  user: vorstand@verein.de
  password_env: CLUB_SMTP_PASSWORD
  draft_only: true                    # Stage 1: never auto-send, only create drafts
```

The fetch adapter polls the club folder nightly and writes new mails into
`inbox/` (identical format — the pipeline doesn't change). The send adapter
takes approved outbox drafts and (a) uploads them as *drafts* into the
mailbox's Drafts folder (default), or (b) sends directly if the club flips
`draft_only: false` in its policy (explicit opt-in to full automation).

Gmail/Outlook specifics: app passwords with 2FA, or OAuth device flow later.
Never store passwords in the repo — `mailbox.yaml` is gitignored per club.

## Option C — Forwarding address (simplest real integration)

The club sets a forwarding rule ("all mails from contact form → agent@...")
on their mailbox. The agent box runs Option B on a dedicated account —
the club's main mailbox is never touched. Good first step for pilots.

## What we deliberately do NOT do

- No sending without a human approving the draft (policy can only loosen this
  explicitly, per intent, in the club's own policy.yaml)
- No reading of non-inbox folders
- No storage of mail credentials outside the club's own server
