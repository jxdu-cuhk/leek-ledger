# 韭菜账本 Leek Ledger 目录说明

日常使用只需要关注主目录这几个入口：

- `Trade Tracker.html`: 最新韭菜账本看板入口。
- `Trade Tracker.xlsx`: 交易记录工作簿，也是唯一手工数据源。
- `Update Preview.command`: 推荐的一键启动入口，会自动检查虚拟环境和依赖。
- `README.md`: 面向使用者的说明。

隐藏支持目录 `.trade-tracker/` 分工：

- `.trade-tracker/preview/`: 自动生成的网页预览文件。
- `.trade-tracker/history/`: 券商导出的历史交易记录，用来补名称、核对交易和识别分红。
- `.trade-tracker/tools/`: 生成网页所需的脚本和核心程序。
- `.trade-tracker/tools/cache/`: 指数、个股历史行情、期权链等本地缓存。
- `.trade-tracker/logs/`: 本地刷新服务日志。
- `.trade-tracker/security_name_cache.json`: 标的名称缓存，避免每次都重新查询。
- `.trade-tracker/DATA_INTERFACES.md`: 当前看板所有显示数据接口、口径来源和待优化点。
- `.venv/`: 本地 Python 运行环境，由 `Update Preview.command` 自动创建。

核心脚本：

- `.trade-tracker/tools/export_trade_tracker_html.py`: 命令行生成入口。
- `.trade-tracker/tools/preview_server.py`: 本地预览和网页刷新服务。
- `.trade-tracker/tools/install_preview_service.py`: macOS LaunchAgent 后台常驻服务安装脚本。
- `.trade-tracker/tools/export_trade_tracker_core.pyc`: 原始看板生成核心。

主要模块：

- `.trade-tracker/tools/trade_tracker/app.py`: 导出流程编排，负责加载核心模块、生成网页、整理输出。
- `.trade-tracker/tools/trade_tracker/patcher.py`: 把持仓、资金口径、交易标签、汇总、行情、刷新面板等扩展挂到核心生成器上。
- `.trade-tracker/tools/trade_tracker/display_payload.py`: 统一展示数据层，先汇总持仓、账户总盈亏、分币种折算、账户级当日盈亏、当前持仓日浮盈、已实现交易列表、已实现日汇总、交易标签、资金口径和数据质量，再给页面区块复用。
- `.trade-tracker/tools/trade_tracker/transaction_tags.py`: 交易标签读取和展示层，识别 `交易记录` 的 `标签` 列，把标签接到交易时间线、盈亏日历和阶段账单。
- `.trade-tracker/tools/trade_tracker/capital_quality.py`: 持仓页的资金口径 / 数据质量区块，把账户资产、风险敞口、期权资金兜底、行情完整度集中展示。
- `.trade-tracker/tools/trade_tracker/dashboard_layout.py`: 顶部业务分组分页、当前页区块快捷跳转、刷新/统一币种操作区、栏目排序、主/辅区块层级和总收益曲线控制区；总收益曲线 hero 首屏占位直接读曲线 payload 的持仓市值现金流收益率；分页配置统一驱动排序和前端按钮，避免重复维护。
- `.trade-tracker/tools/trade_tracker/return_curve.py`: 总收益曲线、baseline、超额收益、K 线、缩放拖动、tooltip，以及指数长期缓存和增量补尾；账户收益率按 `当日盈亏 / (昨日持仓市值 + 今日买入金额)` 逐日连乘，盈亏金额按曲线 `daily_total_value` 逐日累计。
- `.trade-tracker/tools/trade_tracker/daily_pnl_history.py`: 把当前持仓页三个市场的当日浮盈汇总写入本地缓存，并回填到总收益曲线的 `daily_float_value`；`daily_total_value` 始终由累计总盈亏点差得到。
- `.trade-tracker/tools/trade_tracker/historical_curve.py`: 个股真实历史行情、近两周行情缓存刷新、账户总盈亏曲线，以及按月/按年切片的个股收益 payload；个股收益率对齐券商 App 的持仓盈亏率口径，仍持仓标的用总盈亏除以调整后持仓成本，已清仓标的回退到盈亏除以投入本金；券商原始明细回补会限制在导入汇总行自己的日期窗口内，并把交易已实现和分红净额分开输出；聚合行备注写明买入费用和卖出税费时，会把费用拆到正确买入/卖出日期，备注含“本行分摊”时优先取行级卖出费用。
- `.trade-tracker/tools/trade_tracker/holdings_overview.py`: 当前持仓顶部汇总卡，展示持仓总资产、当前持仓总盈亏、总市值和账户级当日盈亏；累计总盈亏不把账户级已实现收益混进持仓页顶部，当日盈亏则读取曲线 `daily_total_value`，包含当天平仓和当前持仓波动。
- `.trade-tracker/tools/trade_tracker/holdings_daily.py`: 当日持仓盈亏分段，A/H 按本地自然日，美股按纽约时间 0 点滚日；当前仍有隔夜仓的普通 T 操作继承行情源昨收涨跌；隔夜仓当天已完全平掉、当前只剩当天重买新仓时，按新仓买入成本到现价计算。
- `.trade-tracker/tools/trade_tracker/reporting_currency.py`: 看板统一口径币种切换。
- `.trade-tracker/tools/trade_tracker/html_tables.py`: 表格列顺序、分年度个股汇总、汇总行、上下横向滚动条、人民币折算汇总。
- `.trade-tracker/tools/trade_tracker/overview.py`: 总体概览、分币种概览和交易费用汇总。
- `.trade-tracker/tools/trade_tracker/options.py`: 期权和已完成现股收益口径，比如 covered call、short put、缺失保证金兜底、当前持仓周期成本回冲，以及持仓汇总收益率同步。
- `.trade-tracker/tools/trade_tracker/option_analysis.py`: 期权收益分析页面。
- `.trade-tracker/tools/trade_tracker/realized_analysis.py`: 盈亏日历 / 阶段账单，日历展示统一当日盈亏，已实现明细可按交易标签筛选；当日盈亏读取曲线 `daily_total_value`，持仓浮盈只作为明细来源。
- `.trade-tracker/tools/trade_tracker/clearance_analysis.py`: 清仓分析。
- `.trade-tracker/tools/trade_tracker/performance_report.py`: 收益报告。
- `.trade-tracker/tools/trade_tracker/market_data.py`: 东方财富、腾讯、Yahoo、HKEX 行情和汇率获取。
- `.trade-tracker/tools/trade_tracker/names.py`: 标的名称缓存和历史券商文件映射。
- `.trade-tracker/tools/trade_tracker/refresh_panel.py`: 网页里的刷新状态条和刷新进度面板；顶部刷新按钮会共用这一套逻辑。
- `.trade-tracker/tools/trade_tracker/styling.py`: 生成后的 CSS 和表格显示微调。
- `.trade-tracker/tools/trade_tracker/analytics.py`: 持有天数、最后清仓时间等交易分析辅助。

