# SMM Agent Project (Microfluidics Protocol → BioChip Design)

This project implements a **two-stage microfluidics/biochip design agent**:

* **Stage 1 (Generator):** converts an experimental protocol (natural language) into a structured chip design.
* **Stage 2 (Verifier):** validates and minimally repairs the design to satisfy strict schema + connectivity + port rules.

It supports **RAG (Retrieval-Augmented Generation)** using **Chroma** as a local vector store and a static web UI served by **FastAPI**.

---

## Features

* ✅ Build a local **RAG knowledge base** from a Markdown file (`data/knowledge.md`)
* ✅ Two-stage compilation pipeline:

  * RAG retrieval → Generator → Verifier
* ✅ Output structured design as a Pydantic model (`BioChipDesign`)
* ✅ Web UI:

  * `/` shows the Generator page
  * `/history.html` shows local history (current MVP stores in memory unless you add persistence)

---

## Project Structure (Typical)

```text
microchip_designer/
├─ server.py
├─ cli.py
├─ build_knowledge.py
├─ core/
│  ├─ __init__.py
│  ├─ agent.py
│  ├─ knowledge_builder.py
│  ├─ rag.py
│  └─ schema.py
├─ data/
│  ├─ knowledge.md
│  ├─ compiler_prompt.md
│  └─ verifier_prompt.md
├─ chroma_db/              # created after building the knowledge base
└─ static/
   ├─ index.html
   ├─ history.html
   ├─ api_test.html        # optional: manual API testing page
   ├─ css/...
   └─ js/...
```

---

## Requirements

* Python **3.12** (recommended)
* A compatible LLM API endpoint (your custom `API_BASE`) that supports:

  * chat completions (structured output preferred)
  * embeddings

---

## 1) Create Your Environment

### Option A: Conda (recommended)

```bash
conda create -n smmagent python=3.12
conda activate smmagent

pip install -U langchain
pip install langchain-openai langchain_community langchain-chroma
pip install python-dotenv chromadb fastapi uvicorn
```

### Option B: venv

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U langchain
pip install langchain-openai langchain_community langchain-chroma
pip install python-dotenv chromadb fastapi uvicorn
```

> If you use `tqdm` for progress bars while building the KB:

```bash
pip install tqdm
```

---

## 2) Configure Environment Variables

Create a `.env` file in the project root:

```ini
API_BASE=http://127.0.0.1:8001/v1
API_KEY=YOUR_API_KEY

# model names used across CLI + server
llm_model_name=DeepSeek-V3.2
embedding_model_name=GLM-Embedding-2

# optional
temperature=0.0
```

* `API_BASE` should point to your LLM gateway (your LLMapi).
* `llm_model_name` and `embedding_model_name` should match what your API supports.

---

## 3) Build the Knowledge Base (Chroma)

Before running the compiler, build a local vector database from `data/knowledge.md`.

### Using build_knowledge.py

```bash
python build_knowledge.py --input ./data/knowledge.md --output ./chroma_db
```

### Or using the CLI helper

```bash
python cli.py build-kb --input ./data/knowledge.md --output ./chroma_db
```

This will:

* Load Markdown
* Split by header structure and chunk size
* Embed chunks
* Persist to `./chroma_db`

---

## 4) Run the Web Server (FastAPI)

Start the server:

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Then open:

* UI home: `http://127.0.0.1:8000/`
* History: `http://127.0.0.1:8000/history.html`
* Optional API tester: `http://127.0.0.1:8000/api_test.html`

## 5) Run CLI Compilation (Optional)

You can run the two-stage compiler directly via CLI:

```bash
python cli.py compile \
  --db-path ./chroma_db \
  --compiler-prompt ./data/compiler_prompt.md \
  --verifier-prompt ./data/verifier_prompt.md \
  --output ./data/final_design.json
```

Or provide a protocol file:

```bash
python cli.py compile --protocol ./data/protocol.txt
```

---

## 6) Prompts

* `data/compiler_prompt.md` — Generator prompt (“protocol compiler”)
* `data/verifier_prompt.md` — Verifier prompt (“structured validator + repair”)

**Tip:** If validations fail frequently, tighten:

* allowed keys / exact schema keys
* port naming requirements
* “only declare ports you actually use”
* force final output to be strict JSON only
