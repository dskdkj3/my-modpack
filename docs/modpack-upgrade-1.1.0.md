# My Modpack 1.1.0 升级说明

## 背景

- 这次升级把 `desktop` 当前 `1.21.1` pack 中仍有更新的关键依赖一次性拉齐。
- 目标是同时覆盖三类问题：
  - 模组自身的版本落后
  - 启动期由旧版更新检查带来的额外噪声
  - `Distant Horizons` 的大版本升级窗口

## 本次升级内容

- `fabric-loader`: `0.18.4 -> 0.19.2`
- `Distant Horizons`: `2.4.5-b -> 3.0.1-b`
- `Fabric API`: `0.116.9+1.21.1 -> 0.116.11+1.21.1`
- `Fabric Language Kotlin`: `1.13.9+kotlin.2.3.10 -> 1.13.10+kotlin.2.3.20`
- `Inventory Profiles Next`: `2.2.4 -> 2.2.6`
- `libIPN`: `6.6.2 -> 6.6.3`
- `Mod Menu`: `11.0.3 -> 11.0.4`

## Warning 处理边界

- 这次主要处理“能通过升级或 pack 默认值解决”的 warning。
- 下面这些仍可能继续出现，但它们不属于本次无损升级的主修范围：
  - `lspci` / `udev` 缺失
  - narrator 的 `flite` 动态库缺失
  - Realms / profile key 的 `401`
  - 某些可选集成的 mixin target not found
  - 第三方汉化资源包自身的 JSON 结构告警

## preserve 语义

- `1.0.3` 引入的 5 个客户端启动优化配置仍保持 `preserve = true`。
- 这意味着：
  - 新实例会拿到这些默认值
  - 已存在实例如果本地已经写过旧配置，不会被 pack 更新自动覆盖
- 所以本次 `1.1.0` 只承诺仓库和后续声明式收敛更新，不承诺直接改变 `desktop` 当前实例里的本地客户端配置。

## 已知风险

- `Distant Horizons` 升到了 `3.0.1-b`，但仓库里配套的 DH 汉化资源包当前仍停留在 `2.4.3` 系列。
- 如果 DH 3.x 新增了配置项或界面文案，相关条目可能会回退成英文，而不是完整中文。
- 这不会阻止游戏启动，但属于本轮可接受的兼容残余。
