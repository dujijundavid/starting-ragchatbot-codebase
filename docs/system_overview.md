# RAG 课程问答系统概览

> 写给刚接触 RAG 项目的你：这份文档帮你快速弄明白“它是做什么的、用到了哪些技术、怎么跑起来、遇到问题怎么办”。

---

## 这是什么项目？

这是一个 **RAG（Retrieval-Augmented Generation）** 课程资料问答系统：当用户提问时，系统会先检索课程脚本里的相关片段，再把最相关的内容交给 OpenAI 兼容的大语言模型（默认 DeepSeek 或 Qwen）生成回答。这样既能提供准确引用，又能给出自然语言解释。

项目采用全栈架构：
- **后端 FastAPI**：负责加载课程、完成检索、调用大模型。
- **前端静态页面**：提供聊天界面、课程统计、推荐问题。
- **向量数据库 ChromaDB**：保存课程资料的向量表示，支持语义搜索。

项目目录包括：
- `backend/`：后端源码，封装 RAG 的各个步骤。
- `frontend/`：简洁的聊天 UI。
- `docs/`：课程脚本示例，启动时自动入库。
- `pyproject.toml` / `uv.lock`：依赖清单（使用 uv 管理）。
- `run.sh`：一键启动脚本。
- `README.md`：安装和快速开始指南。

---

## 核心技术原理（入门版）

- **向量检索为何重要？**  
  让文本“变成向量”后，就可以用语义相似度来找相关内容，摆脱关键词匹配的局限。

- **Chunking（文本切片）怎么做？**  
  一篇课程脚本会按句子切成约 800 字的片段，并且每一段和下一段有 100 字的重叠，避免被截断后漏掉关键信息。

- **RAG 流程步骤**  
  1. 预处理课程 → 生成向量 → 存入 Chroma。  
  2. 用户提问 → 检索最相似的片段 → 附加到 prompt。  
  3. 交给大模型 → 生成回答 + 引用来源。  
  4. 前端展示回答、可折叠查看引用。

- **为什么要限制工具调用次数？**  
  OpenAI 兼容接口的 Function Calling 会让模型根据需要调用检索工具。限制 “一次调用” 可以保持交互高效，防止模型循环调用工具。

---

## ChromaDB 如何在项目中工作？

- **持久化客户端与集合初始化**  
  系统启动时，`VectorStore` 会用 `config.CHROMA_PATH` 初始化 `chromadb.PersistentClient`，并创建两个集合：`course_catalog` 保存课程元数据，`course_content` 保存正文片段。嵌入由 `SentenceTransformerEmbeddingFunction`（默认 `all-MiniLM-L6-v2`）生成，避免手动管理向量模型。参见 `backend/vector_store.py` 中的 `__init__` 与 `_create_collection()`。

- **课程与片段写入流程**  
  `DocumentProcessor` 负责解析脚本并生成 `Course`、`CourseChunk` 数据结构；随后 `RAGSystem.add_course_document()` 或 `add_course_folder()` 调用 `VectorStore.add_course_metadata()` 与 `add_course_content()` 完成写入。课程在 `course_catalog` 中以 `course.title` 作为 ID，并保存讲师、课程链接、课时 JSON 等字段；片段在 `course_content` 中记录 `course_title`、`lesson_number`、`chunk_index` 便于过滤。

- **查询与过滤**  
  检索入口是 `VectorStore.search()`：若用户指定课程或课时，会通过 `_resolve_course_name()` 与 `_build_filter()` 构造 Chroma 的 `where` 条件，仅返回匹配的片段。最终结果封装成 `SearchResults`，便于前端展示来源标签和距离分数。

- **与工具链的衔接**  
  `CourseSearchTool` 调用上述 `search()`，将检索到的 chunk 转成 OpenAI Function schema 所需的 JSON，`AIGenerator` 再把这些片段附加到 prompt 中生成最终回复。整个链路保证了 “向量检索 → Prompt 增强 → 模型回复” 的闭环。

---

## 后端模块逐个看

- **`backend/config.py`**  
  读取 `.env` 配置，解析 `LLM_PROVIDER`、对应的 API Key/模型/Base URL，并统一提供嵌入模型名称（`all-MiniLM-L6-v2`）、chunk 大小、Chroma 存储路径（默认 `./chroma_db`）。集中管理配置可以方便地更换模型或调整参数。

- **`backend/document_processor.py`**  
  - 解析 `docs/` 下的课程脚本，提取标题、链接、讲师等元数据。  
  - 识别 “Lesson N: …” 格式，以课时为单位切片。  
  - 进行带重叠的句子级 chunking，并在每个课时的首段加 `Lesson X content:` 前缀，提升检索上下文理解。  
  - 输出 Pydantic 数据模型（`Course`、`Lesson`、`CourseChunk`），保证后续处理类型安全。

- **`backend/vector_store.py`**  
  - 基于 ChromaDB 初始化两个集合：`course_catalog`（课程元信息）和 `course_content`（正文片段）。  
  - 提供插入、清理、统计、查询等方法。  
  - 检索时支持按课程、课时过滤，并为前端整理好来源信息。

- **`backend/search_tools.py`**  
  - `CourseSearchTool` 将用户问题向量化，执行语义检索，返回附带标签（如 `[Course - Lesson 2]`）和来源的结果。  
  - `ToolManager` 提供 OpenAI Function schema 兼容的工具注册方式，方便模型按需触发课程检索。

