# Fanqie Export

Use this reference when exporting final chapters for Fanqie-style posting.

## Format Rules

- Output plain UTF-8 `.txt`.
- Keep chapter title as a single line: `第N章 标题`.
- Remove Markdown markers: `#`, `**`, `*`, `>`, code fences, links, horizontal rules.
- Remove metadata blocks such as word count, hook notes, review notes, or gate reports.
- Use one newline between paragraphs.
- Do not indent paragraphs with spaces or tabs.
- Do not leave blank lines between paragraphs.
- Keep Chinese punctuation consistent.

## Pre-Export Checks

- Every exported file contains正文 only.
- No beat sheet, TODO, author note, analysis, or gate comments.
- No empty chapter body.
- Chapter order is numeric.
- File names sort correctly enough for the platform package.

## Manual Conversion Example

Input:

```markdown
# 第1章：雨夜退婚

林晚醒来时，婚书正砸在她脸上。

---

**本章字数**：2780
```

Output:

```text
第1章 雨夜退婚
林晚醒来时，婚书正砸在她脸上。
```
