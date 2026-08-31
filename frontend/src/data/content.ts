// Real content pulled from README.md, PRESENTATION.md, docs/test_results.md
// and docs/performance_notes.md. No placeholder copy.

export const architectureSteps = [
  {
    label: "Ingest",
    detail: "docs/*.txt read, split into paragraph-level chunks",
  },
  {
    label: "Embed",
    detail: "qwen3-embedding-0.6b (Foundry Local)",
    mono: true,
  },
  {
    label: "Store",
    detail: "SQLite — knowledge.db",
    mono: true,
  },
  {
    label: "Retrieve",
    detail: "cosine similarity, top-5 chunks, threshold 0.2",
  },
  {
    label: "Generate",
    detail: "phi-3.5-mini (Foundry Local), temperature 0.2",
    mono: true,
  },
];

export const keyFeatures = [
  { feature: "RAG pipeline", detail: "Retrieve → Augment → Generate, fully implemented in Python" },
  { feature: "Offline inference", detail: "Foundry Local runtime; models run on CPU/GPU locally" },
  { feature: "Semantic retrieval", detail: "qwen3-embedding-0.6b + cosine similarity over SQLite" },
  { feature: "Answer generation", detail: "phi-3.5-mini (~3.8B params), temperature=0.2 for consistency" },
  { feature: "Source citations", detail: "Model instructed to cite [Source Name] in every answer" },
  { feature: "Responsible fallback", detail: "Returns “I don’t have enough information” when context is insufficient" },
];

export const sampleQA = [
  {
    question: "What is RAG and what problem does it solve?",
    answer:
      "RAG, or Retrieval-Augmented Generation, is a technique that enhances responses from large language models by retrieving relevant information from a document store. According to What Is Rag, it solves the problem of general LLMs lacking domain-specific or up-to-date knowledge by grounding answers in retrieved context, reducing hallucination.",
  },
  {
    question: "What are the three steps of the RAG pipeline?",
    answer:
      "According to the provided context, the three steps of the RAG pipeline are: 1. Retrieve: Find the most relevant text chunks from a document store using semantic similarity. 2. Augment: Add the retrieved chunks to the prompt as context. 3. Generate: Use the LLM to produce an answer grounded in that context.",
  },
  {
    question: "What is the capital of France?",
    answer:
      "I'm sorry, but the information provided does not contain the answer to your question. I don't have enough information to answer that question.",
    unanswerable: true,
  },
];

export const testSummary = {
  date: "2026-08-14",
  chunkCount: 29,
  documentCount: 6,
  categories: [
    { category: "Answerable questions", total: 10, passed: 10 },
    { category: "Unanswerable questions", total: 4, passed: 4 },
    { category: "Edge cases", total: 3, passed: 3 },
  ],
  answerable: [
    "What is RAG and what problem does it solve?",
    "What are the three steps of the RAG pipeline?",
    "What is Microsoft Foundry Local?",
    "How do I install Foundry Local?",
    "What is cosine similarity?",
    "What embedding model does Foundry Local recommend?",
    "What is SQLite and why is it good for local apps?",
    "What is a system prompt?",
    "What chunking strategy should I use for RAG?",
    "What Python commands do I type to ingest documents and start the assistant?",
  ],
  unanswerable: [
    "What is the capital of France?",
    "Who won the FIFA World Cup in 2022?",
    "What is the recipe for chocolate cake?",
    "What is the population of Tokyo?",
  ],
  edgeCases: [
    { label: "Empty input", input: "“”", result: "Returns “Please enter a question.” (24 chars)" },
    { label: "Single word", input: "“hello”", result: "Returns graceful fallback (32 chars)" },
    { label: "Very general", input: "“tell me everything”", result: "Returns a bounded answer (928 chars)" },
  ],
};

export const performanceData = {
  date: "2026-08-14",
  hardware: "Apple Silicon (macOS, CPU inference via Foundry Local)",
  coldStart: 28.69,
  warmAvg: 8.41,
  warmRange: [4.63, 11.25] as [number, number],
  raw: [
    { question: "What is RAG and what problem does it solve?", elapsed: 28.69, chunks: 5, cold: true },
    { question: "What are the three steps of the RAG pipeline?", elapsed: 10.36, chunks: 5 },
    { question: "What is Microsoft Foundry Local?", elapsed: 8.16, chunks: 5 },
    { question: "What is cosine similarity?", elapsed: 11.25, chunks: 5 },
    { question: "What is a system prompt?", elapsed: 7.65, chunks: 5 },
    { question: "What is the capital of France? (unanswerable)", elapsed: 4.63, chunks: 5 },
  ],
};

export const designNotes = [
  {
    title: "Storage",
    body: "SQLite with embeddings stored as JSON text. Simple and dependency-free. For larger knowledge bases (10,000+ chunks), a dedicated vector database (Chroma, Qdrant) would be faster.",
  },
  {
    title: "Chunking",
    body: "Paragraph-level splits. Works well for structured text; may miss context for very short or very long paragraphs.",
  },
  {
    title: "Relevance threshold",
    body: "Chunks with cosine similarity < 0.2 are excluded. Adjustable via RELEVANCE_THRESHOLD in rag.py.",
  },
  {
    title: "Models",
    body: "qwen3-embedding-0.6b (fast, compact) + phi-3.5-mini (good quality/speed balance). Larger models will give better answers but run slower.",
  },
  {
    title: "Offline",
    body: "All inference runs locally. No data leaves the machine.",
  },
];

export const lessonsLearned = [
  {
    title: "Chunking strategy directly determines retrieval quality.",
    body: "Early tests used top_k=3. A question about the recommended embedding model consistently failed because the relevant chunk ranked 4th. Increasing top_k to 5 resolved it — but also grew the context window.",
  },
  {
    title: "Relevance threshold tuning is non-trivial.",
    body: "The initial threshold of 0.3 was too strict: some valid answers were filtered out. After lowering to 0.2, all 10 answerable questions passed.",
  },
  {
    title: "Model warm-up dominates first-query latency.",
    body: "The first query took ~28s because both models had to be loaded into memory. Subsequent queries averaged ~8s. Pre-loading models at startup would eliminate this perceived slowness.",
  },
];
