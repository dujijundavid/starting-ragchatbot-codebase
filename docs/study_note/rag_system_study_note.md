# RAG 系统学习笔记

> 这份笔记聚焦“结构化理解与快速索引”，不再重复源码细节，而是回答：每个模块负责什么？端到端流程怎么跑？遇到问题去哪儿查？

---

## 项目速览

| 模块 | 职责 | 关键文件 |
| --- | --- | --- |
| FastAPI 后端 | 加载课程、维护会话、驱动 RAG 流程 | `backend/app.py`、`backend/rag_system.py` |
| 向量检索层 | 解析课程、生成/存储语义向量、提供过滤检索 | `backend/document_processor.py`、`backend/vector_store.py` |
| Claude 集成 | 构造 prompt、协调工具调用、输出引用化回答 | `backend/ai_generator.py`、`backend/search_tools.py` |
| 会话与配置 | 记录对话上下文、集中管理参数 | `backend/session_manager.py`、`backend/config.py` |
| 前端 UI | 展示聊天界面、推荐问题、引用折叠 | `frontend/index.html`、`frontend/script.js`、`frontend/style.css` |
| 项目文档 | 课程脚本、系统说明、学习笔记 | `docs/` 目录（含 `overview.md`、`system_overview.md`、`study_note/`） |

---

## 端到端流程（RAG 工作流）

1. **文档导入**  
   `DocumentProcessor` 解析课程脚本，按课时切块并生成带重叠的 chunk；`VectorStore` 将元数据与正文写入 ChromaDB 的 `course_catalog`、`course_content` 两个集合。
2. **用户提问**  
   前端调用 `POST /api/query`，`app.py` 负责校验输入、管理 `session_id`，并把历史记录交给 `RAGSystem.query`。
3. **智能检索**  
   `AIGenerator` 与 Claude 交互。当模型请求工具时，`CourseSearchTool` 会执行语义检索，支持按课程或课时过滤，并返回带 `[Course - Lesson]` 标签的引用块。
4. **答案生成与反馈**  
   Claude 将检索结果注入 prompt，生成含引用的回答。`SessionManager` 更新对话历史；响应被前端渲染成消息气泡，并提供可折叠的来源详情与课程统计。

---

## 后端核心模块速记

### `backend/app.py`
- FastAPI 入口：注册中间件、静态资源和两条主要路由（`POST /api/query`、`GET /api/courses`）。
- `startup_event` 在启动时扫描 `../docs`，调用 `RAGSystem.add_course_folder` 自动入库新课程。
- `query_documents` 负责创建/复用会话、触发 `RAGSystem.query`，组合答案、引用与 `session_id` 返回。

### `backend/rag_system.py`
- 作为编排层串联 `DocumentProcessor`、`VectorStore`、`AIGenerator` 与 `SessionManager`。
- `add_course_folder` 过滤重复课程再导入 metadata 与 chunk。
- `query` 组装系统提示与历史消息，驱动模型完成工具调用，整理最终响应。

### `backend/document_processor.py`
- 解析课程文本、识别 `Lesson N:` 段落、执行句子级 chunking（约 800 字长度、100 字重叠）。
- 生成结构化的 `Course`、`Lesson`、`CourseChunk` 实例供后续流程消费。

### `backend/vector_store.py`
- 初始化 ChromaDB 持久化客户端，创建/缓存集合。
- `add_course_metadata`、`add_course_content` 分别写入课程级信息与正文 chunk。
- `search` 提供语义检索并返回标准化的 `SearchResults`，支持 where 过滤与分页字段。

### `backend/search_tools.py`
- `CourseSearchTool` 将 Claude 的查询请求映射为向量检索，输出包含摘要、距离等字段的 JSON。
- `ToolManager` 统一注册/派发工具，缓存引用数据供回答阶段使用。

### `backend/ai_generator.py`
- `generate_response` 构造系统提示、对话历史与工具结果，限制单轮最多一次工具调用。
- `_handle_tool_execution` 接收 Claude 的 tool_use payload，执行检索并重新请求模型生成最终回答。

### `backend/session_manager.py`
- 使用内存队列维护会话历史（最大 `max_history * 2` 条），按 `User:`/`Assistant:` 前缀输出。
- `add_exchange` 与 `get_conversation_history` 分别负责记录新消息与拼装可读历史。

### `backend/config.py`
- 从 `.env` 读取 API Key、嵌入模型名称、chunk 配置、Chroma 路径等，提供统一访问接口。

---

## 前端与静态资源

- `frontend/index.html` 定义双栏布局：左侧课程概览与推荐问题，右侧聊天窗口。
- `frontend/style.css` 提供响应式布局、消息气泡样式、加载动画、引用折叠状态等视觉层规则。
- `frontend/script.js` 负责：
  - 初始化课程统计与推荐问题。
  - `sendMessage`：发送用户输入、显示加载状态、渲染 Markdown 回答与引用明细。
  - 维护 `session_id` 与对话历史，确保刷新前的连续上下文。

---

## 文档与辅助脚本

- `docs/overview.md`：四门课程的要点速览与课时结构。
- `docs/system_overview.md`：系统技术架构、运行步骤、常见问题排查。
- `docs/study_note/`：本笔记与后续学习记录的归档目录。
- `pyproject.toml`：使用 `uv` 管理依赖（FastAPI、ChromaDB、Sentence Transformers、OpenAI SDK 等）。
- `run.sh`：检查环境变量后调用 `uv run uvicorn app:app --reload --port 8000`，提供一键启动体验。
- `main.py`：轻量占位脚本，可扩展为 CLI 或快速测试入口。

---

## 运行与调试建议

1. `uv sync` 安装依赖 → 创建 `.env` 设定 `LLM_PROVIDER` 及对应的 API Key（可覆盖模型名、向量库路径）。
2. `chmod +x run.sh` 后执行脚本，或手动 `cd backend && uv run uvicorn app:app --reload --port 8000`。
3. 浏览器访问 `http://localhost:8000` 体验前端，`http://localhost:8000/docs` 查看 Swagger。
4. 生产部署需移除 `--reload`、配置受信主机、将 `CHROMA_PATH` 指向持久卷，并使用 Redis 等替代内存 Session。

---

## 复盘：关键概念

- **RAG 主流程**：课程处理 → 语义检索 → 模型工具调用 → 引用化回答。
- **工具调用约束**：限制单轮一次检索，提升响应速度与引用准确性。
- **数据模型贯通**：`Course`/`Lesson`/`CourseChunk` 在解析、存储、检索三个阶段保持一致。
- **前后端分工**：FastAPI 输出 JSON API 与静态资源，前端通过 `fetch` + `marked.js` 呈现对话。
- **配置集中化**：通过 `Config` 统一改动模型、chunk 策略或向量库路径，减少散落参数。

---

遇到细节问题时，建议优先查阅 `system_overview.md` 获取架构上下文，再跳转具体源码定位实现。
