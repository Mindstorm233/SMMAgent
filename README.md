# 🧬 SMM Agent Project

## Microfluidics Protocol → BioChip Design → Layout Rendering

SMM Agent is a lightweight microfluidic design system that turns **natural-language experimental protocols** into **structured biochip designs**, then optionally renders them into **layout images** for visualization and review.

It combines:

* 🤖 a **two-stage LLM pipeline**
* 📚 **RAG** with a local **Chroma** vector store
* 🌐 a **FastAPI** backend with static web pages
* 🖼️ optional **scheme/layout rendering**
* 🗂️ local **history persistence** for completed runs

---

## Features

* ✅ Build a local **RAG knowledge base** from a Markdown file (`data/knowledge.md`)
* ✅ Two-stage compilation pipeline:

  * RAG retrieval → Generator → Verifier
* ✅ Output structured design as a Pydantic model (`BioChipDesign`)
* ✅ Render the final design into a **microfluidic layout image**
* ✅ Web UI:

  * `/` shows the Generator page
  * `/history.html` shows persisted local history
* ✅ Persist each completed run under `./history/` with:

  * original protocol text
  * draft JSON
  * final JSON
  * generated scheme / layout image
  * metadata

---

## Project Structure (Typical)

```text
microchip_designer/
├─ server.py
├─ cli.py
├─ build_knowledge.py
├─ requirements.txt
├─ core/
│  ├─ __init__.py
│  ├─ agent.py
│  ├─ knowledge_builder.py
│  ├─ rag.py
│  └─ schema.py
├─ draw/
│  ├─ __init__.py
│  ├─ components.py
│  ├─ layout.py
│  └─ renderer.py
├─ data/
│  ├─ knowledge.md
│  ├─ compiler_prompt.md
│  └─ verifier_prompt.md
├─ chroma_db/              # created after building the knowledge base
├─ history/                # persisted run history, created automatically
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
* The dependencies required by your rendering backend in `draw/`

> The renderer may require additional graphics-related Python packages or system libraries depending on how `draw.renderer.draw_chip(...)` is implemented.

---

## 1) Create Your Environment

### Option A: Conda (recommended)

```bash
conda create -n smmagent python=3.12
conda activate smmagent

pip install -U langchain
pip install langchain-openai langchain_community langchain-chroma
pip install python-dotenv chromadb fastapi uvicorn tqdm
pip install schemdraw
```

### Option B: venv

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -U langchain
pip install langchain-openai langchain_community langchain-chroma
pip install python-dotenv chromadb fastapi uvicorn tqdm
pip install schemdraw
```

### Option C: install directly from `requirements.txt`

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Optional: install Jupyter

```bash
pip install jupyter
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

# optional: history root
HISTORY_DIR=./history
```

* `API_BASE` should point to your LLM gateway.
* `llm_model_name` and `embedding_model_name` should match what your API supports.
* `HISTORY_DIR` controls where completed runs are persisted.

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

---

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

## 6) Rendering the Microfluidic Layout

The project can render the final design JSON into a visual microfluidic layout through the `draw` package.

Typical usage:

```python
from draw.renderer import draw_chip

chip_data = {}
draw_chip(chip_data, "microfluidic_layout.png")
```

Supported output formats depend on the renderer implementation, but common examples include:

* `.png`
* `.svg`
* `.pdf`

In the web workflow, the backend can call the renderer automatically after a successful compile and persist the output image into the corresponding history directory.

---

## 7) API Summary

Main endpoints:

* `POST /api/v1/compile` — submit a compile job
* `GET /api/v1/jobs/{job_id}` — check job status
* `GET /api/v1/compile/{compile_id}/result` — fetch compile result
* `POST /api/v1/draw` — render layout from JSON
* `GET /api/v1/history` — list persisted runs
* `GET /api/v1/history/{compile_id}` — load one historical run
* `DELETE /api/v1/history/{compile_id}` — delete one historical run
* `GET /api/v1/compile/{compile_id}/layout.png` — get saved or regenerated layout image

---

## 8) Frontend Summary

### Generator Page (`/`)

Provides protocol input, async generation, progress tracking, and result tabs:
**JSON / Compare / Evidence / Runbook / Schemes**

### History Page (`/history.html`)

Provides searchable persisted history, detailed run review, and deletion support.
Tabs include:
**Protocol / JSON / Compare / Evidence / Runbook / Schemes**
