# Course Materials Overview

## Course 1: Building Towards Computer Use with Anthropic

**Instructor:** Colt Steele  
**Link:** https://www.deeplearning.ai/short-courses/building-toward-computer-use-with-anthropic/  

### Overview
This course, taught by Colt Steele (Anthropic's Head of Curriculum), explores Anthropic's AI models and features enabling computer use, such as processing screenshots for mouse/keyboard actions. It covers API basics, multi-modal image analysis, prompting techniques (chain-of-thought, n-shot), prompt caching for long contexts, tool use, structured outputs, and a full computer use demo via Docker. Emphasizes AI safety, alignment, and interpretability.

### Lessons
- **Lesson 0: Introduction** - Overview of computer use capabilities, Anthropic's vision, and course structure.
- **Lesson 1: Overview** - Anthropic's approach to AI research, safety principles, and model family.
- (Additional lessons: Basic API requests, multi-modal requests, prompting tips, prompt caching, tool generation, structured JSON outputs, complete computer use example.)

## Course 2: MCP: Build Rich-Context AI Apps with Anthropic

**Instructor:** Elie Schoppik  
**Link:** https://www.deeplearning.ai/short-courses/mcp-build-rich-context-ai-apps-with-anthropic/  

### Overview
This course introduces the Model Context Protocol (MCP), an open protocol for standardizing LLM app connections to tools and data via client-server architecture. It covers MCP origins, ecosystem growth, client-server communication, primitives (tools, resources, prompts), and building MCP-compatible chatbots, servers, and integrations (e.g., GitHub, Google Drive, Asana). Includes deployment of remote MCP servers.

### Lessons
- **Lesson 0: Introduction** - MCP fundamentals, client-server model, and ecosystem overview.
- **Lesson 1: Why MCP** - Benefits of standardization, comparisons to LSP/REST, demo of GitHub/Asana integration.
- **Lesson 2: MCP Architecture** - Primitives (tools, resources, prompts), communication (initialization, messages), transports (StdIO, HTTP/SSE, Streamable HTTP).
- **Lesson 3: Chatbot Example** - Building a basic chatbot with ArXiv search tools using Anthropic SDK.
- (Additional lessons: Building MCP servers/clients, connecting to third-party servers, reusing servers across apps, remote deployment.)

## Course 3: Advanced Retrieval for AI with Chroma

**Instructor:** Anton Troynikov  
**Link:** https://www.deeplearning.ai/short-courses/advanced-retrieval-for-ai/  

### Overview
Taught by Chroma co-founder Anton Troynikov, this course advances RAG beyond basic semantic similarity. It reviews embeddings-based retrieval pitfalls, then covers query expansion (generated answers, multi-queries), cross-encoder reranking, query adapters (user feedback), and emerging techniques. Uses Microsoft 2022 annual report as example; emphasizes visualization (UMAP) and geometric intuition in embedding space.

### Lessons
- **Lesson 0: Introduction** - RAG overview, pitfalls of simple vector search, course techniques.
- **Lesson 1: Overview of Embeddings-Based Retrieval** - System diagram, chunking (character/token), SentenceTransformer embeddings, Chroma setup, basic RAG loop with GPT.
- **Lesson 2: Pitfalls of Retrieval** - Distractors/irrelevant results, visualization with UMAP, failure modes (topical vs. answer-containing docs).
- **Lesson 3: Query Expansion** - Generated hypothetical answers, multi-query generation; visualization of expanded queries.
- **Lesson 4: Cross-Encoder Reranking** - Scoring query-doc pairs, reranking long-tail/multi-query results.
- **Lesson 5: Embedding Adapters** - Adapting query embeddings via feedback (e.g., HyDE).

## Course 4: Prompt Compression and Query Optimization

**Instructor:** Richmond Alake  
**Link:** https://www.deeplearning.ai/short-courses/prompt-compression-and-query-optimization/  

### Overview
Partnered with MongoDB, this course optimizes RAG costs using vector databases. Covers vanilla vector search, metadata filtering (pre/post), projections (field selection), boosting (reranking via scores/reviews), and prompt compression (fine-tuned LLMs to shorten contexts). Builds Airbnb recommendation RAG app; focuses on MongoDB aggregation pipelines, Pydantic validation, and reducing token costs (e.g., from $36M/year).

### Lessons
- **Lesson 0: Introduction** - RAG basics, hybrid search (semantic + structured), cost reduction (filtering, projection, reranking, compression).
- **Lesson 1: Vanilla Vector Search** - Data loading (HuggingFace Airbnb), Pydantic modeling, MongoDB ingestion/indexing, basic RAG with OpenAI embeddings.
- **Lesson 2: Filtering with Metadata** - Post-filtering (match stage after vector search), pre-filtering (index-embedded filters on accommodates/bedrooms).
- **Lesson 3: Projections** - $project stage to include/exclude fields (e.g., name, score), reducing payload; inclusion/exclusion patterns.
- **Lesson 4: Boosting** - Add fields ($addFields for avg review/ review count), weighting/multiply ($add/$multiply), sorting by combined score.
- **Lesson 5: Prompt Compression** - Fine-tuned small LLMs to compress long retrieved contexts before LLM input, minimizing token costs.

*Note: This overview is generated from the script files in the docs folder. For full details, refer to the individual course scripts or original links.*
