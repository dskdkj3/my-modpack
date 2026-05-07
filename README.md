# Prominence II Hasturian Era client profile

This branch contains a Packwiz client profile for Prominence II Hasturian Era 3.9.26 with Distant Horizons enabled for the 32 GiB desktop baseline.

- Minecraft: 1.20.1
- Loader: Fabric 0.18.4
- Shader stack: Iris/Sodium are included, shaders are enabled by default, and Complementary Reimagined r5.7.1 is the selected shaderpack.
- Extra client/server-compatible mod: Distant Horizons 3.0.2-b for 1.20.1 Fabric/Forge.
- CurseForge-only FTB dependencies included: FTB Library 2001.2.9, FTB Quests 2001.4.13, FTB Teams 2001.3.1, and FTB XMod Compat 2.1.3.

Import `client/pack.toml` in a Packwiz-capable launcher or serve this profile with Packwiz for HMCL-style import.

For HMCL, set the instance memory manually: disable automatic memory and set maximum memory to `8192 MiB`. This profile keeps Distant Horizons distant generation enabled and uses a high-detail LOD default, so lower memory settings are no longer the intended baseline.
