---
name: principle-migrate-callers-then-delete-legacy-apis
description: "适用于引入新的内部 API 而旧调用方还在时。在同一波里迁完调用方并删掉旧 API,而不是保留兼容层。"
disable-model-invocation: true
---

# Migrate Callers Then Delete Legacy APIs

- Update tests to assert the new contract, and delete tests that only protect pre-refactor implementation details

**When this applies:**
- No external users depend on backward compatibility
- The project can absorb coordinated breaking changes
- The new API is part of a simplification or refactor initiative
