# FTB StoneBlock 4 Packwiz

Private Packwiz profiles for Hopper's `desktop` StoneBlock 4 deployment.

- `server/`: server-side profile consumed by `nixos-config` through `pkgs.fetchPackwizModpack`.
- `client/`: client-side profile and HMCL/PCL2 `.mrpack` source.

Base pack: FTB StoneBlock 4 `1.13.1`, FTB pack `130`, FTB version `100312`, Minecraft `1.21.1`, NeoForge `21.1.228`, Java `21.0.4+7-LTS`.

Client additions:

- VM Chinese translation release `1.13.1`.
- Distant Horizons `3.0.3-b-1.21.1` for NeoForge/Fabric.
- Euphoria Patcher `1.8.6-r5.7.1-neoforge`.
- FTB's bundled Complementary Reimagined `r5.7.1`; this branch intentionally does not upgrade to `r5.8`.
- Default client overrides for `zh_cn` and Iris shader activation.

This branch is for a small private friend group. Do not publish the generated `.mrpack` as a public Modrinth pack.

## Generate

```bash
curl -fsSL https://api.feed-the-beast.com/v1/modpacks/public/modpack/130/100312 \
  -o /tmp/stoneblock4-ftb-130-100312.json
curl -fL https://github.com/VM-Chinese-translate-group/StoneBlock4-Chinese/releases/download/1.13.1/FTB-StoneBlock4-1.13.1_V1.zip \
  -o /tmp/FTB-StoneBlock4-1.13.1_V1.zip

python3 tools/generate-stoneblock4-packwiz.py \
  --ftb-manifest /tmp/stoneblock4-ftb-130-100312.json \
  --vm-zip /tmp/FTB-StoneBlock4-1.13.1_V1.zip \
  --output .

packwiz refresh --pack-file server/pack.toml
packwiz refresh --pack-file client/pack.toml

python3 tools/export-stoneblock4-mrpack.py \
  --ftb-manifest /tmp/stoneblock4-ftb-130-100312.json \
  --vm-zip /tmp/FTB-StoneBlock4-1.13.1_V1.zip \
  --client-profile client \
  --output /srv/xsy-agent-share/FTB-StoneBlock-4-1.13.1+zh+dh.mrpack
```

`packwiz modrinth export` is not used for this pack because it can hang while resolving this large FTB/VM mixed-source profile. The checked-in exporter writes the `.mrpack` index directly from pinned upstream manifests and includes only small override files in the archive.

## Launcher Notes

The generated `.mrpack` targets HMCL and PCL2. If a launcher refuses non-Modrinth download domains, install the official FTB StoneBlock 4 `1.13.1` client first and then import or copy this branch's client additions manually.
