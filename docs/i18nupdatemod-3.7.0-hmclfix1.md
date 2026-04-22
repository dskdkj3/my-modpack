# I18nUpdateMod 3.7.0 HMCL 热修复

## 背景

- 客户端启动时，`I18nUpdateMod` 会同步下载汉化资源包。
- `v3.7.0` 默认的镜像测速逻辑会把 `http://8.137.167.65:64684/` 当成“最快”源，但该源实际吞吐极慢，导致 HMCL 启动卡在资源包下载阶段。
- 现场复现里，该镜像下载 `Minecraft-Mod-Language-Modpack-1-19.zip` 只有约 `3.4 KB/s`，而 GitHub release 约 `350-400 KB/s`。

## 上游基线

- 仓库：`CFPAOrg/I18nUpdateMod3`
- tag：`v3.7.0`
- commit：`2eddc6287f7276850bd79d89ecf3b3534cb82c2e`
- 补丁文件：[`patches/i18nupdatemod-3.7.0-hmclfix1.patch`](../patches/i18nupdatemod-3.7.0-hmclfix1.patch)

## 热修内容

- `getFastestUrl()` 先检查 GitHub index 是否可用；可用时直接选 `https://raw.githubusercontent.com/`
- 其余镜像改为顺序 fallback，不再用“谁先 HEAD 成功就是谁”
- `download()` 改为手动流式下载，并加总超时 `20s`，避免慢速连接无限拖住启动

## 构建方式

```bash
./scripts/build-i18nupdatemod-3.7.0-hmclfix1.sh
```

本地运行脚本需要 `git`、`python3` 和可用的 JDK。

脚本会从上游 `v3.7.0` 拉源码、应用补丁、构建 `shadowJar`，再做一次固定时间戳和排序的稳定重打包，并在 `dist/` 下生成 release asset 和校验文件。

## 发布产物

- release tag：`i18nupdatemod-3.7.0-hmclfix1`
- asset：`I18nUpdateMod-3.7.0-hmclfix1-all.jar`
- sha256：`c56f843a37c341f7c086cee1e6b5a28b02b3958ddf87ad59ad1b04e51435a8ca`
- sha512：`80e4401902bdd33bbad367143b6fd970226a04d58b18123fc6680511db08b3f32a7c212a207364281890a91ce47fa7dd9ebbc797f70762e4bb193569f4feae61`

## 消费方式

- `mods/i18nupdatemod.pw.toml` 固定引用这个 release asset
- 为避免后续 `packwiz update` 覆盖热修，已移除 `update.modrinth`
