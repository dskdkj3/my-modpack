#!/usr/bin/env python3
"""Generate StoneBlock 4 Packwiz profiles from FTB and VM manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote


FTB_MODPACK_ID = 130
FTB_VERSION_ID = 100312
MINECRAFT_VERSION = "1.21.1"
NEOFORGE_VERSION = "21.1.228"
JAVA_VERSION = "21.0.4+7-LTS"
PACK_VERSION = "1.13.1+zh+dh"

VM_REPO = "VM-Chinese-translate-group/StoneBlock4-Chinese"
VM_TAG = "1.13.1"
VM_ASSET = "FTB-StoneBlock4-1.13.1_V1.zip"
VM_RELEASE_URL = (
    "https://github.com/"
    f"{VM_REPO}/releases/download/{VM_TAG}/{VM_ASSET}"
)
VM_RAW_BASE = f"https://raw.githubusercontent.com/{VM_REPO}/{VM_TAG}/CNPack"
VM_EXCLUDED_SUBSTRINGS = ("别给玩家", "誰人的日志", "谁人的日志")

EXTRA_CLIENT_FILES = [
    {
        "name": "Distant Horizons 3.0.3-b",
        "path": "mods/DistantHorizons-3.0.3-b-1.21.1-fabric-neoforge.jar",
        "side": "client",
        "url": "https://cdn.modrinth.com/data/uCdwusMi/versions/oYXIfeus/DistantHorizons-3.0.3-b-1.21.1-fabric-neoforge.jar",
        "hash": "bc865b11c94581949384b6d5820b58aee8b7273c",
        "hash_format": "sha1",
        "sha512": "8b39994ee6c5d71b8afacc80c2d13dd92fad10281374392c0049d1b6aebc823d7e137125268dee7383d3ff753eacf708fbe87d773cf0087d7b6057a05cf18ad3",
        "update": {
            "modrinth": {
                "mod-id": "uCdwusMi",
                "version": "oYXIfeus",
            },
        },
    },
    {
        "name": "Euphoria Patcher 1.8.6-r5.7.1",
        "path": "mods/EuphoriaPatcher-1.8.6-r5.7.1-neoforge.jar",
        "side": "client",
        "url": "https://cdn.modrinth.com/data/4H6sumDB/versions/m7RqzZJP/EuphoriaPatcher-1.8.6-r5.7.1-neoforge.jar",
        "hash": "48e7c3aa59315069b79025f09bc2f291569c8a2a",
        "hash_format": "sha1",
        "sha512": "da27371209629901a2e01d3413f08677119a5a9aa8deda8dc787b6124d2240e2ea748865a6b3a3065cca81428d57ffe4a8db855d19517aa6c3ec41c14535fd7e",
        "update": {
            "modrinth": {
                "mod-id": "4H6sumDB",
                "version": "m7RqzZJP",
            },
        },
    },
]


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def normalize_manifest_path(path: str, filename: str) -> str:
    base = path.removeprefix("./").strip("/")
    rel = PurePosixPath(base) / filename if base else PurePosixPath(filename)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"unsafe manifest path: {path!r} {filename!r}")
    return rel.as_posix()


def raw_url_for_cnpack_path(path: str) -> str:
    return VM_RAW_BASE + "/" + "/".join(quote(part) for part in path.split("/"))


def side_for_file(entry: dict) -> str:
    if entry.get("clientonly"):
        return "client"
    if entry.get("serveronly"):
        return "server"
    return "both"


def write_metafile(profile: Path, rel_path: str, meta: dict) -> None:
    rel = PurePosixPath(rel_path)
    target = profile / rel.parent / f"{rel.name}.pw.toml"
    target.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"name = {toml_string(meta['name'])}",
        f"filename = {toml_string(rel.name)}",
        f"side = {toml_string(meta['side'])}",
        "",
        "[download]",
        f"url = {toml_string(meta['url'])}",
        f"hash-format = {toml_string(meta['hash_format'])}",
        f"hash = {toml_string(meta['hash'])}",
    ]
    if update := meta.get("update"):
        for update_type, values in update.items():
            lines.extend(["", f"[update.{update_type}]"])
            for key, value in values.items():
                lines.append(f"{key} = {toml_string(value)}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_pack_toml(profile: Path, name: str) -> None:
    profile.mkdir(parents=True, exist_ok=True)
    (profile / ".packwizignore").write_text(
        "\n".join(
            [
                ".packwizignore",
                "*.mrpack",
                "*.zip",
                "*.jar",
                "dist/",
                "README.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (profile / "pack.toml").write_text(
        "\n".join(
            [
                f"name = {toml_string(name)}",
                f"author = {toml_string('FTB Team, VM Chinese translate group, dskdkj3')}",
                f"version = {toml_string(PACK_VERSION)}",
                'pack-format = "packwiz:1.1.0"',
                "",
                "[index]",
                'file = "index.toml"',
                'hash-format = "sha256"',
                'hash = ""',
                "",
                "[versions]",
                f'minecraft = "{MINECRAFT_VERSION}"',
                f'neoforge = "{NEOFORGE_VERSION}"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (profile / "index.toml").write_text('hash-format = "sha256"\n\n', encoding="utf-8")


def vm_entries(vm_zip_path: Path) -> list[dict]:
    entries: list[dict] = []
    with zipfile.ZipFile(vm_zip_path) as zf:
        for info in zf.infolist():
            path = info.filename
            if path.endswith("/") or any(marker in path for marker in VM_EXCLUDED_SUBSTRINGS):
                continue
            data = zf.read(info)
            entries.append(
                {
                    "name": f"VM Chinese Translation: {path}",
                    "path": path,
                    "side": "client",
                    "url": raw_url_for_cnpack_path(path),
                    "hash": hashlib.sha256(data).hexdigest(),
                    "hash_format": "sha256",
                }
            )
    return entries


def server_vm_entries(entries: list[dict]) -> list[dict]:
    server_entries = []
    for entry in entries:
        path = entry["path"]
        if path.startswith("config/ftbquests/quests/"):
            server_entry = dict(entry)
            server_entry["side"] = "both"
            server_entries.append(server_entry)
    return server_entries


def ftb_entries(manifest: dict) -> list[dict]:
    entries = []
    for item in manifest["files"]:
        rel_path = normalize_manifest_path(item["path"], item["name"])
        hashes = item.get("hashes") or {}
        sha256 = hashes.get("sha256")
        if not sha256:
            raise ValueError(f"missing sha256 for {rel_path}")
        url = item.get("url")
        if not url:
            raise ValueError(f"missing url for {rel_path}")
        entries.append(
            {
                "name": item["name"],
                "path": rel_path,
                "side": side_for_file(item),
                "url": url,
                "hash": sha256,
                "hash_format": "sha256",
                "clientonly": bool(item.get("clientonly")),
                "serveronly": bool(item.get("serveronly")),
            }
        )
    return entries


def write_profile(
    profile: Path,
    pack_name: str,
    entries: list[dict],
    overlay_entries: list[dict],
    extra_entries: list[dict] | None = None,
) -> int:
    if profile.exists():
        shutil.rmtree(profile)
    write_pack_toml(profile, pack_name)

    overlay_paths = {entry["path"] for entry in overlay_entries}
    count = 0
    for entry in entries:
        if entry["path"] in overlay_paths:
            continue
        write_metafile(profile, entry["path"], entry)
        count += 1
    for entry in overlay_entries:
        write_metafile(profile, entry["path"], entry)
        count += 1
    for entry in extra_entries or []:
        write_metafile(profile, entry["path"], entry)
        count += 1
    return count


def write_client_overrides(profile: Path) -> None:
    overrides = profile / "overrides"
    (overrides / "config").mkdir(parents=True, exist_ok=True)
    (overrides / "options.txt").write_text(
        "\n".join(
            [
                "lang:zh_cn",
                "skipMultiplayerWarning:true",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (overrides / "config" / "iris.properties").write_text(
        "\n".join(
            [
                "colorSpace=SRGB",
                "disableUpdateMessage=true",
                "enableDebugOptions=false",
                "maxShadowRenderDistance=8",
                "shaderPack=ComplementaryReimagined_r5.7.1.zip",
                "enableShaders=true",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ftb-manifest", required=True, type=Path)
    parser.add_argument("--vm-zip", required=True, type=Path)
    parser.add_argument("--output", default=Path("."), type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.ftb_manifest.read_text(encoding="utf-8"))
    entries = ftb_entries(manifest)
    vm_client = vm_entries(args.vm_zip)
    vm_server = server_vm_entries(vm_client)

    client_entries = [entry for entry in entries if not entry["serveronly"]]
    server_entries = [entry for entry in entries if not entry["clientonly"]]

    client_count = write_profile(
        args.output / "client",
        "FTB StoneBlock 4 1.13.1 + zh + DH",
        client_entries,
        vm_client,
        EXTRA_CLIENT_FILES,
    )
    write_client_overrides(args.output / "client")
    server_count = write_profile(
        args.output / "server",
        "FTB StoneBlock 4 1.13.1 Server + zh",
        server_entries,
        vm_server,
    )

    print(
        json.dumps(
            {
                "ftb_files": len(entries),
                "client_files": client_count,
                "server_files": server_count,
                "vm_client_files": len(vm_client),
                "vm_server_files": len(vm_server),
                "extra_client_files": len(EXTRA_CLIENT_FILES),
                "ftb_modpack_id": FTB_MODPACK_ID,
                "ftb_version_id": FTB_VERSION_ID,
                "minecraft": MINECRAFT_VERSION,
                "neoforge": NEOFORGE_VERSION,
                "java": JAVA_VERSION,
                "vm_release_url": VM_RELEASE_URL,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
