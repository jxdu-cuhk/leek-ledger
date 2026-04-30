# Trade Tracker Template

一个本地交易看板模板。这个公开版本只保留可运行框架和空白工作簿，不包含任何真实交易记录、券商导出、标的缓存或个人数据。

## 来源与致谢

本项目基于 B 站 / YouTube UP 主 @靠卖期权实现早日自由 推荐的 Google 表格模板，并使用 Codex 进一步开发为本地 Excel + HTML 看板版本。

原始 Google 表格模板：[Ultimate Options Tracking Spreadsheet - Version 2](https://docs.google.com/spreadsheets/d/1Oe_ETcQWmCRg07Vc_hJb8wrnGS8GGR5yclYFnRpmcd4/copy)

## 使用方式

1. 打开 `Trade Tracker.xlsx`，在 `交易记录` 工作表里录入交易。
2. 双击 `Update Preview.command` 启动本地预览服务。
3. 打开 `Trade Tracker.html` 查看生成后的看板。

## 目录说明

- `Trade Tracker.xlsx`: 空白交易记录模板。
- `Trade Tracker.html`: 看板入口页。
- `Update Preview.command`: 本地预览服务启动脚本。
- `.trade-tracker/tools/`: 看板生成和刷新脚本。
- `.trade-tracker/preview/`: 由空白模板生成的静态预览。

## 隐私说明

公开版本不会提交 `.trade-tracker/history/`、`.trade-tracker/logs/`、`.trade-tracker/tools/cache/` 或真实的 `security_name_cache.json`。如果你基于这个模板记录自己的交易，建议把包含真实数据的仓库设为 private。
