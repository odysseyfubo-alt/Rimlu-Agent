# primer · 前置篇配套代码

前置篇三篇「大模型到底是个啥，它又缺了什么」「Agent 是怎么让大模型动手干活的」「如何用 LangChain 写一个 Agent」的例子。每个文件都能单独跑。前四个只依赖 `openai`，后四个用 LangChain。

## 装环境

项目本身 `uv sync` 装过的，什么都不用再装，在仓库根目录下 `uv run python primer/s1_hello.py` 就能跑。

没装项目、只想跑这几个例子的，Python 3.10 以上，装这几个包（前两个跑第一、二篇的例子，后三个跑第三篇的）：

```bash
pip install openai python-dotenv langchain langchain-openai langgraph
```

LangChain 认 1.x 系列，项目里锁的也是它。

配置跟项目共用仓库根目录的 `.env`，只用到三行，脚本会往上级目录找。只跑这几个例子的，在仓库根目录或 `primer/` 下建一个 `.env` 写这三行也行：

```bash
CHAT_BASE_URL=https://api.deepseek.com/v1
CHAT_API_KEY=sk-你的密钥
CHAT_MODEL=deepseek-v4-flash
```

## 文件

| 文件 | 对应哪一篇 | 演示什么 |
|---|---|---|
| `shop.py` | 共用 | 连模型的客户端，查订单、查物流两个假数据函数 |
| `s1_hello.py` | 第一篇 | 在代码里跟大模型说一句话，看回答和 token 账单 |
| `s2_memory.py` | 第一篇 | 两次各问各的它记不住，把聊天记录一起发过去就记住了 |
| `s3_tools.py` | 第二篇 | 给它一份工具清单，看它回来的 `tool_calls`，执行后把结果还给它 |
| `s4_agent.py` | 第二篇 | 工具调用包进循环，它自己先查订单再查物流 |
| `s5_workflow.py` | 第二篇 | 同一个问题换成 Workflow，查询顺序由代码写死 |
| `s6_langchain_hello.py` | 第三篇 | 换成 `ChatOpenAI` 说一句话，对照 s1 |
| `s7_prompt_chain.py` | 第三篇 | 提示词模板加 `\|` 串成链 |
| `s8_tool_decorator.py` | 第三篇 | `@tool` 装饰器，打印它自动生成的参数 schema |
| `s9_langchain_agent.py` | 第三篇 | `create_agent` 二十行跑通两步工具链，加 `checkpointer` 就有记忆 |

订单和物流是写死在 `shop.py` 里的假数据，不连数据库。正文会换成真查 MySQL。
