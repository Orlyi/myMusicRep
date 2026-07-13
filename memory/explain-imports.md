---
name: explain-imports
description: 解释代码时同时解释 import 引入的库/函数是什么、原理是什么
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b2477a33-5495-4c02-add5-c1c5fd53eea2
---

用户要求：以后解释代码时，如果代码里有 import 的库或函数（如 `AsyncSession`、`async_sessionmaker`、`create_async_engine`、`BaseSettings`、`Mapped`、`mapped_column`、`Depends`、`APIRouter`、`Field`、`BaseModel`、`@asynccontextmanager` 等），不光解释主代码，还要顺带说明引入的东西是什么、起什么作用、原理是什么。

**Why:** 用户自述基础知识不太牢固，希望在学习项目代码的同时把依赖的库和框架概念也一并理解。

**How to apply:** 每次解释包含 import 语句的代码时，先拆解每个 import 的东西（它来自哪个库、在框架中的角色、解决了什么问题），再解释主逻辑。