说明：

- `.trade-tracker/preview/` 里的内容会被刷新脚本重新生成，通常不用手动改。
- 数值口径和页面接口先看 `.trade-tracker/DATA_INTERFACES.md`，优先扩展 `display_payload.py`，再改具体模块，避免同一个指标在多个区块里各算一遍；持仓页的资金口径 / 数据质量区块也读这层，不单独推导。
- 盈亏核验要分清账户总额和持仓行展示：账户 `总盈亏` / 总收益曲线使用 `当前持仓市值 + 累计卖出金额 - 累计买入金额`，交易费用跟随买入/卖出现金流进入；当前持仓页顶部 `总盈亏` 使用当前持仓汇总浮盈；当前持仓表的单行 `浮动盈亏` 可以把本轮持仓起始日之后的部分卖出、已平仓期权和分红回冲进成本，用来对齐券商 App 的持仓收益率。清仓归零前的历史收益不能进入新一轮持仓浮盈，也不能通过成本回冲额外抬高账户总盈亏。分年度个股汇总的 `已实现盈亏` 是交易平仓盈亏，`分红净额` 单列股息和扣税，`总盈亏` 是最终对账数。
- 总收益曲线的历史点位：买入日用订单买入价作为历史起点，卖出日用订单卖出价确认已实现，两个交易日之间用历史收盘价盯市；最新实盘价存在时会覆盖当天缓存收盘价，也会覆盖当天新买入且仍持有仓位的市值。
- `.trade-tracker/tools/cache/` 可以删除，刷新时会按需重建；保留它能明显减少行情请求。指数缓存按版本管理，旧版本会整体重建；日常刷新只加载一次缓存、只补缺口，请求结束日是今天时 A/H 指数会强制用腾讯实时尾点覆盖当天，最后一次性落盘。个股历史价缓存会对近两周窗口做版本化刷新，避免旧日线把昨日/今日当日浮盈算反；`daily_pnl_history.json` 会保存每天刷新时当前持仓页的三市场当日浮盈汇总，复盘日历和收益报告的“当日盈亏”仍以曲线点的 `daily_total_value` 为准。科创综指从 `2022-04-11` 起，用中证指数官方接口补腾讯缺失的早期历史。美股现股报价会优先取 Yahoo 盘前/盘后价格，拿不到时再回退到常规价或腾讯行情。
- `.trade-tracker/history/` 里的原始文件建议保留，后续补数据时还能继续用。
- 如果看板没有更新，先直接刷新网页；如果后台服务没有响应，再双击 `Update Preview.command`。
