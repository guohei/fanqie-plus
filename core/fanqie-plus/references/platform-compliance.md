# Platform Compliance

Use this reference before publishing, signing, exporting, or checkpoint review. It is a practical safety checklist, not legal advice. Current public Fanqie guidance says platform content may be rejected, recommendation-limited, removed, or account-penalized when it violates content publishing rules, including illegal/policy-violating content, improper monetization, meaningless batch content, malicious padding, attack/harassment/doxxing, and platform-abuse guidance.

## Default Rule For Chapter Text

In chapter正文, block by default:

- URLs and domains: `http://`, `https://`, `www.`, `.com`, `.cn`, `.net`, short links.
- Emails.
- Phone numbers, QQ numbers, WeChat/VX, Telegram, Discord, group numbers, QR code prompts.
- Any wording that asks readers to add, follow, scan, join a group, private message, search an external account, or move to another platform.
- Advertising, commercial promotion, sponsorship copy, coupons, product/service sales, payment, crowdfunding, tipping, private transactions.
- Piracy or off-platform access: "完整版见...", "加群看番外", "网盘链接", "未删减版".

Exception: if Fanqie provides an official non正文 author-note/link feature, treat it as platform UI metadata, not novel正文. Keep this skill's exported chapter text clean.

## Unsafe Content Categories

Flag for manual review or rewrite:

- Illegal/policy-violating content presented as endorsement or instruction.
- Pornographic/explicit sexual content, especially with coercion, minors, or exploitative framing.
- Gambling, drugs, terrorism, extremist content, or detailed criminal methods.
- Self-harm encouragement or operational instructions.
- Doxxing, privacy invasion, real-person harassment, attack mobilization, or hate/incitement.
- Infringement risk: copied passages, unauthorized lyrics/poems, real brands/celebrities used in defamatory or rights-risky ways.
- Student/underage negative guidance when framed as aspirational or instructional.

## Low-Quality / Malicious Padding Risk

Flag:

- Repeated near-identical chapters or paragraphs.
- Symbol/emoji/乱码 filler.
- Long unrelated encyclopedia/news/tutorial paste.
- Plotless water chapters that exist only to hit word count.
- Abrupt stitching of unrelated scenes with no causal connection.

## Review Output

Use this section in review reports:

```markdown
## Platform Compliance
- URL/contact/diversion: pass/fail
- Advertising/transaction: pass/fail
- Unsafe content: pass/fail/manual review
- Low-quality/padding: pass/fail
- Copyright/privacy risk: pass/fail/manual review
- Required repair:
```
