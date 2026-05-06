# 跨 Agent 双智能体审稿协议

`scripts/cross_agent_reviewer.py` 来源于 novelist-skill。核心思路：用**与写作 Agent 不同的另一个 LLM** 充当资深编辑，专门找茬。

它解决的痛点：写作 Agent 自审有显著偏差（自己写的容易"看得顺"），跨 Agent 能找到 30-50% 自审漏掉的硬伤。

## 何时使用

- 完成一卷收束章后
- Fanqie 节点：8w / 10w / 15w
- 当读者模拟（reader-review.md）连续两章 `surprise` 或 `retention` 子项低于阈值时

## 三维度审稿

1. **逻辑与连续性硬伤**（P0/P1/P2）：时间线、空间、设定、伏笔。
2. **节奏与爽点**：拖沓段、爽点缺失、铺垫过头、铺垫不够。
3. **AI 味与人物腔调**：翻译腔、过度总结、对话同质化（角色 A 和角色 B 说话像同一个人）。

## 如何调用

通过 `scripts/fanqie_audit.py` 适配层调用。审稿是**两步**工作流，因为需要把 prompt 真正喂给一个不同的 LLM：

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
# 让它扮演"资深网文编辑"，把它的回复保存为：
#   05_reviews/cross/ch042_review_report.md

# 步骤 3：解析另一个 Agent 的回复（使用底层脚本，未通过适配层封装）
python <skill>/scripts/cross_agent_reviewer.py parse \
  --report 05_reviews/cross/ch042_review_report.md \
  --output 05_reviews/cross/ch042_issues.json
```

退出码：`0` 无未解决问题 / `1` 有未解决 P0/P1 / `2` 输入错误。

## 卷末批量审稿

```bash
python <skill>/scripts/fanqie_audit.py --project-root . cross-batch \
  --chapter-start 40 --chapter-end 50
```

## 操作守则

- **不要让写作 Agent 自审**：必须切换到另一个模型/会话，否则等于没审。
- **P0 必须在写下一章前修复**；P1 在卷末修复；P2 进 backlog。
- 审稿 Agent 的回复中不允许出现"写得不错"——若出现，重提示，强调 `REVIEWER_PERSONA`：唯一任务是找茬。
- 审稿报告不进入 `04_chapters/final/`，仅留在 `05_reviews/`。