- **`backend/session_manager.py`**  
  - 单机内存实现的简易 Session 系统，用 `session_{n}` 作为 ID。  
  - 保存最近的用户/助手对话历史（最多 `max_history * 2` 条），格式为 `User:`、`Assistant:`。  
  - 保持适当历史能让模型理解上下文，但不会让 prompt 过长。

- **`backend/ai_generator.py`**  
  - 封装 OpenAI 兼容客户端，内置系统提示词，要求回答简洁、引用来源、禁止多次工具调用。  
  - 如果模型返回 `tool_calls`，会自动执行检索并带着搜索结果再次请求模型，得到最终回答。

- **`backend/rag_system.py`**  
  - 将所有组件粘合起来，提供对外接口。  
  - `add_course_document` / `add_course_folder`：为新课程入库。  
  - `query()`：主流程（构造 prompt → 调用模型 → 处理工具调用 → 整理回答和来源 → 更新会话）。  
  - `get_course_analytics()`：返回课程数量和标题，供前端展示。

- **`backend/app.py`**  
  - FastAPI 入口，配置 CORS、静态文件挂载、受信主机。  
  - 路由：  
    - `POST /api/query`：执行一次问答，返回 `answer`、`sources`、`session_id`。  
    - `GET /api/courses`：查看课程统计。  
  - 启动时扫描 `../docs`，自动调用 `RAGSystem` 完成课程入库。

---

## 前端做了什么？

- **`frontend/index.html` / `style.css`**  
  构建了一个对话式界面：左侧为课程信息和推荐问题，右侧为聊天窗口。使用 `marked.js` 将 Markdown 格式的回答渲染成 HTML。

- **`frontend/script.js`**  
  - 初始化时调用 `/api/courses` 获取课程统计。  
  - `sendMessage()`：提交问题、显示加载动画、接收回答并渲染在对话区。  
  - Sources 以折叠面板展示，点击可展开查看原始片段。  
  - 推荐问题按钮会自动填充输入框，降低新手的提问门槛。  
  - 会把后端返回的 `session_id` 保存到浏览器内存，保证同一会话上下文连续。

---

## 端到端数据流（再回顾一次）

1. **启动服务**  
   - 执行 `./run.sh` → 读取 `.env` → 进入 `backend/`。  
   - 用 `uv run uvicorn app:app --reload --port 8000` 启动 FastAPI。  
   - `RAGSystem` 自动加载 `docs/` 中的所有脚本并导入 Chroma。

2. **发送问题**  
   - 前端调用 `POST /api/query`，附带提问内容和 `session_id`（若无则后端新建）。  
   - 后端从 `SessionManager` 取出历史，拼成 prompt。

3. **检索 + 生成**  
   - 模型判断是否需要工具；若需要，则触发 `CourseSearchTool`。  
   - 检索结果（若干 chunk + metadata）被追加到 prompt 中，再次请求模型。  
   - 模型输出最终回答和引用列表。

4. **返回结果**  
   - FastAPI 将 `answer`、`sources`（含课程名、课时、摘要）、`session_id` 返回前端。  
   - 前端渲染答案，并在 sources 面板展示引用内容。

---

## 如何运行？

1. **准备环境**
   - Python ≥ 3.13  
   - 安装 uv（[官方安装指南](https://github.com/astral-sh/uv)）  
   - 在项目根目录执行 `uv sync` 安装依赖。

2. **配置密钥**
   - 在项目根目录创建 `.env`，设置 `LLM_PROVIDER`（`deepseek` / `qwen`）及对应的 API Key、模型、base URL。  
   - 如果要修改嵌入模型或 Chroma 路径，也可以在 `.env` 中覆盖默认值。

3. **启动服务**
   - 执行 `./run.sh`（确保有执行权限：`chmod +x run.sh`）。  
   - 脚本会检查密钥、确保 `docs/` 存在、启动 FastAPI。

4. **访问应用**
   - 浏览器打开 `http://localhost:8000` 查看前端界面。  
   - `http://localhost:8000/docs` 可查看自动生成的 API 文档。  
   - 首次启动时会创建 `./chroma_db`，存放向量数据。

---

## 常见问题与排查

- **Q：为何需要 chunk 重叠？**  
  A：保证句子跨 chunk 时不会被截断，检索出的上下文更完整。

- **Q：ChromaDB 数据存在哪里？**  
  A：默认在项目根目录下的 `./chroma_db`，可以在 `.env` 中改路径。

- **Q：模型会乱编吗？**  
  A：RAG 设计能显著降低幻觉，因为回答基于检索结果。但还是建议在 sources 中查看原文确认关键结论。

- **Q：如何添加新的课程？**  
  A：把格式正确的脚本文件放入 `docs/`，重启服务即可自动入库。

- **Q：能换别的大模型吗？**  
  A：可以在 `.env` / `config.py` 中调整模型名称或改用其他 API。记得检查系统 prompt 和工具 schema 是否兼容。

- **Q：多人共享时会话如何持久化？**  
  A：当前 Session 保存在内存里，只适用于本地或单实例。若要部署到服务器，可改用 Redis、数据库或自定义存储。

---

## 下一步可以学什么？

- 了解 RAG 的基本原理与常见架构模式。  
- 熟悉向量数据库（Chroma、Faiss、Milvus 等）的适用场景。  
- 深入学习 FastAPI（依赖注入、后台任务、身份验证）。  
- 在前端尝试增加流式输出、消息标注、引用高亮等增强体验。  
- 研究部署策略：容器化（Docker）、CI/CD、API Key 安全管理。

---

准备好了就动手试试吧！如果想进一步拓展功能，可以先从增加更多课程资料或接入新的检索工具开始。
