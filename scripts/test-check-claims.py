#!/usr/bin/env python3
"""Regression suite for check-claims.py.

    python3 scripts/test-check-claims.py

Each fixture in scripts/fixtures/ asserts one outcome. The suite exists because
check-claims.py is the gate on the site's central rule, and a checker nobody tests is
a checker that quietly stops checking. Two of these cases are real bugs that shipped:

  * the citation year. C-054 carries the scope caveat "do not generalise", which the
    register once read as a publication ban. That held the whole row back, which made
    every numeral in it banned, which banned "2025" site-wide — on a register that
    mandates "Donati & Rao, 2025" in every source line. pass.html carries that source
    line, so this suite fails if the bug returns.

  * the comparison. pass.html encoded the three-way MAD ranking until D-023 withheld
    C-006 through C-009. The checker caught the stale fixture rather than the fixture
    hiding the change, which is the behaviour being locked in here.

The quotation pair is the one to read before widening anything. quote-abstract.html is
the case the shield exists for; fail-quote-unattributed.html is the same mechanism used
as a loophole, in the three shapes it could take. If a change makes the first pass and
the second pass too, the shield has stopped being a shield.

Run it after touching check-claims.py, and after any change to the status vocabulary
or the publication rules in CLAIMS.md.
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKER = os.path.join(REPO, "scripts", "check-claims.py")
FIXTURES = os.path.join(REPO, "scripts", "fixtures")

# (fixture, expected exit, what it proves)
CASES = [
    ("pass-own-record.html", 0,
     "first-party figures with NO source line - the citation rule, and the half that "
     "fail-provenance.html cannot assert. If both ever pass, citation has stopped "
     "applying to anything"),
    ("pass.html", 0,
     "annotated copy deck with every figure sourced - including the 2025 citation year"),
    ("fail-unsourced.html", 1, "a numeral with no VERIFIED row"),
    ("fail-placeholder.html", 1, "a PLACEHOLDER value published"),
    ("fail-withheld.html", 1, "a WITHHELD value published, and rounding does not launder it"),
    ("fail-provenance.html", 1, "a stat cell with no source line in the same visual unit"),
    ("fail-phrase.html", 1, "platform language, against publication rule 2"),
    ("fail-mixed-heuristic.html", 1, "un-annotated page, invented figures caught by scan"),
    ("quote-abstract.html", 0,
     "the paper's abstract quoted verbatim - $0.30 shielded as attributed speech, warned"),
    ("fail-quote-unattributed.html", 1,
     "quotation used as a loophole: no attribution, a non-id source, a withheld source"),
]


def main():
    if not os.path.isdir(FIXTURES):
        print(f"no fixtures at {FIXTURES}")
        return 2

    failures = []
    for name, expected, what in CASES:
        path = os.path.join(FIXTURES, name)
        if not os.path.exists(path):
            failures.append((name, "missing", expected, what))
            print(f"  MISS {name:28s} fixture not found")
            continue
        code = subprocess.run(
            [sys.executable, CHECKER, "--only-failures", path],
            capture_output=True, text=True).returncode
        ok = code == expected
        print(f"  {'ok  ' if ok else 'FAIL'} {name:28s} exit {code} "
              f"(want {expected})  {what}")
        if not ok:
            failures.append((name, code, expected, what))

    print()
    if failures:
        print(f"{len(failures)} case(s) did not behave as expected:")
        for name, got, expected, what in failures:
            print(f"  {name}: got {got}, wanted {expected} — {what}")
        print("\nEither check-claims.py regressed, or CLAIMS.md changed in a way the")
        print("fixture no longer reflects. Read the failure before editing the fixture:")
        print("a stale fixture is the checker working, not the checker broken.")
        return 1
    print(f"All {len(CASES)} cases behave as expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
