#!/usr/bin/env python3
"""Generate raw sprite image(s) from a text prompt via the Nano Banana API.

Does NOT post-process. Pipe the output through pixelize.py.
"""
import argparse
import sys

from lib import client as C
from lib.paths import numbered_path


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="Generate raw sprite images.")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pro", action="store_true", help="use Nano Banana Pro")
    ap.add_argument("--reference", action="append", default=[],
                    help="reference PNG path (repeatable)")
    ap.add_argument("--count", type=int, default=1)
    return ap.parse_args(argv)


def chosen_model(ns):
    return C.model_id(pro=ns.pro)


def _load_refs(paths):
    refs = []
    for p in paths:
        with open(p, "rb") as f:
            refs.append(f.read())
    return refs


def main(argv=None):
    ns = parse_args(argv)
    model = chosen_model(ns)
    refs = _load_refs(ns.reference)
    for i in range(ns.count):
        png = C.generate_image(ns.prompt, model=model, reference_images=refs)
        p = numbered_path(ns.out, i, ns.count)
        with open(p, "wb") as f:
            f.write(png)
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
