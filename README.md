# MewHelp — 电商售后智能客服 Agent

一套跑在 FastAPI + LangGraph 上的电商售后客服系统。查订单物流、答政策 FAQ、走退款判定、
建工单、从线上对话里挖知识补库，还带一个自己训练的主题分类器。

设计上只守一条主线——**关键路径用 Workflow 兜住，语义模糊的部分才交给 Agent**。
模型不能跳过「查订单 → 查政策 → 校验证据」直接给出承诺；这条约束焊在图里，不靠提示词叮嘱。

## 能力

| 模块 | 做什么 |
| - | - |
| 意图路由 | 九类意图 → 五个出口，分流规则写死在路由表里，模型只负责判意图 |
| 指代消解 | 多轮对话里的「它 / 这一单」补成能独立看懂的完整问句 |
| 混合检索 | BGE-M3 稠密 + BM25 稀疏双路召回，RRF 融合，BGE-Reranker 精排 |
| 证据闸 | 四信号加权置信度（Top1 分 / 有效证据数 / 分差 / 关键条款命中），证据弱就在生成前短路 |
| 回答约束 | 编号引用、拒答兜底、型号与数值的机械校验——能机械校验的就不交给模型判 |
| 工具系统 | 统一注册 + JSON Schema 校验 + 只读/写权限门 + 超时重试 + 审计；MCP Server 动态接入 |
| 确认流 | 建工单 / 选订单 / 退款表单走 interrupt→resume，用户点确认之后才落库 |
| 上下文 | 滑窗 + 异步分段摘要 + 前缀缓存；消息带 DB 锚点，摘要边界和滑窗对齐 |
| 数据飞轮 | 线上兜底、人工转写、用户 👎 三入口 → 审核 → 写回知识库 → 重新向量化 |
| 主题分类 | RoBERTa-wwm-ext 多标签微调 → ONNX 导出 → 旁路批量归类 |
| 可观测 | Langfuse 自部署；按意图算 token 成本、评估趋势、置信度阈值校准 |

## 架构

```
START
 └─ resolve_reference            指代消解
     └─ classify_intent          九类意图 + confidence
         ├─ knowledge            商品咨询 → retrieve_knowledge → confidence_check
         │                                             ├─ 证据强 → main_agent
         │                                             └─ 证据弱 → fallback_reply
         ├─ refund_flow          退款退货 / 售后 → fetch_order → retrieve_policy → main_agent
         ├─ business             物流 / 订单 / 人工 ───────────────────────────→ main_agent
         ├─ escalate             投诉 → complaint_reply
         └─ fallback_script      闲聊 / 其他 → script_reply

main_agent ⇄ agent_tools  (ReAct，步数封顶)
         └→ log → END
```

- 消解、意图、分流三段和末尾的 log 是确定性路径，模型在这几处只做单点判断；
- `main_agent` 是唯一自由发挥的地方，但它能调什么由工具注册表决定，写操作必须先过确认流；
- 证据闸放在检索之后、生成之前——流式输出一旦吐错字，收回来的成本比降回答率高得多。

## 技术栈

FastAPI + LangGraph / LangChain；业务库 MySQL（SQLAlchemy + asyncmy），向量库 Milvus。

聊天、嵌入、重排三组上游各自直连，没有额外网关层。模型名与地址都放在 `.env`
（`CHAT_*` / `EMBED_*` / `RERANK_*` 三组），换供应商、换模型不用改代码。

## 启动

```bash
cp .env.example .env      # 填 CHAT_* / EMBED_* / RERANK_* 三组
docker compose up -d      # MySQL + Milvus + MinIO + etcd
make seed                 # 灌业务测试数据
make dev                  # 依赖容器 + MCP Server + 应用
```

打开 <http://localhost:8000> 就是聊天页。第一次跑还要把知识库建起来：

```bash
make kb-build        # 切块落 MySQL
make kb-vectorize    # 向量化写进 Milvus
```

## 目录

| 位置 | 装的是什么 |
| - | - |
| `app/api/` | HTTP 入口：聊天、Agent、知识库录入、复核、验收页、成本看板 |
| `app/graph/` | LangGraph 那张图：`state` 状态、`nodes` 节点、`routing` 分流、`build` 组装 |
| `app/core/` | 单点能力：上游客户端、检索、重排、意图、指代、摘要、置信度、飞轮、可观测 |
| `app/kb/` | 知识怎么进库：切块、嵌入、双写 MySQL 与 Milvus、去重、从对话里挖问答对 |
| `app/tools/` | 工具系统：内置 `@tool`、MCP 客户端、注册表、统一执行引擎 |
| `app/db/` | 表模型与仓储 |
| `app/static/` | 前端页面：聊天、知识库录入、飞轮待审、观测与成本、主题分布、分类器验收 |
| `mcp_servers/` | 业务 MCP Server，物流和售后各一台，独立进程 |
| `sql/` | 建表与迁移，容器首启按文件名顺序自动执行 |
| `scripts/` | 建库、评估、微调这些离线活 |
| `docs/` | 各模块的设计文档与实现计划 |
| `primer/` | 大模型与 Agent 的最小可运行例子，跟主项目无依赖关系 |

## 验证

`make test` 跑全部单测，不打真实模型；下面这些要真服务在跑。

| 想验证什么 | 命令 |
| - | - |
| 检索质量（四策略对照） | `make eval-rag` |
| 评估集自检 | `make eval-check` |
| 事实性裁判回归 | `make judge-check` |
| 意图分类 | `uv run python scripts/eval_intent.py` |
| 端到端对话 | `make eval-agent` |
| 工具系统与 MCP | `make eval-toolkit` |
| 数据飞轮 | `make flywheel` / `make eval-flywheel` |
| 按意图成本账 | `make cost-report` |
| 分类器训练与评测 | `make topic-corpus` / `make topic-train` / `make topic-eval` |

`make help` 能看到带说明的完整目标清单。

## 页面与端口

| 端口 | 是什么 |
| - | - |
| 8000 | 应用 |
| 8101 / 8102 | 业务 MCP Server，物流 / 售后 |
| 8110 | 主题分类器推理服务 |
| 3000 | Langfuse |
| 19530 | Milvus |

| 路径 | 页面 |
| - | - |
| `/` | 聊天 |
| `/kb` | 知识库录入 |
| `/review` | 飞轮待审 |
| `/observability` | 观测与成本 |
| `/topics` | 主题分布 |
| `/acceptance` | 分类器验收 |