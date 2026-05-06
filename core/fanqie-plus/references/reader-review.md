# 读者模拟审稿（advisory gate）

读者模拟脚本 `scripts/reader_simulator.py` 来源于 novelist-skill v1.2.0，用于在每 10 章 / 番茄节点（首3、8w、10w、15w）跑一次「四画像 × 六维度」的读者视角评分，输出可读的修订建议清单。

它是 **advisory** 级别（不阻塞 Step 3 主流程），用于 Step 5「Review a stage」。

## 何时使用

- 每 10 章的常规复盘
- Fanqie 节点：黄金三章末、8w 字、10w 字、15w 字
- 当人工读者反馈"看起来 AI 味重 / 节奏拖 / 没啥追读欲"，但 `gate_check.py` 全部 PASS

## 六个评分子项与权重

| 子项 | 权重 | 含义 |
|------|------|------|
| `end_hook` | 25 | 章尾钩子是否产生追读欲（与本仓库 `genres/INDEX-hook-techniques.md` 对照） |
| `retention` | 25 | 中段是否能撑住，避免读者中途滑走（避免长段铺垫、避免大段总结） |
| `surprise` | 15 | 单章是否有≥1 个意料之外/合情合理的转折 |
| `immersion` | 15 | 文字是否让读者"看到画面"，避免概括式叙述与翻译腔 |
| `payoff` | 10 | 本章是否兑现了上章末尾或前置铺垫的某项承诺 |
| `share` | 10 | 是否有可被截图/转发的金句或名场面 |

`DEFAULT_THRESHOLD = 70`，低于阈值视为未通过。

## 如何调用

novelist-skill 原生 `reader_simulator.py` 假定 novelist 项目布局（`02-写作计划.json` / `03_manuscript/` / `04_editing/`）。在 fanqie-plus 项目中**通过 `scripts/fanqie_audit.py` 适配层调用**——它会临时构造 novelist 期望的目录形状，跑完后把产物拷贝到 `05_reviews/reader/`。

启发式评分模式（默认，零依赖）：

```bash
# 在 fanqie-plus 书籍项目根目录下执行
python <skill>/scripts/fanqie_audit.py --project-root . reader \
  --chapter 42 \
  --threshold 70 \
  --reader-profile webnovel_veteran
```

实际产物：`05_reviews/reader/gate_artifacts/ch042/reader_report.md`

Prompt 驱动模式（让另一个 LLM 来填模板）：

```bash
python <skill>/scripts/fanqie_audit.py --project-root . reader \
  --chapter 42 \
  --prompt-only \
  --dry-run
```

退出码：`0` 通过 / `1` 未达阈值 / `2` 输入错误。

可选配置文件 `00_config/audit_config.json`（影响阈值与画像）：

```json
{
  "gateThresholds": { "reader": 70 },
  "readerProfile": "webnovel_veteran"
}
```

## 与 fanqie-plus quality-gates 的关系

- `scripts/gate_check.py`：**blocking** 单章门禁，每章必跑（机械模式）。
- `scripts/reader_simulator.py`：**advisory**，节点 Review 跑（语义模式）。
- 两者结果合并到 `05_reviews/`，由 Step 5 的 stage review 汇总成"必修"与"可缓"。

## 不要做的事

- 不要把读者模拟塞进 Step 3 的单章流程，那会拖慢日更节奏。
- 不要因为读者模拟单子项低分就立刻重写——先看 `gate_check.py` 是否也红，机械级问题优先于审美级问题。
- 不要把审稿报告内容塞进章节正文。
