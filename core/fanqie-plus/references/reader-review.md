# 读者模拟诊断（optional heuristic）

读者模拟脚本 `scripts/reader_simulator.py` 来源于 novelist-skill v1.2.0，用于快速生成一个启发式 `reader_report.md`。它检查章尾钩子、段落节奏、对话比例、AI 模板句、反转词和伏笔关键词。

它不是默认审稿流程，也不是真实读者反馈。优先级低于 `gate_check.py`、10 章一致性审查和 `cross-review.md` 的外部 AI 审稿。

## 何时使用

- 用户明确想要一个快速形式诊断
- 章尾钩子、节奏、对话比例或 AI 模板句风险不确定
- `gate_check.py` 通过，但人工或外部反馈仍觉得"AI 味重 / 节奏拖 / 没追读欲"

不要在每 10 章、8w/10w/15w、卷末默认运行它。那些节点优先做一致性审查和必要的外部 AI 审稿。

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

novelist-skill 原生 `reader_simulator.py` 假定 novelist 项目布局（`02-写作计划.json` / `03_manuscript/` / `04_editing/`）。在 fanqie-plus 项目中通过 `scripts/fanqie_audit.py` 适配层调用。它会临时构造 novelist 期望的目录形状，跑完后把产物拷贝到 `05_reviews/reader/`。

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

可选配置文件 `00_config/audit_config.json`：

```json
{
  "gateThresholds": { "reader": 70 },
  "readerProfile": "webnovel_veteran"
}
```

## 与 fanqie-plus quality-gates 的关系

- `scripts/gate_check.py`：**blocking** 单章门禁，每章必跑（机械模式）。
- `references/consistency-audit.md`：**blocking when conflict exists**，每 10 章和关键漂移风险时跑。
- `references/cross-review.md`：关键节点外部 AI 审稿，P0 阻塞继续写。
- `scripts/reader_simulator.py`：**optional heuristic**，只给提示，不单独阻塞继续写。

## 不要做的事

- 不要把读者模拟塞进 Step 3 的单章流程，那会拖慢日更节奏。
- 不要把它当 10 章复盘、商业节点、卷末审稿的默认步骤。
- 不要因为读者模拟单子项低分就立刻重写。先看 `gate_check.py`、一致性审查、外部审稿或用户反馈是否也指向同一问题。
- 不要把审稿报告内容塞进章节正文。
