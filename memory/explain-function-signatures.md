---
name: explain-function-signatures
description: 解释函数时同时说明参数列表和返回值形态
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b2477a33-5495-4c02-add5-c1c5fd53eea2
---

用户要求：以后解释新函数/方法时，不光解释逻辑，还要明确列出：
1. 接受的参数（每个参数的类型、含义、是否必填）
2. 返回值（类型、结构、大概长什么样）

**Why:** 用户在学习阶段，想要对函数的输入输出有完整认知，不只是知道"这函数干嘛的"。

**How to apply:** 解释每个函数时，先列出签名和参数表，再解释逻辑，最后给出返回值形态。
