---
name: principle-laziness-protocol
description: "适用于重构、评估 diff 大小、或忍不住要加抽象、加层、透传信号时。偏向删除,用能解决问题的最小改动。"
disable-model-invocation: true
---

# Laziness Protocol

- **Consolidate decisions.** Do not repeat the same choice in several places. Put it behind one source of truth and pass the result as a simple flag.
- **Minimize the diff.** Make the smallest change that solves the problem. Fewer lines beat "elegant" boilerplate.
