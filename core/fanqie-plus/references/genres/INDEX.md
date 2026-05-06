# 网文流派写作库（INDEX）

> 来源：从 `oh-story-codex` 移植，已按子主题预拆分。
> 加载顺序：先读本文件 → 选定一个子库 → 再读对应的子库 INDEX → 最后按 INDEX 表只读你需要的子文件。
> 切勿一次性读取整个 `genres/` 目录，那会让本次整合的 token 优化彻底失效。

## 何时来此查阅

| 场景 | 应去的子库 |
|------|----------|
| 题材定位、卷级结构、卖点提炼（Step 1/2 开书与规划） | [INDEX-genre-frameworks.md](INDEX-genre-frameworks.md) |
| 章末钩子、悬念断点、章首回钩（Step 3 写章节时设计 hook） | [INDEX-hook-techniques.md](INDEX-hook-techniques.md) |
| 镜头式写作、爽点释放、装逼打脸、骚话密度、番茄风格细节（Step 3 落笔风格） | [INDEX-style-modules.md](INDEX-style-modules.md) |
| 开局公式：困境切入 / 系统激活 / 重生复仇 / 黄金三章模板（Step 3 写第 1-3 章前必读） | [INDEX-opening-design.md](INDEX-opening-design.md) |

## 与 fanqie-plus 既有资源的关系

- 本目录是「**写作技法库**」，提供具体的桥段公式、台词模板、钩子套路。
- `references/style_bible.md`（fanqie-plus 原生）是「**项目级风格契约**」，记录本书的 PoV/语气/禁忌。
- `references/quality-gates.md`（fanqie-plus 原生）是「**机械门禁规则**」，与本目录互不重复。
- 优先级：本书项目内的 `00_config/style_bible.md` > 本目录的题材模板。冲突时以项目内为准。

## 数据规模

- 共 4 个子库 / 201 个叶子文件。
- 单次按需加载：1 个 META-INDEX (~1KB) + 1 个子库 INDEX (~3-5KB) + 1-2 个叶子文件 (~1-3KB)。
- 严禁：用一条 Read 把某个子库 INDEX 表里的所有叶子文件都加载——那会一次吃掉 ~30-100KB。
