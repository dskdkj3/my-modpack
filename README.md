# FTB Skies 2 Packwiz

Packwiz profiles for Hopper's `desktop` FTB Skies 2 deployment.

- `server/`: server-side pack consumed by `nixos-config` through `pkgs.fetchPackwizModpack`.
- `client/`: client-side pack for launcher import, including Distant Horizons and Complementary Reimagined.

Base pack: FTB Skies 2 1.14.3, Minecraft 1.21.1, NeoForge 21.1.220, Java 21.0.4+7-LTS.

## Update

Regenerate from the FTB API manifest for pack `129` version `100250`, then run `packwiz refresh` in both `server/` and `client/`.
After committing, update the pinned raw `server/pack.toml` URL and fixed-output hash in `nixos-config`.
