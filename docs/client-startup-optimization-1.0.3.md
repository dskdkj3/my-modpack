# 1.0.3 客户端启动优化

## 背景

- `i18nupdatemod-3.7.0-hmclfix1` 解决了最严重的卡死问题后，`desktop` 上 `1.0.2` 的客户端冷启动仍有约 `10s`。
- `2026-04-23 00:58` 的启动日志显示，剩余耗时里有一部分来自客户端模组自己的启动期联网检查，而不是 HMCL 本体或 `I18nUpdateMod`。

## 收敛内容

- `config/modmenu.json`
  - 关闭 `update_checker`
  - 关闭 `button_update_badge`
- `config/euphoria_patcher/settings.toml`
  - 把 `doUpdateChecking` 从 `"important"` 改为 `"none"`
- `config/xaero/lib/common.cfg`
  - 关闭 `allow_internet_access`
- `config/xaero/minimap/client.cfg`
  - 关闭 `update_notifications`
- `config/xaero/world-map/client.cfg`
  - 关闭 `update_notifications`

这些改动只移除启动期的更新检查，不改变着色器、地图或其他功能默认是否启用。

## packwiz 下发方式

- 这些文件作为普通客户端配置文件进入 `index.toml`
- `preserve = true`
  - 新安装实例会拿到这些默认值
  - 以后用户自己在本地改过这些文件时，pack 更新不会覆盖

## 现有实例迁移

- 脚本：[`scripts/apply-client-startup-optimizations-1.0.3.sh`](../scripts/apply-client-startup-optimizations-1.0.3.sh)
- 默认目标：`~/.minecraft/versions/1.0.2`
- 行为：
  - 先把原文件备份到 `~/.minecraft/.mod-config-backups/<timestamp>-startup-opt-1.0.3/`
  - 再只修改这 5 个已确认会影响启动期联网检查的键

## 暂不纳入 1.0.3 的项

- `Distant Horizons` 仍会在启动时打印更新检查日志，但其现有配置里已经是 `enableAutoUpdater = false`
- 在确认明确有效的配置键之前，不把它混进这次“无损优化”
