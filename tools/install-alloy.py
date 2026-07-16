#!/usr/bin/env python3
"""Install Archwright's pinned Alloy runtime after SHA-256 verification."""

import hashlib
import json
import sys
import urllib.request
from pathlib import Path


ROOT = Path(__file__).parent.parent
MANIFEST = Path(__file__).with_name("alloy-runtime.json")


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def install():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    destination = ROOT / ".references" / manifest["filename"]
    if destination.is_file() and file_sha256(destination) == manifest["sha256"]:
        return {"status": "pass", "version": manifest["version"], "path": str(destination), "downloaded": False}

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".download")
    urllib.request.urlretrieve(manifest["url"], temporary)
    actual = file_sha256(temporary)
    if actual != manifest["sha256"]:
        temporary.unlink(missing_ok=True)
        raise ValueError(f"Alloy SHA-256 mismatch: expected {manifest['sha256']}, got {actual}")
    temporary.replace(destination)
    return {"status": "pass", "version": manifest["version"], "path": str(destination), "downloaded": True}


def main():
    try:
        result = install()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "error", "errors": [str(error)]}))
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
