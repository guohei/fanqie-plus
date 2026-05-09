# 外部 AI 审稿使用文档

`scripts/cross_agent_reviewer.py` 来源于 novelist-skill。核心思路：用**与写作 Agent 不同的另一个 LLM/会话**充当资深编辑，专门找茬。

它解决的痛点：写作 Agent 自审有显著偏差，容易放过自己刚写出来的逻辑、节奏和 AI 味问题。外部审稿不是日更主流程的一部分，而是关键节点的独立检查。

## 何时使用

- 8w / 10w / 15w 等 Fanqie 商业节点
- 完成一卷收束章后
- 每 10 章一致性审查发现硬伤、漂移、支线遗忘或节奏异常
- 用户明确要求另一个 AI 通读并给审稿报告
- 重大改纲、连续修文、准备发布或导出前

不要因为 `reader_report` 分数低就自动触发外部审稿。`reader_report` 只是启发式诊断；是否需要外部审稿取决于真实风险和用户目标。

## 三维度审稿

1. **逻辑与连续性硬伤**（P0/P1/P2）：时间线、空间、设定、伏笔。
2. **节奏与爽点**：拖沓段、爽点缺失、铺垫过头、铺垫不够。
3. **AI 味与人物腔调**：翻译腔、过度总结、对话同质化（角色 A 和角色 B 说话像同一个人）。

## 单章审稿

通过 `scripts/fanqie_audit.py` 适配层调用。审稿是**三步**工作流，因为需要把 prompt 真正喂给一个不同的 LLM，再把报告解析回 fanqie-plus 项目：

```bash
# 步骤 1：生成审稿 Prompt（自动定位章节文件）
python <skill>/scripts/fanqie_audit.py --project-root . cross-review \
  --chapter 42 \
  --reviewer "gpt-5" \
  --round 1
# → 产物：05_reviews/cross/cross_review/ch042_review_prompt.md
```

```bash
# 步骤 2：把上面那个 prompt 文件复制到一个不同的 LLM（不同模型/不同会话），
# 让它扮演"资深网文编辑"，只找问题。
# 把它的回复保存为：
#   05_reviews/cross/ch042_review_report.md

# 步骤 3：解析另一个 Agent 的回复
python <skill>/scripts/fanqie_audit.py --project-root . cross-parse \
  --report-file 05_reviews/cross/ch042_review_report.md
# → 产物：05_reviews/cross/ch042_issues.json
```

退出码：`0` 无 P0 / `1` 有 P0 / `2` 输入错误。P1 会进入 issues JSON，但不靠退出码阻塞日更。

## 批量审稿

用于 10 章段落、卷末、8w/10w/15w 节点。它只生成批量审稿 prompt，不会自动调用另一个 LLM。

```bash
python <skill>/scripts/fanqie_audit.py --project-root . cross-batch \
  --chapter-start 40 --chapter-end 50
```

产物：`05_reviews/cross/cross_review/batch_ch040-050_review_prompt.md`。把 prompt 交给外部 LLM 后，将报告保存到 `05_reviews/cross/`，再用 `cross-parse` 解析或按报告里的 P0/P1/P2 修复。

## 推荐使用顺序

1. 每章默认只跑 `gate_check.py`，不要为了审稿额外增加日更负担。
2. 每 10 章先跑 `references/consistency-audit.md`，修复 blocking conflict。
3. 如果 10 章审查发现漂移、节奏异常、支线遗忘，或遇到 8w/10w/15w/卷末节点，再生成 `cross-batch` prompt。
4. 把 prompt 交给另一个 AI，不要让写作 Agent 自审。
5. 保存外部报告，用 `cross-parse` 解析成 `05_reviews/cross/*_issues.json`，或人工整理成 P0/P1/P2。
6. P0 写下一章前修；P1 在当前节点或卷末修；P2 进入待办，不阻塞日更。

## 操作守则

- **不要让写作 Agent 自审**：必须切换到另一个模型/会话，否则等于没审。
- **P0 必须在写下一章前修复**；P1 在卷末修复；P2 进 backlog。
- 审稿 Agent 的回复中不允许出现"写得不错"——若出现，重提示，强调 `REVIEWER_PERSONA`：唯一任务是找茬。
- 审稿报告不进入 `04_chapters/final/`，仅留在 `05_reviews/`。
- 外部报告不改正文；写作 Agent 只根据报告执行最小必要修复，并更新 memory/outline。
