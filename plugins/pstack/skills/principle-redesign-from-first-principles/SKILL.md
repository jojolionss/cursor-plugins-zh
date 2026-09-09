---
name: principle-redesign-from-first-principles
description: "适用于把新需求整合进既有设计时。当作这个需求从第一天起就是基础假设那样去重新设计,而不是往上焊补丁。"
disable-model-invocation: true
---

# Redesign From First Principles

When integrating a change, don't bolt it onto the existing design. Redesign as if the requirement had been there from the start.

- Read all affected files and understand the current design
- Ask: "if we were writing this from scratch with this new requirement, what would we build?"
- Propagate the change through every reference: types, docs, examples, rationale sections
- Think about the whole redesign, then deliver it incrementally

This is the method for preserving option value when integrating changes into an existing design.
