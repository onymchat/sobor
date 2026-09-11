#!/usr/bin/env python3
"""Read the RSVP register back off the Stellar ledger.

Every RSVP is a 1-stroop payment to the sobor account carrying a text memo:

    sobor2026 p 0009     in person, seats 0 and 3
    sobor2026 r ffff     remote, all sixteen
    sobor2026 out        withdrawn

Latest transaction per sender wins, and `out` is a tombstone — so the current register
is a fold over the account's payment history. There is no database anywhere; this only
reads what anyone else can read.

    python3 tools/register.py            # write content/register.json
    python3 tools/register.py --show     # also print what it found

Writes an honestly empty register when the account is unset or has no RSVPs yet.
Stdlib only. Run it, then `python3 tools/build.py`, then commit both.
"""
import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
RSVP = json.loads((ROOT / "content" / "rsvp.json").read_text(encoding="utf-8"))
I18N = json.loads((ROOT / "content" / "i18n.json").read_text(encoding="utf-8"))
SEATS = [s["h"] for s in I18N["en"]["seats"]["items"]]

ACCOUNT = RSVP.get("account", "").strip()
HORIZON = RSVP.get("horizon", "https://horizon.stellar.org").rstrip("/")
EVENT = RSVP["event"]

# MTLAP / MTLAC are the Montelibero Association participation tokens; holding one is
# what "pre-approved" means on the site. Same issuer for both.
MTLA_ISSUER = "GCNVDZIHGX473FEI7IXCUAEXUJ4BGCKEMHF36VYP5EMS7PX2QBLAMTLA"
MEMO_RE = re.compile(r"^%s (?:(p|r) ([0-9a-f]{4})|out)$" % re.escape(EVENT))


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def payments(account):
    """Every payment into the account, oldest first, with its transaction joined on."""
    url = "%s/accounts/%s/payments?%s" % (HORIZON, account, urllib.parse.urlencode(
        {"join": "transactions", "order": "asc", "limit": 200}))
    while url:
        try:
            page = get(url)
        except urllib.error.HTTPError as ex:
            if ex.code == 404:
                return                      # account not funded yet — no RSVPs, not an error
            raise
        records = page.get("_embedded", {}).get("records", [])
        if not records:
            return
        for rec in records:
            yield rec
        url = page.get("_links", {}).get("next", {}).get("href")


def is_pre_approved(account):
    try:
        acct = get("%s/accounts/%s" % (HORIZON, account))
    except urllib.error.HTTPError:
        return False
    for b in acct.get("balances", []):
        if b.get("asset_issuer") == MTLA_ISSUER and b.get("asset_code") in ("MTLAP", "MTLAC"):
            if float(b.get("balance", "0")) > 0:
                return True
    return False


def build():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    empty = {"account": ACCOUNT, "synced": now, "count": 0, "in_person": 0,
             "remote": 0, "pre_approved": 0, "seats": {}, "senders": []}
    if not ACCOUNT:
        return empty, "no account configured — register is empty by definition"

    latest = {}                              # sender -> (mode, mask) or None for withdrawn
    seen = 0
    for rec in payments(ACCOUNT):
        if rec.get("to") != ACCOUNT or rec.get("type") != "payment":
            continue
        tx = rec.get("transaction") or {}
        if tx.get("memo_type") != "text":
            continue
        m = MEMO_RE.match((tx.get("memo") or "").strip().lower())
        if not m:
            continue
        seen += 1
        sender = rec.get("from")
        latest[sender] = None if m.group(1) is None else (m.group(1), int(m.group(2), 16))

    live = {k: v for k, v in latest.items() if v}
    seats = {}
    for mode, mask in live.values():
        for i in range(16):
            if mask & (1 << i):
                seats[SEATS[i]] = seats.get(SEATS[i], 0) + 1

    senders = sorted(live)
    return {
        "account": ACCOUNT,
        "synced": now,
        "count": len(live),
        "in_person": sum(1 for m, _ in live.values() if m == "p"),
        "remote": sum(1 for m, _ in live.values() if m == "r"),
        "pre_approved": sum(1 for s in senders if is_pre_approved(s)),
        "seats": dict(sorted(seats.items(), key=lambda kv: -kv[1])),
        "senders": senders,
    }, "%d matching memo(s), %d live after withdrawals" % (seen, len(live))


def main():
    reg, note = build()
    out = ROOT / "content" / "register.json"
    out.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  %s" % note)
    print("  wrote content/register.json — %d RSVP(s), %d pre-approved"
          % (reg["count"], reg["pre_approved"]))
    if "--show" in sys.argv:
        print(json.dumps(reg, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
