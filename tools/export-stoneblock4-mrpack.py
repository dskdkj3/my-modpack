#!/usr/bin/env python3
"""Export the generated StoneBlock 4 client profile as a private .mrpack."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote


MINECRAFT_VERSION = "1.21.1"
NEOFORGE_VERSION = "21.1.228"
PACK_VERSION = "1.13.1+zh+dh"
VM_REPO = "VM-Chinese-translate-group/StoneBlock4-Chinese"
VM_TAG = "1.13.1"
VM_RAW_BASE = f"https://raw.githubusercontent.com/{VM_REPO}/{VM_TAG}/CNPack"
VM_EXCLUDED_SUBSTRINGS = ("别给玩家", "誰人的日志", "谁人的日志")

EXTRA_CLIENT_FILES = [
    {
        "path": "mods/DistantHorizons-3.0.3-b-1.21.1-fabric-neoforge.jar",
        "downloads": [
            "https://cdn.modrinth.com/data/uCdwusMi/versions/oYXIfeus/DistantHorizons-3.0.3-b-1.21.1-fabric-neoforge.jar"
        ],
        "hashes": {
            "sha1": "bc865b11c94581949384b6d5820b58aee8b7273c",
            "sha512": "8b39994ee6c5d71b8afacc80c2d13dd92fad10281374392c0049d1b6aebc823d7e137125268dee7383d3ff753eacf708fbe87d773cf0087d7b6057a05cf18ad3",
        },
        "env": {"client": "required", "server": "unsupported"},
    },
    {
        "path": "mods/EuphoriaPatcher-1.8.6-r5.7.1-neoforge.jar",
        "downloads": [
            "https://cdn.modrinth.com/data/4H6sumDB/versions/m7RqzZJP/EuphoriaPatcher-1.8.6-r5.7.1-neoforge.jar"
        ],
        "hashes": {
            "sha1": "48e7c3aa59315069b79025f09bc2f291569c8a2a",
            "sha512": "da27371209629901a2e01d3413f08677119a5a9aa8deda8dc787b6124d2240e2ea748865a6b3a3065cca81428d57ffe4a8db855d19517aa6c3ec41c14535fd7e",
        },
        "env": {"client": "required", "server": "unsupported"},
    },
]


def normalize_manifest_path(path: str, filename: str) -> str:
    base = path.removeprefix("./").strip("/")
    rel = PurePosixPath(base) / filename if base else PurePosixPath(filename)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"unsafe manifest path: {path!r} {filename!r}")
    return rel.as_posix()


def raw_url_for_cnpack_path(path: str) -> str:
    return VM_RAW_BASE + "/" + "/".join(quote(part, safe="") for part in path.split("/"))


def env_for_file(clientonly: bool) -> dict[str, str]:
    if clientonly:
        return {"client": "required", "server": "unsupported"}
    return {"client": "required", "server": "required"}


def ftb_index_files(manifest: dict) -> list[dict]:
    files = []
    for item in manifest["files"]:
        if item.get("serveronly"):
            continue
        hashes = item.get("hashes") or {}
        path = normalize_manifest_path(item["path"], item["name"])
        files.append(
            {
                "path": path,
                "hashes": {
                    "sha1": hashes["sha1"],
                    "sha512": hashes["sha512"],
                },
                "env": env_for_file(bool(item.get("clientonly"))),
                "downloads": [item["url"]],
                "fileSize": item.get("size"),
            }
        )
    return files


def vm_index_files(vm_zip_path: Path) -> list[dict]:
    files = []
    with zipfile.ZipFile(vm_zip_path) as zf:
        for info in zf.infolist():
            path = info.filename
            if path.endswith("/") or any(marker in path for marker in VM_EXCLUDED_SUBSTRINGS):
                continue
            data = zf.read(info)
            files.append(
                {
                    "path": path,
                    "hashes": {
                        "sha1": hashlib.sha1(data).hexdigest(),
                        "sha512": hashlib.sha512(data).hexdigest(),
                    },
                    "env": {"client": "required", "server": "unsupported"},
                    "downloads": [raw_url_for_cnpack_path(path)],
                    "fileSize": len(data),
                }
            )
    return files


def write_overrides(zip_out: zipfile.ZipFile, overrides_dir: Path) -> int:
    if not overrides_dir.exists():
        return 0
    count = 0
    for path in sorted(overrides_dir.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(overrides_dir).as_posix()
        zip_out.write(path, f"overrides/{rel}")
        count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ftb-manifest", required=True, type=Path)
    parser.add_argument("--vm-zip", required=True, type=Path)
    parser.add_argument("--client-profile", default=Path("client"), type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.ftb_manifest.read_text(encoding="utf-8"))
    files = ftb_index_files(manifest)
    overlay_paths = {entry["path"] for entry in vm_index_files(args.vm_zip)}
    files = [entry for entry in files if entry["path"] not in overlay_paths]
    files.extend(vm_index_files(args.vm_zip))
    files.extend(EXTRA_CLIENT_FILES)
    files.sort(key=lambda entry: entry["path"])

    index = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": PACK_VERSION,
        "name": "FTB StoneBlock 4 1.13.1 + zh + DH",
        "summary": "Private HMCL/PCL2 client pack with VM Chinese translation, Distant Horizons, Complementary Reimagined r5.7.1, and Euphoria Patches.",
        "files": files,
        "dependencies": {
            "minecraft": MINECRAFT_VERSION,
            "neoforge": NEOFORGE_VERSION,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as zip_out:
        zip_out.writestr(
            "modrinth.index.json",
            json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )
        override_count = write_overrides(zip_out, args.client_profile / "overrides")

    print(
        json.dumps(
            {
                "output": str(args.output),
                "files": len(files),
                "overrides": override_count,
                "minecraft": MINECRAFT_VERSION,
                "neoforge": NEOFORGE_VERSION,
                "version": PACK_VERSION,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
