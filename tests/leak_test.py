"""leak_test.py - fail if any raw PaySim-style identifier (C1234567890 / M1234567890) appears.

Usage:
  python leak_test.py alerts.csv other_output.txt        # scan files
  docker logs stark-scoring-api 2>&1 | python leak_test.py -   # scan stdin
  python leak_test.py --api http://127.0.0.1:8000        # send a probe, scan the reply
Exit code 0 = clean, 1 = leak found.
"""
import json
import re
import sys
import urllib.request

RAW = re.compile(r"(?<![A-Za-z0-9_])[CM]\d{6,}(?![A-Za-z0-9_])")
TOKEN = re.compile(r"TK_[0-9a-f]{16}")


def scan(name, text):
    hits = sorted(set(RAW.findall(text)))
    tokens = len(TOKEN.findall(text))
    status = "LEAK" if hits else "ok"
    print(f"{status:5} {name}: {tokens} tokens, {len(hits)} raw-looking ids {hits[:3]}")
    return not hits


def api_probe(base):
    raw_c, raw_m = "C1234567890", "M9876543210"
    body = json.dumps({"tx_id": "LEAK1", "customer_id": raw_c, "counterparty_id": raw_m,
                       "amount": 5000, "type": "TRANSFER", "step": 100}).encode()
    req = urllib.request.Request(base + "/score", body, {"Content-Type": "application/json"})
    reply = urllib.request.urlopen(req).read().decode()
    ok = raw_c not in reply and raw_m not in reply
    print(f"{'ok' if ok else 'LEAK':5} API reply: {reply}")
    return ok


def main(args):
    if not args:
        print(__doc__)
        return 2
    results = []
    if args[0] == "--api":
        results.append(api_probe(args[1]))
    else:
        for a in args:
            text = sys.stdin.read() if a == "-" else open(a, encoding="utf-8", errors="ignore").read()
            results.append(scan("stdin" if a == "-" else a, text))
    print("PASS: no raw identifiers found" if all(results) else "FAIL: raw identifiers found")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
